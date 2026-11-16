"""Consume matching requests and dead-letter invalid messages."""
import json
import re
import sys

import pika

EXCHANGE = "rapido-dispatch"
DEAD_LETTER_EXCHANGE = "rapido-dispatch.dlx"
REQUIRED_FIELDS = {"id", "city", "zone", "type", "ts"}


def validate_message(message):
    if not isinstance(message, dict):
        return False, "Message body must be a JSON object"
    missing = sorted(REQUIRED_FIELDS - message.keys())
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    if message["type"] not in {"ride", "food"}:
        return False, "Unsupported request type"
    return True, ""


def main():
    if len(sys.argv) != 3:
        print("Usage: python driver.py NAME PATTERN")
        raise SystemExit(1)

    name, pattern = sys.argv[1], sys.argv[2]
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "-", name)
    queue_name = f"driver.{safe_name}"
    dlq_name = f"{queue_name}.dlq"

    params = pika.ConnectionParameters(
        host="localhost",
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE, exchange_type="topic", durable=True
    )
    channel.exchange_declare(
        exchange=DEAD_LETTER_EXCHANGE, exchange_type="fanout", durable=True
    )
    channel.queue_declare(queue=dlq_name, durable=True)
    channel.queue_bind(
        exchange=DEAD_LETTER_EXCHANGE, queue=dlq_name
    )

    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={"x-dead-letter-exchange": DEAD_LETTER_EXCHANGE},
    )
    channel.queue_bind(
        exchange=EXCHANGE, queue=queue_name, routing_key=pattern
    )
    channel.basic_qos(prefetch_count=1)

    def process_message(ch, method, properties, body):
        try:
            message = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"{name} | NACK | Invalid JSON: {exc}", flush=True)
            ch.basic_nack(
                delivery_tag=method.delivery_tag, requeue=False
            )
            return

        valid, reason = validate_message(message)
        if not valid:
            print(f"{name} | NACK | {reason} | {message}", flush=True)
            ch.basic_nack(
                delivery_tag=method.delivery_tag, requeue=False
            )
            return

        print(
            f"{name} | ACK | {method.routing_key} | {message}",
            flush=True,
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    print(
        f"{name} listening with pattern: {pattern}; "
        f"queue: {queue_name}; dead-letter queue: {dlq_name}",
        flush=True,
    )
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=process_message,
        auto_ack=False,
    )
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"{name} stopped", flush=True)
        channel.stop_consuming()
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
