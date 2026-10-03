/**
 * VaultFlow - Personal Money & Loan Tracking Application
 * Robust Local-First State Management, Multi-Currency Engine,
 * Image Compressor, jsPDF Generator, Chart.js Visualizer
 */

// ==========================================
// 1. CONFIGURATION & MULTI-CURRENCY ENGINE
// ==========================================
const CURRENCY_CONFIG = {
  USD: { symbol: '$', rateToUSD: 1.0, name: 'US Dollar', pdfPrefix: '$' },
  EUR: { symbol: '€', rateToUSD: 1.09, name: 'Euro', pdfPrefix: 'EUR ' },
  GBP: { symbol: '£', rateToUSD: 1.27, name: 'British Pound', pdfPrefix: 'GBP ' },
  INR: { symbol: '₹', rateToUSD: 0.012, name: 'Indian Rupee', pdfPrefix: 'INR ' },
  BDT: { symbol: '৳', rateToUSD: 0.0091, name: 'Bangladeshi Taka', pdfPrefix: 'BDT ' },
  CAD: { symbol: 'CAD $', rateToUSD: 0.74, name: 'Canadian Dollar', pdfPrefix: 'CAD $' },
  AUD: { symbol: 'AUD $', rateToUSD: 0.66, name: 'Australian Dollar', pdfPrefix: 'AUD $' },
  JPY: { symbol: '¥', rateToUSD: 0.0066, name: 'Japanese Yen', pdfPrefix: 'JPY ' }
};

const DEFAULT_CATEGORIES = [
  { id: 'housing', name: 'Housing & Rent', color: '#6366f1', type: 'expense' },
  { id: 'food', name: 'Food & Dining', color: '#f59e0b', type: 'expense' },
  { id: 'transport', name: 'Transport & Fuel', color: '#3b82f6', type: 'expense' },
  { id: 'entertainment', name: 'Entertainment & Subs', color: '#ec4899', type: 'expense' },
  { id: 'utilities', name: 'Utilities & Bills', color: '#8b5cf6', type: 'expense' },
  { id: 'healthcare', name: 'Healthcare & Fitness', color: '#10b981', type: 'expense' },
  { id: 'shopping', name: 'Shopping & Gadgets', color: '#06b6d4', type: 'expense' },
  { id: 'salary', name: 'Salary & Wages', color: '#10b981', type: 'income' },
  { id: 'freelance', name: 'Freelance & Consulting', color: '#84cc16', type: 'income' },
  { id: 'investment', name: 'Investments & Dividends', color: '#14b8a6', type: 'income' }
];

const SECTION_METADATA = {
  dashboard: { title: 'Financial Dashboard', subtitle: 'Vault Overview & Real-Time Analytics', icon: 'layout-dashboard' },
  transactions: { title: 'Transaction Ledger', subtitle: 'Search, Filter & Review Receipts', icon: 'arrow-left-right' },
  loans: { title: 'Loans & Debts', subtitle: 'Debts Owed & Money Lent Records', icon: 'hand-coins' },
  recurring: { title: 'Subscriptions', subtitle: 'Recurring Bills & Income Schedules', icon: 'calendar-sync' },
  analytics: { title: 'Analytics & Reports', subtitle: 'Visual Breakdowns & PDF Statements', icon: 'pie-chart' },
  settings: { title: 'Settings & Backup', subtitle: 'Preferences, Currencies & Vault Data', icon: 'settings' }
};

// In-Memory App State
let state = {
  settings: {
    baseCurrency: 'USD',
    userName: 'Shahtab',
    monthlyBudget: 6000,
    categoryLimits: {
      food: 1200,
      housing: 2500,
      transport: 600,
      entertainment: 500,
      shopping: 800
    },
    widgets: {
      quickActions: true,
      metrics: true,
      budget: true,
      bills: true,
      charts: true,
      recent: true
    },
    theme: 'dark'
  },
  categories: [...DEFAULT_CATEGORIES],
  transactions: [],
  loans: [],
  recurring: []
};

let currentView = 'dashboard';
let currentLoanTab = 'owe';
let currentReceiptBase64 = null;
let weeklyChartInstance = null;
let trendChartInstance = null;
let doughnutChartInstance = null;

// ==========================================
// 2. STORAGE ENGINE (IndexedDB / LocalStorage)
// ==========================================
const DB_NAME = 'VaultFlow_DB';
const DB_VERSION = 1;
const DB_STORE = 'vault_data';

function initStorage() {
  return new Promise((resolve) => {
    if (!window.indexedDB) {
      loadFromLocalStorage();
      resolve();
      return;
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(DB_STORE)) {
        db.createObjectStore(DB_STORE);
      }
    };

    request.onsuccess = (e) => {
      const db = e.target.result;
      const tx = db.transaction(DB_STORE, 'readonly');
      const store = tx.objectStore(DB_STORE);
      const getReq = store.get('root_state');
      getReq.onsuccess = () => {
        if (getReq.result) {
          state = Object.assign(state, getReq.result);
        } else {
          loadFromLocalStorage();
          if (state.transactions.length === 0) {
            seedSampleData();
          }
          saveState();
        }
        resolve();
      };
      getReq.onerror = () => {
        loadFromLocalStorage();
        resolve();
      };
    };

    request.onerror = () => {
      loadFromLocalStorage();
      resolve();
    };
  });
}

function saveState() {
  try {
    localStorage.setItem('vaultflow_state', JSON.stringify(state));
  } catch (e) {
    console.warn('LocalStorage limit exceeded, relying on IndexedDB', e);
  }

  if (window.indexedDB) {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onsuccess = (e) => {
      const db = e.target.result;
      const tx = db.transaction(DB_STORE, 'readwrite');
      const store = tx.objectStore(DB_STORE);
      store.put(state, 'root_state');
    };
  }
}

function loadFromLocalStorage() {
  try {
    const data = localStorage.getItem('vaultflow_state');
    if (data) {
      state = Object.assign(state, JSON.parse(data));
    } else {
      seedSampleData();
    }
  } catch (err) {
    console.error('Error loading LocalStorage', err);
    seedSampleData();
  }
}

// Sample Data Generator
function seedSampleData() {
  const today = new Date();
  const formatD = (offsetDays) => {
    const d = new Date(today);
    d.setDate(d.getDate() - offsetDays);
    return d.toISOString().split('T')[0];
  };

  state.transactions = [
    {
      id: 'tx_' + Date.now() + '_1',
      type: 'income',
      category: 'salary',
      amount: 4500,
      currency: 'USD',
      amountInBase: 4500,
      exchangeRate: 1.0,
      date: formatD(2),
      note: 'Senior Engineering Salary Deposit',
      paymentMethod: 'Bank Transfer',
      receipt: null
    },
    {
      id: 'tx_' + Date.now() + '_2',
      type: 'expense',
      category: 'housing',
      amount: 1450,
      currency: 'USD',
      amountInBase: 1450,
      exchangeRate: 1.0,
      date: formatD(1),
      note: 'Apartment Monthly Rent',
      paymentMethod: 'Bank Transfer',
      receipt: null
    },
    {
      id: 'tx_' + Date.now() + '_3',
      type: 'expense',
      category: 'food',
      amount: 142.50,
      currency: 'USD',
      amountInBase: 142.50,
      exchangeRate: 1.0,
      date: formatD(0),
      note: 'Weekly Organic Grocery Basket',
      paymentMethod: 'Credit Card',
      receipt: null
    },
    {
      id: 'tx_' + Date.now() + '_4',
      type: 'expense',
      category: 'transport',
      amount: 65.00,
      currency: 'USD',
      amountInBase: 65.00,
      exchangeRate: 1.0,
      date: formatD(3),
      note: 'EV Supercharging & Highway Toll',
      paymentMethod: 'Credit Card',
      receipt: null
    },
    {
      id: 'tx_' + Date.now() + '_5',
      type: 'income',
      category: 'freelance',
      amount: 850.00,
      currency: 'USD',
      amountInBase: 850.00,
      exchangeRate: 1.0,
      date: formatD(4),
      note: 'Web Design Milestone Completion',
      paymentMethod: 'Mobile Wallet / UPI',
      receipt: null
    },
    {
      id: 'tx_' + Date.now() + '_6',
      type: 'expense',
      category: 'entertainment',
      amount: 19.99,
      currency: 'USD',
      amountInBase: 19.99,
      exchangeRate: 1.0,
      date: formatD(5),
      note: 'Streaming Service Subscription',
      paymentMethod: 'Credit Card',
      receipt: null
    }
  ];

  state.loans = [
    {
      id: 'loan_' + Date.now() + '_1',
      type: 'owe',
      contact: 'Apex Auto Financing',
      amount: 4500,
      currency: 'USD',
      interestRate: 3.5,
      dueDate: formatD(-60),
      note: 'Vehicle repair package financing',
      repayments: [
        {
          id: 'rep_1',
          amount: 1500,
          date: formatD(10),
          method: 'Bank Transfer',
          note: 'First monthly installment'
        }
      ]
    },
    {
      id: 'loan_' + Date.now() + '_2',
      type: 'lent',
      contact: 'Marcus Vance',
      amount: 950,
      currency: 'USD',
      interestRate: 0,
      dueDate: formatD(-14),
      note: 'Camera lens purchase loan',
      repayments: [
        {
          id: 'rep_2',
          amount: 300,
          date: formatD(4),
          method: 'Mobile Wallet / UPI',
          note: 'Partial cash settlement'
        }
      ]
    }
  ];

  state.recurring = [
    {
      id: 'rec_' + Date.now() + '_1',
      name: 'Apartment Rent',
      type: 'expense',
      category: 'housing',
      amount: 1450,
      currency: 'USD',
      frequency: 'monthly',
      nextDueDate: formatD(-25),
      paymentMethod: 'Bank Transfer',
      active: true,
      lastProcessed: formatD(1)
    },
    {
      id: 'rec_' + Date.now() + '_2',
      name: 'Netflix 4K Ultra',
      type: 'expense',
      category: 'entertainment',
      amount: 19.99,
      currency: 'USD',
      frequency: 'monthly',
      nextDueDate: formatD(-2),
      paymentMethod: 'Credit Card',
      active: true,
      lastProcessed: formatD(5)
    },
    {
      id: 'rec_' + Date.now() + '_3',
      name: 'Equinox Gym Pass',
      type: 'expense',
      category: 'healthcare',
      amount: 110,
      currency: 'USD',
      frequency: 'monthly',
      nextDueDate: formatD(-5),
      paymentMethod: 'Credit Card',
      active: true,
      lastProcessed: null
    },
    {
      id: 'rec_' + Date.now() + '_4',
      name: 'Primary Tech Salary',
      type: 'income',
      category: 'salary',
      amount: 4500,
      currency: 'USD',
      frequency: 'monthly',
      nextDueDate: formatD(-28),
      paymentMethod: 'Bank Transfer',
      active: true,
      lastProcessed: formatD(2)
    }
  ];
}

