import pandas as pd
from pathlib import Path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter, test

@data_exporter
def save_results(result, *args, **kwargs):
    output = pd.DataFrame({
        'actual': result['y_test'],
        'predicted': result['predictions'],
    })
    output_path = Path('iris_predictions.csv')
    output.to_csv(output_path, index=False)
    print(f'Saved {len(output)} predictions to {output_path.resolve()}')
    return str(output_path.resolve())

@test
def test_output(output, *args):
    assert output is not None
    assert Path(output).exists()
    saved = pd.read_csv(output)
    assert len(saved) == 30
