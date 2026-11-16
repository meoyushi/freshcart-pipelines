from sklearn.datasets import load_iris

from iris_project.transformers.extra_quality_check import extra_quality_check


def test_extra_quality_check_accepts_valid_iris_data():
    df = load_iris(as_frame=True).frame
    assert len(extra_quality_check(df)) == 150


def test_extra_quality_check_rejects_missing_values():
    df = load_iris(as_frame=True).frame.copy()
    df.loc[0, "sepal length (cm)"] = float("nan")
    try:
        extra_quality_check(df)
    except ValueError as exc:
        assert "missing values" in str(exc)
    else:
        raise AssertionError("Expected missing-value validation to fail")