// ==========================================
// 3. CURRENCY CONVERSION & FORMATTING
// ==========================================
function convertAmount(amount, fromCurrency, toCurrency) {
  if (fromCurrency === toCurrency) return amount;
  const rateFrom = CURRENCY_CONFIG[fromCurrency]?.rateToUSD || 1.0;
  const rateTo = CURRENCY_CONFIG[toCurrency]?.rateToUSD || 1.0;
  const inUSD = amount * rateFrom;
  return inUSD / rateTo;
}

function formatMoney(amount, currencyCode = state.settings.baseCurrency) {
  const conf = CURRENCY_CONFIG[currencyCode] || { symbol: currencyCode + ' ' };
  const absAmount = Math.abs(amount);
  const formatted = absAmount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  const prefix = amount < 0 ? '-' : '';
  return `${prefix}${conf.symbol}${formatted}`;
}

// Safe formatting for jsPDF to prevent corrupted non-latin glyphs (like ৳ or ₹)
function formatMoneyForPdf(amount, currencyCode = state.settings.baseCurrency) {
  const conf = CURRENCY_CONFIG[currencyCode];
  const safePrefix = conf?.pdfPrefix || `${currencyCode} `;
  const absAmount = Math.abs(amount);
  const formatted = absAmount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  const sign = amount < 0 ? '-' : '';
  return `${sign}${safePrefix}${formatted}`;
}

function changeBaseCurrency(newCurr) {
  if (!CURRENCY_CONFIG[newCurr]) return;
  const oldCurr = state.settings.baseCurrency;
  state.settings.baseCurrency = newCurr;

  state.transactions.forEach(tx => {
    tx.amountInBase = convertAmount(tx.amount, tx.currency, newCurr);
  });

  state.settings.monthlyBudget = convertAmount(state.settings.monthlyBudget, oldCurr, newCurr);
  for (let cat in state.settings.categoryLimits) {
    state.settings.categoryLimits[cat] = convertAmount(state.settings.categoryLimits[cat], oldCurr, newCurr);
  }

  saveState();
  syncUIPreferences();
  refreshCurrentView();
  showToast(`Primary currency set to ${newCurr}`, 'success');
}

// ==========================================
// 4. IMAGE COMPRESSION (Client-Side Canvas)
// ==========================================
function compressReceiptImage(file, maxWidth = 800, quality = 0.75) {
  return new Promise((resolve, reject) => {
    if (!file || !file.type.match(/image.*/)) {
      return reject(new Error('Invalid image file'));
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        let width = img.width;
        let height = img.height;

        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        const dataUrl = canvas.toDataURL('image/jpeg', quality);
        const approxKb = Math.round((dataUrl.length * 3 / 4) / 1024);
        resolve({ dataUrl, width, height, sizeKb: approxKb });
      };
      img.onerror = reject;
      img.src = e.target.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ==========================================
// 5. RECURRING BILLS ENGINE
// ==========================================
function calculateNextDueDate(currentDateStr, frequency) {
  const d = new Date(currentDateStr);
  switch (frequency) {
    case 'daily':
      d.setDate(d.getDate() + 1);
      break;
    case 'weekly':
      d.setDate(d.getDate() + 7);
      break;
    case 'monthly':
      d.setMonth(d.getMonth() + 1);
      break;
    case 'quarterly':
      d.setMonth(d.getMonth() + 3);
      break;
    case 'yearly':
      d.setFullYear(d.getFullYear() + 1);
      break;
    default:
      d.setMonth(d.getMonth() + 1);
  }
  return d.toISOString().split('T')[0];
}

function processDueRecurringRules(silent = false) {
  const today = new Date().toISOString().split('T')[0];
  let processedCount = 0;

  state.recurring.forEach(rule => {
    if (!rule.active) return;

    if (rule.nextDueDate <= today) {
      const baseAmt = convertAmount(rule.amount, rule.currency, state.settings.baseCurrency);
      const newTx = {
        id: 'tx_rec_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
        type: rule.type,
        category: rule.category,
        amount: rule.amount,
        currency: rule.currency,
        amountInBase: baseAmt,
        exchangeRate: 1.0,
        date: rule.nextDueDate,
        note: `[Recurring] ${rule.name}`,
        paymentMethod: rule.paymentMethod,
        receipt: null
      };

      state.transactions.unshift(newTx);
      rule.lastProcessed = today;
      rule.nextDueDate = calculateNextDueDate(rule.nextDueDate, rule.frequency);
      processedCount++;
    }
  });

  if (processedCount > 0) {
    saveState();
    refreshCurrentView();
    showToast(`${processedCount} recurring transaction(s) auto-processed!`, 'success');
  } else if (!silent) {
    showToast('All recurring schedules are up to date.', 'info');
  }
}

// ==========================================
// 6. DASHBOARD & METRICS CALCULATIONS
// ==========================================
function getVaultMetrics() {
  const currentYearMonth = new Date().toISOString().slice(0, 7);

  let totalIncome = 0;
  let totalExpense = 0;
  let monthSpend = 0;

  state.transactions.forEach(tx => {
    const amt = tx.amountInBase || convertAmount(tx.amount, tx.currency, state.settings.baseCurrency);
    if (tx.type === 'income') {
      totalIncome += amt;
    } else {
      totalExpense += amt;
      if (tx.date.startsWith(currentYearMonth)) {
        monthSpend += amt;
      }
    }
  });

  const totalBalance = totalIncome - totalExpense;

  let totalDebtOwed = 0;
  let activeDebtsCount = 0;
  let totalMoneyLent = 0;
  let activeCreditsCount = 0;

  state.loans.forEach(loan => {
    const principal = convertAmount(loan.amount, loan.currency, state.settings.baseCurrency);
    const repaid = (loan.repayments || []).reduce((sum, r) => sum + convertAmount(r.amount, loan.currency, state.settings.baseCurrency), 0);
    const remaining = Math.max(0, principal - repaid);

    if (loan.type === 'owe') {
      totalDebtOwed += remaining;
      if (remaining > 0.01) activeDebtsCount++;
    } else {
      totalMoneyLent += remaining;
      if (remaining > 0.01) activeCreditsCount++;
    }
  });

  return {
    totalBalance,
    monthSpend,
    totalDebtOwed,
    activeDebtsCount,
    totalMoneyLent,
    activeCreditsCount,
    totalIncome,
    totalExpense
  };
}

function updateDashboardUI() {
  const metrics = getVaultMetrics();

  document.getElementById('metric-total-balance').textContent = formatMoney(metrics.totalBalance);
  document.getElementById('metric-month-spend').textContent = formatMoney(metrics.monthSpend);
  document.getElementById('metric-debt-owed').textContent = formatMoney(metrics.totalDebtOwed);
  document.getElementById('metric-active-debts').textContent = `${metrics.activeDebtsCount} active loan obligation(s)`;
  document.getElementById('metric-money-lent').textContent = formatMoney(metrics.totalMoneyLent);
  document.getElementById('metric-active-credits').textContent = `${metrics.activeCreditsCount} pending receivable(s)`;

  const budgetLimit = state.settings.monthlyBudget || 3000;
  const spentPct = Math.min(100, Math.round((metrics.monthSpend / budgetLimit) * 100));
  const remaining = budgetLimit - metrics.monthSpend;

  document.getElementById('budget-health-spent').textContent = `${formatMoney(metrics.monthSpend)} spent`;
  document.getElementById('budget-health-limit').textContent = `Target: ${formatMoney(budgetLimit)}`;
  document.getElementById('budget-health-bar').style.width = `${spentPct}%`;
  document.getElementById('metric-spend-pct').textContent = `${spentPct}% of monthly limit`;

  const bar = document.getElementById('budget-health-bar');
  const tag = document.getElementById('budget-health-tag');
  const banner = document.getElementById('budget-alert-banner');
  const bannerText = document.getElementById('budget-alert-text');

  if (spentPct > 90) {
    bar.className = 'h-full rounded-full transition-all duration-500 bg-rose-500';
    tag.className = 'px-2 py-0.5 rounded-full font-semibold bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-400 text-[11px]';
    tag.textContent = spentPct >= 100 ? 'Limit Exceeded!' : 'Critical Budget (>90%)';
    banner.classList.remove('hidden');
    bannerText.textContent = `Warning: You have used ${spentPct}% of your ${formatMoney(budgetLimit)} monthly budget!`;
  } else if (spentPct >= 75) {
    bar.className = 'h-full rounded-full transition-all duration-500 bg-amber-500';
    tag.className = 'px-2 py-0.5 rounded-full font-semibold bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400 text-[11px]';
    tag.textContent = 'Caution Zone (75-90%)';
    banner.classList.add('hidden');
  } else {
    bar.className = 'h-full rounded-full transition-all duration-500 bg-emerald-500';
    tag.className = 'px-2 py-0.5 rounded-full font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400 text-[11px]';
    tag.textContent = 'Safe Spending (<75%)';
    banner.classList.add('hidden');
  }

  document.getElementById('budget-health-remaining').textContent = remaining >= 0 ? `${formatMoney(remaining)} remaining` : `${formatMoney(Math.abs(remaining))} over target`;

  renderUpcomingBillsWidget();
  renderRecentActivityWidget();
  renderWeeklyChart();
}

function renderUpcomingBillsWidget() {
  const container = document.getElementById('upcoming-bills-list');
  const countBadge = document.getElementById('upcoming-bills-count');

  const today = new Date();
  const nextWeek = new Date();
  nextWeek.setDate(today.getDate() + 7);
  const nextWeekStr = nextWeek.toISOString().split('T')[0];
  const todayStr = today.toISOString().split('T')[0];

  const dueItems = state.recurring.filter(r => r.active && r.nextDueDate <= nextWeekStr);
  countBadge.textContent = dueItems.length;

  if (dueItems.length === 0) {
    container.innerHTML = '<div class="text-xs text-slate-400 py-3 text-center">No recurring bills due in next 7 days.</div>';
    return;
  }

  container.innerHTML = dueItems.map(item => {
    const isOverdue = item.nextDueDate < todayStr;
    const cat = state.categories.find(c => c.id === item.category);
    return `
      <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-2.5">
          <div class="w-2.5 h-2.5 rounded-full" style="background-color: ${cat?.color || '#6366f1'}"></div>
          <div>
            <p class="text-xs font-semibold text-slate-800 dark:text-slate-200">${escapeHtml(item.name)}</p>
            <p class="text-[10px] ${isOverdue ? 'text-rose-500 font-bold' : 'text-slate-400'}">${isOverdue ? 'Overdue: ' : 'Due: '} ${item.nextDueDate}</p>
          </div>
        </div>
        <span class="text-xs font-mono font-bold text-slate-700 dark:text-slate-300">${formatMoney(item.amount, item.currency)}</span>
      </div>
    `;
  }).join('');
}

function renderRecentActivityWidget() {
  const container = document.getElementById('dashboard-recent-list');
  const recent = state.transactions.slice(0, 5);

  if (recent.length === 0) {
    container.innerHTML = '<div class="text-xs text-slate-400 py-4 text-center">No recent transactions recorded.</div>';
    return;
  }

  container.innerHTML = recent.map(tx => {
    const isInc = tx.type === 'income';
    const cat = state.categories.find(c => c.id === tx.category);
    return `
      <div class="flex items-center justify-between py-1.5 border-b border-slate-100 dark:border-slate-800/80 last:border-0">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${isInc ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}">
            <i data-lucide="${isInc ? 'arrow-down-left' : 'arrow-up-right'}" class="w-4 h-4"></i>
          </div>
          <div class="min-w-0">
            <p class="text-xs font-semibold truncate text-slate-800 dark:text-slate-200">${escapeHtml(tx.note || cat?.name || 'Transaction')}</p>
            <p class="text-[10px] text-slate-400 flex items-center gap-1.5">
              <span>${tx.date}</span>
              <span>•</span>
              <span style="color: ${cat?.color || '#6366f1'}">${escapeHtml(cat?.name || tx.category)}</span>
              ${tx.receipt ? `<span class="cursor-pointer text-indigo-500 underline" onclick="openReceiptLightbox('${tx.id}')">Receipt</span>` : ''}
            </p>
          </div>
        </div>
        <span class="text-xs font-mono font-bold shrink-0 ${isInc ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-900 dark:text-slate-100'}">
          ${isInc ? '+' : '-'}${formatMoney(tx.amountInBase || tx.amount, state.settings.baseCurrency)}
        </span>
      </div>
    `;
  }).join('');
  lucide.createIcons();
}

// ==========================================
// 7. CHART.JS VISUALIZATIONS
// ==========================================
function isDarkMode() {
  return document.documentElement.classList.contains('dark');
}

function renderWeeklyChart() {
  const ctx = document.getElementById('weeklyBarChart')?.getContext('2d');
  if (!ctx) return;

  const dark = isDarkMode();
  const days = [];
  const amounts = [];
  const today = new Date();

  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split('T')[0];
    const dayLabel = d.toLocaleDateString('en-US', { weekday: 'short' });
    days.push(dayLabel);

    const sum = state.transactions
      .filter(t => t.type === 'expense' && t.date === dateStr)
      .reduce((acc, t) => acc + (t.amountInBase || convertAmount(t.amount, t.currency, state.settings.baseCurrency)), 0);

    amounts.push(sum);
  }

  if (weeklyChartInstance) weeklyChartInstance.destroy();

  weeklyChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: days,
      datasets: [{
        label: `Expenses (${state.settings.baseCurrency})`,
        data: amounts,
        backgroundColor: dark ? 'rgba(99, 102, 241, 0.85)' : 'rgba(79, 70, 229, 0.85)',
        borderRadius: 8,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Spent: ${formatMoney(ctx.raw, state.settings.baseCurrency)}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: dark ? '#94a3b8' : '#64748b', font: { size: 11 } }
        },
        y: {
          grid: { color: dark ? '#1e293b' : '#f1f5f9' },
          ticks: {
            color: dark ? '#94a3b8' : '#64748b',
            font: { size: 11 },
            callback: (v) => formatMoney(v, state.settings.baseCurrency)
          }
        }
      }
    }
  });
}

