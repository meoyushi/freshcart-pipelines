# Mage Iris classifier project

Part C implementation for the Iris classification pipeline. The project uses scikit-learn's built-in Iris dataset and Mage blocks.

## Pipeline

`load_iris -> validate_data -> extra_quality_check -> prepare_data -> train_model -> (save_results, evaluate_model)`

- `load_iris` loads 150 rows and adds readable species labels.
- `validate_data` checks for nulls and exactly three target classes.
- `extra_quality_check` independently checks required feature/target columns, nulls, non-empty input, and three classes.
- `prepare_data` assigns a stratified 80:20 train/test split (120/30) with `random_state=42`.
- `train_model` trains a decision tree using `max_depth` (default 3) and enforces test accuracy >= 0.70.
- `save_results` exports 30 actual/predicted pairs to `iris_predictions.csv`.
- `evaluate_model` prints a 3x3 confusion matrix and per-class classification metrics.

## Local tests

From the directory containing `iris_project`, run:

```bash
python -m pip install -r iris_project/requirements.txt
python -m pytest iris_project/tests -q
```

## Run in Mage

Run these commands from the directory containing the `iris_project` folder:

```bash
mage run iris_project iris_classifier --test
```

For the max-depth experiment, remove the previous `iris_predictions.csv` before each run and execute:

```bash
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 1}'
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 2}'
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 3}'
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 4}'
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 5}'
```

The training block's quality test is expected to stop downstream execution whenever test accuracy is below 0.70. The exact results must be captured from the user's own Mage run; this repository does not claim a Mage execution has been performed in this environment.

## Reproducibility note

This is a reconstructed implementation based on the available assignment context, not a copy of an unavailable classroom Mage notebook. Local Python tests can be run independently of Mage; the full pipeline and runtime-variable behavior still require verification in Mage.
