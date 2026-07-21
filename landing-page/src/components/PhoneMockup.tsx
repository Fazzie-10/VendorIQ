import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  MessageSquare, 
  Send, 
  RefreshCw, 
  ChevronLeft, 
  Phone, 
  Video, 
  CheckCheck, 
  Plus,
  Users,
  BarChart3,
  Settings
} from "lucide-react";
import { ChatMessage, LedgerState } from "../types";
import { BrandLogo } from "./BrandAssets";

export default function PhoneMockup({ theme = "dark" }: { theme?: "dark" | "light" }) {
  const [isInteractive, setIsInteractive] = useState<boolean>(false);
  const [inputText, setInputText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState<boolean>(false);

  // Business state updated by chatting
  const [ledgerState, setLedgerState] = useState<LedgerState>({
    sales: [],
    debts: [],
    expenses: []
  });

  // Chat message logs
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const userHasScrolledUpRef = useRef<boolean>(false);

  // Run the auto-demo timeline (natural conversational typing loop)
  useEffect(() => {
    if (isInteractive) return;

    let timeoutIds: NodeJS.Timeout[] = [];
    
    const runTimeline = () => {
      setMessages([]);
      setLedgerState({ sales: [], debts: [], expenses: [] });
      setIsTyping(false);
      userHasScrolledUpRef.current = false;

      const addMsg = (sender: "user" | "bot" | "timestamp", text: string, delay: number, id: string) => {
        const tId = setTimeout(() => {
          setMessages(prev => [
            ...prev,
            {
              id,
              sender,
              text,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }
          ]);
        }, delay);
        timeoutIds.push(tId);
      };

      const setTyping = (typingState: boolean, delay: number) => {
        const tId = setTimeout(() => {
          setIsTyping(typingState);
        }, delay);
        timeoutIds.push(tId);
      };

      const updateState = (updater: (prev: LedgerState) => LedgerState, delay: number) => {
        const tId = setTimeout(() => {
          setLedgerState(updater);
        }, delay);
        timeoutIds.push(tId);
      };

      // Step 0: Timestamp "Today"
      addMsg("timestamp", "Today", 300, "demo-0");

      // Step 1: User logs sale
      addMsg("user", "Sold 3 bags rice at 52k", 1300, "demo-1");

      // Step 2: Bot starts typing
      setTyping(true, 1800);

      // Step 3: Bot finishes typing & sends logged confirmation, updates chart
      setTyping(false, 3200);
      addMsg("bot", "Logged: 3 × ₦52,000 = ₦156,000 sales recorded. Today's total is ₦156,000.", 3200, "demo-2");
      updateState(prev => ({
        ...prev,
        sales: [{ description: "bags of rice", quantity: 3, pricePerUnit: 52000, total: 156000, date: "Today" }]
      }), 3200);

      // Step 4: User logs debt
      addMsg("user", "Emeka owes me 45k", 4800, "demo-3");

      // Step 5: Bot starts typing
      setTyping(true, 5300);

      // Step 6: Bot finishes typing & sends logged confirmation, updates debts
      setTyping(false, 6800);
      addMsg("bot", "Logged: Emeka: ₦45,000 outstanding credit added. Reminders scheduled.", 6800, "demo-4");
      updateState(prev => ({
        ...prev,
        debts: [{ debtor: "Emeka", amount: 45000, date: "Today", status: "unpaid" }]
      }), 6800);

      // Step 7: User queries total
      addMsg("user", "How much today?", 8300, "demo-5");

      // Step 8: Bot starts typing
      setTyping(true, 8800);

      // Step 9: Bot sends full daily report summary
      setTyping(false, 10300);
      addMsg("bot", "Daily Summary Report:\n\nTotal Sales: ₦156,000\nOutstanding Debts: ₦45,000\nTotal Expenses: ₦0\n\nEstimated Profit: ₦156,000. All entries synchronized.", 10300, "demo-6");
    };

    runTimeline();

    // Loop interval to keep running the demo
    const intervalId = setInterval(() => {
      timeoutIds.forEach(clearTimeout);
      timeoutIds = [];
      runTimeline();
    }, 18000);

    return () => {
      timeoutIds.forEach(clearTimeout);
      clearInterval(intervalId);
    };
  }, [isInteractive]);

  // Scroll event handler to check if user has manually scrolled up
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const el = e.currentTarget;
    if (el) {
      const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 35;
      userHasScrolledUpRef.current = !isAtBottom;
    }
  };

  // Scroll to bottom of the chat container without affecting the main page scroll
  useEffect(() => {
    const el = chatContainerRef.current;
    if (el && !userHasScrolledUpRef.current) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages, isLoading, isTyping]);

  // Handle User Input in Test Drive (Pure Front-End simulated natural language parser)
  const handleSendMessage = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    const userText = inputText.trim();
    setInputText("");
    setIsInteractive(true);
    userHasScrolledUpRef.current = false; // reset scroll lock on user sending message

    // Push User message
    setMessages(prev => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        sender: "user",
        text: userText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);

    setIsLoading(true);

    // Simulate natural response typing (staggered delay)
    setTimeout(() => {
      let replyMessage = "";
      const lowercaseMsg = userText.toLowerCase();
      let nextState = { ...ledgerState };

      if (
        lowercaseMsg.includes("rice") || 
        lowercaseMsg.includes("bag") || 
        lowercaseMsg.includes("sold") || 
        lowercaseMsg.includes("sell") || 
        lowercaseMsg.includes("indomie") || 
        lowercaseMsg.includes("carton") || 
        lowercaseMsg.includes("shoe")
      ) {
        let qty = 1;
        let price = 15000;
        let item = "goods";
        
        const qtyMatch = lowercaseMsg.match(/\b\d+\b/);
        if (qtyMatch) {
          qty = parseInt(qtyMatch[0]);
        }

        if (lowercaseMsg.includes("rice")) {
          item = "bags of rice";
          price = 52000;
        } else if (lowercaseMsg.includes("indomie")) {
          item = "cartons of Indomie";
          price = 4500;
        } else if (lowercaseMsg.includes("shoe")) {
          item = "shoes";
          price = 3000;
        }

        const kMatch = lowercaseMsg.match(/at\s+(\d+)\s*k/);
        if (kMatch) {
          price = parseInt(kMatch[1]) * 1000;
        } else {
          const numMatch = lowercaseMsg.match(/at\s+(\d+)/);
          if (numMatch) {
            price = parseInt(numMatch[1]);
          }
        }

        const total = qty * price;
        nextState.sales = [
          ...nextState.sales, 
          { description: item, quantity: qty, pricePerUnit: price, total: total, date: "Today" }
        ];
        replyMessage = `Logged: ${qty} × ₦${price.toLocaleString()} = ₦${total.toLocaleString()} for ${item}. Ledger updated successfully.`;

      } else if (lowercaseMsg.includes("owes") || lowercaseMsg.includes("debt") || lowercaseMsg.includes("borrow")) {
        let debtor = "Customer";
        let amount = 10000;

        if (lowercaseMsg.includes("emeka")) debtor = "Emeka";
        else if (lowercaseMsg.includes("chioma")) debtor = "Chioma";
        else if (lowercaseMsg.includes("tunde")) debtor = "Tunde";
        else if (lowercaseMsg.includes("alhaji")) debtor = "Alhaji";

        const kMatch = lowercaseMsg.match(/me\s+(\d+)\s*k/) || lowercaseMsg.match(/owes\s+(\d+)\s*k/) || lowercaseMsg.match(/(\d+)\s*k/);
        if (kMatch) {
          amount = parseInt(kMatch[1]) * 1000;
        } else {
          const numMatch = lowercaseMsg.match(/me\s+(\d+)/) || lowercaseMsg.match(/owes\s+(\d+)/) || lowercaseMsg.match(/(\d+)/);
          if (numMatch) {
            amount = parseInt(numMatch[1]);
          }
        }

        nextState.debts = [
          ...nextState.debts, 
          { debtor: debtor, amount: amount, date: "Today", status: "unpaid" }
        ];
        replyMessage = `Logged: Outstanding debt of ₦${amount.toLocaleString()} for ${debtor}. Reminders scheduled.`;

      } else if (lowercaseMsg.includes("summary") || lowercaseMsg.includes("how much") || lowercaseMsg.includes("today") || lowercaseMsg.includes("total")) {
        const totalSales = nextState.sales.reduce((acc, s) => acc + s.total, 0);
        const totalDebts = nextState.debts.reduce((acc, d) => acc + (d.status === "unpaid" ? d.amount : 0), 0);
        const netProfit = totalSales;

        replyMessage = `Daily Summary Report:\n\nTotal Sales: ₦${totalSales.toLocaleString()}\nOutstanding Debts: ₦${totalDebts.toLocaleString()}\nTotal Expenses: ₦0\n\nEstimated Profit: ₦${netProfit.toLocaleString()}. All entries synchronized.`;

      } else if (lowercaseMsg.includes("hello") || lowercaseMsg.includes("hi") || lowercaseMsg.includes("start")) {
        replyMessage = `Welcome to VendorIQ! Your WhatsApp assistant is ready.\n\nTry entering:\n- "Sold 3 bags rice at 52k"\n- "Emeka owes me 45k"\n- "Summary"`;
      } else {
        replyMessage = `Received: "${userText}". Entry stored. Log sales using 'Sold [item] at [price]' or debts using '[name] owes [amount]'. Type 'Summary' for reports.`;
      }

      setMessages(prev => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          sender: "bot",
          text: replyMessage,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      setLedgerState(nextState);
      setIsLoading(false);
    }, 1200);
  };

  const handleReset = () => {
    setIsInteractive(false);
    setInputText("");
    setMessages([]);
    setLedgerState({ sales: [], debts: [], expenses: [] });
    userHasScrolledUpRef.current = false;
  };

  const triggerPreset = (text: string) => {
    setInputText(text);
    setIsInteractive(true);
    userHasScrolledUpRef.current = false;
  };

  const isLight = theme === "light";
  const waHeaderBg = isLight ? "bg-[#f0f2f5]" : "bg-[#1f2c34]";
  const waHeaderCol = isLight ? "text-[#111b21]" : "text-[#e9edef]";
  const waHeaderSubCol = isLight ? "text-zinc-500" : "text-[#8696a0]";
  const waUserBubble = isLight ? "bg-[#d9fdd3] text-[#111b21] border-[#d9fdd3] rounded-tr-none shadow-[0_1px_0.5px_rgba(0,0,0,0.1)]" : "bg-[#005c4b] text-[#e9edef] border-[#005c4b] rounded-tr-none shadow-[0_1px_0.5px_rgba(0,0,0,0.15)]";
  const waBotBubble = isLight ? "bg-white text-[#111b21] border-white rounded-tl-none shadow-[0_1px_0.5px_rgba(0,0,0,0.1)]" : "bg-[#202c33] text-[#e9edef] border-[#202c33] rounded-tl-none shadow-[0_1px_0.5px_rgba(0,0,0,0.15)]";
  const waInputBg = isLight ? "bg-white border-zinc-200" : "bg-[#2a3942] border-[#2a3942]";
  const waInputText = isLight ? "text-[#111b21]" : "text-[#e9edef]";
  const waInputPlaceholder = isLight ? "placeholder-[#8696a0]" : "placeholder-[#8696a0]";
  const waFormBg = isLight ? "bg-[#f0f2f5] border-t border-zinc-200" : "bg-[#1f2c34] border-t border-zinc-800/80";

  return (
    <div className="relative flex items-center justify-center w-full max-w-[340px] px-2" id="iphone-showcase">
      
      {/* Background Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] sm:w-[400px] sm:h-[400px] bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.15)_0%,rgba(6,182,212,0.06)_50%,transparent_70%)] rounded-full -z-10 pointer-events-none" />

      {/* HIGH-FIDELITY IPHONE 17 PRO MAX CHASSIS (Adapts border & metal look to theme with rich high-contrast shadows) */}
      <div className={`relative w-[290px] sm:w-[310px] h-[610px] rounded-[52px] p-2.5 transition-all duration-300 flex flex-col shrink-0 z-10 ${
        isLight 
          ? "bg-zinc-200 shadow-[0_30px_70px_rgba(0,0,0,0.32),0_0_0_2.5px_rgba(15,15,15,0.95),inset_0_0_1px_2px_rgba(255,255,255,0.4)] border border-zinc-400"
          : "bg-zinc-900 shadow-[0_30px_70px_rgba(0,0,0,0.92),0_0_0_2.5px_rgba(240,240,240,0.28),inset_0_0_1px_2px_rgba(255,255,255,0.12)] border border-zinc-700"
      }`}>
        
        {/* Physical Buttons on Left (Action Button, Volume Up, Volume Down) */}
        <div className={`absolute left-[-2px] top-[90px] w-[3.5px] h-[24px] rounded-l-sm transition-all z-0 ${isLight ? "bg-zinc-400/90" : "bg-zinc-800"}`} />
        <div className={`absolute left-[-2px] top-[130px] w-[3.5px] h-[46px] rounded-l-sm transition-all z-0 ${isLight ? "bg-zinc-400/90" : "bg-zinc-800"}`} />
        <div className={`absolute left-[-2px] top-[186px] w-[3.5px] h-[46px] rounded-l-sm transition-all z-0 ${isLight ? "bg-zinc-400/90" : "bg-zinc-800"}`} />
        
        {/* Physical Button on Right (Power/Side Button) */}
        <div className={`absolute right-[-2px] top-[140px] w-[3.5px] h-[64px] rounded-r-sm transition-all z-0 ${isLight ? "bg-zinc-400/90" : "bg-zinc-800"}`} />

        {/* Bezel & Screen Container */}
        <div className="relative w-full h-full rounded-[43px] overflow-hidden flex flex-col border border-black/40 z-10 bg-transparent">
          
          {/* Dynamic Island (iPhone Slim style) */}
          <div className="absolute top-2 left-1/2 -translate-x-1/2 w-20 h-[18px] bg-black rounded-full z-40 flex items-center justify-between px-3 shadow-[inset_0_0_1px_rgba(255,255,255,0.2)]">
            <div className="w-1 h-1 rounded-full bg-zinc-900 flex items-center justify-center">
              <div className="w-0.5 h-0.5 rounded-full bg-indigo-950/85" />
            </div>
            <div className="w-1.5 h-[3px] rounded-full bg-zinc-950" />
          </div>

          {/* iOS Status Bar (Adapts background and text dynamically to blend flawlessly) */}
          <div className={`h-8 w-full flex items-center justify-between px-5 text-[9px] font-semibold select-none z-30 shrink-0 border-b pt-2 transition-colors duration-300 ${
            isLight 
              ? "bg-[#f0f2f5] border-zinc-200/80 text-zinc-800" 
              : "bg-[#1f2c34] border-zinc-800/40 text-zinc-100"
          }`}>
            <span>09:41</span>
            <div className="flex items-center gap-1.5">
              <span className="text-[8px] opacity-70">5G</span>
              {/* Signal strength bars */}
              <div className="flex gap-[1px] items-end h-2">
                <div className="w-[1.5px] h-[3px] bg-current rounded-3xs opacity-80" />
                <div className="w-[1.5px] h-[4.5px] bg-current rounded-3xs opacity-80" />
                <div className="w-[1.5px] h-[6px] bg-current rounded-3xs opacity-80" />
                <div className="w-[1.5px] h-[8px] bg-current" />
              </div>
              {/* Battery percentage */}
              <div className="w-5 h-2.5 border border-current/30 rounded-md p-[1px] flex items-center relative">
                <div className="w-full h-full bg-emerald-500 rounded-xs" />
                <div className="absolute -right-[2px] top-[2px] w-[1px] h-1 bg-current/30 rounded-r-xs" />
              </div>
            </div>
          </div>

          {/* WHATSAPP CHAT CONTAINER */}
          <div className="flex-1 flex flex-col overflow-hidden bg-transparent">
            
            {/* WhatsApp Contact Header */}
            <div className={`${waHeaderBg} ${waHeaderCol} px-3.5 py-2.5 flex items-center justify-between border-b border-black/5 shadow-sm shrink-0 select-none transition-colors duration-300`}>
              <div className="flex items-center gap-2">
                <div className="hover:opacity-80 transition">
                  <ChevronLeft className="w-4 h-4 cursor-pointer text-emerald-500" />
                </div>
                {/* Avatar with transparent checkmark vector logo */}
                <div className={`w-8 h-8 rounded-full overflow-hidden flex items-center justify-center shadow-inner border transition-colors duration-300 ${
                  isLight ? "bg-zinc-100 border-zinc-300/60" : "bg-[#111b21] border-[#2a3942]"
                }`}>
                  <BrandLogo className="w-5.5 h-5.5" theme={theme} />
                </div>
                <div>
                  <div className="font-bold text-xs leading-none flex items-center gap-1">
                    VendorIQ
                  </div>
                  <span className={`${waHeaderSubCol} text-[9px] font-medium leading-none flex items-center gap-1 mt-0.5 transition-colors duration-300`}>
                    {isTyping ? (
                      <span className={`font-bold animate-pulse ${isLight ? "text-emerald-600" : "text-[#25D366]"}`}>typing...</span>
                    ) : (
                      <>
                        <span className="w-1.5 h-1.5 bg-[#25D366] rounded-full animate-ping shrink-0" />
                        <span>online</span>
                      </>
                    )}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-3.5 opacity-90 text-emerald-500">
                {isInteractive && (
                  <button 
                    onClick={handleReset}
                    title="Reset Simulation"
                    className={`p-1 transition rounded-full ${isLight ? "hover:bg-zinc-200/50" : "hover:bg-white/10"}`}
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                )}
                <Video className="w-3.5 h-3.5 cursor-pointer hover:opacity-80" />
                <Phone className="w-3.5 h-3.5 cursor-pointer hover:opacity-80" />
              </div>
            </div>

            {/* Chat Messages Logs Container with Static high-fidelity WhatsApp Wallpaper */}
            <div className="flex-1 relative overflow-hidden flex flex-col bg-transparent">
              {/* Static High-Fidelity Genuine WhatsApp Wallpaper */}
              <div 
                className="absolute inset-0 pointer-events-none select-none z-0 transition-all duration-300"
                style={{
                  backgroundColor: isLight ? "#efeae2" : "#0b141a",
                  backgroundImage: `url("https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png")`,
                  backgroundSize: "280px",
                  backgroundRepeat: "repeat",
                  opacity: isLight ? 0.38 : 0.06,
                  filter: isLight ? "none" : "invert(1) brightness(0.8)",
                }}
              />

              <div 
                ref={chatContainerRef}
                onScroll={handleScroll}
                className="flex-1 overflow-y-auto p-3.5 space-y-2.5 flex flex-col no-scrollbar z-10 relative bg-transparent"
              >
              {messages.length === 0 && (
                <div className="my-auto text-center text-zinc-500 text-[11px] max-w-[200px] mx-auto space-y-2">
                  <MessageSquare className="w-6 h-6 mx-auto opacity-35 text-[#00a884]" />
                  <p>Initializing secure assistant ledger...</p>
                </div>
              )}
              <AnimatePresence initial={true}>
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, scale: 0.92, y: 8 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.92 }}
                    transition={{ type: "spring", stiffness: 400, damping: 26 }}
                    className={`flex flex-col ${
                      msg.sender === "user" 
                        ? "max-w-[85%] self-end items-end" 
                        : msg.sender === "timestamp"
                        ? "self-center text-center my-2"
                        : "max-w-[85%] self-start items-start"
                    }`}
                  >
                    {msg.sender === "timestamp" ? (
                      <span className={`text-[10px] font-medium px-3 py-[4px] rounded-[10px] select-none shadow-[0_1px_0.5px_rgba(0,0,0,0.06)] ${
                        isLight 
                          ? "bg-[#daebd5] text-[#54656f]" 
                          : "bg-[#1f2c34]/85 text-[#8696a0]"
                      }`}>
                        {msg.text}
                      </span>
                    ) : (
                      <div
                        className={`p-2.5 rounded-2xl text-[11.5px] leading-relaxed transition-all whitespace-pre-line relative border ${
                          msg.sender === "user" ? waUserBubble : waBotBubble
                        }`}
                      >
                        {msg.text}
                        <div className="flex items-center justify-end gap-1 mt-1 text-[8px] opacity-60 select-none">
                          <span>{msg.timestamp || "12:00"}</span>
                          {msg.sender === "user" && <CheckCheck className="w-3 h-3 text-[#53bdeb]" />}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}

                {/* Typing Dot bubble with framer-motion entrance */}
                {isTyping && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.92, y: 8 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ type: "spring", stiffness: 400, damping: 26 }}
                    className="self-start items-start max-w-[85%]"
                  >
                    <div className={`px-3 py-2.5 rounded-2xl border flex items-center gap-1 shadow-sm ${waBotBubble}`}>
                      <span className="w-1.5 h-1.5 bg-[#25D366] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-1.5 h-1.5 bg-[#25D366] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-1.5 h-1.5 bg-[#25D366] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              </div>
            </div>



            {/* Input Form with Attachment Icon & Send button */}
            <form onSubmit={handleSendMessage} className={`p-2 border-t ${waFormBg} flex items-center gap-1.5 shrink-0 transition-colors duration-300`}>
              {/* Attachment Plus Icon on the left */}
              <button 
                type="button"
                className={`p-1.5 rounded-full transition shrink-0 ${
                  isLight 
                    ? "text-[#008069] hover:bg-zinc-200" 
                    : "text-[#00a884] hover:bg-zinc-800"
                }`}
                title="Add Attachment"
              >
                <Plus className="w-5 h-5" />
              </button>

              <div className={`flex-1 rounded-full px-3.5 py-1.5 flex items-center border transition-all duration-300 ${waInputBg}`}>
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onFocus={() => setIsInteractive(true)}
                  placeholder="Type (e.g. Sold 3 bags rice)..."
                  disabled={isLoading}
                  className={`w-full bg-transparent border-none text-[11px] focus:outline-none ${waInputText} ${waInputPlaceholder}`}
                />
              </div>

              {/* Send icon adapts elegantly */}
              <button
                type="submit"
                disabled={!inputText.trim() || isLoading}
                className={`p-2 rounded-full flex items-center justify-center transition-all shrink-0 ${
                  inputText.trim() && !isLoading
                    ? "bg-[#00a884] text-white cursor-pointer hover:bg-[#00c298]"
                    : isLight
                    ? "bg-[#008069]/10 text-[#008069] cursor-not-allowed border border-transparent"
                    : "bg-[#2a3942] text-zinc-500 cursor-not-allowed border border-[#2a3942]"
                }`}
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>

            {/* Elegant iOS Home Indicator Area (replaces bottom tab bar for real WhatsApp chat focus) */}
            <div className={`h-6 w-full flex items-center justify-center pb-2 select-none shrink-0 transition-colors duration-300 ${
              isLight ? "bg-[#f0f2f5]" : "bg-[#1f2c34]"
            }`}>
              <div className={`w-24 h-[4px] rounded-full transition-colors duration-300 ${
                isLight ? "bg-black/20" : "bg-white/20"
              }`} />
            </div>

          </div>
        </div>
      </div>

    </div>
  );
}
