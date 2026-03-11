# Arabic Restaurant Ordering Agent

Multi-agent Arabic conversational ordering system for restaurant delivery orders.

This project implements an **AI backend for restaurant ordering systems** such as:

- WhatsApp ordering bots
- website chat ordering
- voice assistants
- kiosk ordering

The system uses **multiple specialized agents** to handle different stages of the ordering process.

---

# Features

- Arabic conversational ordering
- Multi-agent architecture
- LLM-powered order parsing
- Deterministic cart management
- Menu search from 100+ items
- Delivery location validation
- Structured logging
- Streamlit chat UI
- Modular architecture

---

# Agent Architecture

Conversation flows through multiple agents:

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

Each agent has a **single responsibility**, making the system easier to debug and extend.

---

# Agents

| Agent | Purpose |
|------|--------|
GreetingAgent | Detect greeting, order intent, or complaint |
LocationAgent | Extract delivery district and validate coverage |
OrderAgent | Parse order requests and update cart |
CheckoutAgent | Display order summary and confirm order |
EscalationAgent | Handle complaints and escalate to human |

---

# Conversation Example

Example ordering flow:

```
User: hi

Bot: أدخل الحي:

User: malqa

Bot: تم تأكيد التوصيل إلى حي الملقا.

Bot: ماذا تريد أن تطلب؟

User: abi 2 zinger

Bot: تمت إضافة راب زنجر × 2

User: add fries

Bot: تمت إضافة بطاطس × 1

User: change fries to 3

Bot: تم تعديل كمية بطاطس إلى 3

User: checkout

Bot:
ملخص الطلب:
راب زنجر × 2
بطاطس × 3
المجموع الفرعي: 80
رسوم التوصيل: 10
الإجمالي: 90
هل تؤكد الطلب؟ (نعم / تعديل)

User: نعم

Bot: تم استلام الطلب. شكراً لك!
```

---

# Project Structure

```
restaurant_agent/

agents/
  greeting_agent.py
  location_agent.py
  order_agent.py
  checkout_agent.py
  escalation_agent.py

tools/
  menu_tools.py
  order_tools.py
  delivery_tools.py

models/
  session_state.py

services/
  llm_service.py

utils/
  arabic_text.py
  logger.py

data/
  menu.json

tests/
  test_conversation_complex.py

app.py
main.py
requirements.txt
.env.example
DESIGN.md
README.md
```

---

# Menu

The system supports **100+ menu items** across categories:

- Main dishes
- Appetizers
- Beverages
- Desserts
- Sides

Menu items contain:

```
id
name_ar
name_en
price
category
description_ar
```

Menu search is handled through tools rather than sending the full menu to the LLM.

---

# LLM Usage

LLMs are used for **language understanding tasks**.

| Task | Agent |
|----|----|
Intent detection | GreetingAgent |
Location extraction | LocationAgent |
Order parsing | OrderAgent |

Checkout summary is deterministic.

Example parsed order JSON:

```
{
 "action": "add",
 "item": "zinger",
 "quantity": 2
}
```

---

# Context Management

The system avoids sending the full conversation history to the LLM.

Instead it relies on:

- structured `SessionState`
- deterministic tools
- limited message history

This reduces:

- token usage
- latency
- hallucination risk

---

# Logging

The system logs important events.

Example logs:

```
[14:23:01] AGENT_TRIGGER GreetingAgent
[14:23:01] HANDOFF GreetingAgent → LocationAgent
[14:23:10] LLM_CALL OrderParser
[14:23:12] ORDER_ADD راب زنجر x2
[14:23:15] CHECKOUT subtotal=60 delivery=10 total=70
```

Logs include:

- agent transitions
- tool calls
- LLM calls
- order updates

---

# Installation

Clone the repository:

```
git clone <repo-url>
cd restaurant_agent
```

Create a virtual environment (recommended):

```
python -m venv open_env
source open_env/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Environment Variables

Create `.env` file.

Example:

```
OPENROUTER_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
```

---

# Running the System (CLI)

Run the CLI ordering interface:

```
python main.py
```

Example:

```
User: hi
Bot: أدخل الحي:
```

---

# Running the Streamlit Chat UI

Install dependencies:

```
pip install -r requirements.txt
```

If Streamlit is not installed:

```
pip install streamlit
```

Run the Streamlit application:

```
streamlit run app.py
```

You will see output similar to:

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Open in your browser:

```
http://localhost:8501
```

---

# Streamlit Project Layout

Make sure `app.py` is located in the project root:

```
restaurant_agent/

app.py
main.py
requirements.txt

agents/
tools/
models/
services/
utils/
data/
```

Then run:

```
streamlit run app.py
```

---

# Streamlit Troubleshooting

### Module not found

Reinstall dependencies:

```
pip install -r requirements.txt
```

---

### Port already in use

Run Streamlit on a different port:

```
streamlit run app.py --server.port 8502
```

---

### Auto-reload issues (Mac)

Install watchdog:

```
pip install watchdog
```

or install watchman:

```
brew install watchman
```

---

# Testing

Run automated conversation tests:

```
python tests/test_conversation_complex.py
```

Tests simulate:

- ordering items
- modifying orders
- removing items
- checkout flow

---

# Design Document

See `DESIGN.md` for full design explanation including:

- agent architecture
- context management
- LLM usage
- edge cases
- cost considerations

---

# Future Improvements

Possible production improvements:

- Redis session storage
- WhatsApp API integration
- voice interface (ASR + TTS)
- improved Arabic dialect handling
- recommendation engine

---

# License

This project is provided for assessment purposes.