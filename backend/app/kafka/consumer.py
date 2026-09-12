from confluent_kafka import Consumer
from app.postgres import postgres_handler

import json
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'postgres-consumer-group',
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest'
})

def consumer_subscribe():
    try:
        consumer.subscribe(['curato_user_events'])
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            event_json = json.loads(msg.value().decode('utf-8'))
            print(f"Received event: {event_json}")
            try:
                 postgres_handler.send_to_postgres(event_json)
                 print(f"Event sent to PostgreSQL:")
                 consumer.commit(message=msg)
            except Exception as e:
                 print(f"Error sending event to PostgreSQL: {e}")     
    except Exception as e:
        print(f"Error at consumer_subscribe: {e}")
    finally:
        consumer.close()