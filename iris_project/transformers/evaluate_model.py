import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer, test

@transformer
def evaluate_model(result, *args, **kwargs):
    y_true = result['y_test']
    y_pred = result['predictions']
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
    report = classification_report(
        y_true, y_pred, labels=[0, 1, 2],
        target_names=['setosa', 'versicolor', 'virginica'],
        output_dict=True, zero_division=0,
    )
    metrics = pd.DataFrame(report).transpose().reset_index(names='class')
    print('Confusion matrix (rows=actual, columns=predicted):')
    print(cm)
    print(metrics.to_string(index=False))
    return {
        'confusion_matrix': cm.tolist(),
        'metrics': metrics.to_dict(orient='records'),
        'accuracy': float(accuracy_score(y_true, y_pred)),
    }

@test
def test_output(output, *args):
    assert len(output['confusion_matrix']) == 3
    assert all(len(row) == 3 for row in output['confusion_matrix'])
    assert output['accuracy'] >= 0.70
