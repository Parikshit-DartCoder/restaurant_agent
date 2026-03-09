# DESIGN.md

## Arabic Restaurant Ordering Multi-Agent System

---

# 1. System Overview

This project implements an **Arabic-language restaurant ordering assistant** designed for messaging platforms such as WhatsApp, web chat, or call-center chat interfaces.

The system is designed using a **multi-agent architecture** where each agent is responsible for a specific stage of the ordering process. Separating responsibilities across agents allows:

* smaller prompts
* clearer reasoning
* easier debugging
* better scalability

The system focuses on **food order placement**, while detecting other intents (such as complaints) and redirecting them appropriately.

---

# 2. Architecture Overview

The system processes a conversation through a pipeline of specialized agents.

### Agent Pipeline

```
User
 │
 ▼
Greeting Agent
 │
 ▼
Location Agent
 │
 ▼
Order Agent
 │
 ▼
Checkout Agent
 │
 ▼
Order Confirmed
```

Each agent performs a specific task and passes minimal context to the next agent.

---

# 3. Architecture Diagram

```
                         +-------------------+
                         |        USER       |
                         +---------+---------+
                                   |
                                   v
                         +-------------------+
                         |  Greeting Agent   |
                         | Detect intent     |
                         +----+---------+----+
                              |         |
                              |         |
                              v         v
                    +--------------+  +----------------+
                    | Location     |  | Human Support  |
                    | Agent        |  | (complaints)   |
                    +------+-------+  +----------------+
                           |
                           v
                    +--------------+
                    |  Order Agent |
                    |  Menu search |
                    |  Add items   |
                    +------+-------+
                           |
                           v
                    +--------------+
                    | Checkout     |
                    | Agent        |
                    +------+-------+
                           |
                           v
                    +--------------+
                    | Order        |
                    | Confirmed    |
                    +--------------+
```

The architecture separates **conversation reasoning (agents)** from **deterministic business logic (tools)**.

---

# 4. Conversation State Machine

The ordering workflow is modeled as a **conversation state machine**.

This ensures predictable transitions and easier debugging.

### States

| State      | Agent          | Description                    |
| ---------- | -------------- | ------------------------------ |
| GREETING   | Greeting Agent | Detect user intent             |
| LOCATION   | Location Agent | Validate delivery district     |
| ORDERING   | Order Agent    | Build and modify order         |
| CHECKOUT   | Checkout Agent | Show summary and confirm order |
| ESCALATION | Human Support  | Handle complaints              |

---

### State Transitions

| Current State | Event                  | Next State               |
| ------------- | ---------------------- | ------------------------ |
| GREETING      | delivery order         | LOCATION                 |
| GREETING      | pickup order           | ORDERING                 |
| GREETING      | complaint              | ESCALATION               |
| LOCATION      | district valid         | ORDERING                 |
| LOCATION      | district invalid       | ORDERING (pickup option) |
| ORDERING      | user finished ordering | CHECKOUT                 |
| CHECKOUT      | user modifies order    | ORDERING                 |
| CHECKOUT      | order confirmed        | END                      |

This structure ensures deterministic flow and simplifies debugging.

---

# 5. Context Management Strategy

Large prompt contexts increase both latency and cost.
This design therefore minimizes prompt size while maintaining the necessary conversational context.

---

## Message Roles

The system uses standard chat message roles.

| Role      | Usage              |
| --------- | ------------------ |
| system    | Agent instructions |
| user      | User input         |
| assistant | Agent response     |

Example:

```
[
 {"role":"system","content":"You are an Arabic restaurant ordering assistant."},
 {"role":"user","content":"أبغى برجر دجاج"}
]
```

---

## Menu Handling Strategy

The restaurant menu contains **100+ items**, which would create large prompts if injected directly.

Instead, the system retrieves menu items via tools.

Example:

User message

```
أبغى برجر دجاج
```

Agent tool call

```
search_menu("برجر دجاج")
```

Tool response

```
[
 {"id":"burger12","name_ar":"برجر دجاج كلاسيك","price":25},
 {"id":"burger14","name_ar":"برجر دجاج سبايسي","price":27}
]
```

Only relevant items are inserted into context.

This dramatically reduces token usage.

### Menu Storage

For this implementation, the restaurant menu is stored as a **local JSON file** rather than a database.

Example structure:

[
{
"id": "burger12",
"name_ar": "برجر دجاج كلاسيك",
"name_en": "Classic Chicken Burger",
"price": 25,
"category": "main",
"description_ar": "برجر دجاج مشوي مع صوص خاص"
}
]


The `search_menu()` tool performs lightweight keyword matching over this JSON file to retrieve relevant items.

This approach keeps the implementation simple and removes the need for a database during development.

In a production deployment, the menu would typically be stored in a database or search index.

### Menu Retrieval Pipeline

