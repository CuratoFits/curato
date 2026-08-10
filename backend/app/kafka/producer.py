from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def producer_send(event_json):
    try:
            user_key=event_json["userId"]
            event_json = json.dumps(event_json)
            producer.produce('curato_user_events', value=event_json ,key=user_key)
            print(f"Sent event: {json.loads(event_json)}")
            producer.flush()
    except Exception as e:
        print(f"Error at producer_send: {e}")