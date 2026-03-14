"""Interfaces for MUSR murder mystery reasoning."""

from secretagent.core import interface


@interface
def extract_evidence(narrative: str) -> str:
    """Extract all suspects and evidence from this murder mystery.

    For each suspect, describe their motive, means, opportunity,
    alibi (and whether it holds up), suspicious behavior, and
    any physical evidence linking them to the crime.
    """


@interface
def deduce_answer(narrative: str, evidence: str, question: str, choices: list) -> int:
    """Given a murder mystery, extracted evidence, and answer choices,
    deduce who committed the murder.

    Weigh physical evidence and alibi contradictions most heavily.
    Consider motive as supporting but not sufficient alone.
    Return the 0-based index of the correct choice.
    """


@interface
def answer_question(narrative: str, question: str, choices: list) -> int:
    """Read the murder mystery narrative and answer the question.
    Return the 0-based index of the correct choice.
    """
    evidence = extract_evidence(narrative)
    return deduce_answer(narrative, evidence, question, choices)