function renderAnalyticsCharts() {
  const dark = isDarkMode();

  const trendCtx = document.getElementById('trendLineChart')?.getContext('2d');
  if (trendCtx) {
    const months = [];
    const incomeData = [];
    const expenseData = [];
    const now = new Date();

    for (let i = 5; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const ym = d.toISOString().slice(0, 7);
      months.push(d.toLocaleDateString('en-US', { month: 'short' }));

      let inc = 0;
      let exp = 0;
      state.transactions.forEach(t => {
        if (t.date.startsWith(ym)) {
          const val = t.amountInBase || convertAmount(t.amount, t.currency, state.settings.baseCurrency);
          if (t.type === 'income') inc += val;
          else exp += val;
        }
      });
      incomeData.push(inc);
      expenseData.push(exp);
    }

    if (trendChartInstance) trendChartInstance.destroy();
    trendChartInstance = new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: months,
        datasets: [
          {
            label: 'Income',
            data: incomeData,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            tension: 0.35,
            fill: true
          },
          {
            label: 'Expenses',
            data: expenseData,
            borderColor: '#f43f5e',
            backgroundColor: 'rgba(244, 63, 94, 0.12)',
            tension: 0.35,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: dark ? '#cbd5e1' : '#334155' } },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${formatMoney(ctx.raw, state.settings.baseCurrency)}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: dark ? '#1e293b' : '#f1f5f9' },
            ticks: { color: dark ? '#94a3b8' : '#64748b' }
          },
          y: {
            grid: { color: dark ? '#1e293b' : '#f1f5f9' },
            ticks: {
              color: dark ? '#94a3b8' : '#64748b',
              callback: (v) => formatMoney(v, state.settings.baseCurrency)
            }
          }
        }
      }
    });
  }

  const doughnutCtx = document.getElementById('categoryDoughnutChart')?.getContext('2d');
  if (doughnutCtx) {
    const catMap = {};
    state.transactions.filter(t => t.type === 'expense').forEach(t => {
      const val = t.amountInBase || convertAmount(t.amount, t.currency, state.settings.baseCurrency);
      catMap[t.category] = (catMap[t.category] || 0) + val;
    });

    const labels = [];
    const dataVals = [];
    const colors = [];

    Object.keys(catMap).forEach(catId => {
      const catObj = state.categories.find(c => c.id === catId);
      labels.push(catObj ? catObj.name : catId);
      dataVals.push(catMap[catId]);
      colors.push(catObj ? catObj.color : '#6366f1');
    });

    if (doughnutChartInstance) doughnutChartInstance.destroy();
    doughnutChartInstance = new Chart(doughnutCtx, {
      type: 'doughnut',
      data: {
        labels: labels.length ? labels : ['No Expenses'],
        datasets: [{
          data: dataVals.length ? dataVals : [1],
          backgroundColor: colors.length ? colors : ['#94a3b8'],
          borderWidth: 2,
          borderColor: dark ? '#0f172a' : '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.label}: ${formatMoney(ctx.raw, state.settings.baseCurrency)}`
            }
          }
        }
      }
    });

    const legendList = document.getElementById('category-legend-list');
    if (legendList) {
      legendList.innerHTML = labels.map((l, idx) => `
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${colors[idx]}"></span>
            <span class="text-slate-700 dark:text-slate-300 font-medium">${escapeHtml(l)}</span>
          </div>
          <span class="font-mono text-slate-500">${formatMoney(dataVals[idx], state.settings.baseCurrency)}</span>
        </div>
      `).join('');
    }
  }

  renderCategoryLimitsAnalytics();
}

function renderCategoryLimitsAnalytics() {
  const container = document.getElementById('analytics-category-limits');
  if (!container) return;

  const currentYearMonth = new Date().toISOString().slice(0, 7);
  const expenseCategories = state.categories.filter(c => c.type === 'expense');

  if (expenseCategories.length === 0) {
    container.innerHTML = `
      <div class="col-span-full p-6 text-center text-slate-400 text-xs bg-slate-50 dark:bg-slate-850/40 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
        No expense categories available. Add categories in Settings to configure limits.
      </div>
    `;
    return;
  }

  container.innerHTML = expenseCategories.map(cat => {
    const limit = (state.settings.categoryLimits && state.settings.categoryLimits[cat.id]) || 0;
    const spent = state.transactions
      .filter(t => t.type === 'expense' && t.category === cat.id && t.date.startsWith(currentYearMonth))
      .reduce((sum, t) => sum + (t.amountInBase || convertAmount(t.amount, t.currency, state.settings.baseCurrency)), 0);

    const pct = limit > 0 ? Math.min(100, Math.round((spent / limit) * 100)) : 0;
    const isOver = limit > 0 && spent > limit;

    return `
      <div class="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850/50 space-y-2">
        <div class="flex justify-between items-center text-xs">
          <div class="flex items-center gap-2 min-w-0">
            <span class="w-3 h-3 rounded-md shrink-0" style="background-color: ${cat.color}"></span>
            <span class="font-semibold text-slate-800 dark:text-slate-200 truncate">${escapeHtml(cat.name)}</span>
          </div>
          <span class="font-mono text-right shrink-0 ${isOver ? 'text-rose-500 font-bold' : 'text-slate-500 dark:text-slate-400'}">
            ${formatMoney(spent)} / ${limit > 0 ? formatMoney(limit) : '<span class="text-slate-400">No cap</span>'}
          </span>
        </div>
        <div class="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
          <div class="h-full rounded-full transition-all duration-300 ${isOver ? 'bg-rose-500' : pct > 75 ? 'bg-amber-500' : 'bg-indigo-500'}" style="width: ${limit > 0 ? pct : 0}%"></div>
        </div>
        ${limit > 0 ? `
          <div class="flex justify-between items-center text-[10px] text-slate-400 font-mono">
            <span>${pct}% used</span>
            <span class="${isOver ? 'text-rose-500 font-semibold' : ''}">${isOver ? 'Over budget!' : formatMoney(Math.max(0, limit - spent)) + ' left'}</span>
          </div>
        ` : `
          <div class="text-[10px] text-slate-400 font-mono">
            <span>No spending cap set</span>
          </div>
        `}
      </div>
    `;
  }).join('');
}

