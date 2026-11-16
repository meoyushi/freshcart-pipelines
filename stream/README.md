# RabbitMQ Food-Order / Dispatch Stream

## Components

- `dispatcher.py`: publishes JSON ride/food request events to the durable
  `rapido-dispatch` topic exchange.
- `driver.py`: consumes events matching a topic pattern using manual ACKs.
- Invalid JSON or messages missing required fields are rejected with
  `requeue=False` and routed to a durable dead-letter queue (DLQ).

## Message shape

A valid event contains `id`, `city`, `zone`, `type`, and `ts`.
`type` must be `ride` or `food`.

The dispatcher intentionally removes `zone` from every tenth event to
exercise validation and dead-letter handling. Its routing key is constructed
before the field is removed, so the invalid event still reaches a matching
consumer.

## Requirements

Python 3.10+ and RabbitMQ running on `localhost:5672`.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run

Start RabbitMQ first. In separate terminals:

```bash
python driver.py bangalore-food "bangalore.*.food"
python driver.py chennai-food "chennai.*.food"
python dispatcher.py
```

Stop a process with Ctrl+C.

Each consumer uses a durable named queue (`driver.NAME`) and a durable
dead-letter queue (`driver.NAME.dlq`). The consumer uses `prefetch_count=1`
and explicit acknowledgements. Rejected messages are routed through the
durable `rapido-dispatch.dlx` fanout exchange.

## Inspecting rejected messages

Use the RabbitMQ Management UI (if enabled) or `rabbitmqadmin` to inspect
`driver.bangalore-food.dlq` and `driver.chennai-food.dlq`. The expected
invalid events are those with the `zone` field removed.

## Notes

- The topic patterns determine which events a consumer receives.
- A queue persists across consumer restarts; it does not imply that a message
  is processed exactly once. Consumers should make processing idempotent in
  production.
- The live broker workflow has not been executed as part of this local
  source cleanup. Verify it against your RabbitMQ instance and capture your
  own run screenshots for the report.
