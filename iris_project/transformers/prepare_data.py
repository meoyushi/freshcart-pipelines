
from sklearn.model_selection import train_test_split


def transform(df):
    train_indices, test_indices = train_test_split(
        df.index,
        test_size=0.2,
        random_state=42,
        stratify=df["target"]
    )

    out = df.copy()
    out["split"] = "train"
    out.loc[test_indices, "split"] = "test"

    return out