// ==========================================
// 8. TRANSACTIONS VIEW & FILTERS
// ==========================================
function renderTransactionsTable() {
  const tbody = document.getElementById('transaction-table-body');
  const empty = document.getElementById('tx-empty-state');
  const stats = document.getElementById('filter-stats');
  if (!tbody) return;

  const search = document.getElementById('filter-search')?.value.toLowerCase() || '';
  const typeFilter = document.getElementById('filter-type')?.value || 'all';
  const categoryFilter = document.getElementById('filter-category')?.value || 'all';
  const receiptOnly = document.getElementById('filter-receipt-only')?.checked || false;
  const startDate = document.getElementById('filter-start-date')?.value || '';
  const endDate = document.getElementById('filter-end-date')?.value || '';

  const filtered = state.transactions.filter(t => {
    if (typeFilter !== 'all' && t.type !== typeFilter) return false;
    if (categoryFilter !== 'all' && t.category !== categoryFilter) return false;
    if (receiptOnly && !t.receipt) return false;
    if (startDate && t.date < startDate) return false;
    if (endDate && t.date > endDate) return false;
    if (search) {
      const matchNote = (t.note || '').toLowerCase().includes(search);
      const matchCat = (t.category || '').toLowerCase().includes(search);
      const matchMethod = (t.paymentMethod || '').toLowerCase().includes(search);
      if (!matchNote && !matchCat && !matchMethod) return false;
    }
    return true;
  });

  stats.textContent = `Showing ${filtered.length} of ${state.transactions.length} records`;
  document.getElementById('badge-tx-count').textContent = state.transactions.length;

  if (filtered.length === 0) {
    tbody.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');

  tbody.innerHTML = filtered.map(t => {
    const isInc = t.type === 'income';
    const cat = state.categories.find(c => c.id === t.category);
    return `
      <tr class="hover:bg-slate-50/75 dark:hover:bg-slate-850/50 transition-colors">
        <td class="py-3 px-4 font-mono text-slate-500 whitespace-nowrap">${t.date}</td>
        <td class="py-3 px-4">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${cat?.color || '#6366f1'}"></span>
            <div>
              <p class="font-semibold text-slate-800 dark:text-slate-200">${escapeHtml(t.note || cat?.name || 'Transaction')}</p>
              <p class="text-[11px] text-slate-400">${escapeHtml(cat?.name || t.category)}</p>
            </div>
          </div>
        </td>
        <td class="py-3 px-4 text-slate-600 dark:text-slate-400">${escapeHtml(t.paymentMethod || 'Other')}</td>
        <td class="py-3 px-4 text-right font-mono font-bold ${isInc ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-900 dark:text-slate-100'}">
          ${isInc ? '+' : '-'}${formatMoney(t.amount, t.currency)}
          ${t.currency !== state.settings.baseCurrency ? `<span class="block text-[10px] text-slate-400 font-normal">(${formatMoney(t.amountInBase, state.settings.baseCurrency)})</span>` : ''}
        </td>
        <td class="py-3 px-4 text-center">
          ${t.receipt ? `
            <button onclick="openReceiptLightbox('${t.id}')" class="p-1 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-500 hover:text-indigo-600" title="View attached receipt">
              <i data-lucide="image" class="w-4 h-4"></i>
            </button>
          ` : '<span class="text-slate-300 dark:text-slate-700">-</span>'}
        </td>
        <td class="py-3 px-4 text-right whitespace-nowrap">
          <button onclick="editTransaction('${t.id}')" class="p-1 text-slate-400 hover:text-indigo-500 rounded" title="Edit">
            <i data-lucide="pencil" class="w-3.5 h-3.5"></i>
          </button>
          <button onclick="deleteTransaction('${t.id}')" class="p-1 text-slate-400 hover:text-rose-500 rounded ml-1" title="Delete">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
  lucide.createIcons();
}

function applyTransactionFilters() {
  renderTransactionsTable();
}

function resetDateFilter() {
  document.getElementById('filter-start-date').value = '';
  document.getElementById('filter-end-date').value = '';
  applyTransactionFilters();
}

// ==========================================
// 9. LOANS & DEBTS ENGINE
// ==========================================
function switchLoanTab(tab) {
  currentLoanTab = tab;
  const oweBtn = document.getElementById('tab-loan-owe');
  const lentBtn = document.getElementById('tab-loan-lent');

  if (tab === 'owe') {
    oweBtn.className = 'pb-3 text-xs sm:text-sm font-semibold border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 transition-all flex items-center gap-1.5';
    lentBtn.className = 'pb-3 text-xs sm:text-sm font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-all flex items-center gap-1.5';
  } else {
    lentBtn.className = 'pb-3 text-xs sm:text-sm font-semibold border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 transition-all flex items-center gap-1.5';
    oweBtn.className = 'pb-3 text-xs sm:text-sm font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-all flex items-center gap-1.5';
  }
  renderLoansGrid();
}

function renderLoansGrid() {
  const grid = document.getElementById('loans-grid');
  const empty = document.getElementById('loans-empty-state');
  if (!grid) return;

  const filtered = state.loans.filter(l => l.type === currentLoanTab);
  const todayStr = new Date().toISOString().split('T')[0];

  const metrics = getVaultMetrics();
  document.getElementById('loan-stat-owe').textContent = formatMoney(metrics.totalDebtOwed);
  document.getElementById('loan-stat-owe-count').textContent = `${metrics.activeDebtsCount} active obligation(s)`;
  document.getElementById('loan-stat-lent').textContent = formatMoney(metrics.totalMoneyLent);
  document.getElementById('loan-stat-lent-count').textContent = `${metrics.activeCreditsCount} pending receivable(s)`;
  document.getElementById('loan-stat-net').textContent = formatMoney(metrics.totalMoneyLent - metrics.totalDebtOwed);

  document.getElementById('badge-loans-count').textContent = metrics.activeDebtsCount;

  if (filtered.length === 0) {
    grid.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');

  grid.innerHTML = filtered.map(loan => {
    const repayments = loan.repayments || [];
    const totalRepaid = repayments.reduce((s, r) => s + Number(r.amount), 0);
    const balance = Math.max(0, loan.amount - totalRepaid);
    const pctRepaid = Math.min(100, Math.round((totalRepaid / loan.amount) * 100));

    const isSettled = balance <= 0.01;
    const isOverdue = !isSettled && loan.dueDate < todayStr;

    let statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400">Partially Paid</span>';
    if (isSettled) {
      statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400">Settled</span>';
    } else if (isOverdue) {
      statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-400 animate-pulse">Overdue</span>';
    } else if (repayments.length === 0) {
      statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Unpaid</span>';
    }

    return `
      <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between space-y-4">
        <div>
          <div class="flex items-start justify-between">
            <div>
              <h3 class="font-bold text-sm text-slate-800 dark:text-slate-100">${escapeHtml(loan.contact)}</h3>
              <p class="text-[11px] text-slate-400 mt-0.5">Due: ${loan.dueDate || 'Flexible'}</p>
            </div>
            ${statusBadge}
          </div>

          <div class="mt-3">
            <span class="text-xs text-slate-400">Outstanding Balance:</span>
            <div class="text-xl font-bold font-mono text-slate-900 dark:text-white">${formatMoney(balance, loan.currency)}</div>
            <div class="text-[11px] text-slate-400">Original: ${formatMoney(loan.amount, loan.currency)} ${loan.interestRate ? `(${loan.interestRate}% interest)` : ''}</div>
          </div>

          <div class="mt-3">
            <div class="flex justify-between text-[11px] mb-1">
              <span class="text-slate-400 font-medium">Repaid: ${pctRepaid}%</span>
              <span class="font-mono text-slate-500">${formatMoney(totalRepaid, loan.currency)}</span>
            </div>
            <div class="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
              <div class="h-full rounded-full bg-indigo-500 transition-all duration-300" style="width: ${pctRepaid}%"></div>
            </div>
          </div>

          ${loan.note ? `<p class="mt-3 text-xs text-slate-500 italic bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg">"${escapeHtml(loan.note)}"</p>` : ''}
        </div>

        <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div class="flex items-center gap-1">
            <button onclick="editLoan('${loan.id}')" class="p-1.5 text-slate-400 hover:text-indigo-500 rounded" title="Edit">
              <i data-lucide="pencil" class="w-4 h-4"></i>
            </button>
            <button onclick="deleteLoan('${loan.id}')" class="p-1.5 text-slate-400 hover:text-rose-500 rounded" title="Delete">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
          <button onclick="openRepaymentModal('${loan.id}')" class="px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 font-semibold text-xs flex items-center gap-1">
            <i data-lucide="receipt" class="w-3.5 h-3.5"></i> ${isSettled ? 'View Log' : 'Record Pay'}
          </button>
        </div>
      </div>
    `;
  }).join('');
  lucide.createIcons();
}

// ==========================================
// 10. RECURRING & SUBSCRIPTIONS VIEW
// ==========================================
function renderRecurringView() {
  const tbody = document.getElementById('recurring-table-body');
  const empty = document.getElementById('recurring-empty-state');
  if (!tbody) return;

  const rules = state.recurring;
  let monthlyEquivalent = 0;

  rules.forEach(r => {
    if (!r.active) return;
    const baseAmt = convertAmount(r.amount, r.currency, state.settings.baseCurrency);
    if (r.frequency === 'daily') monthlyEquivalent += baseAmt * 30;
    else if (r.frequency === 'weekly') monthlyEquivalent += baseAmt * 4.33;
    else if (r.frequency === 'monthly') monthlyEquivalent += baseAmt;
    else if (r.frequency === 'quarterly') monthlyEquivalent += baseAmt / 3;
    else if (r.frequency === 'yearly') monthlyEquivalent += baseAmt / 12;
  });

  document.getElementById('sub-monthly-cost').textContent = formatMoney(monthlyEquivalent);
  document.getElementById('sub-active-count').textContent = `${rules.filter(r => r.active).length} active`;

  const sortedUpcoming = [...rules].filter(r => r.active).sort((a, b) => a.nextDueDate.localeCompare(b.nextDueDate));
  if (sortedUpcoming.length > 0) {
    document.getElementById('sub-next-due').textContent = sortedUpcoming[0].name;
    document.getElementById('sub-next-date').textContent = `Due: ${sortedUpcoming[0].nextDueDate}`;
  } else {
    document.getElementById('sub-next-due').textContent = 'None due soon';
    document.getElementById('sub-next-date').textContent = '-';
  }

  if (rules.length === 0) {
    tbody.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');

  tbody.innerHTML = rules.map(rule => {
    const isInc = rule.type === 'income';
    const cat = state.categories.find(c => c.id === rule.category);
    return `
      <tr class="hover:bg-slate-50/75 dark:hover:bg-slate-850/50 transition-colors">
        <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-200">
          ${escapeHtml(rule.name)}
        </td>
        <td class="py-3 px-4">
          <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold" style="background-color: ${cat?.color || '#6366f1'}15; color: ${cat?.color || '#6366f1'}">
            ${escapeHtml(cat?.name || rule.category)}
          </span>
        </td>
        <td class="py-3 px-4 text-slate-500 capitalize">${rule.frequency}</td>
        <td class="py-3 px-4 font-mono text-slate-600 dark:text-slate-300">${rule.nextDueDate}</td>
        <td class="py-3 px-4 text-right font-mono font-bold ${isInc ? 'text-emerald-600' : 'text-slate-900 dark:text-slate-100'}">
          ${isInc ? '+' : '-'}${formatMoney(rule.amount, rule.currency)}
        </td>
        <td class="py-3 px-4 text-center">
          <button onclick="toggleRecurringActive('${rule.id}')" class="px-2 py-0.5 rounded-full text-[10px] font-bold ${rule.active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400' : 'bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-400'}">
            ${rule.active ? 'Active' : 'Paused'}
          </button>
        </td>
        <td class="py-3 px-4 text-right whitespace-nowrap">
          <button onclick="editRecurring('${rule.id}')" class="p-1 text-slate-400 hover:text-indigo-500 rounded" title="Edit">
            <i data-lucide="pencil" class="w-3.5 h-3.5"></i>
          </button>
          <button onclick="deleteRecurring('${rule.id}')" class="p-1 text-slate-400 hover:text-rose-500 rounded ml-1" title="Delete">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
  lucide.createIcons();
}

function toggleRecurringActive(id) {
  const r = state.recurring.find(item => item.id === id);
  if (r) {
    r.active = !r.active;
    saveState();
    renderRecurringView();
    showToast(`${r.name} is now ${r.active ? 'active' : 'paused'}`, 'info');
  }
}

// ==========================================
// 11. PDF FINANCIAL STATEMENT EXPORTER (jsPDF)
// ==========================================
function generateFinancialStatementPDF() {
  const { jsPDF } = window.jspdf;
  if (!jsPDF) {
    showToast('jsPDF library loading error', 'error');
    return;
  }
  showToast('Generating PDF statement...', 'info');

  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const metrics = getVaultMetrics();
  const baseCurr = state.settings.baseCurrency;
  const userName = state.settings.userName || 'Account Holder';
  const generatedDate = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const filename = `VaultFlow_Statement_${new Date().toISOString().slice(0, 10)}.pdf`;

  // Header Banner
  doc.setFillColor(15, 23, 42);
  doc.rect(0, 0, 210, 38, 'F');

  // Title
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(22);
  doc.setFont('helvetica', 'bold');
  doc.text('VaultFlow Financial Statement', 15, 18);

  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(148, 163, 184);
  doc.text(`Generated on ${generatedDate} | Base Currency: ${baseCurr}`, 15, 26);
  doc.text(`Account / Owner: ${userName}`, 15, 32);

  // Summary Metrics Section (Grid of 4 boxes)
  const boxY = 46;
  const boxW = 42;
  const boxH = 22;

  // Box 1: Inflow
  doc.setFillColor(240, 253, 244);
  doc.setDrawColor(187, 247, 208);
  doc.roundedRect(15, boxY, boxW, boxH, 3, 3, 'FD');
  doc.setFontSize(8);
  doc.setTextColor(22, 101, 52);
  doc.text('TOTAL INFLOW', 19, boxY + 7);
  doc.setFontSize(10.5);
  doc.setFont('helvetica', 'bold');
  doc.text(formatMoneyForPdf(metrics.totalIncome, baseCurr), 19, boxY + 16);

  // Box 2: Outflow
  doc.setFillColor(255, 241, 242);
  doc.setDrawColor(254, 205, 211);
  doc.roundedRect(62, boxY, boxW, boxH, 3, 3, 'FD');
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(159, 18, 57);
  doc.text('TOTAL EXPENSES', 66, boxY + 7);
  doc.setFontSize(10.5);
  doc.setFont('helvetica', 'bold');
  doc.text(formatMoneyForPdf(metrics.totalExpense, baseCurr), 66, boxY + 16);

  // Box 3: Net Cashflow
  doc.setFillColor(238, 242, 255);
  doc.setDrawColor(199, 210, 254);
  doc.roundedRect(109, boxY, boxW, boxH, 3, 3, 'FD');
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(67, 56, 202);
  doc.text('NET BALANCE', 113, boxY + 7);
  doc.setFontSize(10.5);
  doc.setFont('helvetica', 'bold');
  doc.text(formatMoneyForPdf(metrics.totalBalance, baseCurr), 113, boxY + 16);

  // Box 4: Active Debt Owed
  doc.setFillColor(254, 243, 199);
  doc.setDrawColor(253, 230, 138);
  doc.roundedRect(156, boxY, boxW, boxH, 3, 3, 'FD');
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(146, 64, 14);
  doc.text('OUTSTANDING DEBT', 160, boxY + 7);
  doc.setFontSize(10.5);
  doc.setFont('helvetica', 'bold');
  doc.text(formatMoneyForPdf(metrics.totalDebtOwed, baseCurr), 160, boxY + 16);

  // Table of Transactions using autoTable with formatMoneyForPdf
  const tableData = state.transactions.map(t => {
    const isInc = t.type === 'income';
    const cat = state.categories.find(c => c.id === t.category);
    return [
      t.date,
      isInc ? 'Income' : 'Expense',
      cat?.name || t.category,
      t.note || '-',
      t.paymentMethod || '-',
      `${isInc ? '+' : '-'}${formatMoneyForPdf(t.amount, t.currency)}`
    ];
  });

  doc.autoTable({
    startY: 76,
    head: [['Date', 'Type', 'Category', 'Description / Note', 'Method', 'Amount']],
    body: tableData,
    theme: 'striped',
    headStyles: {
      fillColor: [15, 23, 42],
      textColor: [255, 255, 255],
      fontSize: 9,
      fontStyle: 'bold'
    },
    styles: {
      fontSize: 8,
      cellPadding: 3,
      textColor: [51, 65, 85]
    },
    alternateRowStyles: {
      fillColor: [248, 250, 252]
    },
    margin: { left: 15, right: 15 },
    didDrawPage: (data) => {
      const pageStr = `Page ${doc.internal.getNumberOfPages()}`;
      doc.setFontSize(8);
      doc.setTextColor(148, 163, 184);
      doc.text('VaultFlow Offline Vault • Confidential', 15, 290);
      doc.text(pageStr, 190, 290);
    }
  });

  try {
    const dataUri = doc.output('datauristring');
    if (window.AndroidBridge && window.AndroidBridge.downloadFile) {
      window.AndroidBridge.downloadFile(dataUri, filename, 'application/pdf');
    } else {
      doc.save(filename);
    }
    showToast('Financial Statement PDF saved!', 'success');
  } catch (err) {
    console.error('PDF export error:', err);
    doc.save(filename);
    showToast('PDF Statement downloaded', 'success');
  }
}

// ==========================================
// 12. CSV EXPORT & BACKUP JSON ENGINE
// ==========================================
function exportTransactionsCSV() {
  if (state.transactions.length === 0) {
    showToast('No transactions to export', 'info');
    return;
  }

  const filename = `VaultFlow_Transactions_${new Date().toISOString().slice(0, 10)}.csv`;
  const headers = ['Date', 'Type', 'Category', 'Note/Merchant', 'PaymentMethod', 'Amount', 'Currency', 'AmountInBase', 'HasReceipt'];
  const rows = state.transactions.map(t => [
    `"${t.date}"`,
    `"${t.type}"`,
    `"${(t.category || '').replace(/"/g, '""')}"`,
    `"${(t.note || '').replace(/"/g, '""')}"`,
    `"${(t.paymentMethod || '').replace(/"/g, '""')}"`,
    t.amount,
    `"${t.currency}"`,
    t.amountInBase || t.amount,
    t.receipt ? 'YES' : 'NO'
  ]);

  const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\r\n');

  if (window.AndroidBridge && window.AndroidBridge.downloadFile) {
    const base64Data = 'data:text/csv;base64,' + btoa(unescape(encodeURIComponent(csvContent)));
    window.AndroidBridge.downloadFile(base64Data, filename, 'text/csv');
  } else {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }
  showToast('Transactions exported to CSV spreadsheet!', 'success');
}

function exportVaultBackupJSON() {
  const filename = `VaultFlow_Backup_${new Date().toISOString().slice(0, 10)}.json`;
  const jsonStr = JSON.stringify(state, null, 2);

  if (window.AndroidBridge && window.AndroidBridge.downloadFile) {
    const base64Data = 'data:application/json;base64,' + btoa(unescape(encodeURIComponent(jsonStr)));
    window.AndroidBridge.downloadFile(base64Data, filename, 'application/json');
  } else {
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }
  showToast('Vault backup JSON saved!', 'success');
}

function importVaultBackupJSON(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const parsed = JSON.parse(e.target.result);
      if (!parsed.transactions || !Array.isArray(parsed.transactions)) {
        throw new Error('Invalid VaultFlow backup schema');
      }
      state = Object.assign(state, parsed);
      saveState();
      syncUIPreferences();
      refreshCurrentView();
      showToast('Vault backup restored successfully!', 'success');
    } catch (err) {
      showToast('Failed to import backup: invalid file', 'error');
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

function executeVaultWipe() {
  const input = document.getElementById('reset-confirm-input');
  if (input.value.trim().toUpperCase() !== 'DELETE') {
    showToast('Please type DELETE to confirm', 'error');
    return;
  }

  state.transactions = [];
  state.loans = [];
  state.recurring = [];
  saveState();
  closeDoubleConfirmResetModal();
  refreshCurrentView();
  showToast('All local vault data has been erased', 'info');
}

// ==========================================
// 13. MODAL HANDLERS & FORM SUBMISSIONS
// ==========================================
function openTransactionModal(type = 'expense') {
  document.getElementById('tx-id').value = '';
  document.getElementById('modal-tx-title').textContent = 'Log Transaction';
  document.getElementById('tx-amount').value = '';
  document.getElementById('tx-note').value = '';
  document.getElementById('tx-date').value = new Date().toISOString().split('T')[0];
  document.getElementById('tx-currency').value = state.settings.baseCurrency;
  document.getElementById('tx-exchange-rate-box').classList.add('hidden');

  setTxType(type);
  populateCategorySelect('tx-category', type);
  resetReceiptUploader();

  document.getElementById('modal-transaction').classList.remove('hidden');
}

function closeTransactionModal() {
  document.getElementById('modal-transaction').classList.add('hidden');
}

function setTxType(type) {
  const btnExp = document.getElementById('btn-type-expense');
  const btnInc = document.getElementById('btn-type-income');

  if (type === 'expense') {
    btnExp.className = 'py-2 rounded-lg font-bold text-white bg-rose-600 shadow-sm transition-all flex items-center justify-center gap-1.5';
    btnInc.className = 'py-2 rounded-lg font-bold text-slate-600 dark:text-slate-400 hover:text-emerald-500 transition-all flex items-center justify-center gap-1.5';
  } else {
    btnInc.className = 'py-2 rounded-lg font-bold text-white bg-emerald-600 shadow-sm transition-all flex items-center justify-center gap-1.5';
    btnExp.className = 'py-2 rounded-lg font-bold text-slate-600 dark:text-slate-400 hover:text-rose-500 transition-all flex items-center justify-center gap-1.5';
  }
  btnExp.dataset.selected = type === 'expense';
  populateCategorySelect('tx-category', type);
}

function handleTxCurrencyChange() {
  const txCurr = document.getElementById('tx-currency').value;
  const baseCurr = state.settings.baseCurrency;
  const box = document.getElementById('tx-exchange-rate-box');

  if (txCurr === baseCurr) {
    box.classList.add('hidden');
  } else {
    box.classList.remove('hidden');
    document.getElementById('tx-foreign-label').textContent = txCurr;
    document.getElementById('tx-base-label').textContent = baseCurr;

    const defaultRate = (CURRENCY_CONFIG[txCurr]?.rateToUSD || 1.0) / (CURRENCY_CONFIG[baseCurr]?.rateToUSD || 1.0);
    document.getElementById('tx-exchange-rate').value = defaultRate.toFixed(4);
    updateConvertedPreview();
  }
}

function updateConvertedPreview() {
  const amount = Number(document.getElementById('tx-amount').value) || 0;
  const rate = Number(document.getElementById('tx-exchange-rate').value) || 1.0;
  const converted = amount * rate;
  document.getElementById('tx-exchange-converted-preview').textContent = formatMoney(converted, state.settings.baseCurrency);
}

async function handleReceiptFileSelect(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  try {
    showToast('Compressing receipt image...', 'info');
    const result = await compressReceiptImage(file, 800, 0.75);
    currentReceiptBase64 = result.dataUrl;

    document.getElementById('receipt-upload-prompt').classList.add('hidden');
    document.getElementById('receipt-preview-container').classList.remove('hidden');
    document.getElementById('receipt-preview-img').src = result.dataUrl;
    document.getElementById('receipt-preview-size').textContent = `Ready (~${result.sizeKb} KB)`;
    showToast('Receipt compressed & attached!', 'success');
  } catch (err) {
    showToast('Failed to process image file', 'error');
  }
}

function removeReceiptAttachment(e) {
  if (e) e.stopPropagation();
  resetReceiptUploader();
}

function resetReceiptUploader() {
  currentReceiptBase64 = null;
  const input = document.getElementById('tx-receipt-input');
  if (input) input.value = '';
  document.getElementById('receipt-upload-prompt')?.classList.remove('hidden');
  document.getElementById('receipt-preview-container')?.classList.add('hidden');
  const previewImg = document.getElementById('receipt-preview-img');
  if (previewImg) previewImg.src = '';
}

function handleTransactionSubmit(e) {
  e.preventDefault();
  const txId = document.getElementById('tx-id').value;
  const isExpense = document.getElementById('btn-type-expense').dataset.selected === 'true';
  const type = isExpense ? 'expense' : 'income';
  const amount = Number(document.getElementById('tx-amount').value);
  const currency = document.getElementById('tx-currency').value;
  const category = document.getElementById('tx-category').value;
  const date = document.getElementById('tx-date').value;
  const paymentMethod = document.getElementById('tx-payment-method').value;
  const note = document.getElementById('tx-note').value.trim();

  let exchangeRate = 1.0;
  if (currency !== state.settings.baseCurrency) {
    exchangeRate = Number(document.getElementById('tx-exchange-rate').value) || 1.0;
  }
  const amountInBase = currency === state.settings.baseCurrency ? amount : amount * exchangeRate;

  if (txId) {
    const existing = state.transactions.find(t => t.id === txId);
    if (existing) {
      existing.type = type;
      existing.amount = amount;
      existing.currency = currency;
      existing.amountInBase = amountInBase;
      existing.exchangeRate = exchangeRate;
      existing.category = category;
      existing.date = date;
      existing.paymentMethod = paymentMethod;
      existing.note = note;
      if (currentReceiptBase64 !== null) {
        existing.receipt = currentReceiptBase64;
      }
    }
  } else {
    const newTx = {
      id: 'tx_' + Date.now(),
      type,
      amount,
      currency,
      amountInBase,
      exchangeRate,
      category,
      date,
      paymentMethod,
      note,
      receipt: currentReceiptBase64
    };
    state.transactions.unshift(newTx);
  }

  saveState();
  closeTransactionModal();
  refreshCurrentView();
  showToast('Transaction saved successfully!', 'success');
}

function editTransaction(id) {
  const tx = state.transactions.find(t => t.id === id);
  if (!tx) return;

  openTransactionModal(tx.type);
  document.getElementById('tx-id').value = tx.id;
  document.getElementById('modal-tx-title').textContent = 'Edit Transaction';
  document.getElementById('tx-amount').value = tx.amount;
  document.getElementById('tx-currency').value = tx.currency;
  document.getElementById('tx-date').value = tx.date;
  document.getElementById('tx-category').value = tx.category;
  document.getElementById('tx-payment-method').value = tx.paymentMethod || 'Credit Card';
  document.getElementById('tx-note').value = tx.note || '';

  if (tx.receipt) {
    currentReceiptBase64 = tx.receipt;
    document.getElementById('receipt-upload-prompt').classList.add('hidden');
    document.getElementById('receipt-preview-container').classList.remove('hidden');
    document.getElementById('receipt-preview-img').src = tx.receipt;
    document.getElementById('receipt-preview-size').textContent = 'Attached';
  }

  handleTxCurrencyChange();
}

function deleteTransaction(id) {
  if (!confirm('Are you sure you want to delete this transaction record?')) return;
  state.transactions = state.transactions.filter(t => t.id !== id);
  saveState();
  refreshCurrentView();
  showToast('Transaction deleted', 'info');
}

// Receipt Lightbox
function openReceiptLightbox(txId) {
  const tx = state.transactions.find(t => t.id === txId);
  if (!tx || !tx.receipt) return;

  const cat = state.categories.find(c => c.id === tx.category);
  document.getElementById('lightbox-tx-info').textContent = `${tx.date} • ${cat?.name || tx.category} • ${formatMoney(tx.amount, tx.currency)}`;
  document.getElementById('lightbox-img').src = tx.receipt;
  document.getElementById('lightbox-download-link').href = tx.receipt;
  document.getElementById('modal-receipt-lightbox').classList.remove('hidden');
}

function closeReceiptLightbox() {
  document.getElementById('modal-receipt-lightbox').classList.add('hidden');
}

// ==========================================
// 14. LOAN & REPAYMENT MODAL HANDLERS
// ==========================================
let currentLoanDirection = 'owe';

function openLoanModal() {
  document.getElementById('loan-id').value = '';
  document.getElementById('modal-loan-title').textContent = 'Add Loan / Debt';
  document.getElementById('loan-contact').value = '';
  document.getElementById('loan-amount').value = '';
  document.getElementById('loan-interest').value = '';
  document.getElementById('loan-note').value = '';
  document.getElementById('loan-currency').value = state.settings.baseCurrency;
  document.getElementById('loan-due-date').value = new Date().toISOString().split('T')[0];

  setLoanDirection(currentLoanTab);
  document.getElementById('modal-loan').classList.remove('hidden');
}

function closeLoanModal() {
  document.getElementById('modal-loan').classList.add('hidden');
}

function setLoanDirection(dir) {
  currentLoanDirection = dir;
  const btnOwe = document.getElementById('btn-loan-owe');
  const btnLent = document.getElementById('btn-loan-lent');

  if (dir === 'owe') {
    btnOwe.className = 'py-2 rounded-lg font-bold text-white bg-rose-600 shadow-sm transition-all flex items-center justify-center gap-1.5';
    btnLent.className = 'py-2 rounded-lg font-bold text-slate-600 dark:text-slate-400 hover:text-emerald-500 transition-all flex items-center justify-center gap-1.5';
  } else {
    btnLent.className = 'py-2 rounded-lg font-bold text-white bg-emerald-600 shadow-sm transition-all flex items-center justify-center gap-1.5';
    btnOwe.className = 'py-2 rounded-lg font-bold text-slate-600 dark:text-slate-400 hover:text-rose-500 transition-all flex items-center justify-center gap-1.5';
  }
}

function handleLoanSubmit(e) {
  e.preventDefault();
  const id = document.getElementById('loan-id').value;
  const contact = document.getElementById('loan-contact').value.trim();
  const amount = Number(document.getElementById('loan-amount').value);
  const currency = document.getElementById('loan-currency').value;
  const interestRate = Number(document.getElementById('loan-interest').value) || 0;
  const dueDate = document.getElementById('loan-due-date').value;
  const note = document.getElementById('loan-note').value.trim();

  if (id) {
    const existing = state.loans.find(l => l.id === id);
    if (existing) {
      existing.contact = contact;
      existing.amount = amount;
      existing.currency = currency;
      existing.interestRate = interestRate;
      existing.dueDate = dueDate;
      existing.note = note;
      existing.type = currentLoanDirection;
    }
  } else {
    const newLoan = {
      id: 'loan_' + Date.now(),
      type: currentLoanDirection,
      contact,
      amount,
      currency,
      interestRate,
      dueDate,
      note,
      repayments: []
    };
    state.loans.unshift(newLoan);
  }

  saveState();
  closeLoanModal();
  renderLoansGrid();
  showToast('Loan record saved!', 'success');
}

function editLoan(id) {
  const loan = state.loans.find(l => l.id === id);
  if (!loan) return;

  openLoanModal();
  document.getElementById('loan-id').value = loan.id;
  document.getElementById('modal-loan-title').textContent = 'Edit Loan / Debt';
  document.getElementById('loan-contact').value = loan.contact;
  document.getElementById('loan-amount').value = loan.amount;
  document.getElementById('loan-currency').value = loan.currency;
  document.getElementById('loan-interest').value = loan.interestRate || '';
  document.getElementById('loan-due-date').value = loan.dueDate || '';
  document.getElementById('loan-note').value = loan.note || '';
  setLoanDirection(loan.type);
}

function deleteLoan(id) {
  if (!confirm('Are you sure you want to delete this loan agreement?')) return;
  state.loans = state.loans.filter(l => l.id !== id);
  saveState();
  renderLoansGrid();
  showToast('Loan agreement deleted', 'info');
}

// Repayment modal
function openRepaymentModal(loanId) {
  const loan = state.loans.find(l => l.id === loanId);
  if (!loan) return;

  document.getElementById('repay-loan-id').value = loan.id;
  document.getElementById('repay-contact-name').textContent = `Contact: ${loan.contact}`;

  const repayments = loan.repayments || [];
  const totalRepaid = repayments.reduce((s, r) => s + Number(r.amount), 0);
  const remaining = Math.max(0, loan.amount - totalRepaid);

  document.getElementById('repay-remaining-amount').textContent = formatMoney(remaining, loan.currency);
  document.getElementById('repay-original-amount').textContent = formatMoney(loan.amount, loan.currency);
  document.getElementById('repay-amount').value = remaining > 0 ? remaining : '';
  document.getElementById('repay-date').value = new Date().toISOString().split('T')[0];
  document.getElementById('repay-note').value = '';

  const list = document.getElementById('repay-history-list');
  if (repayments.length === 0) {
    list.innerHTML = '<div class="text-slate-400 py-2">No repayments logged yet.</div>';
  } else {
    list.innerHTML = repayments.map(r => `
      <div class="flex items-center justify-between p-2 rounded-lg bg-slate-100 dark:bg-slate-800">
        <div>
          <span class="font-bold text-slate-800 dark:text-slate-200">${formatMoney(r.amount, loan.currency)}</span>
          <span class="text-[10px] text-slate-400 ml-2">${r.date} • ${escapeHtml(r.method || 'Other')}</span>
        </div>
        ${r.note ? `<span class="text-[10px] text-slate-400 truncate max-w-[120px]">${escapeHtml(r.note)}</span>` : ''}
      </div>
    `).join('');
  }

  document.getElementById('modal-repayment').classList.remove('hidden');
}

function closeRepaymentModal() {
  document.getElementById('modal-repayment').classList.add('hidden');
}

function handleRepaymentSubmit(e) {
  e.preventDefault();
  const loanId = document.getElementById('repay-loan-id').value;
  const loan = state.loans.find(l => l.id === loanId);
  if (!loan) return;

  const amount = Number(document.getElementById('repay-amount').value);
  const date = document.getElementById('repay-date').value;
  const method = document.getElementById('repay-method').value;
  const note = document.getElementById('repay-note').value.trim();

  if (!loan.repayments) loan.repayments = [];
  loan.repayments.push({
    id: 'rep_' + Date.now(),
    amount,
    date,
    method,
    note
  });

  saveState();
  closeRepaymentModal();
  renderLoansGrid();
  showToast('Repayment logged successfully!', 'success');
}

// ==========================================
// 15. RECURRING RULE MODAL HANDLERS
// ==========================================
function openRecurringModal() {
  document.getElementById('rec-id').value = '';
  document.getElementById('modal-rec-title').textContent = 'Add Recurring Schedule';
  document.getElementById('rec-name').value = '';
  document.getElementById('rec-amount').value = '';
  document.getElementById('rec-currency').value = state.settings.baseCurrency;
  document.getElementById('rec-frequency').value = 'monthly';
  document.getElementById('rec-next-date').value = new Date().toISOString().split('T')[0];

  populateCategorySelect('rec-category', 'expense');
  document.getElementById('modal-recurring').classList.remove('hidden');
}

function closeRecurringModal() {
  document.getElementById('modal-recurring').classList.add('hidden');
}

function handleRecurringSubmit(e) {
  e.preventDefault();
  const id = document.getElementById('rec-id').value;
  const name = document.getElementById('rec-name').value.trim();
  const type = document.getElementById('rec-type').value;
  const category = document.getElementById('rec-category').value;
  const amount = Number(document.getElementById('rec-amount').value);
  const currency = document.getElementById('rec-currency').value;
  const frequency = document.getElementById('rec-frequency').value;
  const nextDueDate = document.getElementById('rec-next-date').value;
  const paymentMethod = document.getElementById('rec-payment-method').value;

  if (id) {
    const existing = state.recurring.find(r => r.id === id);
    if (existing) {
      existing.name = name;
      existing.type = type;
      existing.category = category;
      existing.amount = amount;
      existing.currency = currency;
      existing.frequency = frequency;
      existing.nextDueDate = nextDueDate;
      existing.paymentMethod = paymentMethod;
    }
  } else {
    const newRule = {
      id: 'rec_' + Date.now(),
      name,
      type,
      category,
      amount,
      currency,
      frequency,
      nextDueDate,
      paymentMethod,
      active: true,
      lastProcessed: null
    };
    state.recurring.unshift(newRule);
  }

  saveState();
  closeRecurringModal();
  renderRecurringView();
  showToast('Recurring rule saved!', 'success');
}

function editRecurring(id) {
  const r = state.recurring.find(item => item.id === id);
  if (!r) return;

  openRecurringModal();
  document.getElementById('rec-id').value = r.id;
  document.getElementById('modal-rec-title').textContent = 'Edit Recurring Schedule';
  document.getElementById('rec-name').value = r.name;
  document.getElementById('rec-type').value = r.type;
  populateCategorySelect('rec-category', r.type);
  document.getElementById('rec-category').value = r.category;
  document.getElementById('rec-amount').value = r.amount;
  document.getElementById('rec-currency').value = r.currency;
  document.getElementById('rec-frequency').value = r.frequency;
  document.getElementById('rec-next-date').value = r.nextDueDate;
  document.getElementById('rec-payment-method').value = r.paymentMethod || 'Credit Card';
}

function deleteRecurring(id) {
  if (!confirm('Are you sure you want to delete this recurring schedule?')) return;
  state.recurring = state.recurring.filter(r => r.id !== id);
  saveState();
  renderRecurringView();
  showToast('Recurring schedule deleted', 'info');
}

function processDueRecurringNow() {
  processDueRecurringRules(false);
}

// ==========================================
// 16. SETTINGS & CATEGORIES MODALS
// ==========================================
function saveUserName(name) {
  state.settings.userName = name.trim() || 'Shahtab';
  saveState();
  syncUIPreferences();
  showToast('User name updated', 'info');
}

function saveMonthlyBudget(val) {
  state.settings.monthlyBudget = Number(val) || 6000;
  saveState();
  updateDashboardUI();
  showToast('Monthly spending cap updated', 'success');
}

function openAddCategoryModal() {
  document.getElementById('cat-name').value = '';
  document.getElementById('cat-color').value = '#6366f1';
  document.getElementById('modal-add-category').classList.remove('hidden');
}

function closeAddCategoryModal() {
  document.getElementById('modal-add-category').classList.add('hidden');
}

function handleAddCategorySubmit(e) {
  e.preventDefault();
  const name = document.getElementById('cat-name').value.trim();
  const color = document.getElementById('cat-color').value;
  const id = name.toLowerCase().replace(/[^a-z0-9]/g, '_');

  if (state.categories.some(c => c.id === id)) {
    showToast('A category with this name already exists', 'error');
    return;
  }

  state.categories.push({ id, name, color, type: 'expense' });
  saveState();
  closeAddCategoryModal();
  renderSettingsCategoriesList();
  populateCategorySelect('tx-category');
  populateCategorySelect('rec-category');
  showToast(`Category "${name}" created!`, 'success');
}

function deleteCategory(catId) {
  const cat = state.categories.find(c => c.id === catId);
  if (!cat) return;
  if (state.categories.length <= 1) {
    showToast('You must keep at least one category', 'error');
    return;
  }
  if (!confirm(`Delete category "${cat.name}"?`)) return;

  state.categories = state.categories.filter(c => c.id !== catId);
  delete state.settings.categoryLimits[catId];
  saveState();
  renderSettingsCategoriesList();
  populateCategorySelect('tx-category');
  populateCategorySelect('rec-category');
  showToast(`Category "${cat.name}" removed`, 'info');
}

function renderSettingsCategoriesList() {
  const container = document.getElementById('settings-categories-list');
  if (!container) return;

  container.innerHTML = state.categories.map(c => `
    <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
      <div class="flex items-center gap-2.5">
        <span class="w-3.5 h-3.5 rounded-md shrink-0" style="background-color: ${c.color}"></span>
        <span class="font-medium text-slate-800 dark:text-slate-200 text-xs">${escapeHtml(c.name)}</span>
        <span class="text-[10px] text-slate-400 uppercase font-semibold">(${c.type})</span>
      </div>
      <button onclick="deleteCategory('${c.id}')" class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors" title="Delete category">
        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
      </button>
    </div>
  `).join('');
  lucide.createIcons();
}

// ==========================================
// CATEGORY SPENDING LIMITS MODAL
// ==========================================
function openCategoryLimitsModal() {
  const container = document.getElementById('category-limits-inputs');
  if (!container) return;

  if (!state.settings.categoryLimits) {
    state.settings.categoryLimits = {};
  }

  const expenseCategories = state.categories.filter(c => c.type === 'expense');
  const currencySymbol = CURRENCY_CONFIG[state.settings.baseCurrency]?.symbol || '$';
  const currentYearMonth = new Date().toISOString().slice(0, 7);

  if (expenseCategories.length === 0) {
    container.innerHTML = `
      <div class="p-4 text-center text-slate-400 text-xs">
        No expense categories available. Create categories in Settings first.
      </div>
    `;
  } else {
    container.innerHTML = expenseCategories.map(cat => {
      const limit = state.settings.categoryLimits[cat.id] || 0;
      const spent = state.transactions
        .filter(t => t.type === 'expense' && t.category === cat.id && t.date.startsWith(currentYearMonth))
        .reduce((sum, t) => sum + (t.amountInBase || convertAmount(t.amount, t.currency, state.settings.baseCurrency)), 0);

      return `
        <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-2 min-w-0">
              <span class="w-3.5 h-3.5 rounded-md shrink-0" style="background-color: ${cat.color}"></span>
              <span class="font-semibold text-slate-800 dark:text-slate-200 text-xs truncate">${escapeHtml(cat.name)}</span>
            </div>
            <span class="text-[11px] text-slate-400 shrink-0">Spent this month: <strong class="text-slate-700 dark:text-slate-300 font-mono">${formatMoney(spent)}</strong></span>
          </div>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs font-mono font-bold">${currencySymbol}</span>
            <input
              type="number"
              data-cat-id="${cat.id}"
              min="0"
              step="any"
              placeholder="No limit (unlimited)"
              value="${limit > 0 ? limit : ''}"
              class="w-full pl-8 pr-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs font-mono font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      `;
    }).join('');
  }

  const modal = document.getElementById('modal-category-limits');
  if (modal) {
    modal.classList.remove('hidden');
    lucide.createIcons();
  }
}

function closeCategoryLimitsModal() {
  const modal = document.getElementById('modal-category-limits');
  if (modal) {
    modal.classList.add('hidden');
  }
}

function handleSaveCategoryLimits(e) {
  if (e && e.preventDefault) e.preventDefault();
  if (!state.settings.categoryLimits) {
    state.settings.categoryLimits = {};
  }

  const inputs = document.querySelectorAll('#category-limits-inputs input[data-cat-id]');
  inputs.forEach(inp => {
    const catId = inp.getAttribute('data-cat-id');
    const val = parseFloat(inp.value);
    if (!isNaN(val) && val > 0) {
      state.settings.categoryLimits[catId] = val;
    } else {
      delete state.settings.categoryLimits[catId];
    }
  });

  saveState();
  closeCategoryLimitsModal();
  renderCategoryLimitsAnalytics();
  updateDashboardUI();
  showToast('Category spending limits updated successfully!', 'success');
}

function openDoubleConfirmResetModal() {
  document.getElementById('reset-confirm-input').value = '';
  document.getElementById('modal-reset-confirm').classList.remove('hidden');
}

function closeDoubleConfirmResetModal() {
  document.getElementById('modal-reset-confirm').classList.add('hidden');
}

// Widget Customization Modal
function openCustomizeWidgetsModal() {
  const w = state.settings.widgets;
  const setChk = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.checked = val !== false;
  };
  setChk('toggle-widget-quick-actions', w.quickActions);
  setChk('toggle-widget-metrics', w.metrics);
  setChk('toggle-widget-budget', w.budget);
  setChk('toggle-widget-bills', w.bills);
  setChk('toggle-widget-charts', w.charts);
  setChk('toggle-widget-recent', w.recent);
  document.getElementById('modal-customize-widgets').classList.remove('hidden');
}

function closeCustomizeWidgetsModal() {
  document.getElementById('modal-customize-widgets').classList.add('hidden');
}

function toggleWidgetVisibility(widgetKey, isVisible) {
  state.settings.widgets[widgetKey] = isVisible;
  saveState();
  applyWidgetVisibility();
}

function applyWidgetVisibility() {
  const w = state.settings.widgets;
  const setEl = (id, show) => {
    const el = document.getElementById(id);
    if (el) el.style.display = show !== false ? '' : 'none';
  };
  setEl('widget-quick-actions', w.quickActions);
  setEl('widget-metrics', w.metrics);
  setEl('widget-budget-health', w.budget);
  setEl('widget-upcoming-bills', w.bills);
  setEl('widget-charts', w.charts);
  setEl('widget-recent-activity', w.recent);
}

// Budget Adjustment Modal
function openBudgetModal() {
  const current = state.settings.monthlyBudget || 6000;
  const newVal = prompt(`Enter new monthly spending cap in ${state.settings.baseCurrency}:`, current);
  if (newVal !== null && !isNaN(newVal) && Number(newVal) > 0) {
    saveMonthlyBudget(newVal);
  }
}

function dismissBudgetAlert() {
  document.getElementById('budget-alert-banner')?.classList.add('hidden');
}

// ==========================================
// 17. VIEW NAVIGATION & BACK BUTTON HANDLERS
// ==========================================
function switchView(viewName, pushHistory = true) {
  currentView = viewName;
  document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));

  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.remove('hidden');

  // Update Desktop navigation links
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.className = 'nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60';
  });
  const activeNav = document.getElementById(`nav-${viewName}`);
  if (activeNav) {
    activeNav.className = 'nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 shadow-sm';
  }

  // Update Mobile Navigation links (fix for highlighting active section)
  document.querySelectorAll('.mobile-nav-btn').forEach(btn => {
    btn.className = 'mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800';
  });
  const activeMobileNav = document.getElementById(`mobile-nav-${viewName}`);
  if (activeMobileNav) {
    activeMobileNav.className = 'mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 shadow-sm';
  }

  // Update top header title, subtitle & icon badge
  const meta = SECTION_METADATA[viewName] || { title: 'VaultFlow', subtitle: 'Personal Money & Loan Tracking', icon: 'shield-check' };
  const titleEl = document.getElementById('page-title');
  const subEl = document.getElementById('page-subtitle');
  const iconEl = document.getElementById('section-icon');

  if (titleEl) titleEl.textContent = meta.title;
  if (subEl) subEl.textContent = meta.subtitle;
  if (iconEl) {
    iconEl.setAttribute('data-lucide', meta.icon);
    lucide.createIcons();
  }

  // Push browser history state so back button works across views
  if (pushHistory && window.history && window.history.pushState) {
    window.history.pushState({ view: viewName }, '', `#${viewName}`);
  }

  refreshCurrentView();
}

