from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer, test

def _runtime_depth(kwargs):
    runtime_vars = kwargs.get('runtime_vars') or {}
    context = kwargs.get('context') or {}
    if not runtime_vars:
        runtime_vars = context.get('runtime_vars') or context.get('variables') or {}
    if not runtime_vars:
        pipeline_run = context.get('pipeline_run') or {}
        runtime_vars = pipeline_run.get('variables') or {}
    depth = runtime_vars.get('max_depth', kwargs.get('max_depth', 3))
    return int(depth)

@transformer
def train_model(df, *args, **kwargs):
    depth = _runtime_depth(kwargs)
    features = [c for c in df.columns if c not in ('target', 'species', 'split')]
    train = df[df['split'] == 'train']
    test = df[df['split'] == 'test']
    model = DecisionTreeClassifier(max_depth=depth, random_state=42)
    model.fit(train[features], train['target'])
    predictions = model.predict(test[features])
    accuracy = float(accuracy_score(test['target'], predictions))
    return {
        'model': model,
        'features': features,
        'max_depth': depth,
        'accuracy': accuracy,
        'y_test': test['target'].tolist(),
        'predictions': predictions.tolist(),
        'test_features': test[features].to_dict(orient='records'),
    }

@test
def test_output(output, *args):
    assert output is not None
    assert output['accuracy'] >= 0.70, (
        f"Accuracy {output['accuracy']:.3f} is below the 0.70 quality threshold; "
        'downstream exporters must not run.'
    )
