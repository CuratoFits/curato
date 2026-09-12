# Curato — Kafka Logic & Event Processing

## 1. Purpose

Kafka is used in Curato as the **event-streaming layer** between the ecommerce application and the event-processing/storage layer.

Its primary job is:

> **Receive user interaction events and reliably deliver them to consumers for processing.**

Kafka is **not** responsible for:

* Storing the permanent user history for Curato
* Creating LangGraph user states
* Generating recommendations
* Calculating recommendations
* Deciding what a user's current activity is
* Creating one topic per user

The overall responsibility is divided as follows:

```text
Frontend
    ↓
FastAPI / Service Layer
    ↓
Kafka Producer
    ↓
Kafka
    ↓
Kafka Consumer
    ↓
PostgreSQL
    ↓
Event Fetcher
    ↓
LangGraph State
    ↓
Recommendation System
```

---

# 2. Final Architecture

```text
                    ECOMMERCE WEBSITE
                           │
                           │ User interaction
                           ▼
                    FASTAPI BACKEND
                           │
                           ▼
                    SERVICE LAYER
                           │
                           │ Creates canonical event JSON
                           ▼
                    KAFKA PRODUCER
                           │
                           │ key = userId
                           │ value = event JSON
                           ▼
              ┌───────────────────────────┐
              │           KAFKA           │
              │                           │
              │    curato_user_events     │
              │                           │
              │   P0   P1   P2   P3 ...   │
              └────────────┬──────────────┘
                           │
                           ▼
                    KAFKA CONSUMER
                           │
                           │ Deserialize event
                           ▼
                    POSTGRESQL
                           │
                           │ Permanent event history
                           ▼
                    EVENT FETCHER
                           │
                           │ Fetch user/session data
                           ▼
                   LANGGRAPH STATE
                           │
                           ▼
                    RECOMMENDER
```

---

# 3. Why Kafka Was Added

Initially, user interactions could directly update the backend/state.

Kafka was introduced between the interaction layer and the event-processing layer so that user events become an **event stream**.

Instead of:

```text
User interaction
      ↓
Backend
      ↓
Direct processing
```

the system becomes:

```text
User interaction
      ↓
Backend
      ↓
Kafka
      ↓
Consumer
      ↓
Processing
```

This gives Curato an asynchronous and scalable event pipeline.

---

# 4. What Is a Kafka Topic?

A Kafka **topic** is a named stream/category of messages.

For Curato, the chosen topic is:

```text
curato_user_events
```

All relevant user interaction events are sent to this topic.

Examples:

```text
viewed
searched
clicked
liked
added_to_cart
purchased
```

The event type is stored **inside the message**.

The topic is NOT separated into:

```text
liked_topic
purchased_topic
cart_topic
```

and it is also NOT separated into one topic per user.

---

# 5. Original Topic Design and Why It Was Changed

## Original idea

The initial idea was:

```text
Kafka
│
├── User 1 topic
│     ├── liked partition
│     ├── purchased partition
│     ├── cart partition
│     └── viewed partition
│
├── User 2 topic
│     ├── liked partition
│     ├── purchased partition
│     └── ...
│
└── User 3 topic
      └── ...
```

This was reconsidered.

### Problem 1 — Too many topics

If Curato has a large number of users, this could result in an enormous number of Kafka topics.

Kafka topics are infrastructure objects and should not normally be created dynamically for every individual user.

### Problem 2 — Partitions were being used incorrectly

A partition should not represent:

```text
liked
purchased
viewed
searched
```

Partitions primarily exist to allow Kafka to distribute data and processing across multiple parallel lanes.

### Problem 3 — User events would be unnecessarily separated

A user's sequence:

```text
viewed
→ liked
→ added_to_cart
→ purchased
```

would be spread across different partitions if event types were used as partitions.

That makes per-user event ordering and processing more complicated.

---

# 6. Final Topic Design

The final design is:

```text
Topic:
curato_user_events
```

Inside the topic:

```text
curato_user_events
│
├── Partition 0
├── Partition 1
├── Partition 2
├── Partition 3
└── ...
```

Each message contains information about the user and the event.

Example:

```json
{
    "event_id": "abc123",
    "userId": "12345",
    "sessionId": "session789",
    "eventType": "liked",
    "timestamp": "2026-08-10T21:30:00Z",
    "details": {
        "productId": "P123"
    }
}
```

