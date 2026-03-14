"""Interfaces for MUSR team allocation."""

from secretagent.core import interface


@interface
def extract_profiles(narrative: str) -> str:
    """Extract person profiles and role requirements from the narrative.

    For each person, assess their fit for each role on a 1-5 scale:
    1 = severely unfit (phobia, allergy, physical danger)
    2 = poor fit (discomfort but could manage)
    3 = neutral
    4 = good fit (relevant skills/experience)
    5 = excellent fit

    Also note interpersonal constraints (conflicts, synergies).
    """


@interface
def evaluate_allocations(narrative: str, profiles: str, question: str, choices: list) -> int:
    """Given person profiles and allocation choices, pick the best assignment.

    For each choice, sum the fit scores. Prefer choices with fewer
    score-1 (severely unfit) assignments. When all choices have problems,
    pick the least bad one.
    Return the 0-based index of the best choice.
    """


@interface
def answer_question(narrative: str, question: str, choices: list) -> int:
    """Read the narrative and determine the best team allocation.
    Return the 0-based index of the correct choice.
    """
    profiles = extract_profiles(narrative)
    return evaluate_allocations(narrative, profiles, question, choices)
