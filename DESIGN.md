# DESIGN.md

Arabic Restaurant Ordering Multi-Agent System

---

# 1 Architecture Overview

This system implements an Arabic conversational restaurant ordering assistant using a **multi-agent architecture**.

The goal is to simulate the backend AI of a restaurant ordering system such as:

- WhatsApp ordering
- chatbot ordering
- voice ordering assistant

The system separates conversation responsibilities across multiple agents.

Each agent has a **single responsibility** and communicates through a shared **SessionState object**.

---

# 1.1 Agent Flow

Conversation flows through the following agents:

```
User
 ↓
GreetingAgent
 ↓
LocationAgent
 ↓
OrderAgent
 ↓
CheckoutAgent
 ↓
Order Confirmed
```

Escalation path:

```
GreetingAgent
 ↓
EscalationAgent
```

---

# 1.2 Agent Responsibilities

| Agent | Responsibility |
|------|---------------|
GreetingAgent | Detect greeting, order intent, or complaint |
LocationAgent | Extract delivery district and validate coverage |
OrderAgent | Parse order actions and update cart |
CheckoutAgent | Show order summary and confirm order |
EscalationAgent | Handle complaints and escalate to human support |

---

# 1.3 Handoff Conditions

| From | To | Condition |
|-----|----|----------|
GreetingAgent | LocationAgent | greeting or order intent |
GreetingAgent | EscalationAgent | complaint detected |
LocationAgent | OrderAgent | district validated |
OrderAgent | CheckoutAgent | user requests checkout |
CheckoutAgent | OrderAgent | user chooses تعديل |

---

# 2 Conversation State

The system uses a shared **SessionState object** to persist conversation data.

Example state:

```
{
 "intent": "delivery_order",
 "district": "الملقا",
 "delivery_fee": 10,
 "location_confirmed": true,
 "cart": [
   {"name":"راب زنجر","qty":2,"price":25}
 ]
}
```

Session state contains:

| Field | Purpose |
|------|---------|
intent | user goal (order or complaint) |
district | delivery district |
delivery_fee | delivery cost |
location_confirmed | delivery validation |
cart | list of ordered items |

This state is stored **in memory** for this prototype.

---

# 3 Context Management Strategy

The system minimizes LLM context usage by relying on:

- structured session state
- deterministic tools
- limited message history

Instead of sending the entire menu to the LLM, menu matching is handled through search tools.

---

# 3.1 Message Roles

The LLM interactions use the following message structure:

| Role | Purpose |
|----|----|
system | agent instructions |
user | user message |
assistant | model output |

Example prompt:

```
SYSTEM
أنت مساعد مطعم.

USER
ابي زنجر وبطاطس
```

---

# 3.2 Context Budget

Approximate token usage:

| Component | Tokens |
|----------|--------|
System instructions | ~150 |
User message | ~50 |
Parsed tool results | ~100 |

Total per request:

~300 tokens

This keeps latency low for conversational interaction.

---

# 3.3 Menu Handling

The menu contains 100+ items but is **not placed in the prompt**.

Instead the system uses a tool:

```
get_best_menu_match(query)
```

Workflow:

1 User requests item
2 LLM extracts item name
3 Tool searches menu
4 Matching item returned

This prevents context overflow.

---

# 3.4 Handoff Context

Agents share state via the SessionState object.

### MUST transfer

- intent
- district
- delivery_fee
- cart items

### SHOULD transfer

- location_confirmed

### SHOULD NOT transfer

- previous system prompts
- entire conversation history

This keeps prompts small and predictable.

---

# 3.5 History Handling

Agents do not receive the full conversation history.

Each agent only processes:

- the current user message
- the SessionState

Advantages:

- lower token usage
- faster response time
- simpler debugging

Tradeoff:

- less conversational memory

This is acceptable for structured tasks such as food ordering.

---

# 4 LLM Usage

The system uses LLMs only for **language understanding tasks**.

### GreetingAgent

Uses:

- rule-based detection for greetings
- LLM classification for intent detection

Possible intents:

```
GREETING
ORDER
ESCALATION
```

---

### LocationAgent

Uses LLM JSON extraction to obtain the delivery district.

Example output:

```
{
 "district": "الملقا"
}
```

Delivery coverage is then validated by a tool:

```
check_delivery_district()
```

---

### OrderAgent

The LLM parses order commands into structured JSON.

Example response:

```
{
 "action": "add",
 "item": "zinger",
 "quantity": 2
}
```

Possible actions:

| Action | Meaning |
|------|------|
add | add item |
remove | remove item |
update | change quantity |
checkout | finish order |

Cart operations are executed by deterministic code.

---

### CheckoutAgent

This agent does not use the LLM.

It retrieves order state and renders a summary.

Example response:

```
ملخص الطلب:
راب زنجر × 2
بطاطس × 1

المجموع الفرعي: 60
رسوم التوصيل: 10
الإجمالي: 70
هل تؤكد الطلب؟ (نعم / تعديل)
```

---

# 5 Edge Case Handling

### Unknown menu item

```
add pizza
```

Response:

```
عذراً هذا الصنف غير موجود.
```

---

### Removing non-existing item

Response:

```
العنصر غير موجود في الطلب
```

---

### Checkout with empty cart

CheckoutAgent detects empty order.

Response:

```
الطلب الحالي فارغ.
```

---

### Delivery outside coverage

LocationAgent checks delivery district.

Response:

```
عذراً التوصيل غير متوفر لهذا الحي.
```

---

# 6 Logging Strategy

The system logs important events.

Examples:

```
AGENT_TRIGGER GreetingAgent
HANDOFF GreetingAgent → LocationAgent
LLM_CALL OrderParser
ORDER_ADD راب زنجر x2
ORDER_REMOVE كوكاكولا
CHECKOUT subtotal=50 delivery=10 total=60
```

Logs help with:

- debugging
- monitoring
- understanding agent transitions

---

# 7 Deployment Strategy

This prototype runs locally as a Python application.

Architecture:

```
User
 ↓
Python application
 ↓
Agents
 ↓
LLM provider (OpenRouter / OpenAI)
```

Session state is stored **in memory**.

In production this could be replaced with:

- Redis session storage
- distributed API service

---

# 8 Arabic Language Considerations

The system supports:

- Modern Standard Arabic
- dialect expressions
- Arabic/English code switching

Examples:

```
ابي 2 zinger
add fries
غير البطاطس 3
```

Menu search normalizes text before matching.

---

# 9 Cost Estimate

Estimated token usage per order:

Greeting intent detection ~150  
Location extraction ~150  
Order parsing ~500  
Checkout summary ~50  

Total:

~850 tokens per order.

Using a lightweight model, estimated cost per order is very low (< $0.002).

---

# 10 Summary

This system implements an Arabic restaurant ordering assistant using:

- modular multi-agent architecture
- shared session state
- LLM-based language understanding
- deterministic business logic
- tool-based menu search

The design focuses on:

- clear agent boundaries
- low token usage
- reliable order management
- simple deployment