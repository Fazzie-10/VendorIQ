# VendorIQ

**WhatsApp-native business intelligence for Nigerian SMB owners.**

No app to install. No dashboard to learn. Just WhatsApp.

Log sales, track debts, check revenue, and get daily summaries — all by sending messages on WhatsApp.

---

## Tech Stack

- Python 3.12+, FastAPI 0.115+
- Supabase (PostgreSQL)
- Google Gemini 2.0 Flash (intent parsing + response generation)
- Evolution API v2 (WhatsApp automation)
- APScheduler (daily summary cron)

---

## Setup

### 1. Evolution API (WhatsApp Gateway)

Run Evolution API v2 locally with Docker:

```bash
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=your_chosen_api_key \
  -e DATABASE_ENABLED=false \
  -e CORS_ORIGIN="*" \
  atendai/evolution-api:v2.2.3
```

After running, visit `http://localhost:8080/manager` to create an instance named **vendoriq** and scan the QR code with your WhatsApp.

### 2. Clone and Configure

```bash
git clone <repo-url>
cd vendoriq
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

### 3. Supabase Database

Create a Supabase project and run the schema from `db/schema.sql` in the SQL Editor.

### 4. Gemini API Key

Get a Gemini API key at https://aistudio.google.com/apikey

### 5. Cloudflare Tunnel (for Webhook URL)

For testing, use a quick tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

This gives a temporary `*.trycloudflare.com` URL — fine for MVP testing.

For production, set up a named tunnel:

```bash
cloudflared tunnel login
cloudflared tunnel create vendoriq
```

Configure `~/.cloudflared/config.yml` and run:

```bash
cloudflared tunnel run vendoriq
```

### 6. Run the App

```bash
python main.py
```

### 7. Set Up Webhook

Configure Evolution API to send webhooks to your tunnel URL:

```
POST http://localhost:8080/webhook/set/vendoriq
Body: { "url": "https://your-tunnel-url.trycloudflare.com/webhook" }
```

---

## Usage Flow

1. Owner visits landing page and signs up with WhatsApp number
2. Owner sends **START** to the VendorIQ WhatsApp number
3. Account activates — owner gets a welcome message
4. Owner messages naturally: "Sold 3 bags of rice at 52k", "How much today?", "Emeka owes 45k"
5. VendorIQ logs, tracks, and responds instantly

---

## Project Structure

```
vendoriq/
├── main.py              # FastAPI entry point
├── config.py            # Settings from .env
├── services/            # Supabase, Gemini, Evolution API
├── handlers/            # Message routing and business logic
├── models/              # Pydantic schemas
├── db/schema.sql        # Database tables
├── templates/           # Landing page
├── static/              # CSS
├── scheduler.py         # Daily summary cron
├── requirements.txt
└── .env.example
```

---

## License

MIT
