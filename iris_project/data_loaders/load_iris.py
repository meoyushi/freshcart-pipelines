import pandas as pd
from sklearn.datasets import load_iris

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader, test

@data_loader
def load_iris_data(*args, **kwargs):
    dataset = load_iris(as_frame=True)
    df = dataset.frame.copy()
    df['species'] = df['target'].map(dict(enumerate(dataset.target_names)))
    return df

@test
def test_output(output, *args):
    assert isinstance(output, pd.DataFrame)
    assert len(output) == 150
    assert 'target' in output.columns
