if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer, test

@transformer
def extra_quality_check(data, *args, **kwargs):
    """Validate basic Iris dataset invariants before model training."""
    if data is None or len(data) == 0:
        raise ValueError("Iris dataset is empty")

    required = {
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
        "target",
    }

    missing = required.difference(set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if data[list(required)].isnull().any().any():
        raise ValueError("Iris dataset contains missing values")

    if data["target"].nunique() != 3:
        raise ValueError("Expected exactly three Iris classes")

    return data


@test
def test_extra_quality_check(output, *args):
    assert output is not None
    assert len(output) > 0
    assert output["target"].nunique() == 3
