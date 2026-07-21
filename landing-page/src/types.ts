export interface Sale {
  description: string;
  quantity: number;
  pricePerUnit: number;
  total: number;
  date: string;
}

export interface Debt {
  debtor: string;
  amount: number;
  date: string;
  status: "unpaid" | "paid";
}

export interface Expense {
  description: string;
  amount: number;
  date: string;
}

export interface LedgerState {
  sales: Sale[];
  debts: Debt[];
  expenses: Expense[];
}

export interface ChatMessage {
  id: string;
  sender: "user" | "bot" | "timestamp";
  text: string;
  timestamp?: string;
}