// Native Android & Browser Back Button Dispatcher
window.handleAndroidBack = function() {
  // 1. Close any visible modal first
  const openModals = [
    'modal-transaction',
    'modal-loan',
    'modal-repayment',
    'modal-recurring',
    'modal-receipt-lightbox',
    'modal-customize-widgets',
    'modal-add-category',
    'modal-category-limits',
    'modal-reset-confirm'
  ];
  for (const id of openModals) {
    const el = document.getElementById(id);
    if (el && !el.classList.contains('hidden')) {
      el.classList.add('hidden');
      return true;
    }
  }

  // 2. Close mobile menu drawer if open
  const mobileMenu = document.getElementById('mobile-menu');
  if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
    mobileMenu.classList.add('hidden');
    return true;
  }

  // 3. If currently in a sub-view, navigate back to dashboard
  if (currentView !== 'dashboard') {
    switchView('dashboard', true);
    return true;
  }

  // 4. Already on dashboard and nothing open -> return false so Android can minimize / exit app
  return false;
};

// Browser PopState Listener
window.addEventListener('popstate', (e) => {
  const view = e.state?.view || 'dashboard';
  switchView(view, false);
});

function refreshCurrentView() {
  if (currentView === 'dashboard') {
    updateDashboardUI();
  } else if (currentView === 'transactions') {
    renderTransactionsTable();
  } else if (currentView === 'loans') {
    renderLoansGrid();
  } else if (currentView === 'recurring') {
    renderRecurringView();
  } else if (currentView === 'analytics') {
    renderAnalyticsCharts();
  } else if (currentView === 'settings') {
    renderSettingsCategoriesList();
  }
}