---

# 7. What Is a Partition?

A partition is a **lane inside a Kafka topic**.

For example:

```text
curato_user_events
│
├── Partition 0
├── Partition 1
├── Partition 2
└── Partition 3
```

Partitions allow Kafka to handle messages in parallel.

A partition can contain events belonging to many different users.

For example:

```text
Partition 0

U101 → viewed shoes
U205 → searched laptop
U101 → liked shoes
U309 → viewed phone
U205 → added laptop to cart
U101 → purchased shoes
```

A partition is therefore **not a user state**.

---

# 8. Number of Partitions

Partitions are **not created based directly on the number of users**.

For example:

```text
100 users       → 4 partitions
10,000 users    → 4 partitions
100,000 users   → 4 partitions
```

The number of partitions is mainly decided based on:

* Expected event throughput
* Required processing parallelism
* Number of consumers
* Expected traffic
* Broker capacity
* Message volume

For the initial Curato development environment, a small fixed number such as:

```text
3–4 partitions
```

is sufficient.

Partitions can be increased later as the system grows.

However, changing the partition count can affect key-to-partition mapping, so partition count should not be changed casually.

---

# 9. User ID as Kafka Message Key

The most important Kafka design decision for Curato is:

```text
Kafka message key = userId
```

Example:

```text
Key:
12345

Value:
{
    "userId": "12345",
    "eventType": "liked",
    ...
}
```

Kafka uses the key to determine which partition receives the message.

Therefore, events for the same user are normally routed consistently to the same partition.

Example:

```text
User 12345
    ↓
viewed
    ↓
liked
    ↓
added_to_cart
    ↓
purchased
```

These events can remain ordered within the same partition.

The producer does **not manually select the partition**.

Kafka's partitioner handles it based on the key.

---

# 10. Partition ≠ User

A very important distinction:

```text
Partition ≠ User
```

One partition can contain:

```text
U101
U205
U309
U501
...
```

The application identifies which user's event it received using:

```text
userId
```

For example:

```text
Partition 0
│
├── U101 → liked
├── U205 → searched
├── U101 → cart
└── U309 → viewed
```

The consumer processes the events and uses `userId` to determine which user's data should be updated.

Kafka itself does not create or manage LangGraph user states.

---

# 11. User State Is Not Connected to a Partition

It is incorrect to think:

```text
Partition 0 → State 0
Partition 1 → State 1
```

Instead:

```text
Partition 0
│
├── U101 event → U101 data/state
├── U205 event → U205 data/state
└── U309 event → U309 data/state
```

The user ID identifies the user.

The application decides how that user's data is stored or represented.

---

# 12. Event Types

Curato can track many ecommerce events.

## Discovery / Browsing

```text
search
view_product
view_category
view_brand
view_collection
view_homepage
view_search_results
view_recommendation
```

## Product Interaction

```text
click_product
like_product
unlike_product
favorite_product
remove_from_favorites
share_product
compare_product
zoom_product_image
view_product_image
view_product_video
```

## Cart

```text
add_to_cart
remove_from_cart
increase_cart_quantity
decrease_cart_quantity
view_cart
```

## Checkout / Purchase

```text
begin_checkout
add_shipping_info
add_payment_info
purchase
cancel_purchase
return_product
refund_product
```

## Search Behaviour

```text
search
search_filter_applied
search_sort_applied
search_result_clicked
search_result_skipped
```

## Session / Account

```text
signup
login
logout
session_start
session_end
```

## Recommendation-Specific Events

These are particularly useful for evaluating Curato:

```text
recommendation_shown
recommendation_clicked
recommendation_ignored
recommendation_liked
recommendation_added_to_cart
recommendation_purchased
```

These events allow Curato to distinguish between:

```text
User purchased product
```

and:

```text
Curato recommended product
        ↓
User purchased product
```

The second case is much more useful for evaluating recommendation quality.

---

# 13. Frontend → Backend → Kafka

The frontend detects the user interaction.

For example:

```text
User clicks "Add to Cart"
```

The frontend can send information to the backend.

The backend/service layer creates the canonical event.

Example:

```json
{
    "event_id": "abc123",
    "userId": "12345",
    "sessionId": "session789",
    "eventType": "add_to_cart",
    "timestamp": "2026-08-10T21:30:00Z",
    "details": {
        "productId": "P123"
    }
}
```

