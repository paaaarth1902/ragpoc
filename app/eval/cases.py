from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class EvalCase:
    question: str
    expected_chunk_ids: set[int]
    should_answer: bool


EVAL_CASES: list[EvalCase] = [
    # --- semantic queries  ---
    EvalCase("How do I resume a paused SLA timer?", {60, 62}, True),
    EvalCase("How do I pause an active SLA?", {65, 67}, True),

    # --- sibling disambiguation (must pick resume, not pause) ---
    EvalCase("Which action turns the SLA badge green?", {60, 62, 63}, True),

    # --- EXACT-TERM queries ---
    EvalCase("escalate P1 major incident", {70, 72}, True),
    EvalCase("P1 acknowledge within 5 minutes", {73}, True),
    EvalCase("Set-ADAccountPassword reset command", {77}, True),
    EvalCase("VPN error VPN-619", {82, 84}, True),
    EvalCase("VPN-619 gateway rejected credentials", {82}, True),

    # --- off-topic (must REFUSE) ---
    EvalCase("What is the capital of France?", set(), False),
    EvalCase("How do I bake a chocolate cake?", set(), False),
]