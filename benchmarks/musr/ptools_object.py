"""Interfaces for MUSR object placement (theory of mind)."""

from secretagent.core import interface


@interface
def track_movements(narrative: str) -> str:
    """Track all object movements in the narrative.

    For each movement, note:
    - which object moved, from where to where
    - who moved it
    - who was present and witnessed the movement
    - who was absent and did NOT witness it

    Also note any incidental discoveries: when someone sees or
    is told about an object's location without witnessing the move.
    """


@interface
def infer_belief(narrative: str, movements: str, question: str, choices: list) -> int:
    """Given object movement tracking and a question about where someone
    would look for an object, determine their belief about its location.

    The answer depends on what the person SAW, not where the object
    actually is. A person absent during a move still believes the
    object is in its previous location.
    Return the 0-based index of the correct choice.
    """


@interface
def answer_question(narrative: str, question: str, choices: list) -> int:
    """Read the narrative and answer where someone would look for an object.

    This is a theory-of-mind task: the answer is based on what the person
    believes, not the object's actual location.
    Return the 0-based index of the correct choice.
    """
    movements = track_movements(narrative)
    return infer_belief(narrative, movements, question, choices)
