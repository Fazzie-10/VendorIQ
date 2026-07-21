export interface FAQItem {
  question: string;
  answer: string;
}

export interface PricingPlan {
  name: string;
  price: string;
  period: string;
  tagline: string;
  features: string[];
  cta: string;
  featured: boolean;
  badge?: string;
  href: string;
}

export interface StepItem {
  id: string;
  num: string;
  title: string;
  desc: string;
  chatPreview: { sender: "user" | "bot"; text: string }[];
}

export interface FeatureItem {
  icon: string;
  title: string;
  desc: string;
  command: string;
}

export const TICKER_ITEMS = [
  "Sales Tracking",
  "Daily Reports",
  "Debt Management",
  "Voice Notes",
  "Revenue Queries",
  "Receipts",
  "Inventory Tracking",
  "WhatsApp Native",
];

export const FAQ_DATA: FAQItem[] = [
  {
    question: "What if I type in Pidgin, Yoruba, or voice notes?",
    answer: "VendorIQ is built for Nigeria. It understands Pidgin, English, Yoruba, Igbo, and code-switching (mixed language). Phrases like 'I sell shoe 3k' or 'Emeka never pay 45k' work perfectly. You can even send voice notes; VendorIQ automatically transcribes and logs them.",
  },
  {
    question: "Is my business data private and secure?",
    answer: "Absolutely. Your data is strictly private and stored with bank-grade encryption. It is only accessible to you from your verified WhatsApp phone number. We never share, sell, or disclose your sales or business numbers to anyone.",
  },
  {
    question: "Is VendorIQ really free?",
    answer: "Yes! VendorIQ is currently in Free Beta. You can log as many sales, debts, and transactions as you want, and receive daily reports, entirely for free. We will give you plenty of notice on WhatsApp before introducing any paid features in the future.",
  },
  {
    question: "What features are included in the Free Beta?",
    answer: "All premium features are fully unlocked during the beta phase. This includes unlimited transaction tracking, voice note logging, automated debt tracking, instant digital receipt generation, and the 8pm daily summary report sent directly to your WhatsApp.",
  },
  {
    question: "Can I use VendorIQ for any type of business?",
    answer: "Yes! VendorIQ is optimized for physical goods retail, boutiques, provision stores, supermarket owners, food vendors, restaurants, and wholesalers. Service providers like salons or mechanics can also use it to track their daily revenue and credit book.",
  },
];

export const PRICING_PLANS: PricingPlan[] = [
  {
    name: "Free Beta",
    price: "₦0",
    period: "/ forever in beta",
    tagline: "All features unlocked during our beta phase",
    features: [
      "Unlimited sales logging",
      "Debt tracking & reminders",
      "Daily 8pm summary",
      "Natural language queries",
      "Digital receipt generation",
    ],
    cta: "Start free in Beta",
    featured: true,
    badge: "Beta Phase",
    href: "#signup",
  }
];

export const HOW_IT_WORKS_STEPS: StepItem[] = [
  {
    id: "step1",
    num: "01",
    title: "Sign up below",
    desc: "Fill out the quick form. It takes less than a minute. No credit card required, no app downloads, no complicated setup — 100% free while in beta.",
    chatPreview: [
      { sender: "bot", text: "Welcome to VendorIQ! Send START to activate your free beta account." },
    ],
  },
  {
    id: "step2",
    num: "02",
    title: "Send START on WhatsApp",
    desc: "Simply message our official VendorIQ phone number on WhatsApp with the word START to instantly link and activate your secure ledger.",
    chatPreview: [
      { sender: "user", text: "START" },
      { sender: "bot", text: "Account activated! Let's go. You can now log sales by typing them." },
    ],
  },
  {
    id: "step3",
    num: "03",
    title: "Just text naturally",
    desc: "Sold something? Text it. Customer owes you? Log it. Need to know your profit? Just ask in plain language. We do all the math.",
    chatPreview: [
      { sender: "user", text: "Sold 5 bags indomie at 3500" },
      { sender: "bot", text: "Verified: 5 × ₦3,500 = ₦17,500 logged. Today's total is ₦17,500." },
    ],
  },
];

export const FEATURES_DATA: FeatureItem[] = [
  {
    icon: "Package",
    title: "Log sales by chatting",
    desc: "Text what you sold — in English, Pidgin, or a voice note. VendorIQ calculates the math and records it.",
    command: '"Sold 3 bags rice at 52k"',
  },
  {
    icon: "BarChart3",
    title: "8pm daily business report",
    desc: "Every evening at 8pm, VendorIQ sends your complete summary — total sales, expenses, profit, and outstanding debts.",
    command: '"Summary" or auto at 8pm',
  },
  {
    icon: "Users",
    title: "Debt tracking that works",
    desc: "Log who owes you, how much, and how long. Send automated, gentle reminders directly to their WhatsApp.",
    command: '"Emeka owes 45k for Thursday"',
  },
  {
    icon: "Search",
    title: "Ask anything about your books",
    desc: "Ask your business questions in plain text or voice. Get instant, accurate reports on revenue, trends, or debtors.",
    command: '"How much did I make last month?"',
  },
  {
    icon: "ClipboardList",
    title: "Instant PDF Receipts",
    desc: "Generate professional digital receipts on demand. Send them directly to your customers with one click.",
    command: '"Send me receipt for Emeka"',
  },
  {
    icon: "Mic",
    title: "Voice notes work too",
    desc: "Too busy to type? Just speak. VendorIQ automatically transcribes and logs the transaction for you.",
    command: "Send a voice note",
  },
];
