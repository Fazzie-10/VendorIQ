import json
from google import genai
from google.genai import types
from config import settings
from services.tz import now_nigeria

client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODELS = [m.strip() for m in settings.GEMINI_MODELS.split(",")]

INTENT_SYSTEM_PROMPT = """
You are an intent classifier for a WhatsApp business bot used by Nigerian SMB owners.
They message in English, Pidgin, or Yoruba mixed with numbers and naira amounts.

LANGUAGE RULE: Detect what language the user wrote in. Classify as one of:
"english", "pidgin", "yoruba", "igbo", "hausa", or "mixed".
Include this as the "language" field in your JSON output.

Classify the user's message into one of these intents:
- log_sale: They sold something (e.g. "sold 3 bags of rice at 52k", "I sell phone case 5k")
- log_expense: They spent money (e.g. "bought goods for 30k", "transport 2k")
- add_debt: A customer owes them (e.g. "Emeka owes 45k", "Tunde collect 3 bags credit")
- record_payment: Customer paid (e.g. "Emeka paid 20k", "Tunde settle 10k")
- query_revenue: Asking about their money (e.g. "how much today", "weekly report", "wetin I make")
- query_debt: Asking about who owes them (e.g. "who owes me", "Emeka balance")
- update_inventory: Stock update (e.g. "received 50 bags", "stock: 20 cartons indomie")
- get_summary: Want full report (e.g. "summary", "report", "show me everything")
- delete_record: Want to remove something (e.g. "delete my last sale", "remove the 45k debt for Emeka", "cancel that", "delete Emeka's debt")
- request_receipt: Asking for a receipt or proof of payment (e.g. "send me a receipt", "receipt for last sale", "print receipt for Emeka", "give me a receipt")
- greeting: Casual chat, checking in, gratitude (e.g. "good morning", "how far", "hello", "I'm fine", "thank you", "anything you want to tell me", "how you dey", "you there?")
- help: Asking about capabilities (e.g. "what can you do", "what do you do", "help", "how does this work", "what do you support", "show me what you can do", "features")
- unknown: Cannot classify

AMOUNT CALCULATION RULES (CRITICAL):
- "3 bags at 52k" → "at" means UNIT PRICE. amount = 3 x 52000 = 156000, quantity = 3.
- "3 bags for 150k" → "for" means TOTAL PRICE. amount = 150000, quantity = 3.
- "sold phone case 5k" → no quantity given. amount = 5000, quantity = null.
- "sold 3 bags indomie" → no price given, return amount = 0.
- "Emeka owes 45k" → For add_debt, amount = 45000, customer_name = "Emeka", quantity = null.
- "bought goods for 30k" → For log_expense, amount = 30000.
- Always use the "at" word as a trigger for unit price x quantity multiplication.
- Always use "for" word as a trigger for total price (already the final amount).

NOTE EXTRACTION:
If the message includes extra context like "for wedding", "for restocking", "from customer X", extract it as "note".
Example: "Sold 3 bags at 52k for Chisom's wedding" → note = "Chisom's wedding".
Example: "Bought goods for 30k for restocking" → note = "restocking".
If no extra context, set note = null.

CUSTOMER NAME EXTRACTION:
For add_debt: "Emeka owes 45k" → customer_name = "Emeka".
For record_payment: "Emeka paid 20k" → customer_name = "Emeka".
For debt queries: "who owes me" → customer_name = null (list all). "Emeka balance" → customer_name = "Emeka".

DELETE RECORD RULES:
- "delete my last sale" → target_type = "sale", period = "last"
- "delete my last expense" → target_type = "expense", period = "last"
- "remove the 45k debt for Emeka" → target_type = "debt", amount = 45000, customer_name = "Emeka"
- "delete Emeka's debt" → target_type = "debt", customer_name = "Emeka", period = "all"
- "cancel that" → target_type = null, period = "last"

Return ONLY valid JSON, no markdown, no explanation:
{
  "intent": "log_sale",
  "language": "english",
  "entities": {
    "amount": 156000,
    "item": "bags of rice",
    "quantity": 3,
    "customer_name": null,
    "period": null,
    "note": null,
    "target_type": null
  },
  "confidence": 0.95
}

For amounts: convert "52k" to 52000, "1.5m" to 1500000, "N45,000" to 45000.
For period: "today", "this week", "this month", "yesterday", "last", or null.
For target_type (only for delete_record): "sale", "expense", "debt", or null.
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
                    temperature=0.1,
                )
            )
            raw = response.text.strip()
            return json.loads(raw)
        except Exception as e:
            print(f"WARNING: Model {model} failed in parse_intent. Trying next... Error: {str(e)}")
            last_error = e

    print(f"CRITICAL: All models failed in parse_intent. Last error: {str(last_error)}")
    raise last_error


async def generate_response(context: str, data: dict, language: str = "english") -> str:
    now = now_nigeria()
    today_date = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")

    base_prompt = f"""
You are VendorIQ, a friendly WhatsApp business assistant for Nigerian SMB owners.
Talk like a warm, helpful colleague — not a corporate bot. Use light Pidgin where natural.
Be warm, respond enthusiastically, and match the user's energy. If they're casual, you be casual too.

CRITICAL: Today is {today_date}. The current time is {current_time}.
Base ALL date references on this fact. Do NOT say "yesterday" unless the data explicitly says so.