function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  menu.classList.toggle('hidden');
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  state.settings.theme = isDark ? 'dark' : 'light';
  saveState();
  updateThemeIcon();
  if (weeklyChartInstance) renderWeeklyChart();
  if (trendChartInstance || doughnutChartInstance) renderAnalyticsCharts();
}

function updateThemeIcon() {
  const isDark = document.documentElement.classList.contains('dark');
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.setAttribute('data-lucide', isDark ? 'sun' : 'moon');
    lucide.createIcons();
  }
}

function populateCategorySelect(selectId, filterType = null) {
  const select = document.getElementById(selectId);
  if (!select) return;

  const cats = filterType ? state.categories.filter(c => c.type === filterType) : state.categories;
  select.innerHTML = cats.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
}

function syncUIPreferences() {
  const userName = state.settings.userName || 'Shahtab';
  const initial = userName.slice(0, 2).toUpperCase();

  document.getElementById('sidebar-user-name').textContent = userName;
  document.getElementById('dash-user-name').textContent = userName;
  document.getElementById('sidebar-user-initial').textContent = initial;

  const baseCurr = state.settings.baseCurrency || 'USD';
  document.getElementById('setting-base-currency').value = baseCurr;
  document.getElementById('setting-user-name').value = userName;
  document.getElementById('setting-budget-limit').value = state.settings.monthlyBudget || 6000;
  document.getElementById('setting-currency-symbol').textContent = CURRENCY_CONFIG[baseCurr]?.symbol || '$';

  const filterCat = document.getElementById('filter-category');
  if (filterCat) {
    filterCat.innerHTML = '<option value="all">All Categories</option>' + state.categories.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
  }

  applyWidgetVisibility();
  updateThemeIcon();
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const colorMap = {
    success: 'bg-emerald-600 text-white border-emerald-500',
    error: 'bg-rose-600 text-white border-rose-500',
    info: 'bg-slate-900 dark:bg-slate-800 text-white border-slate-700'
  };

  toast.className = `p-3.5 rounded-2xl shadow-xl border text-xs font-semibold flex items-center justify-between pointer-events-auto transition-all transform duration-300 opacity-0 translate-y-2 ${colorMap[type] || colorMap.info}`;
  toast.innerHTML = `
    <span>${escapeHtml(message)}</span>
    <button onclick="this.parentElement.remove()" class="p-1 hover:opacity-75 ml-2">✕</button>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('opacity-0', 'translate-y-2');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3800);
}

function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ==========================================
// 18. INITIALIZATION ON DOM READY
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
  await initStorage();

  if (state.settings.theme === 'light') {
    document.documentElement.classList.remove('dark');
  } else {
    document.documentElement.classList.add('dark');
  }

  syncUIPreferences();
  processDueRecurringRules(true);
  updateDashboardUI();
  lucide.createIcons();

  const hash = window.location.hash.replace('#', '');
  if (hash && SECTION_METADATA[hash]) {
    switchView(hash, false);
  }
});

// Explicit window bindings for inline handlers
window.openCategoryLimitsModal = openCategoryLimitsModal;
window.closeCategoryLimitsModal = closeCategoryLimitsModal;
window.handleSaveCategoryLimits = handleSaveCategoryLimits;
window.switchView = switchView;
window.switchLoanTab = switchLoanTab;