The Kafka producer then transports this event.

The producer should not recreate the event's business logic.

Its job is:

```text
Receive event
    ↓
Extract userId
    ↓
Serialize event
    ↓
Send to Kafka
```

---

# 14. Producer Responsibilities

The producer has a simple responsibility:

> **Take an already-created event and send it to Kafka.**

Conceptually:

```text
Service Layer
      ↓
event JSON
      ↓
Producer
      ↓
Kafka
```

The producer configuration includes:

```text
bootstrap.servers = localhost:9092
```

This tells the producer where the Kafka broker is located.

The producer sends:

```text
topic = curato_user_events
key = userId
value = event JSON
```

---

# 15. Producer Serialization

The service layer produces a Python object/dictionary.

The producer converts it:

```text
Python dictionary
      ↓
json.dumps()
      ↓
JSON string
      ↓
Kafka message
```

The consumer performs the reverse operation:

```text
Kafka message
      ↓
bytes
      ↓
UTF-8 decode
      ↓
JSON string
      ↓
json.loads()
      ↓
Python dictionary
```

---

# 16. Kafka Docker Setup

Curato currently uses a single Kafka container.

The setup is based on **KRaft**, so ZooKeeper is not required.

Conceptually:

```text
Docker
│
└── Kafka container
      │
      ├── Broker
      └── Controller
```

The Kafka process currently has both roles:

```text
broker,controller
```

This is suitable for local development.

---

# 17. Kafka Broker

The broker is responsible for handling the actual Kafka messages.

It receives events from producers and makes them available to consumers.

```text
Producer
    ↓
Kafka Broker
    ↓
Consumer
```

---

# 18. Kafka Controller

The controller manages Kafka's cluster metadata and coordination.

For the current single-node setup, the same Kafka process acts as both:

```text
Broker
+
Controller
```

This is enabled by:

```text
KAFKA_PROCESS_ROLES=broker,controller
```

---

# 19. Kafka Node ID

The current setup uses:

```text
KAFKA_NODE_ID=1
```

This identifies the Kafka node.

Changing:

```text
1 → 2
```

does NOT make Kafka more powerful.

It simply changes the node's identity.

To actually create another Kafka node, another Kafka container/server would be required.

For example:

```text
Kafka Cluster
│
├── Node 1
│   ├── Broker
│   └── Controller
│
└── Node 2
    ├── Broker
    └── Controller
```

The current Curato development setup only needs one node.

---

# 20. Kafka Ports

The current configuration uses:

```text
9092 → normal Kafka client communication
9093 → controller communication
```

Therefore:

```text
Python Producer ──→ localhost:9092
Python Consumer ──→ localhost:9092
Kafka Controller ─→ 9093
```

The producer and consumer do not need to connect to port 9093.

---

# 21. Advertised Listener

Kafka is configured with:

```text
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
```

This tells Kafka what address it should advertise to clients.

In simple terms:

> "If a client asks where Kafka is, tell it `localhost:9092`."

This is important because Kafka clients receive broker metadata and need an address they can actually reach.

---

# 22. Persistent Kafka Storage

Kafka stores event data on disk.

The current configuration uses:

```text
KAFKA_LOG_DIRS=/tmp/kraft-combined-logs
```

A Docker volume is mounted to the same location:

```text
kafka-data:/tmp/kraft-combined-logs
```

Therefore:

```text
Kafka container
      ↓
/tmp/kraft-combined-logs
      ↓
kafka-data Docker volume
```

This allows Kafka data to persist beyond the lifecycle of the container.

---

# 23. Kafka Replication

The current environment has only one broker.

Therefore internal replication settings use:

```text
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1
KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1
```

These values are appropriate for a single-node development environment.

Increasing the replication factor without adding additional brokers does not create additional copies automatically.

For example:

```text
1 broker + replication factor 3
```

cannot provide three actual broker copies.

A multi-broker cluster would be required.

---

# 24. Consumer

The consumer subscribes to:

```text
curato_user_events
```

Its job is:

```text
Read Kafka event
      ↓
Deserialize event
      ↓
Process event
      ↓
Send event to PostgreSQL
```

The consumer does not directly create recommendations.

---

# 25. Consumer Group

The consumer uses:

