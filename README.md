# Curato

Curato is an **event-driven, personalized e-commerce recommendation system** that uses user interactions, historical behaviour, and LLM-based preference extraction to generate more relevant recommendations.

## Architecture

```text
User Interaction
       ↓
Frontend
       ↓
FastAPI Backend / Service Layer
       ↓
Kafka Producer
       ↓
Apache Kafka
       ↓
Kafka Consumer
       ↓
PostgreSQL
       ↓
Event Fetcher Node
       ↓
User State
       ↓
User Behavior Agent (LLM)
       ↓
Updated User State
       ↓
Recommendation Node
       ↓
Personalized Recommendations
```

## Event Pipeline

User interactions such as:

* Product views
* Searches
* Likes
* Add to cart
* Purchases
* Recommendation clicks
* Other relevant e-commerce actions

are converted into structured events by the backend service layer.

Each event contains information such as:

```json
{
  "event_id": "E123",
  "userId": "U101",
  "sessionId": "S456",
  "eventType": "add_to_cart",
  "timestamp": "2026-08-10T21:30:00Z",
  "details": {
    "productId": "P123"
  }
}
```

The Kafka producer sends these events to the:

```text
curato_user_events
```

topic using `userId` as the Kafka message key. Kafka uses the key to determine the partition, keeping events for the same user consistently routed to the same partition.

## Kafka

Kafka acts as the **event-streaming layer** between the application and persistent event storage.

### Topic

```text
curato_user_events
```

A single topic is used for user events rather than creating separate topics for individual users or event types.

### Partitions

Partitions provide parallelism and scalability. They are not mapped one-to-one with users or event types.

```text
curato_user_events
├── Partition 0
├── Partition 1
├── Partition 2
└── ...
```

The number of partitions is determined based on expected event throughput and processing requirements.

### Consumer Group

The PostgreSQL consumer uses:

```text
postgres-consumer-group
```

Multiple consumer instances belonging to the same group can share partitions and process events in parallel.

### Offset Handling

Automatic offset commits are disabled.

An event is committed only after it has been successfully processed and stored in PostgreSQL:

```text
Kafka Event
    ↓
Consumer
    ↓
PostgreSQL
    ↓
Success
    ↓
Commit Offset
```

This prevents the consumer from marking an event as processed before PostgreSQL successfully handles it.

## PostgreSQL

PostgreSQL acts as the **persistent store for user event history**.

Events are stored with information such as:

* `event_id`
* `userId`
* `sessionId`
* `eventType`
* `timestamp`
* Event details

This allows Curato to retrieve both historical behaviour and activity from the user's current session.

A unique `event_id` can be used to prevent duplicate event storage in cases where Kafka redelivers an event.

## LangGraph Recommendation Workflow

### 1. Event Fetcher

The Event Fetcher retrieves the relevant events for a user from PostgreSQL and places them into the user-specific workflow state.

```text
PostgreSQL
    ↓
Event Fetcher
    ↓
User State
```

The state can contain:

```text
user_id
current_session_id
current_session_events
historical_events
inferred_preferences
```

### 2. User Behavior Agent

The User Behavior Agent uses an LLM to understand the user's behaviour.

It considers:

* Current session activity
* Relevant recent history
* Existing user information in the state

The LLM extracts useful preferences and behavioural signals.

For example:

```text
Current activity:
- searched black sneakers
- viewed Nike sneakers
- liked Nike sneakers
- added Nike sneakers to cart

Recent history:
- purchased running shoes
- frequently viewed sports footwear
```

The agent may infer:

```text
Category → Sneakers
Brand → Nike
Color → Black
Interest → High
Purchase Intent → High
```

These structured signals are then added to the user state.

### 3. Recommendation Node

The Recommendation Node uses the updated user state and inferred preferences to generate/select personalized product recommendations.

```text
User State
    ↓
Preferences + Behaviour
    ↓
Recommendation Node
    ↓
Personalized Recommendations
```

## Technology Stack

* **Frontend:** Existing e-commerce frontend
* **Backend:** FastAPI / Python
* **Event Streaming:** Apache Kafka
* **Kafka Client:** `confluent-kafka`
* **Database:** PostgreSQL
* **Workflow Orchestration:** LangGraph
* **LLM:** Used by the User Behavior Agent
* **Containerization:** Docker / Docker Compose

## Core Design Principle

Curato separates the responsibilities of each layer:

```text
Kafka
→ Moves user events

PostgreSQL
→ Permanently stores event history

Event Fetcher
→ Retrieves relevant user events

User Behavior Agent
→ Uses an LLM to understand behaviour and extract preferences

User State
→ Carries user information through the recommendation workflow

Recommendation Node
→ Generates personalized recommendations
```
