import json
from app.kafka import producer

def eventManager():
    event_json = eventJsonGenerator()
    print(f"Event json generated")
    producer.producer_send(event_json)
    
def eventJsonGenerator():
    # Generate a sample event JSON object
    event = {
        "userId": "12345",
        "eventType": "click",
        "timestamp": "2024-06-01T12:34:56Z",
        "details": {
            "page": "homepage",
            "buttonId": "signup"
        }
    }
    return event