```text
group.id = postgres-consumer-group
```

A consumer group is like a **team of consumers working together**.

If multiple consumers use the same group:

```text
Consumer 1 ─┐
Consumer 2 ─┼── postgres-consumer-group
Consumer 3 ─┘
```

Kafka distributes partitions among them.

This allows processing to scale horizontally.

If consumers have different group IDs:

```text
postgres-consumer-group
analytics-group
recommendation-group
```

each group can independently consume the same Kafka topic.

Therefore:

```text
Same group ID
    ↓
Share work

Different group ID
    ↓
Independent consumption
```

---

# 26. Consumer Polling

The consumer continuously calls:

```text
poll()
```

Conceptually:

```text
Consumer
   ↓
"Do you have an event?"
   ↓
Kafka
   ↓
Event / None
```

If no event is available, the consumer continues waiting/polling.

The infinite loop is appropriate for a continuously running Kafka consumer.

---

# 27. Offset

Every message in a Kafka partition has an **offset**.

Example:

```text
Partition 0

Offset 0 → Event A
Offset 1 → Event B
Offset 2 → Event C
Offset 3 → Event D
```

The offset is essentially the event's position in that partition.

Kafka uses offsets to remember how far a consumer group has progressed.

---

# 28. Offset Commit

A consumer commits an offset to tell Kafka:

> **"I successfully processed this event; I can continue from here."**

For Curato, the desired flow is:

```text
Kafka Event
     ↓
Consumer
     ↓
PostgreSQL
     ↓
SUCCESS
     ↓
Commit Offset
```

If PostgreSQL fails:

```text
Kafka Event
     ↓
Consumer
     ↓
PostgreSQL
     ↓
FAILURE
     ↓
Do NOT Commit
```

This is important because the event can then be processed again.

---

# 29. Manual Offset Commit

The consumer disables automatic offset commits:

```text
enable.auto.commit = False
```

This gives the application control over when an event is considered successfully processed.

The intended logic is:

```text
send_to_postgres(event_json)
        ↓
success
        ↓
consumer.commit(message=msg)
```

The commit occurs **after** PostgreSQL succeeds.

---

# 30. Why Duplicate Events Are Still Possible

There is an important edge case.

Suppose:

```text
Kafka Event
    ↓
PostgreSQL SUCCESS
    ↓
Application crashes
    ↓
Offset NOT committed
```

After restart, Kafka may deliver the same event again.

Therefore:

```text
Kafka
    ↓
Event A
    ↓
PostgreSQL ✓
    ↓
Crash
    ↓
Event A again
```

To protect PostgreSQL from duplicate insertion, every event should have a unique:

```text
event_id
```

and PostgreSQL should eventually enforce uniqueness on that ID.

This gives two separate protections:

```text
Kafka offset
    ↓
Tracks consumer progress

event_id
    ↓
Protects PostgreSQL from duplicate events
```

---

# 31. PostgreSQL's Role

PostgreSQL is the **permanent event history** for Curato.

Kafka is the event stream.

PostgreSQL stores the events long-term.

Example:

| event_id | user_id | session_id | event_type | timestamp |
| -------- | ------- | ---------- | ---------- | --------- |
| E1       | U101    | S1         | viewed     | 10:01     |
| E2       | U101    | S1         | searched   | 10:02     |
| E3       | U101    | S1         | liked      | 10:03     |
| E4       | U205    | S8         | viewed     | 10:04     |
| E5       | U101    | S1         | cart       | 10:05     |

Kafka transports these events.

PostgreSQL remembers them.

---

# 32. Session-Based Current Activity

Curato needs both:

1. Full historical activity
2. Current session activity

Every event should therefore contain:

```text
userId
sessionId
timestamp
```

For example:

```text
U101
│
├── Session S1
│   ├── viewed shoes
│   ├── searched black shoes
│   ├── liked shoes
│   └── added to cart
│
├── Session S2
│   ├── viewed laptop
│   └── searched laptop
│
└── Session S3
    ├── viewed watch
    └── purchased watch
```

The current session can be used to identify the user's **current activity**.

For example, if U101 is currently in session S3:

```text
Current activity:

viewed watch
purchased watch
```

while all previous sessions remain available as historical data.

---

# 33. Why Session ID Is Important

The current session should not be determined only by timestamp.

