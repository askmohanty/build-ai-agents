"""Project 13: evaluate the RAG assistant from project 08.

For each question in questions.jsonl we measure three things:

  retrieval   did search return the runbook that holds the answer?
  facts       does the answer contain the facts it must (simple string check)?
  judge       does a second model call, given the sources, rate the answer
              as correct and grounded (LLM-as-judge)?

    python 08-chat-with-docs-rag/ingest.py      # once
    python 13-evals/run_evals.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "08-chat-with-docs-rag"))
import rag  # noqa: E402

from agentkit import extract  # noqa: E402

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "correct": {"type": "boolean", "description": "Answers the question correctly"},
        "grounded": {"type": "boolean", "description": "Every claim is supported by the sources"},
        "score": {"type": "integer", "description": "1 (wrong) to 5 (fully correct and grounded)"},
        "reason": {"type": "string"},
    },
    "required": ["correct", "grounded", "score", "reason"],
}


def judge(question: str, answer: str, sources: list[dict]) -> dict:
    context = "\n\n".join(f"({s['source']})\n{s['text']}" for s in sources)
    return extract(
        f"Question: {question}\n\nSources:\n{context}\n\nAnswer to grade:\n{answer}\n\n"
        "If the sources do not contain the answer, the correct answer is to say so.",
        name="grade",
        description="Grade the answer",
        schema=JUDGE_SCHEMA,
        system="You are a strict grader of answers from a documentation assistant.",
    )


def main() -> None:
    cases = [json.loads(line) for line in (HERE / "questions.jsonl").read_text().splitlines() if line.strip()]
    results = []
    for case in cases:
        answer, sources = rag.answer(case["question"])
        retrieved = [s["source"] for s in sources]
        result = {
            **case,
            "answer": answer,
            "retrieved": retrieved,
            "retrieval_ok": case["source"] is None or case["source"] in retrieved,
            "facts_ok": all(fact.lower() in answer.lower().replace("’", "'") for fact in case["must_mention"]),
            "judge": judge(case["question"], answer, sources),
        }
        results.append(result)
        mark = lambda ok: "PASS" if ok else "FAIL"  # noqa: E731
        print(
            f"{mark(result['retrieval_ok'])} retrieval  {mark(result['facts_ok'])} facts  "
            f"judge {result['judge']['score']}/5  {case['question']}"
        )

    n = len(results)
    print(
        f"\nRetrieval {sum(r['retrieval_ok'] for r in results)}/{n}   "
        f"Facts {sum(r['facts_ok'] for r in results)}/{n}   "
        f"Judge: correct {sum(r['judge']['correct'] for r in results)}/{n}, "
        f"grounded {sum(r['judge']['grounded'] for r in results)}/{n}, "
        f"mean score {sum(r['judge']['score'] for r in results) / n:.1f}/5"
    )

    out = HERE / "results" / f"{datetime.now():%Y%m%d-%H%M%S}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"Details: {out}")


if __name__ == "__main__":
    main()
