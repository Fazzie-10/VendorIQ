import React, { useState } from "react";
import { motion } from "motion/react";
import { 
  Zap, 
  Check, 
  X, 
  ChevronDown, 
  Phone, 
  MapPin, 
  Mail, 
  Sparkles, 
  ShieldCheck, 
  MessageCircle, 
  Play, 
  Heart, 
  ArrowRight,
  ClipboardList,
  AlertCircle,
  Sun,
  Moon,
  Package,
  BarChart3,
  Users,
  Search,
  Mic,
  FileText
} from "lucide-react";
import PhoneMockup from "./components/PhoneMockup";
import { 
  BrandLogo, 
  BrandFullLogo, 
  ThemeToggle 
} from "./components/BrandAssets";
import { 
  FAQ_DATA, 
  PRICING_PLANS, 
  HOW_IT_WORKS_STEPS, 
  FEATURES_DATA, 
  TICKER_ITEMS 
} from "./data";

declare global {
  interface Window { __VENDORIQ_PHONE__?: string; }
}
const VENDORIQ_PHONE = window.__VENDORIQ_PHONE__ || "";

export default function App() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  
  // Registration form states
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    businessName: ""
  });
  const [formLoading, setFormLoading] = useState(false);
  const [formSuccess, setFormSuccess] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [formError, setFormError] = useState("");

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    if (nextTheme === "light") {
      document.documentElement.classList.add("light");
    } else {
      document.documentElement.classList.remove("light");
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id === "fName" ? "name" : id === "fPhone" ? "phone" : "businessName"]: value
    }));
  };

  const handleSignup = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setFormError("");

    const { name, phone, businessName } = formData;
    if (!name.trim() || !phone.trim() || !businessName.trim()) {
      setFormError("Please fill in all fields, boss!");
      return;
    }

    setFormLoading(true);
    setFormError("");

    try {
      const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name.trim(),
          phone: formData.phone.trim(),
          business_name: formData.businessName.trim(),
        }),
      });
      const data = await res.json();
      if (data.success) {
        setFormSuccess(true);
        setSuccessMsg(`Send START to +${VENDORIQ_PHONE} on WhatsApp to activate your account.`);
      } else {
        setFormError(data.message || "Something went wrong. Try again.");
      }
    } catch {
      setFormError("Network error. Check your connection and try again.");
    } finally {
      setFormLoading(false);
    }
  };

  // Helper to render Lucide Icons based on metadata keys
  const renderFeatureIcon = (iconName: string) => {
    const iconClass = "w-6 h-6 text-[var(--green)]";
    switch (iconName) {
      case "Package": return <Package className={iconClass} />;
      case "BarChart3": return <BarChart3 className={iconClass} />;
      case "Users": return <Users className={iconClass} />;
      case "Search": return <Search className={iconClass} />;
      case "ClipboardList": return <ClipboardList className={iconClass} />;
      case "Mic": return <Mic className={iconClass} />;
      default: return <Zap className={iconClass} />;
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] font-sans antialiased selection:bg-[var(--green)]/20 selection:text-[var(--text)] transition-colors duration-300">
      
      {/* SECTION 01 — NAV */}
      <nav id="nav" className="sticky top-0 z-50 h-16 w-full bg-[var(--nav-bg)] backdrop-blur-md border-b border-[var(--border)] px-4 sm:px-[6%] flex items-center justify-between transition-colors duration-300">
        {/* Left — Logo */}
        <a href="#" className="select-none flex items-center">
          <BrandFullLogo theme={theme} className="w-6 h-6 sm:w-7 sm:h-7" textClassName="text-sm sm:text-base md:text-lg" />
        </a>

        {/* Center — Links (hidden on mobile) */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium">
          <a href="#how" className="text-[var(--text-muted)] hover:text-[var(--text)] transition duration-200">How it works</a>
          <a href="#features" className="text-[var(--text-muted)] hover:text-[var(--text)] transition duration-200">Features</a>
          <a href="#pricing" className="text-[var(--text-muted)] hover:text-[var(--text)] transition duration-200">Pricing</a>
          <a href="#faq" className="text-[var(--text-muted)] hover:text-[var(--text)] transition duration-200">FAQ</a>
        </div>

        {/* Right — Theme toggle + CTA */}
        <div className="flex items-center gap-2 sm:gap-4">
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
          
          <a 
            href="#signup" 
            className="inline-flex items-center justify-center bg-[var(--text)] text-[var(--bg)] font-display font-semibold text-[11px] sm:text-[13px] px-3 py-1.5 sm:px-5 sm:py-2 rounded-full hover:bg-[var(--green)] hover:text-black active:scale-95 transition-all duration-150 shadow-[0_4px_12px_rgba(0,0,0,0.05)] whitespace-nowrap"
          >
            Join Free Beta
          </a>
        </div>
      </nav>

      {/* SECTION 02 — HERO */}
      <section className="max-w-[1160px] mx-auto px-[6%] pt-16 md:pt-24 pb-16 grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-16 items-center">
        
        {/* Left side — Content */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          className="text-left space-y-6"
        >

          {/* Headline */}
          <h1 className="font-display text-4xl sm:text-5xl md:text-[56px] font-extrabold tracking-[-2px] leading-[1.08] text-[var(--text)]">
            Your WhatsApp is now your <span className="text-[var(--green)]">business database.</span>
          </h1>

          {/* Subheadline */}
          <p className="text-[var(--text-muted)] text-base sm:text-lg leading-relaxed max-w-[480px]">
            Your business brain, right on WhatsApp.<br />
            Just text what happened. VendorIQ tracks sales, surfaces live insights, and generates your daily executive reports — automatically.
            <span className="block mt-2 font-medium text-[var(--text)] opacity-90">No complex software. No manual analysis. Just pure business intelligence in your pocket.</span>
          </p>

          {/* CTA actions */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-4">
            <motion.a 
              href="#signup" 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-[var(--green)] text-black font-display font-bold text-[15px] px-8 py-4 rounded-full text-center hover:bg-emerald-300 transition-all shadow-[0_8px_24px_rgba(16,185,129,0.15)]"
            >
              Join Free Beta
            </motion.a>
            <motion.a 
              href="#how" 
              whileHover={{ x: 3 }}
              className="font-display font-medium text-sm text-[var(--text-muted)] hover:text-[var(--text)] py-3 text-center transition flex items-center justify-center gap-1.5"
            >
              See how it works <ArrowRight className="w-4 h-4" />
            </motion.a>
          </div>

          {/* Trust note */}
          <p className="text-xs text-[var(--text-muted)]/60 select-none">
            No credit card required · <span className="text-[var(--green)] font-medium">Free Beta Phase</span> · Works on any WhatsApp
          </p>

          {/* Sophisticated Dark Integrated Stats Grid */}
          <div className="flex items-center gap-4 pt-6 border-t border-[var(--border)]">
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-[var(--text)]">5k+</span>
              <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold">Queries Daily</span>
            </div>
            <div className="w-[1px] h-8 bg-[var(--border)] mx-2"></div>
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-[var(--text)]">98%</span>
              <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold">Accuracy</span>
            </div>
            <div className="w-[1px] h-8 bg-[var(--border)] mx-2"></div>
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-[var(--text)]">24/7</span>
              <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider font-semibold">Monitoring</span>
            </div>
          </div>
        </motion.div>

        {/* Right side — Phone Mockup with Blob */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.94, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.15 }}
          className="flex justify-center items-center w-full min-h-[460px]"
        >
          <PhoneMockup theme={theme} />
        </motion.div>

      </section>

      {/* SECTION 03 — SCROLLING MARQUEE TICKER */}
      <div className="w-full bg-[var(--surface-2)] border-y border-[var(--border)] py-5 overflow-hidden select-none transition-colors duration-300 relative">
        {/* Left side fade gradient */}
        <div 
          className="absolute left-0 top-0 bottom-0 w-16 sm:w-32 z-10 pointer-events-none"
          style={{ background: 'linear-gradient(to right, var(--surface-2), transparent)' }}
        />
        {/* Right side fade gradient */}
        <div 
          className="absolute right-0 top-0 bottom-0 w-16 sm:w-32 z-10 pointer-events-none"
          style={{ background: 'linear-gradient(to left, var(--surface-2), transparent)' }}
        />

        <div className="flex ticker-track">
          {/* Track is duplicated twice for a seamless infinite loop */}
          <div className="flex items-center shrink-0 animate-marquee">
            {TICKER_ITEMS.map((item, idx) => (
              <div key={`ticker-1-${idx}`} className="flex items-center">
                <span className="font-display text-[13px] font-semibold text-[var(--text-muted)] tracking-wider uppercase px-7 whitespace-nowrap">
                  {item}
                </span>
                <span className="text-[var(--green)] font-extrabold text-sm">•</span>
              </div>
            ))}
          </div>
          <div className="flex items-center shrink-0 animate-marquee">
            {TICKER_ITEMS.map((item, idx) => (
              <div key={`ticker-2-${idx}`} className="flex items-center">
                <span className="font-display text-[13px] font-semibold text-[var(--text-muted)] tracking-wider uppercase px-7 whitespace-nowrap">
                  {item}
                </span>
                <span className="text-[var(--green)] font-extrabold text-sm">•</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SECTION 04 — PROBLEM */}
      <section className="bg-[var(--surface)] border-b border-[var(--border)] py-20 px-[6%] transition-colors duration-300">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="max-w-[980px] mx-auto text-left space-y-6"
        >
          <span className="text-[11px] font-bold text-[var(--green)] tracking-[2.5px] uppercase block">The Problem</span>
          
          <h2 className="font-display text-3xl sm:text-4xl md:text-[42px] font-bold tracking-tight text-[var(--text)] leading-[1.15] max-w-[620px]">
            Every evening, most traders guess.
          </h2>

          <div className="text-[var(--text-muted)] text-base sm:text-[17px] leading-[1.85] max-w-[680px] space-y-6">
            <p>
              <strong className="text-[var(--text)] font-semibold">You've been here before.</strong>
            </p>
            <p>
              You close the shop, count the physical cash in the drawer, and still can't say with 100% confidence whether today was a profitable day or a slow loss.
            </p>
            <p>
              The paper notebook is filled with scribbles but practically useless. The mental math never quite adds up. Emeka has owed you ₦45,000 since last Thursday and you keep forgetting to follow up. By month-end, you're doing accounts over a whole precious weekend trying to piece together what actually happened.
            </p>
            <p>
              That's not your fault. That's simply what happens when a serious, hard-working business has no real system.
            </p>
            <p>
              <strong className="text-[var(--text)] font-semibold">VendorIQ gives you one — right on WhatsApp, where you already are.</strong>
            </p>
          </div>
        </motion.div>
      </section>

      {/* SECTION 05 — WITHOUT / WITH COMPARISON */}
      <section className="py-20 px-[6%] max-w-[1060px] mx-auto text-center space-y-12">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="space-y-3"
        >
          <span className="text-[11px] font-bold text-[var(--green)] tracking-[2.5px] uppercase block">Without vs With</span>
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-[var(--text)]">There's a better way to run your books.</h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left mt-12">
          
          {/* Without Card */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="bg-red-500/5 border border-red-500/10 rounded-2xl p-8 space-y-6"
          >
            <span className="text-red-500 font-display text-[13px] font-bold uppercase tracking-wider block flex items-center gap-2">
              <X className="w-4 h-4" /> Without VendorIQ
            </span>
            <ul className="space-y-4">
              {[
                "End the day **guessing** how much you made",
                "Forget who owes you — **until it gets awkward**",
                "No idea which goods are **actually profitable**",
                "Month-end accounts that **eat the whole weekend**",
                "Lose money you **don't even know** you're losing"
              ].map((text, i) => {
                const parts = text.split("**");
                return (
                  <li key={i} className="flex items-start gap-3 text-sm text-[var(--text-muted)]">
                    <div className="w-5 h-5 rounded-full bg-red-500/10 flex items-center justify-center shrink-0 mt-0.5">
                      <X className="w-3.5 h-3.5 text-red-500" />
                    </div>
                    <span>
                      {parts[0]}<strong className="text-[var(--text)] font-semibold">{parts[1]}</strong>{parts[2]}
                    </span>
                  </li>
                );
              })}
            </ul>
          </motion.div>

          {/* With Card */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-[var(--green-dim)] border border-[var(--green-border)] rounded-2xl p-8 space-y-6"
          >
            <span className="text-[var(--green)] font-display text-[13px] font-bold uppercase tracking-wider block flex items-center gap-2">
              <Check className="w-4 h-4" /> With VendorIQ
            </span>
            <ul className="space-y-4">
              {[
                "Real-time sales total — **always up to date**",
                "Every debt tracked with **name, amount, and date**",
                "Know your **best-selling items** automatically",
                "8pm daily summary sent straight to **your WhatsApp**",
                "Full picture of your business — **always in your pocket**"
              ].map((text, i) => {
                const parts = text.split("**");
                return (
                  <li key={i} className="flex items-start gap-3 text-sm text-[var(--text-muted)]">
                    <div className="w-5 h-5 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0 mt-0.5">
                      <Check className="w-3.5 h-3.5 text-[var(--green)]" />
                    </div>
                    <span>
                      {parts[0]}<strong className="text-[var(--text)] font-semibold">{parts[1]}</strong>{parts[2]}
                    </span>
                  </li>
                );
              })}
            </ul>
          </motion.div>

        </div>
      </section>

      {/* SECTION 06 — HOW IT WORKS */}
      <section id="how" className="bg-[var(--surface)] border-y border-[var(--border)] py-20 px-[6%] transition-colors duration-300">
        <div className="max-w-[1060px] mx-auto text-center space-y-12">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="space-y-3"
          >
            <span className="text-[11px] font-bold text-[var(--green)] tracking-[2.5px] uppercase block">How It Works</span>
            <h2 className="font-display text-3xl sm:text-4xl font-bold text-[var(--text)]">Up and running in 60 seconds.</h2>
            <p className="text-[var(--text-muted)] text-sm max-w-[500px] mx-auto">
              Skip complex tutorials. VendorIQ plugs straight into your WhatsApp, molding into your daily routine.
            </p>
          </motion.div>

          {/* Steps Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mt-12">
            {HOW_IT_WORKS_STEPS.map((step, idx) => (
              <motion.div 
                key={step.id} 
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                whileHover={{ 
                  y: -6, 
                  scale: 1.015,
                  borderColor: "rgba(52, 211, 153, 0.35)",
                  boxShadow: "0 20px 40px rgba(0, 0, 0, 0.12)"
                }}
                className="bg-[var(--surface-2)] backdrop-blur-md border border-[var(--border)] rounded-2xl p-6 flex flex-col justify-between hover:border-[var(--green)]/30 transition-all duration-300 shadow-lg group cursor-default"
              >
                <div>
                  {/* Step Num badge */}
                  <div className="w-8 h-8 rounded-lg bg-[var(--green-dim)] border border-[var(--green-border)] flex items-center justify-center text-xs font-bold text-[var(--green)] font-display mb-5">
                    {step.num}
                  </div>
                  <h3 className="font-display font-bold text-[17px] text-[var(--text)] mb-2">{step.title}</h3>
                  <p className="text-sm text-[var(--text-muted)] leading-relaxed mb-6">{step.desc}</p>
                </div>

                {/* Mini WhatsApp Preview */}
                <div className="bg-[var(--surface)] border border-[var(--border)]/50 rounded-xl p-3.5 space-y-2 select-none">
                  {step.chatPreview.map((msg, i) => (
                    <div 
                      key={i} 
                      className={`rounded-lg p-2 max-w-[90%] text-[10px] leading-snug ${
                        msg.sender === "user" 
                          ? "bg-[var(--surface-2)] text-[var(--text)] self-end ml-auto" 
                          : "bg-[var(--green-dim)] text-[var(--text)] self-start border border-[var(--green-border)]"
                      }`}
                    >
                      {msg.text}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 07 — FEATURES */}
      <section id="features" className="py-20 px-[6%] max-w-[1060px] mx-auto text-center space-y-12">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="space-y-3"
        >
          <span className="text-[11px] font-bold text-[var(--green)] tracking-[2.5px] uppercase block">Features</span>
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-[var(--text)]">Everything your trade needs — on WhatsApp.</h2>
        </motion.div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-left mt-12">
          {FEATURES_DATA.map((feat, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, y: 25 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              whileHover={{ 
                y: -6, 
                scale: 1.015,
                borderColor: "rgba(52, 211, 153, 0.35)",
                boxShadow: "0 20px 40px rgba(0, 0, 0, 0.12)"
              }}
              className="bg-[var(--surface-2)] backdrop-blur-md border border-[var(--border)] rounded-2xl p-7 flex flex-col justify-between hover:border-[var(--green)]/35 transition duration-300 shadow-md cursor-default"
            >
              <div className="space-y-4">
                <div className="w-10 h-10 rounded-xl bg-[var(--green-dim)] border border-[var(--green-border)] flex items-center justify-center mb-2">
                  {renderFeatureIcon(feat.icon)}
                </div>
                <h3 className="font-display font-semibold text-[16px] text-[var(--text)]">{feat.title}</h3>
                <p className="text-sm text-[var(--text-muted)] leading-relaxed">{feat.desc}</p>
              </div>

              {/* Command Prompt chip */}
              <div className="mt-5 pt-4 border-t border-[var(--border)]/30">
                <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider block mb-1.5 font-bold">Try texting:</span>
                <div className="inline-block bg-[var(--green-dim)] border border-[var(--green-border)] rounded-md px-3 py-1.5 font-mono text-[11px] text-[var(--green)]">
                  {feat.command}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* SECTION 08 — PRICING */}
      <section id="pricing" className="bg-[var(--surface)] border-y border-[var(--border)] py-20 px-[6%] transition-colors duration-300">
        <div className="max-w-[1060px] mx-auto text-center space-y-12">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="space-y-3"
          >
            <span className="text-[11px] font-bold text-[var(--green)] tracking-[2.5px] uppercase block">Pricing Plans</span>
            <h2 className="font-display text-3xl sm:text-4xl font-bold text-[var(--text)]">100% Free Beta</h2>
            <p className="text-[var(--text-muted)] text-sm max-w-[500px] mx-auto mt-2">
              Get full unrestricted access to all features during our public beta. No credit card required.
            </p>
          </motion.div>

          {/* Pricing Grid */}
          <div className="flex justify-center mt-12 text-center">
            {PRICING_PLANS.map((plan, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, scale: 0.95, y: 30 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6 }}
                whileHover={{ 
                  y: -6, 
                  scale: 1.018,
                  borderColor: plan.featured ? "rgba(52, 211, 153, 0.55)" : "rgba(52, 211, 153, 0.35)",
                  boxShadow: "0 25px 50px rgba(0, 0, 0, 0.18)"
                }}
                className={`bg-[var(--surface-2)] backdrop-blur-[16px] border rounded-3xl p-8 relative flex flex-col justify-between transition-all duration-300 shadow-xl max-w-md w-full cursor-default ${
                  plan.featured 
                    ? "border-[var(--green)]/40 bg-[var(--surface-2)] ring-1 ring-[var(--green)]/20" 
                    : "border-[var(--border)] hover:border-[var(--text-muted)]/30"
                }`}
              >
                {/* Featured Badge */}
                {plan.featured && plan.badge && (
                  <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-[var(--green)] text-black font-display font-bold text-[10px] tracking-widest uppercase px-4 py-1.5 rounded-full select-none shadow">
                    {plan.badge}
                  </span>
                )}

                <div className="space-y-5">
                  <div>
                    <span className="text-xs font-display font-semibold text-[var(--text-muted)] uppercase tracking-wider block">
                      {plan.name}
                    </span>
                    <div className="flex items-baseline justify-center gap-1 mt-2">
                      <span className="font-display text-3xl sm:text-4xl font-bold text-[var(--text)]">{plan.price}</span>
                      <span className="text-xs text-[var(--text-muted)] font-normal">{plan.period}</span>
                    </div>
                    <span className="text-xs text-[var(--text-muted)]/75 block mt-1 font-medium italic">{plan.tagline}</span>
                  </div>

                  <hr className="border-[var(--border)]" />

                  {/* Feature list */}
                  <ul className="space-y-3.5 text-xs text-[var(--text-muted)] inline-block text-left mx-auto">
                    {plan.features.map((feat, fIdx) => (
                      <li key={fIdx} className="flex items-center gap-2.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-[var(--green)] shrink-0" />
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* CTA Button */}
                <div className="mt-8">
                  <motion.a 
                    href={plan.href}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`block w-full py-3.5 rounded-xl font-display font-semibold text-xs text-center tracking-wider uppercase transition-all duration-150 ${
                      plan.featured 
                        ? "bg-[var(--green)] text-black font-bold shadow-[0_4px_12px_rgba(16,185,129,0.15)] hover:bg-emerald-300" 
                        : "border border-[var(--border)] hover:border-[var(--text-muted)] text-[var(--text-muted)] hover:text-[var(--text)] bg-transparent"
                    }`}
                  >
                    {plan.cta}
                  </motion.a>
                </div>

              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 09 — WHY INSIGHTSHUB */}
      <section className="py-20 px-[6%] max-w-[1060px] mx-auto text-center">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 text-left">
          
          <motion.div 
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5 }}
            className="space-y-3"
          >
            <div className="w-12 h-12 rounded-2xl bg-[var(--green-dim)] border border-[var(--green-border)] flex items-center justify-center mb-3">
              <MapPin className="w-6 h-6 text-[var(--green)]" />
            </div>
            <h4 className="font-display font-bold text-[17px] text-[var(--text)]">Built for Nigeria</h4>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">
              In plain English, raw Pidgin, Yoruba, or Igbo. VendorIQ understands how local traders actually speak and write, including native shorthand.
            </p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="space-y-3"
          >
            <div className="w-12 h-12 rounded-2xl bg-[var(--green-dim)] border border-[var(--green-border)] flex items-center justify-center mb-3">
              <Phone className="w-6 h-6 text-[var(--green)]" />
            </div>
            <h4 className="font-display font-bold text-[17px] text-[var(--text)]">Works on any WhatsApp</h4>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">
              No expensive device needed. No custom setup. Simply message VendorIQ from your regular WhatsApp number just like texting a customer.
            </p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="space-y-3"
          >
            <div className="w-12 h-12 rounded-2xl bg-[var(--green-dim)] border border-[var(--green-border)] flex items-center justify-center mb-3">
              <Zap className="w-6 h-6 text-[var(--green)]" />
            </div>
            <h4 className="font-display font-bold text-[17px] text-[var(--text)]">Live in 60 seconds</h4>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">
              Sign up, send START on WhatsApp, and you are logged. Zero onboarding calls, zero configs, and absolutely zero manuals.
            </p>
          </motion.div>

        </div>
      </section>

      {/* SECTION 10 — FAQ */}
      <section id="faq" className="bg-[var(--surface)] border-y border-[var(--border)] py-20 px-[6%] transition-colors duration-300">
        <div className="max-w-[820px] mx-auto text-center space-y-12">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="space-y-3"
          >
            <span className="text-[11px] font-bold text-[var(--green)] tracking-[2.5px] uppercase block">FAQ</span>
            <h2 className="font-display text-3xl sm:text-4xl font-bold text-[var(--text)]">Honest answers to real questions.</h2>
          </motion.div>

          {/* Accordion List */}
          <div className="divide-y divide-[var(--border)] text-left mt-12">
            {FAQ_DATA.map((faq, i) => {
              const isOpen = openFaq === i;
              return (
                <div key={i} className="py-5">
                  <button 
                    onClick={() => toggleFaq(i)}
                    className="w-full flex items-center justify-between text-left font-display font-semibold text-[15px] text-[var(--text)] py-2 cursor-pointer group hover:text-[var(--green)] transition duration-150 select-none"
                  >
                    <span>{faq.question}</span>
                    <span className={`text-xl font-light text-[var(--text-muted)] transition-transform duration-300 ${isOpen ? "rotate-45 text-[var(--green)]" : "rotate-0"}`}>
                      +
                    </span>
                  </button>
                  
                  {/* Expandable Panel */}
                  <div 
                    className={`overflow-hidden transition-all duration-300 ${
                      isOpen ? "max-h-[220px] opacity-100 mt-3" : "max-h-0 opacity-0 pointer-events-none"
                    }`}
                  >
                    <p className="text-sm text-[var(--text-muted)] leading-relaxed pb-2">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* SECTION 11 — SIGNUP FORM */}
      <section id="signup" className="py-20 px-[6%] text-center max-w-[1060px] mx-auto space-y-12">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="space-y-3"
        >
          <span className="text-[11px] font-bold text-[var(--green)] tracking-[2.5px] uppercase block">Get Started</span>
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-[var(--text)]">Join the Free Beta today.</h2>
          <p className="text-[var(--text-muted)] text-sm max-w-[400px] mx-auto">
            No credit card. No apps to download. Just simple trading intelligence on WhatsApp.
          </p>
        </motion.div>

        {/* Lead Form Container Card */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.6 }}
          className="max-w-[460px] mx-auto bg-[var(--surface-2)] backdrop-blur-[16px] border border-[var(--border)] rounded-3xl p-8 sm:p-10 shadow-2xl text-left"
        >
          
          {!formSuccess ? (
            /* ACTIVE REGISTRATION FORM */
            <form id="viqForm" onSubmit={handleSignup} className="space-y-5">
              
              <div className="space-y-2">
                <label htmlFor="fName" className="block text-[11px] font-bold text-[var(--text-muted)] uppercase tracking-wider">
                  Your Name
                </label>
                <input 
                  type="text" 
                  id="fName" 
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g. Chisom Okafor" 
                  autoComplete="name"
                  className="w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm text-[var(--text)] focus:border-[var(--green)]/50 focus:outline-none transition duration-200 placeholder-[var(--text-muted)]/50"
                  required
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="fPhone" className="block text-[11px] font-bold text-[var(--text-muted)] uppercase tracking-wider">
                  WhatsApp Number
                </label>
                <input 
                  type="tel" 
                  id="fPhone" 
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="e.g. 08012345678" 
                  autoComplete="tel"
                  className="w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm text-[var(--text)] focus:border-[var(--green)]/50 focus:outline-none transition duration-200 placeholder-[var(--text-muted)]/50"
                  required
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="fBiz" className="block text-[11px] font-bold text-[var(--text-muted)] uppercase tracking-wider">
                  Business Name
                </label>
                <input 
                  type="text" 
                  id="fBiz" 
                  value={formData.businessName}
                  onChange={handleInputChange}
                  placeholder="e.g. Chisom's Provisions" 
                  autoComplete="organization"
                  className="w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm text-[var(--text)] focus:border-[var(--green)]/50 focus:outline-none transition duration-200 placeholder-[var(--text-muted)]/50"
                  required
                />
              </div>

              {formError && (
                <div className="flex items-center gap-2 text-xs text-red-400 bg-red-500/10 border border-red-500/20 p-3 rounded-lg select-none">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              <button 
                type="submit" 
                id="submitBtn"
                disabled={formLoading}
                className="w-full bg-[var(--green)] text-black font-display font-bold text-[15px] py-4 rounded-xl cursor-pointer hover:bg-emerald-300 active:scale-98 transition disabled:opacity-65 disabled:cursor-not-allowed select-none shadow-[0_4px_12px_rgba(16,185,129,0.15)] mt-4 animate-none"
              >
                {formLoading ? "Creating account..." : "Create account — it's free"}
              </button>

            </form>
          ) : (
            /* SUCCESS RESPONSE SCREEN */
            <div id="viqSuccess" className="bg-[var(--green-dim)] border border-[var(--green-border)] rounded-2xl p-7 text-center space-y-4">
              <Sparkles className="w-10 h-10 text-[var(--green)] mx-auto animate-bounce" />
              <h3 className="font-display font-extrabold text-[var(--green)] text-lg">Account created!</h3>
              
              <p className="text-xs text-[var(--text-muted)] leading-relaxed whitespace-pre-line" id="successMsg">
                {successMsg}
              </p>

              <div className="pt-4">
                <a 
                  href={`https://wa.me/${VENDORIQ_PHONE}`}
                  target="_blank"
                  referrerPolicy="no-referrer"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 bg-[var(--green)] text-black font-display font-bold text-xs tracking-wider uppercase px-6 py-3 rounded-xl hover:bg-emerald-300 transition shadow"
                >
                  <MessageCircle className="w-4 h-4" /> Go To WhatsApp
                </a>
              </div>
            </div>
          )}

        </motion.div>
      </section>

      {/* SECTION 12 — FOOTER */}
      <footer className="bg-[var(--surface-2)] border-t border-[var(--border)] py-12 px-[6%] transition-colors duration-300">
        <div className="max-w-[1060px] mx-auto flex flex-col items-center justify-center text-center gap-6 select-none">
          
          <div className="flex items-center gap-2 font-display font-bold text-lg tracking-tight text-[var(--text)]">
            <BrandFullLogo theme={theme} className="w-5.5 h-5.5 sm:w-6.5 sm:h-6.5" textClassName="text-sm sm:text-base" />
          </div>

          <div className="flex flex-wrap justify-center gap-x-8 gap-y-3 text-[11px] font-bold uppercase tracking-widest text-[var(--text-muted)]">
            <a href="#how" className="hover:text-[var(--green)] transition">How It Works</a>
            <a href="#features" className="hover:text-[var(--green)] transition">Features</a>
            <a href="#pricing" className="hover:text-[var(--green)] transition">Pricing</a>
            <a href="#faq" className="hover:text-[var(--green)] transition">FAQ</a>
          </div>

          <div className="space-y-2 mt-2">
            <p className="text-xs text-[var(--text-muted)]">© 2026 InsightsHub Ltd. All Rights Reserved. Abuja, Nigeria.</p>
          </div>

        </div>
      </footer>

    </div>
  );
}
