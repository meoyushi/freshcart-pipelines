if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer, test

@transformer
def validate_data(df, *args, **kwargs):
    assert not df.isnull().any().any(), 'Iris data contains missing values'
    assert df['target'].nunique() == 3, 'Expected exactly 3 classes'
    return df

@test
def test_output(output, *args):
    assert output.isnull().sum().sum() == 0
    assert output['target'].nunique() == 3
