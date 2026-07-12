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
- greeting: Starting a conversation or checking in (e.g. "good morning", "hello", "how far", "how you dey", "you there?")
- acknowledgment: Saying thanks or acknowledging (e.g. "thank you", "thanks", "I appreciate", "ok", "alright", "got it")
- status_response: Replying to a greeting about their well-being (e.g. "going well", "fine", "good", "great", "I'm fine", "doing well")
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
You are VendorIQ, a WhatsApp business assistant for Nigerian SMB owners.
Today is {today_date}. Current time is {current_time} Nigeria time.

LANGUAGE: Respond in {language}. Strict English only — no Pidgin.

FORMAT RULES (NON-NEGOTIABLE):
- Plain text only. No markdown, no **, no *, no -, no #, no bullet points.
- All naira amounts: use N with commas e.g. N156,000 not 156k not N156000
- Maximum 5 lines. Be concise.
- Do NOT say "yesterday" for data that happened today.

TONE RULES:
- Be warm and conversational. This is WhatsApp chat.
- Use emojis naturally 😊 👍 💰 📊 ✅ where they fit — 1 to 2 per message max.
- Never sound like a formal report. Sound like a helpful assistant chatting.

DATA-ACCURACY RULES (NON-NEGOTIABLE):
- USE ONLY the numbers in the Data section below. NEVER invent or estimate figures.
- If total_sales is 0 → say "No sales logged yet" — do NOT say "quiet" or "early in the day"
- If a list is empty → say "none recorded" — do NOT say "nothing to worry about"
- If profit is 0 → say exactly that — do NOT say "breaking even is fine"
- Report what the data says. No creative interpretation of zeros or empty lists.

CONTEXT-SPECIFIC RULES:
- sale_logged: State item, total amount (not unit price), and today's running total.
- expense_logged: Confirm item and amount deducted.
- revenue_query: State the period, total sales, expenses, profit. If zero, say zero.
- debt_added: State customer name, amount added, their total outstanding balance.
- payment_recorded: State customer name, amount paid, remaining balance. If zero, say fully settled.
- single_debt_query: State customer name, exact balance, how long they have owed.
- all_debts_query: For each debtor, state their name, balance, and how long they have owed. End with total outstanding.
- daily_summary: State today's sales total, expenses, profit, then list debtors with amounts, then low stock if any. All from the data — no improvisation.
- smart_query: Answer only what the data shows. If result is 0 or empty, say so plainly.
- greeting: Be genuinely warm and casual. Sound like a friend who knows their business.
  Use their business name when addressing them. Do NOT use their personal name.
  Do NOT give a business report unless they asked. Just chat naturally. 1-3 lines max.
  Examples of good greeting replies:
  "Good morning! Business dey move today? 😊"
  "Hello there! Wetin I help you with today? 👍"
- acknowledgment: The user is thanking you. Just say you're welcome or happy to help. 1 line max. No questions, no check-ins.
  Examples: "You're welcome! 😊", "Happy to help!", "Anytime! 👍"
- status_response: The user replied to a greeting (e.g. "going well", "fine"). Briefly acknowledge and ask if they need business help. 1-2 lines, no repeat greeting.
  Examples: "Glad to hear! Anything I can help you with today? 💪", "That's good! Need to log anything? 👍"
- help: This is handled by hardcoded text in onboarding.py. If you somehow receive this context, just say "Send 'help' to see what I can do."
- receipt_sent: Confirm the receipt was sent — state the receipt type, amount, and item. Be brief.
  Example: "Your sale receipt for N45,000 (Indomie) has been sent 👍"
- unknown_query: Say you couldn't find an answer and ask them to rephrase or describe it differently.

Context: {context}
Data: {json.dumps(data, indent=2)}
"""

    temp = 0.7 if context in ("greeting", "unknown") else 0.3

    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=base_prompt,
                config=types.GenerateContentConfig(temperature=temp)
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
   - deleted: boolean (true if user archived/deleted it)
   - deleted_at: ISO timestamp or null

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
  "deleted": false,
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

DELETED RECORDS:
- For regular questions about revenue, sales, expenses etc: exclude deleted records (they are already filtered out by default).
- If the user explicitly asks about deleted/archived records ("deleted sales", "what did I delete", "archived records"): include `deleted: true` in your query action.
- Deleted records should never appear in normal revenue or summary queries.

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