The preferred approach is:

```text
session starts
     ↓
sessionId created/maintained
     ↓
all events in that session use same sessionId
```

Then PostgreSQL can retrieve:

```text
WHERE userId = U101
AND sessionId = current_session
```

to obtain the current activity.

Timestamp remains useful for ordering events.

---

# 34. LangGraph State

The existing Curato system already has a **user-based LangGraph state** containing a list of events.

The state is not tied to Kafka partitions.

For example:

```text
User U101
    ↓
Event Fetcher
    ↓
LangGraph State

{
    userId: U101,
    events: [...]
}
```

Another user gets another workflow/state:

```text
User U205
    ↓
Event Fetcher
    ↓
LangGraph State

{
    userId: U205,
    events: [...]
}
```

The same LangGraph workflow can therefore be used for many users.

---

# 35. Event Fetcher's Responsibility

Kafka Consumer and Event Fetcher have different jobs.

## Kafka Consumer

The consumer answers:

> **"What new event just happened?"**

Its pipeline is:

```text
Kafka
  ↓
Consumer
  ↓
PostgreSQL
```

## Event Fetcher

The Event Fetcher answers:

> **"What information do I need about this user for the current recommendation workflow?"**

It can retrieve the user's relevant historical/current-session events from PostgreSQL and put them into LangGraph state.

Therefore:

```text
Kafka Consumer
      ↓
Permanent history
      ↓
PostgreSQL
      ↓
Event Fetcher
      ↓
LangGraph State
```

The Event Fetcher should not be responsible for directly reading Kafka in the current architecture.

---

# 36. Multiple Users Getting Recommendations

There is no need for:

```text
one Kafka topic per user
```

or:

```text
one Kafka partition per user
```

Instead:

```text
Kafka
   ↓
PostgreSQL
   ↓
        ┌──────────────┬──────────────┐
        ↓              ↓              ↓
      U101           U205           U309
        ↓              ↓              ↓
    Workflow       Workflow       Workflow
        ↓              ↓              ↓
      State          State          State
        ↓              ↓              ↓
 Recommendation   Recommendation  Recommendation
```

Each recommendation request identifies the relevant `userId`.

The Event Fetcher obtains the appropriate information for that user.

---

# 37. Redis — Future Optimization

Redis is **not required for the first version**.

The current stack is sufficient:

```text
FastAPI
Kafka
PostgreSQL
LangGraph
```

Redis could be introduced later as a fast cache/current-state store:

```text
Kafka
  ↓
Consumer
  ↓
PostgreSQL ─────→ Permanent history
  ↓
Redis ──────────→ Fast current data/cache
  ↓
LangGraph
```

Redis would be useful if PostgreSQL queries become a performance bottleneck for frequently requested current user information.

It should therefore be treated as an **optimization**, not a mandatory component.

---

# 38. Current Technology Stack

The current Curato architecture consists of:

```text
Frontend
   ↓
FastAPI
   ↓
Service Layer
   ↓
Kafka Producer
   ↓
Apache Kafka
   ↓
Kafka Consumer
   ↓
PostgreSQL
   ↓
Event Fetcher
   ↓
LangGraph
   ↓
Recommendation System
```

Potential future optimization:

```text
Redis
```

but it is not currently required.

---

# 39. Final Mental Model

The easiest way to remember the entire system is:

```text
FRONTEND
"What did the user do?"
        ↓
SERVICE LAYER
"Create the proper event."
        ↓
KAFKA PRODUCER
"Send the event."
        ↓
KAFKA
"Transport and temporarily retain the event stream."
        ↓
CONSUMER
"Read the event."
        ↓
POSTGRESQL
"Remember it permanently."
        ↓
EVENT FETCHER
"Get the information needed for this user."
        ↓
LANGGRAPH STATE
"Represent the user's information for this workflow."
        ↓
RECOMMENDER
"Use the user information to generate recommendations."
```

### The four most important distinctions

```text
Topic
= category/stream of events

Partition
= parallel lane inside a topic

User ID
= identifies which user's event it is
  and is used as Kafka message key

LangGraph State
= application-level state for a user's recommendation workflow
```

And the central Curato principle is:

> **Kafka moves events. PostgreSQL remembers events. The Event Fetcher retrieves relevant user information. LangGraph uses that information to perform the recommendation workflow.**