User Message  
↓  
Order Agent  
↓  
search_menu(query)  
↓  
menu.json  
↓  
Top Matching Items  
↓  
Inserted Into LLM Context  
↓  
Agent Selects Item

Example:

User input:  
أبغى برجر دجاج

Tool response:

[
 {"id":"burger12","name_ar":"برجر دجاج كلاسيك","price":25},
 {"id":"burger14","name_ar":"برجر دجاج سبايسي","price":27}
]

Only the **top relevant results** are inserted into the LLM prompt instead of the full menu.

Benefits:

- prevents prompt bloat  
- reduces token usage  
- improves reasoning accuracy  
- reduces latency

---

## Token Budget Estimate

This estimate represents the token usage for a single LLM request.  
A full order flow typically involves multiple LLM interactions across different agents.

Estimated context usage per request:

| Component            | Tokens |
| -------------------- | ------ |
| System instructions  | ~150   |
| Conversation history | ~300   |
| Menu search results  | ~120   |
| Session state        | ~50    |

Estimated total:

```
~620 tokens
```

---

## Conversation History Handling

To avoid context overflow:

* only the **last 6 messages** are included
* structured session state stores order information
* older messages are discarded

Benefits:

* lower latency
* lower cost
* simpler prompts

---

## Context Transfer Between Agents

Only minimal structured context is transferred.

### Context Transfer Rules

To minimize token usage and prevent context explosion, only structured session state is transferred between agents.

| Category | Data |
|---|---|
MUST transfer | intent, delivery type, district, delivery_fee, order_items |
SHOULD transfer | user name, conversation summary |
SHOULD NOT transfer | full conversation history, previous agent prompts |

### Greeting → Location

```
{
 "intent":"delivery_order"
}
```

### Location → Order

```
{
 "district":"النرجس",
 "delivery_fee":15
}
```

### Order → Checkout

```
{
 "items":[...],
 "subtotal":120,
 "delivery_fee":15
}
```

Full chat history and prompts are not transferred.



---

# 6. Deterministic Logic (Reducing LLM Usage)

To improve reliability and reduce cost, the system avoids using LLM reasoning for operations that are deterministic.

Instead, these tasks are implemented using structured tools.

| Operation | Implementation |
|-----------|---------------|
| Delivery coverage validation | Local district lookup |
| Menu retrieval | JSON search |
| Order updates | Structured session state |
| Price calculation | Deterministic function |


# 7. Model Selection

For simplicity and consistency, the system uses a **single model: GPT-4o-mini** for all agents.

Although different stages of the ordering flow have different reasoning complexity, GPT-4o-mini provides a strong balance of **Arabic capability, low latency, reliable tool calling, and cost efficiency**, making it suitable for all stages of the pipeline.

Using a single model simplifies the architecture by:

- avoiding cross-model latency differences
- simplifying deployment and monitoring
- reducing integration complexity
- maintaining consistent conversational tone across agents

Each agent uses the same model but with **different system prompts and tools** to control behavior.

| Agent    | Model       | Responsibility |
|----------|-------------|---------------|
| Greeting | GPT-4o-mini | Detect intent and start the conversation |
| Location | GPT-4o-mini | Collect delivery district and call validation tool |
| Order    | GPT-4o-mini | Interpret menu queries and add items to the order |
| Checkout | GPT-4o-mini | Summarize the order and confirm checkout |

---

### Model Benchmark Summary

| Benchmark Category | Observation (GPT-4o-mini) | Why It Matters for This System |
|--------------------|---------------------------|--------------------------------|
| Arabic Capability | Strong multilingual performance and reliable Arabic conversation | The assistant must understand Saudi dialect, MSA, and code-switching (e.g. "أبي large meal") |
| Latency (TTFT) | ~400–600 ms typical response start | Restaurant ordering requires fast conversational responses for WhatsApp/chat interfaces |
| Cost Efficiency | ~$0.0005 per 1K tokens | Keeps cost per completed order extremely low even at high volume |
| Tool / Function Calling | High reliability with structured JSON outputs | Agents must reliably call tools like `search_menu()` and `add_to_order()` |
| Context Efficiency | Performs well with small prompts (~500–600 tokens) | Important since prompts are intentionally kept small to reduce latency and cost |

This combination of benchmarks makes **GPT-4o-mini an appropriate choice for a production conversational ordering assistant.**

---

## Selection Criteria

### Arabic Capability

Selected models provide reliable Arabic conversational support.

### Latency

Greeting and location agents require fast responses.

### Cost

Routing simple tasks to smaller models reduces cost per order.

### Tool Reliability

Order agent requires reliable function calling.

---

# 8. Edge Case Handling

Robust conversational systems must handle unexpected inputs.

---

## User Changes Order Type

Example

```
خلّيها استلام بدل توصيل
```

Action

* switch order type to pickup
* remove delivery fee
* skip location validation

---

## Item Not On Menu

Example

```
أبغى بيتزا
```

If no results are found:

