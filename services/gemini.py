import json
from datetime import datetime
from google import genai
from google.genai import types
from config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Strip any accidental spaces from the Railway variable list
MODELS = [m.strip() for m in settings.GEMINI_MODELS]

INTENT_SYSTEM_PROMPT = """
You are an intent classifier for a WhatsApp business bot used by Nigerian SMB owners.
They message in English, Pidgin, or Yoruba mixed with numbers and naira amounts.

Classify the user's message into one of these intents:
- log_sale: They sold something (e.g. "sold 3 bags of rice at 52k", "I sell phone case 5k")
- log_expense: They spent money (e.g. "bought goods for 30k", "transport 2k")
- add_debt: A customer owes them (e.g. "Emeka owes 45k", "Tunde collect 3 bags credit")
- record_payment: Customer paid (e.g. "Emeka paid 20k", "Tunde settle 10k")
- query_revenue: Asking about their money (e.g. "how much today", "weekly report", "wetin I make")
- query_debt: Asking about who owes them (e.g. "who owes me", "Emeka balance")
- update_inventory: Stock update (e.g. "received 50 bags", "stock: 20 cartons indomie")
- get_summary: Want full report (e.g. "summary", "report", "show me everything")
- greeting: Just saying hi or testing
- unknown: Cannot classify

Return ONLY valid JSON, no markdown, no explanation:
{
  "intent": "log_sale",
  "entities": {
    "amount": 156000,
    "item": "bags of rice",
    "quantity": 3,
    "customer_name": null,
    "period": null
  },
  "confidence": 0.95
}

For amounts: convert "52k" to 52000, "1.5m" to 1500000, "N45,000" to 45000.
For period: "today", "this week", "this month", "yesterday", or null.
"""

async def parse_intent(message: str) -> dict:
    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=INTENT_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            raw = response.text.strip()
            return json.loads(raw)
        except Exception as e:
            print(f"WARNING: Model {model} failed in parse_intent. Trying next... Error: {str(e)}")
            last_error = e
            
    print(f"CRITICAL: All models failed in parse_intent. Last error: {str(last_error)}")
    raise last_error

async def generate_response(context: str, data: dict) -> str:
    current_time = datetime.now().strftime("%I:%M %p")
    
    prompt = f"""
You are VendorIQ, a friendly WhatsApp business assistant for Nigerian SMB owners.
Generate a SHORT, warm WhatsApp reply in plain text (no markdown, no asterisks, no bullet symbols).
Use simple English or light Pidgin. Keep it under 5 lines. Use emojis sparingly.

IMPORTANT: The current local time is {current_time}. Match your greeting (morning, afternoon, or evening) to this specific time.

Context: {context}
Data: {json.dumps(data, indent=2)}

Rules:
- Format naira amounts with commas: N156,000
- Never use markdown formatting (no **, no *, no -, no #)
- Sound like a helpful colleague, not a corporate bot
- If showing revenue up/down, note the percentage change
- End with a brief motivating line only if appropriate
"""
    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )
            return response.text.strip()
        except Exception as e:
            print(f"WARNING: Model {model} failed in generate_response. Trying next... Error: {str(e)}")
            last_error = e
            
    print(f"CRITICAL: All models failed in generate_response. Last error: {str(last_error)}")
    raise last_error