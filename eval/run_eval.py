"""
eval/run_eval.py

Validates the pipeline against KNOWN ground truth (ingestion/case_generator.py
labels every synthetic case with its true category, urgency, and correct KB
topic). Measures:
  1. Category routing accuracy
  2. Urgency routing accuracy
  3. KB retrieval accuracy (topic match), for cases where KB was consulted
  4. Escalation reachability: confirms critical/low-confidence cases actually escalate
"""
from ingestion.case_generator import generate_cases
from agents.graph import run_case


def run(n_cases: int = 150):
    cases = generate_cases(n=n_cases, seed=99)
    results = [run_case(c) for c in cases]

    category_correct = sum(1 for c, r in zip(cases, results) if r["category"] == c["true_category"])
    urgency_correct = sum(1 for c, r in zip(cases, results) if r["urgency"] == c["true_urgency"])

    kb_checked = [(c, r) for c, r in zip(cases, results) if not r["escalated"]]
    kb_correct = sum(1 for c, r in kb_checked if r["kb_match"]["topic"] == c["true_kb_topic"])

    escalated_cases = [(c, r) for c, r in zip(cases, results) if r["escalated"]]
    critical_true = [c for c in cases if c["true_urgency"] == "critical"]
    critical_escalated = [
        (c, r) for c, r in zip(cases, results) if c["true_urgency"] == "critical" and r["escalated"]
    ]

    print(f"Total cases: {len(cases)}")
    print(f"Category routing accuracy: {category_correct}/{len(cases)} = {category_correct/len(cases):.1%}")
    print(f"Urgency routing accuracy:  {urgency_correct}/{len(cases)} = {urgency_correct/len(cases):.1%}")
    if kb_checked:
        print(f"KB retrieval accuracy (non-escalated cases): {kb_correct}/{len(kb_checked)} = {kb_correct/len(kb_checked):.1%}")
    print(f"Total escalated: {len(escalated_cases)}/{len(cases)} ({len(escalated_cases)/len(cases):.1%})")
    if critical_true:
        print(f"Critical-urgency cases correctly escalated: {len(critical_escalated)}/{len(critical_true)}")
        print("PASS: escalation path is reachable and fires on critical cases"
              if len(critical_escalated) == len(critical_true)
              else "WARNING: some critical cases did NOT escalate -- investigate before trusting this pipeline")

    print("\n--- Sample escalated case ---")
    if escalated_cases:
        c, r = escalated_cases[0]
        print(f"transcript: {r['transcript']}")
        print(f"true urgency: {c['true_urgency']} | predicted: {r['urgency']}")
        print(f"reply: {r['reply']}")


if __name__ == "__main__":
    run()
