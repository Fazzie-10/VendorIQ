# VendorIQ

**WhatsApp-native business intelligence for Nigerian SMB owners.**

No app to install. No dashboard to learn. Just WhatsApp.

Log sales, track debts, check revenue, and get daily summaries — all by sending messages on WhatsApp.

---

## Tech Stack

- Python 3.12+, FastAPI
- Supabase (PostgreSQL)
- Google Gemini 2.0 Flash (intent parsing + response generation)
- Green API (WhatsApp automation — cloud-hosted, no Docker)
- APScheduler (daily summary cron)

---

## Quick Start

### 1. Green API Setup

1. Sign up at [green-api.com](https://green-api.com)
2. Create an instance and pair your WhatsApp number
3. Note your `idInstance` and `apiToken`

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

Create a Supabase project and run `db/schema.sql` in the SQL Editor.

### 4. Gemini API Key

Get a Gemini API key at https://aistudio.google.com/apikey

### 5. Run the App

```bash
python main.py
```

### 6. Set Up Webhook

Configure Green API to send incoming messages to your webhook URL:

1. Go to Green API → your instance → Settings
2. Set Webhook URL to `https://your-url.com/webhook`
3. Or for local testing, use a tunnel: `cloudflared tunnel --url http://localhost:8000`

---

## Usage Flow

1. Owner visits landing page and signs up with WhatsApp number
2. Owner sends **START** to the VendorIQ WhatsApp number
3. Account activates — owner gets a welcome message
4. Owner messages naturally: "Sold 3 bags of rice at 52k", "How much today?", "Emeka owes 45k"
5. VendorIQ logs, tracks, and responds instantly

---

## Railway Deployment

Deploy directly from GitHub:

1. Push to a GitHub repo
2. Create a new Railway project from the repo
3. Add the environment variables from `.env.example` in Railway dashboard
4. Railway auto-detects `Procfile` and `railway.json`
5. Set the domain and update your Green API webhook URL

No Docker needed. Railway handles Python natively via Nixpacks.

---

## Project Structure

```
vendoriq/
├── main.py              # FastAPI entry point
├── config.py            # Settings from .env
├── Procfile             # Railway start command
├── railway.json         # Railway config
├── services/            # Supabase, Gemini, Green API
├── handlers/            # Message routing and business logic
├── models/              # Pydantic schemas
├── db/schema.sql        # Database tables
├── templates/           # Landing page
├── static/              # CSS
├── scheduler.py         # Daily summary cron
├── requirements.txt
├── .env.example
└── README.md
```

---

## License

MIT
