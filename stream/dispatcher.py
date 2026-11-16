"""Publish sample ride/food requests to the rapido-dispatch topic exchange."""
import json
import random
import time
import uuid
from datetime import datetime, timezone

import pika

EXCHANGE = "rapido-dispatch"
CITIES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "whitefield"],
}
PUBLISH_INTERVAL_SECONDS = 2


def main():
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

    count = 0
    try:
        while True:
            count += 1
            city = random.choice(list(CITIES))
            zone = random.choice(CITIES[city])
            request_type = random.choice(["ride", "food"])
            routing_key = f"{city}.{zone}.{request_type}"
            message = {
                "id": str(uuid.uuid4()),
                "city": city,
                "zone": zone,
                "type": request_type,
                "ts": datetime.now(timezone.utc).isoformat(),
            }

            # Deliberately publish one invalid event every 10 messages
            # to demonstrate consumer rejection and dead-letter handling.
            if count % 10 == 0:
                message.pop("zone")

            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
                mandatory=True,
            )
            print(
                f"PUBLISHED #{count} | {routing_key} | {message}",
                flush=True,
            )
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Dispatcher stopped", flush=True)
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