```
عذراً، هذا الصنف غير موجود في القائمة.
هل ترغب في تجربة شيء مشابه؟
```

---

## Modify Existing Order

Example

```
شيل البطاطس
```

Tool call

```
remove_item(item_id)
```

Order state is updated.

---

## Outside Delivery Coverage

Tool result

```
{"covered": false}
```

Response

```
عذراً، لا نوصل لهذه المنطقة حالياً.
يمكنك اختيار الاستلام من المطعم.
```

---

## Complaint Handling

Example

```
عندي شكوى
```

Action

* escalate to human support
* preserve session context

---

# 9. Logging Strategy

The system logs operational events.

Logged events include:

* agent transitions
* tool calls
* token estimates
* order updates

Example logs

```
[14:23:01] HANDOFF greeting → location
[14:23:03] TOOL check_delivery_district {district: "النرجس"}
[14:23:04] RESULT {covered: true, delivery_fee: 15}
[14:24:10] TOOL add_to_order {item_id: burger12, quantity: 2}
```

Logs improve debugging and monitoring.

---

# 10. Cost and Latency Estimation

Because deterministic logic handles delivery validation and menu retrieval, only a subset of the pipeline requires LLM inference.

LLM calls occur primarily during:

- Greeting (intent understanding)
- Order interpretation
- Checkout confirmation

The **Location Agent** relies on deterministic tools to validate delivery coverage, which avoids an additional LLM call.

---

## Estimated Tokens Per Complete Order

| Stage | Tokens |
|------|------|
Greeting | ~250 |
Ordering | ~500–600 |
Checkout | ~200 |

Estimated total tokens per completed order:

```
~900 – 1100 tokens
```

This aligns with the earlier estimate of **~450–600 tokens per individual LLM request**, multiplied across several agent interactions in the conversation.

---

## Estimated LLM Cost

Using small-model pricing (~$0.0005–$0.002 per 1K tokens):

```
~$0.001 – $0.002 per completed order
```

Because deterministic tools handle menu search and delivery validation, the system avoids unnecessary model calls, significantly reducing operational cost.

---

## Latency Estimate

| Agent | Latency |
|------|------|
Greeting | ~0.5 s |
Location (deterministic) | ~0.1 s |
Ordering | ~1.0 – 1.2 s |
Checkout | ~0.5 s |

Estimated total interaction latency:

```
~2.1 – 2.8 seconds
```

Latency is primarily driven by LLM inference time, while deterministic operations such as menu search and district validation execute almost instantly.

---

## Cost Optimization Strategy

Operational costs are minimized using several strategies:

- deterministic delivery coverage validation
- tool-based menu retrieval instead of injecting the full menu
- limiting conversation history to the most recent messages
- routing simple tasks to smaller models
- caching delivery validation results

These strategies ensure the system remains scalable and cost-efficient even under high order volumes.


---

# 11. Design Tradeoffs

### Tool-based Menu Retrieval vs Prompt Menu

Using tools prevents context overflow and reduces token cost.

### Multi-Agent vs Single Agent

Advantages:

* clearer responsibilities
* smaller prompts
* easier debugging
* easier scaling

### Limited History vs Full History

Short history reduces tokens but slightly reduces conversational memory.

This is acceptable for transactional ordering flows.

---

# 12. Bonus Considerations

## Deployment Strategy

Recommended architecture:

```
Client (WhatsApp / Web)
        │
        ▼
API Gateway
        │
        ▼
FastAPI Agent Service
        │
 ┌──────┴──────────┐
 ▼                 ▼
LLM Provider    Session Store
(OpenRouter)    (Redis)
```

Redis is used to store session state for each conversation, including:
- current order items
- delivery district
- conversation state

This allows the system to remain stateless at the API layer while maintaining persistent order context.

Suggested regions:

* AWS Bahrain (me-south-1)
* GCP Dammam

These provide low latency for Saudi Arabia.

---

## Arabic Language Nuances

Arabic conversation includes dialect mixing and code switching.

Example input

```
أبي large meal
```

The system normalizes common English terms and dialect variations before menu search.

Diacritics are also removed to improve matching.

Example

```
بُرْجَر → برجر
```

---

## Human Escalation

Certain situations trigger escalation.

| Trigger                   | Example                |
| ------------------------- | ---------------------- |
| Complaint                 | "عندي شكوى"            |
| Repeated misunderstanding | agent fails repeatedly |
| Sensitive requests        | refund requests        |

The system forwards conversation context to a human operator.

---

## Cost Optimization

Costs are reduced by:

* routing simple tasks to smaller models
* retrieving menu items via tools
* limiting prompt history
* caching delivery checks

---

# 13. Summary

This system design emphasizes:

* modular multi-agent architecture
* efficient context management
* tool-based menu retrieval
* scalable deployment
* cost-efficient model usage

The architecture enables a responsive and reliable Arabic ordering assistant suitable for real restaurant messaging systems.