LANGUAGE RULE (STRICT — FOLLOW THIS EXACTLY):
The user wrote to you in **{language}**. You MUST write your entire response in **{language}**.
Do NOT switch languages mid-response. If the language is "english", you may use light Pidgin words naturally.
If the language is "yoruba", "igbo", or "hausa", respond entirely in that language.
If the language is "pidgin", respond entirely in Nigerian Pidgin.
If the language is "mixed", respond in the dominant language from their message.

Generate a SHORT, warm WhatsApp reply in plain text (no markdown, no asterisks, no bullet symbols).
Keep it under 5 lines. Use emojis sparingly. Sound human, not robotic.

Context: {context}
Data: {json.dumps(data, indent=2)}

Rules:
- Format naira amounts with commas: N156,000
- Never use markdown formatting (no **, no *, no -, no #)
- If greeting or small talk, be warm and natural — ask how they're doing
- If showing revenue up/down, note the percentage change
- End with a brief motivating line only if appropriate
- Respond ONLY in {language}
"""

    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=base_prompt,
                config=types.GenerateContentConfig(temperature=0.8)
            )
            return response.text.strip()
        except Exception as e:
            print(f"WARNING: Model {model} failed in generate_response. Trying next... Error: {str(e)}")
            last_error = e

    print(f"CRITICAL: All models failed in generate_response. Last error: {str(last_error)}")
    raise last_error


async def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """Transcribe voice note audio using Gemini."""
    prompt = "Transcribe this audio message word for word. Return only the transcribed text, nothing else."
    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    prompt,
                ]
            )
            return response.text.strip()
        except Exception as e:
            print(f"WARNING: Model {model} failed in transcribe_audio. Trying next... Error: {str(e)}")
            last_error = e

    print(f"CRITICAL: All models failed in transcribe_audio. Last error: {str(last_error)}")
    raise last_error


QUERY_SYSTEM_PROMPT = """
You are a data query planner for VendorIQ, a WhatsApp business assistant for Nigerian SMB owners.
Given a user's natural language question about their business data, return a structured JSON action
specifying what data to fetch from their database.

Today's date is {today_date}. The current time is {current_time}.
The user's business name is "{business_name}".

AVAILABLE DATA:
1. transactions table — records of sales and expenses
   - type: "sale" or "expense"
   - amount: number (in naira)
   - item: string (what was sold/bought)
   - quantity: number or null
   - note: string or null
   - created_at: ISO timestamp

2. customers table — debtors
   - name: string
   - balance: number (outstanding debt in naira)
   - updated_at: ISO timestamp

3. inventory table — stock items
   - item: string
   - quantity: number
   - unit: string
   - updated_at: ISO timestamp

CRITICAL: Translate relative time phrases to actual dates based on today being {today_date}.
- "today" → start = today's date, end = today
- "yesterday" → start = yesterday, end = yesterday
- "this week" → start = Monday of this week, end = today
- "last week" → start = Monday of last week, end = Sunday of last week
- "this month" → start = 1st of this month, end = today
- "last month" → start = 1st of last month, end = last day of last month
- "this year" → start = Jan 1 this year, end = today
- "last 7 days" / "past week" → start = 7 days ago, end = today
- "last 30 days" / "past month" → start = 30 days ago, end = today
- "last 3 months" → start = 90 days ago, end = today
- "this morning" → start = today, end = today
- "total sales" / "all time" → start = null, end = today

Return ONLY valid JSON, no markdown, no explanation:
{{
  "table": "transactions",
  "type_filter": "sale",
  "start_date": "2026-06-01",
  "end_date": "2026-06-30",
  "aggregation": "total",
  "item_filter": null,
  "customer_filter": null,
  "explanation": "User asked about last month's sales"
}}

Aggregation options:
- "total": sum of amounts (return single number)
- "list": list individual records (return all matching rows)
- "count": count of records
- "daily": group by day with totals per day
- "top": return highest amounts (use with item_filter or customer_filter)
- "comparison": comparing two periods

For customer/debt questions:
- "who owes me" → table: "customers", aggregation: "list"
- "how much does Emeka owe" → table: "customers", customer_filter: "Emeka", aggregation: "total"

For inventory questions:
- "what's in stock" → table: "inventory", aggregation: "list"
- "what's low on stock" → table: "inventory", aggregation: "list" (quantity < 5)

For comparison questions like "compare this month to last month":
- aggregation: "comparison"
- use start_date and end_date for the first period
- include "comparison_start" and "comparison_end" fields for the second period

If you cannot determine the query, return:
{{"table": null, "error": "Could not understand the query"}}
"""


async def generate_query_action(question: str, business_name: str) -> dict:
    now = now_nigeria()
    today_date = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")

    prompt = QUERY_SYSTEM_PROMPT.format(
        today_date=today_date,
        current_time=current_time,
        business_name=business_name,
    )

    full_prompt = f"{prompt}\n\nUser question: {question}"

    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                )
            )
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"WARNING: Model {model} failed in generate_query_action. Trying next... Error: {str(e)}")
            last_error = e

    print(f"CRITICAL: All models failed in generate_query_action. Last error: {str(last_error)}")
    return {"table": None, "error": "All models failed"}


async def format_query_results(question: str, data: dict, language: str = "english") -> str:
    """Format query results into a natural language response."""
    return await generate_response("smart_query", {
        "question": question,
        "result": data,
    }, language=language)
