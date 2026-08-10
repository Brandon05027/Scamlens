import json
from dataclasses import dataclass
from pathlib import Path

from app.services.analysis import analyze_text


DATASET_PATH = Path(__file__).with_name("dataset.json")


@dataclass(frozen=True)
class EvaluationCounts:
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int


@dataclass(frozen=True)
class EvaluationMetrics:
    accuracy: float
    precision: float
    recall: float
    false_positive_rate: float
    false_negative_rate: float


def is_scam_prediction(
    risk_score: int,
    threshold: int = 20, #default number
) -> bool:
    return risk_score >= threshold 

def evaluate_threshold(
    dataset: list[dict[str, str]],
    threshold: int,
) -> tuple[EvaluationCounts, EvaluationMetrics]:
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    for example in dataset:
        result = analyze_text(example["text"])

        actual_is_scam = example["label"] == "scam"
        predicted_is_scam = is_scam_prediction(
            result.risk_score,
            threshold,
        )

        if actual_is_scam and predicted_is_scam:
            true_positive += 1
        elif not actual_is_scam and predicted_is_scam:
            false_positive += 1
        elif not actual_is_scam and not predicted_is_scam:
            true_negative += 1
        else:
            false_negative += 1

    counts = EvaluationCounts(
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
    )

    return counts, calculate_metrics(counts)

def calculate_metrics(
    counts: EvaluationCounts,
) -> EvaluationMetrics:
    total = (
        counts.true_positive
        + counts.false_positive
        + counts.true_negative
        + counts.false_negative
    )

    predicted_positive = (
        counts.true_positive
        + counts.false_positive
    )

    actual_positive = (
        counts.true_positive
        + counts.false_negative
    )

    actual_negative = (
        counts.true_negative
        + counts.false_positive
    )

    accuracy = (
        (
            counts.true_positive
            + counts.true_negative
        )
        / total
        if total
        else 0.0
    )

    precision = (
        counts.true_positive / predicted_positive
        if predicted_positive
        else 0.0
    )

    recall = (
        counts.true_positive / actual_positive
        if actual_positive
        else 0.0
    )

    false_positive_rate = (
        counts.false_positive / actual_negative
        if actual_negative
        else 0.0
    )

    false_negative_rate = (
        counts.false_negative / actual_positive
        if actual_positive
        else 0.0
    )

    return EvaluationMetrics(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        false_positive_rate=false_positive_rate,
        false_negative_rate=false_negative_rate,
    )


def load_dataset() -> list[dict[str, str]]:
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as dataset_file:
        return json.load(dataset_file)


def run_evaluation() -> None:
    dataset = load_dataset()

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    mistakes: list[dict[str, object]] = []

    for example in dataset:
        result = analyze_text(example["text"])

        actual_is_scam = example["label"] == "scam"
        predicted_is_scam = is_scam_prediction(
            result.risk_score
        )

        if actual_is_scam and predicted_is_scam:
            true_positive += 1

        elif not actual_is_scam and predicted_is_scam:
            false_positive += 1

            mistakes.append(
                {
                    "id": example["id"],
                    "type": "false_positive",
                    "score": result.risk_score,
                    "text": example["text"],
                }
            )

        elif not actual_is_scam and not predicted_is_scam:
            true_negative += 1

        else:
            false_negative += 1

            mistakes.append(
                {
                    "id": example["id"],
                    "type": "false_negative",
                    "score": result.risk_score,
                    "text": example["text"],
                }
            )

    counts = EvaluationCounts(
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
    )

    metrics = calculate_metrics(counts)

    print()
    print("ScamLens Evaluation")
    print("=" * 40)
    print(f"Examples: {len(dataset)}")
    print()

    print("Confusion matrix")
    print("-" * 40)
    print(f"True positives:  {counts.true_positive}")
    print(f"False positives: {counts.false_positive}")
    print(f"True negatives:  {counts.true_negative}")
    print(f"False negatives: {counts.false_negative}")
    print()

    print("Metrics")
    print("-" * 40)
    print(f"Accuracy:            {metrics.accuracy:.1%}")
    print(f"Precision:           {metrics.precision:.1%}")
    print(f"Recall:              {metrics.recall:.1%}")
    print(
        "False-positive rate: "
        f"{metrics.false_positive_rate:.1%}"
    )
    print(
        "False-negative rate: "
        f"{metrics.false_negative_rate:.1%}"
    )

    print()
    print("Threshold comparison")
    print("-" * 65)

    print(
        f"{'Threshold':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'FPR':<12}"
        f"{'FNR':<12}"
        )

    for threshold in (10, 12, 15, 20, 25, 30):
        _, threshold_metrics = evaluate_threshold(
            dataset,
            threshold,
        )

        print(
            f"{threshold:<12}"
            f"{threshold_metrics.precision:<12.1%}"
            f"{threshold_metrics.recall:<12.1%}"
            f"{threshold_metrics.false_positive_rate:<12.1%}"
            f"{threshold_metrics.false_negative_rate:<12.1%}"
        )

    if mistakes:
        print()
        print("Misclassified examples")
        print("-" * 40)

        for mistake in mistakes:
            print(
                f"{mistake['id']} | "
                f"{mistake['type']} | "
                f"score={mistake['score']}"
            )
            print(mistake["text"])
            print()


if __name__ == "__main__":
    run_evaluation()