"""Decision-level metrics: confusion matrix, precision and recall."""

from dataclasses import dataclass

DECISIONS = ["BLOCKED", "CONDITIONAL", "BUY_CANDIDATE", "NOT_WORTH_IT", "INSUFFICIENT_DATA"]


@dataclass
class DecisionScore:
    """Precision and recall of one decision over all runs.

    Attributes:
        expected_count: Runs where this decision was the expected one.
        predicted_count: Runs where the model returned this decision.
        correct_count: Runs where expected and returned decision were both this one.
        precision: correct / predicted, None when the model never returned the decision.
        recall: correct / expected, None when the decision was never expected.
    """

    expected_count: int
    predicted_count: int
    correct_count: int
    precision: float | None
    recall: float | None


def build_confusion_matrix(pairs: list[tuple[str, str]]) -> dict[str, dict[str, int]]:
    """Count (expected, got) decision pairs.

    Args:
        pairs: One (expected decision, returned decision) tuple per run.

    Returns:
        matrix[expected][got] = number of runs. Every decision has a row and a column, even when zero.
    """
    matrix = {expected: dict.fromkeys(DECISIONS, 0) for expected in DECISIONS}
    for expected, got in pairs:
        # An output that failed the schema has no valid decision; it is already counted as an error
        if got in matrix[expected]:
            matrix[expected][got] += 1
    return matrix


def compute_decision_scores(matrix: dict[str, dict[str, int]]) -> dict[str, DecisionScore]:
    """Compute precision and recall of every decision from the confusion matrix.

    Args:
        matrix: Output of build_confusion_matrix.

    Returns:
        DecisionScore per decision, in DECISIONS order.
    """
    scores = {}
    for decision in DECISIONS:
        expected_count = sum(matrix[decision].values())
        predicted_count = sum(matrix[expected][decision] for expected in DECISIONS)
        correct_count = matrix[decision][decision]
        scores[decision] = DecisionScore(
            expected_count=expected_count,
            predicted_count=predicted_count,
            correct_count=correct_count,
            precision=correct_count / predicted_count if predicted_count else None,
            recall=correct_count / expected_count if expected_count else None,
        )
    return scores


def format_decision_metrics(matrix: dict[str, dict[str, int]], scores: dict[str, DecisionScore]) -> list[str]:
    """Render the confusion matrix and the precision/recall table as markdown lines.

    Args:
        matrix: Output of build_confusion_matrix.
        scores: Output of compute_decision_scores.

    Returns:
        Markdown lines, rows = expected decision, columns = returned decision.
    """

    def percent(value: float | None) -> str:
        return "-" if value is None else f"{value:.0%}"

    lines = [
        "| expected \\ got | " + " | ".join(DECISIONS) + " |",
        "|---|" + "---|" * len(DECISIONS),
    ]
    for expected in DECISIONS:
        counts = " | ".join(str(matrix[expected][got]) for got in DECISIONS)
        lines.append(f"| {expected} | {counts} |")

    lines += [
        "",
        "| Decision | Expected | Returned | Correct | Precision | Recall |",
        "|---|---|---|---|---|---|",
    ]
    for decision, score in scores.items():
        lines.append(
            f"| {decision} | {score.expected_count} | {score.predicted_count} | {score.correct_count} "
            f"| {percent(score.precision)} | {percent(score.recall)} |"
        )
    return lines
