# FreshCart Pipelines

Repository for the **From Git to Gold** assignment.

## Repository layout

- `elt/` — FreshCart Snowflake ELT notebook and SQL scripts.
  - `freshcart_elt.ipynb` is the notebook already present in this repository.
  - `freshcart_elt_reference.ipynb` and `sql/reference_*.sql` are reference material adapted from a collaborator's organized submission. They are not evidence of execution in this repository owner's Snowflake account.
- `iris_project/` — Mage-style Iris pipeline: loader, validation, preparation, training, evaluation branch, and exporter.
- `stream/` — RabbitMQ topic-exchange dispatcher and driver with ACK/NACK handling.
- `tests/` — pytest test used by GitHub Actions.
- `.github/workflows/ci.yml` — Python 3.12 CI workflow.

## Setup

Use Python 3.12 and create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest -v
```

## Running the components

### FreshCart / Snowflake

Open `elt/freshcart_elt.ipynb` in Colab or Jupyter. Configure your own Snowflake connection securely; never commit credentials. Review SQL in `elt/sql/` and execute it against your own account. The `reference_*` files are adaptation references and contain reconstructed sample-data assumptions; verify them against the assignment's original notebook/data before relying on their outputs.

### Mage Iris pipeline

The Mage block files are under `iris_project/`. The pipeline metadata is in `iris_project/pipelines/iris_classifier/metadata.yaml`. Install the dependencies listed in `iris_project/requirements.txt` in the Mage environment and run the pipeline using the Mage CLI appropriate to your installed Mage version. The repository's root CI test checks the importable `prepare_data.transform` function.

### RabbitMQ stream

Start a local RabbitMQ broker, then run the dispatcher:

```bash
python stream/dispatcher.py
```

In separate terminals, start drivers with binding patterns, for example:

```bash
python stream/driver.py Ravi 'bangalore.koramangala.*'
python stream/driver.py Arjun 'bangalore.*.ride'
python stream/driver.py Control 'bangalore.#'
```

The dispatcher publishes every two seconds and intentionally omits `zone` from every tenth message so drivers can demonstrate NACK with `requeue=False`. These scripts currently use `localhost`; change the connection parameters only if using your own broker. Keep hosted broker URLs and credentials out of Git.

## Evidence and reproducibility

Screenshots and result tables in the assignment report must come from runs performed by the student. Reference notebooks, SQL, and code adapted from another submission are starting points only; independently inspect, adapt, execute, and explain them. Do not describe another person's account executions as your own.
