# build_vaultflow.py
# Generator script to write the complete VaultFlow single-file application
import os

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>VaultFlow - Personal Money & Loan Tracker</title>
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eef2ff',
              100: '#e0e7ff',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
            },
            emerald: {
              500: '#10b981',
              600: '#059669',
            },
            rose: {
              500: '#f43f5e',
              600: '#e11d48',
            },
            slate: {
              850: '#131e32',
              900: '#0f172a',
              950: '#090d16',
            }
          },
          fontFamily: {
            sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
          }
        }
      }
    }
  </script>

  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  
  <!-- jsPDF & AutoTable -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>

  <!-- Google Font: Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <style>
    /* Custom Scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.05);
    }
    .dark ::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.5);
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.4);
      border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(99, 102, 241, 0.6);
    }

    /* Glass Effect */
    .glass-card {
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }
  </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans min-h-screen flex flex-col antialiased selection:bg-indigo-500 selection:text-white m-0 p-0">

  <!-- Toast Notification Container -->
  <div id="toast-container" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none max-w-sm w-full px-4 sm:px-0"></div>

  <!-- Budget Breach Alert Banner -->
  <div id="budget-alert-banner" class="hidden bg-rose-600 text-white px-4 py-2 text-xs sm:text-sm font-medium flex items-center justify-between shadow-lg sticky top-0 z-40">
    <div class="flex items-center gap-2">
      <i data-lucide="alert-triangle" class="w-4 h-4 shrink-0 animate-pulse"></i>
      <span id="budget-alert-text">Monthly spending limit exceeded!</span>
    </div>
    <button onclick="dismissBudgetAlert()" class="p-1 hover:bg-rose-700 rounded transition-colors" title="Dismiss">
      <i data-lucide="x" class="w-3.5 h-3.5"></i>
    </button>
  </div>

  <div class="flex flex-1 h-[calc(100vh-theme(spacing.0))] overflow-hidden">
    <!-- Desktop Sidebar -->
    <aside id="sidebar" class="hidden md:flex flex-col w-64 border-r border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 glass-card shrink-0 transition-all duration-300">
      <!-- Logo -->
      <div class="h-16 flex items-center justify-between px-6 border-b border-slate-200 dark:border-slate-800">
        <div class="flex items-center gap-3">
          <img src="ic_vault_minimal.png" alt="VaultFlow Icon" class="w-9 h-9 rounded-xl object-cover shadow-sm border border-slate-200 dark:border-slate-800">
          <div>
            <span class="font-bold text-lg tracking-tight bg-gradient-to-r from-indigo-500 via-purple-500 to-amber-400 bg-clip-text text-transparent">VaultFlow</span>
            <span class="block text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Local Financial Vault</span>
          </div>
        </div>
      </div>

      <!-- Navigation links -->
      <nav class="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        <button onclick="switchView('dashboard')" id="nav-dashboard" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 shadow-sm">
          <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
          <span>Dashboard</span>
        </button>
        <button onclick="switchView('transactions')" id="nav-transactions" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60">
          <i data-lucide="arrow-left-right" class="w-4 h-4"></i>
          <span>Transactions</span>
          <span id="badge-tx-count" class="ml-auto text-xs px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">0</span>
        </button>
        <button onclick="switchView('loans')" id="nav-loans" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60">
          <i data-lucide="hand-coins" class="w-4 h-4"></i>
          <span>Loans & Debts</span>
          <span id="badge-loans-count" class="ml-auto text-xs px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-950/80 text-rose-600 dark:text-rose-400 font-mono">0</span>
        </button>
        <button onclick="switchView('recurring')" id="nav-recurring" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60">
          <i data-lucide="calendar-sync" class="w-4 h-4"></i>
          <span>Subscriptions</span>
          <span id="badge-sub-due" class="ml-auto text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400 font-mono hidden">Due</span>
        </button>
        <button onclick="switchView('analytics')" id="nav-analytics" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60">
          <i data-lucide="pie-chart" class="w-4 h-4"></i>
          <span>Analytics & Reports</span>
        </button>
        <button onclick="switchView('settings')" id="nav-settings" class="nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60">
          <i data-lucide="settings" class="w-4 h-4"></i>
          <span>Settings & Backup</span>
        </button>
      </nav>

      <!-- Bottom User / Vault Info -->
      <div class="p-4 border-t border-slate-200 dark:border-slate-800">
        <div class="flex items-center gap-3 p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800/60">
          <div class="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-500 flex items-center justify-center font-bold text-xs">
            <span id="sidebar-user-initial">VF</span>
          </div>
          <div class="flex-1 min-w-0">
            <p id="sidebar-user-name" class="text-xs font-semibold truncate text-slate-800 dark:text-slate-200">Local Vault</p>
            <p class="text-[11px] text-emerald-500 flex items-center gap-1 font-medium">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Offline Encrypted
            </p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Top Header Bar with Home Button and responsive controls -->
      <header class="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 glass-card px-3 sm:px-6 flex items-center justify-between shrink-0 z-30 gap-2">
        <!-- Left: Mobile Menu & Current Section -->
        <div class="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
          <!-- Mobile Menu Toggle -->
          <button onclick="toggleMobileMenu()" class="md:hidden p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 shrink-0">
            <i data-lucide="menu" class="w-5 h-5"></i>
          </button>
          
          <div class="flex items-center gap-2 min-w-0">
            <div id="section-icon-badge" class="w-7 h-7 rounded-lg bg-indigo-500/10 text-indigo-500 hidden sm:flex items-center justify-center shrink-0">
              <i id="section-icon" data-lucide="layout-dashboard" class="w-4 h-4"></i>
            </div>
            <div class="min-w-0">
              <h1 id="page-title" class="text-sm sm:text-base md:text-lg font-bold truncate text-slate-900 dark:text-slate-100">Financial Dashboard</h1>
              <span id="page-subtitle" class="hidden sm:block text-[10px] text-slate-400 font-medium truncate">Vault Overview & Real-Time Analytics</span>
            </div>
          </div>
        </div>

        <!-- Right Header Actions (Home button, Theme toggle, Quick Add) -->
        <div class="flex items-center gap-2 shrink-0">
          <!-- Home button (Redirects to Dashboard) -->
          <button onclick="switchView('dashboard')" class="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-indigo-500 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors shrink-0 flex items-center justify-center" title="Go to Dashboard">
            <i data-lucide="home" class="w-4 h-4"></i>
          </button>

          <!-- Dark/Light Theme Toggle -->
          <button onclick="toggleTheme()" class="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-indigo-500 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors shrink-0" title="Toggle Theme">
            <i id="theme-icon" data-lucide="moon" class="w-4 h-4"></i>
          </button>

          <!-- Quick Add Button -->
          <button onclick="openTransactionModal('expense')" class="flex items-center gap-1.5 px-3 py-2 sm:px-4 sm:py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs sm:text-sm shadow-sm shadow-indigo-600/30 transition-all active:scale-95 shrink-0">
            <i data-lucide="plus" class="w-3.5 h-3.5 sm:w-4 sm:h-4"></i>
            <span class="hidden sm:inline">Add Record</span>
            <span class="sm:hidden font-semibold">Add</span>
          </button>
        </div>
      </header>

      <!-- Mobile Navigation Drawer Overlay with Dynamic Active Highlighting -->
      <div id="mobile-menu" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm hidden md:hidden">
        <div class="w-64 h-full bg-white dark:bg-slate-900 p-4 flex flex-col shadow-2xl">
          <div class="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
            <div class="flex items-center gap-2.5">
              <img src="ic_vault_minimal.png" alt="VaultFlow Icon" class="w-8 h-8 rounded-lg object-cover shadow-sm border border-slate-200 dark:border-slate-800">
              <span class="font-bold text-base bg-gradient-to-r from-indigo-500 to-amber-400 bg-clip-text text-transparent">VaultFlow</span>
            </div>
            <button onclick="toggleMobileMenu()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
              <i data-lucide="x" class="w-5 h-5"></i>
            </button>
          </div>
          
          <nav class="flex-1 py-4 space-y-1.5 overflow-y-auto">
            <button onclick="switchView('dashboard'); toggleMobileMenu()" id="mobile-nav-dashboard" class="mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 shadow-sm">
              <i data-lucide="layout-dashboard" class="w-4 h-4"></i> Dashboard
            </button>
            <button onclick="switchView('transactions'); toggleMobileMenu()" id="mobile-nav-transactions" class="mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
              <i data-lucide="arrow-left-right" class="w-4 h-4"></i> Transactions
            </button>
            <button onclick="switchView('loans'); toggleMobileMenu()" id="mobile-nav-loans" class="mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
              <i data-lucide="hand-coins" class="w-4 h-4"></i> Loans & Debts
            </button>
            <button onclick="switchView('recurring'); toggleMobileMenu()" id="mobile-nav-recurring" class="mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
              <i data-lucide="calendar-sync" class="w-4 h-4"></i> Subscriptions
            </button>
            <button onclick="switchView('analytics'); toggleMobileMenu()" id="mobile-nav-analytics" class="mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
              <i data-lucide="pie-chart" class="w-4 h-4"></i> Analytics & Reports
            </button>
            <button onclick="switchView('settings'); toggleMobileMenu()" id="mobile-nav-settings" class="mobile-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
              <i data-lucide="settings" class="w-4 h-4"></i> Settings
            </button>
          </nav>

          <div class="pt-4 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500 text-center">
            VaultFlow v1.1 • Classic Vault Edition
          </div>
        </div>
      </div>

      <!-- Scrollable Main View Container -->
      <main id="main-content" class="flex-1 overflow-y-auto p-3 sm:p-6 lg:p-8 space-y-6">

        <!-- ========================================== -->
        <!-- VIEW 1: DASHBOARD -->
        <!-- ========================================== -->
        <section id="view-dashboard" class="space-y-6 view-section">
          <!-- Top Row: Welcome & Customize Widgets Button -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Welcome back, <span id="dash-user-name" class="text-indigo-500">Shahtab</span></h2>
              <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Here is your financial status and real-time vault analytics.</p>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="openCustomizeWidgetsModal()" class="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-1.5 transition-colors">
                <i data-lucide="sliders-horizontal" class="w-3.5 h-3.5"></i> Customize
              </button>
              <button onclick="openTransactionModal('income')" class="px-3 py-2 text-xs font-semibold rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/20 flex items-center gap-1.5 transition-colors">
                <i data-lucide="arrow-down-left" class="w-3.5 h-3.5"></i> + Income
              </button>
              <button onclick="openTransactionModal('expense')" class="px-3 py-2 text-xs font-semibold rounded-xl bg-rose-500/10 text-rose-600 dark:text-rose-400 hover:bg-rose-500/20 flex items-center gap-1.5 transition-colors">
                <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i> + Expense
              </button>
            </div>
          </div>

          <!-- Useful Widget: Quick Actions Bar -->
          <div id="widget-quick-actions" class="p-3 sm:p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-wrap items-center justify-between gap-2.5">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-500 flex items-center justify-center">
                <i data-lucide="zap" class="w-4 h-4"></i>
              </div>
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Quick Actions</span>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <button onclick="openTransactionModal('expense')" class="px-2.5 py-1.5 rounded-lg bg-rose-50 dark:bg-rose-950/50 hover:bg-rose-100 text-rose-600 dark:text-rose-400 text-xs font-semibold flex items-center gap-1 transition-colors">
                <i data-lucide="minus-circle" class="w-3.5 h-3.5"></i> Log Spend
              </button>
              <button onclick="openTransactionModal('income')" class="px-2.5 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/50 hover:bg-emerald-100 text-emerald-600 dark:text-emerald-400 text-xs font-semibold flex items-center gap-1 transition-colors">
                <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i> Log Income
              </button>
              <button onclick="openLoanModal()" class="px-2.5 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/50 hover:bg-amber-100 text-amber-600 dark:text-amber-400 text-xs font-semibold flex items-center gap-1 transition-colors">
                <i data-lucide="hand-coins" class="w-3.5 h-3.5"></i> Add Loan
              </button>
              <button onclick="openTransactionModal('expense'); document.getElementById('tx-receipt-input').click()" class="px-2.5 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 text-indigo-600 dark:text-indigo-400 text-xs font-semibold flex items-center gap-1 transition-colors">
                <i data-lucide="camera" class="w-3.5 h-3.5"></i> Scan Receipt
              </button>
            </div>
          </div>

          <!-- Widget: Key Metrics Cards (Clickable Navigation) -->
          <div id="widget-metrics" class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-5">
            <!-- Card 1: Total Balance -> Transactions -->
            <div onclick="switchView('transactions')" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' ') switchView('transactions')" class="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group cursor-pointer transition-all duration-200 hover:shadow-md hover:border-indigo-300 dark:hover:border-indigo-700/80 hover:-translate-y-0.5 active:scale-[0.98]">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Net Balance</span>
                <div class="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i data-lucide="wallet" class="w-4 h-4"></i>
                </div>
              </div>
              <div class="mt-3">
                <div id="metric-total-balance" class="text-xl sm:text-2xl font-bold tracking-tight font-mono text-slate-900 dark:text-white">$0.00</div>
                <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
                  <span>Liquid Cash & Bank Flow</span>
                  <i data-lucide="chevron-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all"></i>
                </div>
              </div>
            </div>

            <!-- Card 2: Monthly Spend -> Analytics -->
            <div onclick="switchView('analytics')" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' ') switchView('analytics')" class="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group cursor-pointer transition-all duration-200 hover:shadow-md hover:border-rose-300 dark:hover:border-rose-800/80 hover:-translate-y-0.5 active:scale-[0.98]">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">This Month's Spend</span>
                <div class="w-8 h-8 rounded-xl bg-rose-50 dark:bg-rose-950/70 text-rose-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                </div>
              </div>
              <div class="mt-3">
                <div id="metric-month-spend" class="text-xl sm:text-2xl font-bold tracking-tight font-mono text-rose-600 dark:text-rose-400">$0.00</div>
                <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
                  <span id="metric-spend-pct">0% of monthly limit</span>
                  <i data-lucide="chevron-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-rose-500 group-hover:translate-x-0.5 transition-all"></i>
                </div>
              </div>
            </div>

            <!-- Card 3: Total Debt Owed -> Loans (owe tab) -->
            <div onclick="switchView('loans'); switchLoanTab('owe')" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' ') { switchView('loans'); switchLoanTab('owe'); }" class="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group cursor-pointer transition-all duration-200 hover:shadow-md hover:border-amber-300 dark:hover:border-amber-800/80 hover:-translate-y-0.5 active:scale-[0.98]">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">I Owe (Debts)</span>
                <div class="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-950/70 text-amber-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i data-lucide="scale" class="w-4 h-4"></i>
                </div>
              </div>
              <div class="mt-3">
                <div id="metric-debt-owed" class="text-xl sm:text-2xl font-bold tracking-tight font-mono text-amber-600 dark:text-amber-400">$0.00</div>
                <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
                  <span id="metric-active-debts">0 active loan obligations</span>
                  <i data-lucide="chevron-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-amber-500 group-hover:translate-x-0.5 transition-all"></i>
                </div>
              </div>
            </div>

            <!-- Card 4: Total Money Lent -> Loans (lent tab) -->
            <div onclick="switchView('loans'); switchLoanTab('lent')" role="button" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' ') { switchView('loans'); switchLoanTab('lent'); }" class="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group cursor-pointer transition-all duration-200 hover:shadow-md hover:border-emerald-300 dark:hover:border-emerald-800/80 hover:-translate-y-0.5 active:scale-[0.98]">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Owed to Me (Lent)</span>
                <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/70 text-emerald-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i data-lucide="badge-dollar-sign" class="w-4 h-4"></i>
                </div>
              </div>
              <div class="mt-3">
                <div id="metric-money-lent" class="text-xl sm:text-2xl font-bold tracking-tight font-mono text-emerald-600 dark:text-emerald-400">$0.00</div>
                <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
                  <span id="metric-active-credits">0 pending receivables</span>
                  <i data-lucide="chevron-right" class="w-3.5 h-3.5 text-slate-400 group-hover:text-emerald-500 group-hover:translate-x-0.5 transition-all"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- Middle Row: Budget Health & Upcoming Bills -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Widget: Budget Health (2 cols on lg) -->
            <div id="widget-budget-health" class="lg:col-span-2 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 text-indigo-500">
                    <i data-lucide="gauge" class="w-4 h-4"></i>
                  </div>
                  <div>
                    <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">Monthly Budget Health</h3>
                    <p class="text-xs text-slate-400">Pacing against your monthly allowance</p>
                  </div>
                </div>
                <button onclick="openBudgetModal()" class="text-xs text-indigo-500 hover:text-indigo-600 font-semibold flex items-center gap-1">
                  Adjust Limit <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
                </button>
              </div>

              <!-- Progress bar -->
              <div>
                <div class="flex justify-between text-xs font-semibold mb-1.5">
                  <span id="budget-health-spent" class="text-slate-700 dark:text-slate-300 font-mono">$0.00 spent</span>
                  <span id="budget-health-limit" class="text-slate-400 font-mono">Limit: $0.00</span>
                </div>
                <div class="w-full h-3 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden relative">
                  <div id="budget-health-bar" class="h-full rounded-full transition-all duration-500 bg-emerald-500" style="width: 0%"></div>
                </div>
                <div class="flex justify-between items-center mt-2 text-xs">
                  <span id="budget-health-tag" class="px-2 py-0.5 rounded-full font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400 text-[11px]">Safe Spending</span>
                  <span id="budget-health-remaining" class="text-slate-500 dark:text-slate-400 font-mono">$0.00 left this month</span>
                </div>
              </div>
            </div>

            <!-- Widget: Upcoming Bills & Recurring Due -->
            <div id="widget-upcoming-bills" class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center gap-2">
                    <div class="p-2 rounded-lg bg-amber-50 dark:bg-amber-950/50 text-amber-500">
                      <i data-lucide="clock" class="w-4 h-4"></i>
                    </div>
                    <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">Bills Due (7 Days)</h3>
                  </div>
                  <span id="upcoming-bills-count" class="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold">0</span>
                </div>

                <div id="upcoming-bills-list" class="space-y-2.5 max-h-48 overflow-y-auto pr-1">
                  <!-- Dynamically populated bills -->
                </div>
              </div>

              <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center">
                <button onclick="switchView('recurring')" class="text-xs font-semibold text-indigo-500 hover:text-indigo-600">Manage Recurring</button>
                <button onclick="processDueRecurringNow()" class="text-xs px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 transition-colors font-semibold">Process Now</button>
              </div>
            </div>
          </div>

          <!-- Bottom Row: Weekly Chart & Recent Transactions -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Widget: Weekly Spending Chart -->
            <div id="widget-charts" class="lg:col-span-2 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">7-Day Spending Trajectory</h3>
                  <p class="text-xs text-slate-400">Daily expenses recorded this past week</p>
                </div>
                <span class="text-xs px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 font-medium text-slate-500">Live Breakdown</span>
              </div>
              <div class="h-64 relative">
                <canvas id="weeklyBarChart"></canvas>
              </div>
            </div>

            <!-- Widget: Recent Transactions Feed -->
            <div id="widget-recent-activity" class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-4">
                  <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">Recent Transactions</h3>
                  <button onclick="switchView('transactions')" class="text-xs text-indigo-500 font-semibold hover:text-indigo-600">View All</button>
                </div>

                <div id="dashboard-recent-list" class="space-y-3">
                  <!-- Injected recent transactions -->
                </div>
              </div>

              <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-center">
                <button onclick="openTransactionModal('expense')" class="w-full py-2 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:border-indigo-500 hover:text-indigo-500 transition-colors">
                  + Log Another Transaction
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW 2: TRANSACTIONS & RECEIPTS -->
        <!-- ========================================== -->
        <section id="view-transactions" class="space-y-6 view-section hidden">
          <!-- Header & Action Row -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Transaction Ledger</h2>
              <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Search, filter, and inspect detailed records with receipts.</p>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="exportTransactionsCSV()" class="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-1.5 transition-colors">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-emerald-500"></i> Export CSV
              </button>
              <button onclick="openTransactionModal('expense')" class="px-3.5 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-1.5 shadow-sm transition-all">
                <i data-lucide="plus" class="w-3.5 h-3.5"></i> New Transaction
              </button>
            </div>
          </div>

          <!-- Filters Bar -->
          <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              <!-- Search Notes -->
              <div class="relative lg:col-span-2">
                <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-3"></i>
                <input type="text" id="filter-search" oninput="applyTransactionFilters()" placeholder="Search notes, category, merchant..." class="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 focus:ring-2 focus:ring-indigo-500 focus:outline-none">
              </div>

              <!-- Filter: Type -->
              <div>
                <select id="filter-type" onchange="applyTransactionFilters()" class="w-full py-2 px-3 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 focus:ring-2 focus:ring-indigo-500">
                  <option value="all">All Types</option>
                  <option value="expense">Expenses Only</option>
                  <option value="income">Income Only</option>
                </select>
              </div>

              <!-- Filter: Category -->
              <div>
                <select id="filter-category" onchange="applyTransactionFilters()" class="w-full py-2 px-3 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 focus:ring-2 focus:ring-indigo-500">
                  <option value="all">All Categories</option>
                </select>
              </div>

              <!-- Filter: Has Receipt -->
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" id="filter-receipt-only" onchange="applyTransactionFilters()" class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500">
                  <span>Has Receipt Only</span>
                </label>
              </div>
            </div>

            <!-- Date range selector -->
            <div class="flex flex-wrap items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800/60 text-xs text-slate-500 gap-2">
              <div class="flex items-center gap-2">
                <span>Date Range:</span>
                <input type="date" id="filter-start-date" onchange="applyTransactionFilters()" class="py-1 px-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs">
                <span>to</span>
                <input type="date" id="filter-end-date" onchange="applyTransactionFilters()" class="py-1 px-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs">
                <button onclick="resetDateFilter()" class="text-indigo-500 hover:underline">Clear</button>
              </div>
              <div id="filter-stats" class="font-mono text-slate-400">
                Showing 0 of 0 records
              </div>
            </div>
          </div>

          <!-- Transaction Table Card -->
          <div class="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="border-b border-slate-200 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-850/50 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                    <th class="py-3 px-4">Date</th>
                    <th class="py-3 px-4">Category & Note</th>
                    <th class="py-3 px-4">Payment Method</th>
                    <th class="py-3 px-4 text-right">Amount</th>
                    <th class="py-3 px-4 text-center">Receipt</th>
                    <th class="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody id="transaction-table-body" class="divide-y divide-slate-100 dark:divide-slate-800">
                  <!-- Rendered dynamically -->
                </tbody>
              </table>
            </div>

            <div id="tx-empty-state" class="py-12 text-center hidden">
              <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
                <i data-lucide="receipt-text" class="w-6 h-6"></i>
              </div>
              <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">No transactions match your filters</p>
              <p class="text-xs text-slate-400 mt-1">Try clearing filters or add a new transaction record.</p>
            </div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW 3: LOANS & DEBTS -->
        <!-- ========================================== -->
        <section id="view-loans" class="space-y-6 view-section hidden">
          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Loan & Debt Manager</h2>
              <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Track liabilities, borrowed funds, and money lent to friends or clients.</p>
            </div>
            <button onclick="openLoanModal()" class="px-3.5 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-1.5 shadow-sm transition-all">
              <i data-lucide="plus" class="w-3.5 h-3.5"></i> Add Loan/Debt
            </button>
          </div>

          <!-- Debt / Credit Top Stats -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between">
              <div>
                <span class="text-xs font-semibold uppercase tracking-wider text-rose-500">I Owe (My Debts)</span>
                <div id="loan-stat-owe" class="text-2xl font-bold font-mono text-rose-600 dark:text-rose-400 mt-1">$0.00</div>
                <div id="loan-stat-owe-count" class="text-[11px] text-slate-400 mt-0.5">0 unresolved obligations</div>
              </div>
              <div class="w-10 h-10 rounded-xl bg-rose-50 dark:bg-rose-950/70 text-rose-500 flex items-center justify-center">
                <i data-lucide="trending-down" class="w-5 h-5"></i>
              </div>
            </div>

            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between">
              <div>
                <span class="text-xs font-semibold uppercase tracking-wider text-emerald-500">Owed to Me (Lent)</span>
                <div id="loan-stat-lent" class="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-1">$0.00</div>
                <div id="loan-stat-lent-count" class="text-[11px] text-slate-400 mt-0.5">0 pending receivables</div>
              </div>
              <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/70 text-emerald-500 flex items-center justify-center">
                <i data-lucide="trending-up" class="w-5 h-5"></i>
              </div>
            </div>

            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between">
              <div>
                <span class="text-xs font-semibold uppercase tracking-wider text-indigo-500">Net Loan Balance</span>
                <div id="loan-stat-net" class="text-2xl font-bold font-mono text-indigo-600 dark:text-indigo-400 mt-1">$0.00</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Lent minus Owed</div>
              </div>
              <div class="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-500 flex items-center justify-center">
                <i data-lucide="scale" class="w-5 h-5"></i>
              </div>
            </div>
          </div>

          <!-- Tabs: Money I Owe vs Money Owed to Me -->
          <div class="flex border-b border-slate-200 dark:border-slate-800 gap-4">
            <button onclick="switchLoanTab('owe')" id="tab-loan-owe" class="pb-3 text-xs sm:text-sm font-semibold border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 transition-all flex items-center gap-1.5">
              <i data-lucide="arrow-up-right" class="w-4 h-4 text-rose-500"></i> Money I Owe (Debts)
            </button>
            <button onclick="switchLoanTab('lent')" id="tab-loan-lent" class="pb-3 text-xs sm:text-sm font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-all flex items-center gap-1.5">
              <i data-lucide="arrow-down-left" class="w-4 h-4 text-emerald-500"></i> Money Owed to Me (Credits)
            </button>
          </div>

          <!-- Loans Grid -->
          <div id="loans-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Dynamically populated loan cards -->
          </div>

          <div id="loans-empty-state" class="py-12 text-center rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 hidden">
            <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
              <i data-lucide="check-circle-2" class="w-6 h-6"></i>
            </div>
            <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">No active loans or debts in this category</p>
            <p class="text-xs text-slate-400 mt-1">All clean! Click "+ Add Loan/Debt" to record a new agreement.</p>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW 4: RECURRING & SUBSCRIPTIONS -->
        <!-- ========================================== -->
        <section id="view-recurring" class="space-y-6 view-section hidden">
          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Recurring Bills & Subscriptions</h2>
              <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Automate recurring expenses and salary schedules with due date auto-processing.</p>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="processDueRecurringNow()" class="px-3 py-2 text-xs font-semibold rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-1.5 transition-colors">
                <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-indigo-500"></i> Evaluate & Process Due Rules
              </button>
              <button onclick="openRecurringModal()" class="px-3.5 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-1.5 shadow-sm transition-all">
                <i data-lucide="plus" class="w-3.5 h-3.5"></i> Add Rule
              </button>
            </div>
          </div>

          <!-- Subscription Summary Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800">
              <span class="text-xs font-semibold text-slate-400 uppercase">Monthly Projected Subscriptions</span>
              <div id="sub-monthly-cost" class="text-xl font-bold font-mono text-slate-900 dark:text-white mt-1">$0.00</div>
              <div class="text-[11px] text-slate-400 mt-0.5">Normalized monthly recurring expenses</div>
            </div>
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800">
              <span class="text-xs font-semibold text-slate-400 uppercase">Active Rules</span>
              <div id="sub-active-count" class="text-xl font-bold font-mono text-indigo-500 mt-1">0 rules</div>
              <div class="text-[11px] text-slate-400 mt-0.5">Automating transactions</div>
            </div>
            <div class="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800">
              <span class="text-xs font-semibold text-slate-400 uppercase">Next Upcoming Bill</span>
              <div id="sub-next-due" class="text-sm font-bold text-slate-800 dark:text-slate-200 mt-1.5 truncate">None due soon</div>
              <div id="sub-next-date" class="text-[11px] text-slate-400 mt-0.5">-</div>
            </div>
          </div>

          <!-- Recurring Table -->
          <div class="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="border-b border-slate-200 dark:border-slate-800 bg-slate-50/75 dark:bg-slate-850/50 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                    <th class="py-3 px-4">Title / Name</th>
                    <th class="py-3 px-4">Type & Category</th>
                    <th class="py-3 px-4">Frequency</th>
                    <th class="py-3 px-4">Next Due Date</th>
                    <th class="py-3 px-4 text-right">Amount</th>
                    <th class="py-3 px-4 text-center">Status</th>
                    <th class="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody id="recurring-table-body" class="divide-y divide-slate-100 dark:divide-slate-800">
                  <!-- Rendered dynamically -->
                </tbody>
              </table>
            </div>

            <div id="recurring-empty-state" class="py-12 text-center hidden">
              <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
                <i data-lucide="calendar-sync" class="w-6 h-6"></i>
              </div>
              <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">No recurring rules configured</p>
              <p class="text-xs text-slate-400 mt-1">Set up monthly rent, Netflix, insurance, or salaries for automatic tracking.</p>
            </div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW 5: ANALYTICS & REPORTS -->
        <!-- ========================================== -->
        <section id="view-analytics" class="space-y-6 view-section hidden">
          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Analytics & Financial Reports</h2>
              <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Deep visual insights, category allocations, and client-side PDF statements.</p>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="generateFinancialStatementPDF()" class="px-3.5 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-1.5 shadow-sm transition-all">
                <i data-lucide="file-text" class="w-3.5 h-3.5"></i> Export PDF Statement
              </button>
            </div>
          </div>

          <!-- Charts Row 1: Line Chart & Doughnut Chart -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Income vs Expense Trend (2 cols) -->
            <div class="lg:col-span-2 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">Income vs. Expense Trend</h3>
                  <p class="text-xs text-slate-400">Monthly cash inflow vs outflows</p>
                </div>
                <span class="text-xs px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 font-semibold text-indigo-500">6-Month Window</span>
              </div>
              <div class="h-64 relative">
                <canvas id="trendLineChart"></canvas>
              </div>
            </div>

            <!-- Spending by Category Doughnut -->
            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">Category Breakdown</h3>
                  <span class="text-xs text-slate-400">Expenses</span>
                </div>
                <div class="h-56 relative flex items-center justify-center">
                  <canvas id="categoryDoughnutChart"></canvas>
                </div>
              </div>
              <div id="category-legend-list" class="space-y-1.5 text-xs max-h-24 overflow-y-auto pr-1">
                <!-- Dynamically populated category legend -->
              </div>
            </div>
          </div>

          <!-- Category Spending Limit Trackers -->
          <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100">Category Spending Limits</h3>
                <p class="text-xs text-slate-400">Monthly budget thresholds per spending category</p>
              </div>
              <button type="button" onclick="openCategoryLimitsModal()" class="px-3 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:hover:bg-indigo-900/60 text-xs font-semibold text-indigo-600 dark:text-indigo-400 transition-all flex items-center gap-1.5 shadow-sm active:scale-95">
                <i data-lucide="sliders-horizontal" class="w-3.5 h-3.5"></i>
                <span>Configure Limits</span>
              </button>
            </div>

            <div id="analytics-category-limits" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <!-- Dynamically populated category limit bars -->
            </div>
          </div>
        </section>

        <!-- ========================================== -->
        <!-- VIEW 6: SETTINGS & BACKUP -->
        <!-- ========================================== -->
        <section id="view-settings" class="space-y-6 view-section hidden">
          <!-- Header -->
          <div>
            <h2 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Settings & Vault Storage</h2>
            <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Manage currencies, preferences, categories, and offline backups.</p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Global Preferences Card -->
            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
              <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <i data-lucide="sliders" class="w-4 h-4 text-indigo-500"></i> General Preferences
              </h3>

              <div class="space-y-4 text-xs">
                <!-- User Name -->
                <div>
                  <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Account / Statement Name</label>
                  <input type="text" id="setting-user-name" onchange="saveUserName(this.value)" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
                  <p class="text-[11px] text-slate-400 mt-1">Appears on exported PDF financial statements and dashboard header.</p>
                </div>

                <!-- Primary Base Currency -->
                <div>
                  <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Primary Base Currency</label>
                  <select id="setting-base-currency" onchange="changeBaseCurrency(this.value)" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
                    <option value="USD">USD - US Dollar ($)</option>
                    <option value="EUR">EUR - Euro (€)</option>
                    <option value="GBP">GBP - British Pound (£)</option>
                    <option value="INR">INR - Indian Rupee (₹)</option>
                    <option value="BDT">BDT - Bangladeshi Taka (৳)</option>
                    <option value="CAD">CAD - Canadian Dollar ($)</option>
                    <option value="AUD">AUD - Australian Dollar ($)</option>
                    <option value="JPY">JPY - Japanese Yen (¥)</option>
                  </select>
                  <p class="text-[11px] text-slate-400 mt-1">All metrics, charts, and limits automatically convert to this currency.</p>
                </div>

                <!-- Monthly Overall Budget Limit -->
                <div>
                  <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Monthly Spending Target / Cap</label>
                  <div class="relative">
                    <span id="setting-currency-symbol" class="absolute left-3 top-2.5 text-slate-400 font-bold">$</span>
                    <input type="number" id="setting-budget-limit" onchange="saveMonthlyBudget(this.value)" min="0" step="10" class="w-full pl-8 pr-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 font-mono">
                  </div>
                </div>
              </div>
            </div>

            <!-- Custom Categories Manager (With Delete Support) -->
            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    <i data-lucide="tag" class="w-4 h-4 text-emerald-500"></i> Spending Categories
                  </h3>
                  <p class="text-[11px] text-slate-400 mt-0.5">Manage and remove custom spending categories</p>
                </div>
                <button onclick="openAddCategoryModal()" class="text-xs font-semibold text-indigo-500 hover:text-indigo-600">+ Add Category</button>
              </div>

              <div id="settings-categories-list" class="space-y-2 max-h-56 overflow-y-auto pr-1">
                <!-- Dynamically populated categories with delete buttons -->
              </div>
            </div>
          </div>

          <!-- Data Backup, Export & Clear -->
          <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
            <h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <i data-lucide="database" class="w-4 h-4 text-indigo-500"></i> Local-First Vault Backup & Disaster Recovery
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">VaultFlow keeps 100% of your financial records inside your local device. Export JSON backups regularly to keep your assets safe or transfer between devices.</p>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              <!-- Export JSON -->
              <button onclick="exportVaultBackupJSON()" class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-indigo-500 bg-slate-50 dark:bg-slate-800/50 flex flex-col items-center text-center group transition-all">
                <i data-lucide="download" class="w-6 h-6 text-indigo-500 mb-2 group-hover:scale-110 transition-transform"></i>
                <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Backup JSON Vault</span>
                <span class="text-[11px] text-slate-400 mt-1">Download complete snapshot</span>
              </button>

              <!-- Import JSON -->
              <label class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-emerald-500 bg-slate-50 dark:bg-slate-800/50 flex flex-col items-center text-center group transition-all cursor-pointer">
                <input type="file" id="import-json-file" onchange="importVaultBackupJSON(event)" accept=".json" class="hidden">
                <i data-lucide="upload" class="w-6 h-6 text-emerald-500 mb-2 group-hover:scale-110 transition-transform"></i>
                <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Restore From Backup</span>
                <span class="text-[11px] text-slate-400 mt-1">Select valid .json file</span>
              </label>

              <!-- Reset / Clear -->
              <button onclick="openDoubleConfirmResetModal()" class="p-4 rounded-xl border border-rose-200 dark:border-rose-900/40 hover:border-rose-500 bg-rose-50/50 dark:bg-rose-950/20 flex flex-col items-center text-center group transition-all">
                <i data-lucide="trash-2" class="w-6 h-6 text-rose-500 mb-2 group-hover:scale-110 transition-transform"></i>
                <span class="text-xs font-bold text-rose-600 dark:text-rose-400">Wipe All Vault Data</span>
                <span class="text-[11px] text-slate-400 mt-1">Irreversible wipe</span>
              </button>
            </div>
          </div>
        </section>

      </main>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: ADD / EDIT TRANSACTION -->
  <!-- ========================================== -->
  <div id="modal-transaction" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="w-full max-w-lg bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
        <h3 id="modal-tx-title" class="font-bold text-base text-slate-900 dark:text-slate-100">Log Transaction</h3>
        <button onclick="closeTransactionModal()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <form id="form-transaction" onsubmit="handleTransactionSubmit(event)" class="space-y-4 mt-4 text-xs">
        <input type="hidden" id="tx-id">

        <!-- Type Selector -->
        <div class="grid grid-cols-2 gap-2 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
          <button type="button" onclick="setTxType('expense')" id="btn-type-expense" class="py-2 rounded-lg font-bold text-white bg-rose-600 shadow-sm transition-all flex items-center justify-center gap-1.5">
            <i data-lucide="arrow-up-right" class="w-4 h-4"></i> Expense
          </button>
          <button type="button" onclick="setTxType('income')" id="btn-type-income" class="py-2 rounded-lg font-bold text-slate-600 dark:text-slate-400 hover:text-emerald-500 transition-all flex items-center justify-center gap-1.5">
            <i data-lucide="arrow-down-left" class="w-4 h-4"></i> Income
          </button>
        </div>

        <!-- Amount & Currency Multi-currency Engine -->
        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-2">
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Amount *</label>
            <div class="relative">
              <input type="number" id="tx-amount" step="0.01" min="0.01" required placeholder="0.00" class="w-full pl-3 pr-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-bold font-mono focus:ring-2 focus:ring-indigo-500">
            </div>
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Currency</label>
            <select id="tx-currency" onchange="handleTxCurrencyChange()" class="w-full py-2.5 px-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold focus:ring-2 focus:ring-indigo-500">
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="INR">INR (₹)</option>
              <option value="BDT">BDT (৳)</option>
              <option value="CAD">CAD ($)</option>
              <option value="AUD">AUD ($)</option>
              <option value="JPY">JPY (¥)</option>
            </select>
          </div>
        </div>

        <!-- Exchange Rate conversion notice -->
        <div id="tx-exchange-rate-box" class="p-3 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/50 hidden">
          <div class="flex items-center justify-between text-[11px] text-indigo-700 dark:text-indigo-300 mb-1">
            <span class="font-semibold">Foreign Exchange Rate:</span>
            <span id="tx-exchange-converted-preview" class="font-mono font-bold">$0.00 base</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[11px] text-slate-500">1 <span id="tx-foreign-label">EUR</span> = </span>
            <input type="number" id="tx-exchange-rate" step="0.0001" min="0.00001" oninput="updateConvertedPreview()" class="w-24 px-2 py-1 text-xs rounded border border-indigo-200 dark:border-indigo-800 bg-white dark:bg-slate-900 font-mono">
            <span id="tx-base-label" class="text-[11px] text-slate-500">USD</span>
          </div>
        </div>

        <!-- Category & Date -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Category *</label>
            <select id="tx-category" required class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
              <!-- Populated dynamically -->
            </select>
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Date *</label>
            <input type="date" id="tx-date" required class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
          </div>
        </div>

        <!-- Payment Method & Merchant / Note -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Payment Method</label>
            <select id="tx-payment-method" class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
              <option value="Credit Card">Credit Card</option>
              <option value="Debit Card">Debit Card</option>
              <option value="Bank Transfer">Bank Transfer</option>
              <option value="Cash">Cash</option>
              <option value="Mobile Wallet / UPI">Mobile Wallet / UPI</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Note / Merchant</label>
            <input type="text" id="tx-note" placeholder="e.g., Whole Foods groceries" class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
          </div>
        </div>

        <!-- Receipt Image Attachment with Client-Side Canvas Compression -->
        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Receipt Image (Drag & Drop or Tap)</label>
          <div id="receipt-drop-zone" class="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-indigo-500 dark:hover:border-indigo-500 rounded-2xl p-4 text-center cursor-pointer transition-all bg-slate-50/50 dark:bg-slate-850/50 relative">
            <input type="file" id="tx-receipt-input" accept="image/*" onchange="handleReceiptFileSelect(event)" class="absolute inset-0 opacity-0 cursor-pointer w-full h-full">
            <div id="receipt-upload-prompt" class="space-y-1">
              <i data-lucide="camera" class="w-6 h-6 text-slate-400 mx-auto"></i>
              <p class="text-xs font-medium text-slate-600 dark:text-slate-300">Upload receipt image (Auto-compressed to &lt;800px)</p>
              <p class="text-[10px] text-slate-400">PNG, JPG, WebP supported</p>
            </div>
            <!-- Receipt Thumbnail Preview -->
            <div id="receipt-preview-container" class="hidden flex items-center justify-between p-2 rounded-xl bg-slate-100 dark:bg-slate-800">
              <div class="flex items-center gap-2">
                <img id="receipt-preview-img" src="" alt="Receipt" class="w-12 h-12 object-cover rounded-lg border border-slate-200 dark:border-slate-700">
                <div class="text-left">
                  <span class="text-xs font-semibold text-slate-700 dark:text-slate-200 block truncate max-w-[180px]">Receipt attached</span>
                  <span id="receipt-preview-size" class="text-[10px] text-slate-400 font-mono">Compressed</span>
                </div>
              </div>
              <button type="button" onclick="removeReceiptAttachment(event)" class="p-1 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/50">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
          <button type="button" onclick="closeTransactionModal()" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold">Cancel</button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow-sm transition-all">Save Transaction</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: ADD / EDIT LOAN -->
  <!-- ========================================== -->
  <div id="modal-loan" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
        <h3 id="modal-loan-title" class="font-bold text-base text-slate-900 dark:text-slate-100">Add Loan / Debt</h3>
        <button onclick="closeLoanModal()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <form id="form-loan" onsubmit="handleLoanSubmit(event)" class="space-y-4 mt-4 text-xs">
        <input type="hidden" id="loan-id">

        <!-- Loan Category: I Owe vs Owed To Me -->
        <div class="grid grid-cols-2 gap-2 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
          <button type="button" onclick="setLoanDirection('owe')" id="btn-loan-owe" class="py-2 rounded-lg font-bold text-white bg-rose-600 shadow-sm transition-all flex items-center justify-center gap-1.5">
            <i data-lucide="arrow-up-right" class="w-4 h-4"></i> I Owe (Debt)
          </button>
          <button type="button" onclick="setLoanDirection('lent')" id="btn-loan-lent" class="py-2 rounded-lg font-bold text-slate-600 dark:text-slate-400 hover:text-emerald-500 transition-all flex items-center justify-center gap-1.5">
            <i data-lucide="arrow-down-left" class="w-4 h-4"></i> Owed to Me (Lent)
          </button>
        </div>

        <!-- Contact Name -->
        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Contact / Person Name *</label>
          <input type="text" id="loan-contact" required placeholder="e.g., Alex Johnson or Bank ABC" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
        </div>

        <!-- Amount & Currency -->
        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-2">
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Principal Amount *</label>
            <input type="number" id="loan-amount" step="0.01" min="0.01" required placeholder="0.00" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono font-bold focus:ring-2 focus:ring-indigo-500">
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Currency</label>
            <select id="loan-currency" class="w-full py-2 px-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold focus:ring-2 focus:ring-indigo-500">
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="INR">INR (₹)</option>
              <option value="BDT">BDT (৳)</option>
              <option value="CAD">CAD ($)</option>
              <option value="AUD">AUD ($)</option>
              <option value="JPY">JPY (¥)</option>
            </select>
          </div>
        </div>

        <!-- Interest Rate & Due Date -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Interest Rate % (Optional)</label>
            <input type="number" id="loan-interest" step="0.1" min="0" placeholder="0" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 font-mono">
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Due Date *</label>
            <input type="date" id="loan-due-date" required class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
          </div>
        </div>

        <!-- Note -->
        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Terms / Notes</label>
          <textarea id="loan-note" rows="2" placeholder="e.g. Split hotel deposit, interest free, payback by next payday" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500"></textarea>
        </div>

        <!-- Submit Button -->
        <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
          <button type="button" onclick="closeLoanModal()" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold">Cancel</button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow-sm transition-all">Save Loan</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: RECORD LOAN REPAYMENT -->
  <!-- ========================================== -->
  <div id="modal-repayment" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
        <div>
          <h3 class="font-bold text-base text-slate-900 dark:text-slate-100">Record Repayment</h3>
          <p id="repay-contact-name" class="text-xs text-indigo-500 font-semibold">Contact: Alex</p>
        </div>
        <button onclick="closeRepaymentModal()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <!-- Balance Status -->
      <div class="my-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex justify-between items-center text-xs">
        <div>
          <span class="text-slate-400 block">Remaining Balance:</span>
          <span id="repay-remaining-amount" class="text-lg font-bold font-mono text-slate-900 dark:text-white">$0.00</span>
        </div>
        <div class="text-right">
          <span class="text-slate-400 block">Original Loan:</span>
          <span id="repay-original-amount" class="font-mono text-slate-600 dark:text-slate-300 font-semibold">$0.00</span>
        </div>
      </div>

      <form id="form-repayment" onsubmit="handleRepaymentSubmit(event)" class="space-y-4 text-xs">
        <input type="hidden" id="repay-loan-id">

        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Repayment Amount *</label>
          <input type="number" id="repay-amount" step="0.01" min="0.01" required placeholder="0.00" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono font-bold focus:ring-2 focus:ring-indigo-500">
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Date Paid *</label>
            <input type="date" id="repay-date" required class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Payment Channel</label>
            <select id="repay-method" class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
              <option value="Bank Transfer">Bank Transfer</option>
              <option value="Cash">Cash</option>
              <option value="Mobile Wallet / UPI">Mobile Wallet / UPI</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Note / Reference</label>
          <input type="text" id="repay-note" placeholder="e.g., Wire transfer confirmation #8921" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
        </div>

        <!-- Submit Button -->
        <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
          <button type="button" onclick="closeRepaymentModal()" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold">Cancel</button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold shadow-sm transition-all">Record Payment</button>
        </div>
      </form>

      <!-- Repayment History Logs -->
      <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
        <h4 class="font-bold text-xs text-slate-700 dark:text-slate-300 mb-2">Repayment History Log</h4>
        <div id="repay-history-list" class="space-y-2 max-h-36 overflow-y-auto text-xs">
          <!-- Populated dynamically -->
        </div>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: ADD / EDIT RECURRING RULE -->
  <!-- ========================================== -->
  <div id="modal-recurring" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
        <h3 id="modal-rec-title" class="font-bold text-base text-slate-900 dark:text-slate-100">Add Recurring Schedule</h3>
        <button onclick="closeRecurringModal()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <form id="form-recurring" onsubmit="handleRecurringSubmit(event)" class="space-y-4 mt-4 text-xs">
        <input type="hidden" id="rec-id">

        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Schedule Name / Subscription *</label>
          <input type="text" id="rec-name" required placeholder="e.g., Netflix, Office Rent, Gym" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Type *</label>
            <select id="rec-type" class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Category *</label>
            <select id="rec-category" required class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
              <!-- Populated dynamically -->
            </select>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-2">
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Amount *</label>
            <input type="number" id="rec-amount" step="0.01" min="0.01" required placeholder="0.00" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono font-bold focus:ring-2 focus:ring-indigo-500">
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Currency</label>
            <select id="rec-currency" class="w-full py-2 px-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold focus:ring-2 focus:ring-indigo-500">
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="INR">INR (₹)</option>
              <option value="BDT">BDT (৳)</option>
              <option value="CAD">CAD ($)</option>
              <option value="AUD">AUD ($)</option>
              <option value="JPY">JPY (¥)</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Frequency *</label>
            <select id="rec-frequency" class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly" selected>Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">First / Next Due Date *</label>
            <input type="date" id="rec-next-date" required class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
          </div>
        </div>

        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Payment Method</label>
          <select id="rec-payment-method" class="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs focus:ring-2 focus:ring-indigo-500">
            <option value="Credit Card">Credit Card</option>
            <option value="Debit Card">Debit Card</option>
            <option value="Bank Transfer">Bank Transfer</option>
            <option value="Mobile Wallet / UPI">Mobile Wallet / UPI</option>
            <option value="Cash">Cash</option>
          </select>
        </div>

        <!-- Submit Button -->
        <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
          <button type="button" onclick="closeRecurringModal()" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold">Cancel</button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow-sm transition-all">Save Rule</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: RECEIPT LIGHTBOX PREVIEW -->
  <!-- ========================================== -->
  <div id="modal-receipt-lightbox" class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md hidden flex items-center justify-center p-4">
    <div class="max-w-2xl w-full bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative max-h-[90vh] flex flex-col">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <div>
          <h3 class="font-bold text-sm text-slate-900 dark:text-slate-100">Receipt Attachment</h3>
          <p id="lightbox-tx-info" class="text-xs text-slate-400">Transaction Details</p>
        </div>
        <div class="flex items-center gap-2">
          <a id="lightbox-download-link" href="#" download="vaultflow_receipt.jpg" class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Download Image">
            <i data-lucide="download" class="w-4 h-4"></i>
          </a>
          <button onclick="closeReceiptLightbox()" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
      </div>
      <div class="flex-1 overflow-auto flex items-center justify-center py-4 bg-slate-100 dark:bg-slate-950 rounded-2xl my-3">
        <img id="lightbox-img" src="" alt="Receipt Large Preview" class="max-w-full max-h-[60vh] object-contain rounded-lg shadow-md">
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: CUSTOMIZE WIDGETS -->
  <!-- ========================================== -->
  <div id="modal-customize-widgets" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="w-full max-w-sm bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <h3 class="font-bold text-base text-slate-900 dark:text-slate-100">Dashboard Layout & Widgets</h3>
        <button onclick="closeCustomizeWidgetsModal()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>
      <div class="py-4 space-y-3 text-xs">
        <p class="text-slate-400">Toggle dashboard widgets to suit your personal tracking workflow:</p>
        <label class="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800 cursor-pointer">
          <span class="font-medium text-slate-700 dark:text-slate-200">Quick Actions Bar</span>
          <input type="checkbox" id="toggle-widget-quick-actions" onchange="toggleWidgetVisibility('quickActions', this.checked)" checked class="w-4 h-4 rounded text-indigo-600">
        </label>
        <label class="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800 cursor-pointer">
          <span class="font-medium text-slate-700 dark:text-slate-200">Key Metrics Cards</span>
          <input type="checkbox" id="toggle-widget-metrics" onchange="toggleWidgetVisibility('metrics', this.checked)" checked class="w-4 h-4 rounded text-indigo-600">
        </label>
        <label class="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800 cursor-pointer">
          <span class="font-medium text-slate-700 dark:text-slate-200">Monthly Budget Health</span>
          <input type="checkbox" id="toggle-widget-budget" onchange="toggleWidgetVisibility('budget', this.checked)" checked class="w-4 h-4 rounded text-indigo-600">
        </label>
        <label class="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800 cursor-pointer">
          <span class="font-medium text-slate-700 dark:text-slate-200">Upcoming Bills (7 Days)</span>
          <input type="checkbox" id="toggle-widget-bills" onchange="toggleWidgetVisibility('bills', this.checked)" checked class="w-4 h-4 rounded text-indigo-600">
        </label>
        <label class="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800 cursor-pointer">
          <span class="font-medium text-slate-700 dark:text-slate-200">7-Day Trajectory Chart</span>
          <input type="checkbox" id="toggle-widget-charts" onchange="toggleWidgetVisibility('charts', this.checked)" checked class="w-4 h-4 rounded text-indigo-600">
        </label>
        <label class="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800 cursor-pointer">
          <span class="font-medium text-slate-700 dark:text-slate-200">Recent Activity Feed</span>
          <input type="checkbox" id="toggle-widget-recent" onchange="toggleWidgetVisibility('recent', this.checked)" checked class="w-4 h-4 rounded text-indigo-600">
        </label>
      </div>
      <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end">
        <button onclick="closeCustomizeWidgetsModal()" class="px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold">Done</button>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: ADD CUSTOM CATEGORY -->
  <!-- ========================================== -->
  <div id="modal-add-category" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="w-full max-w-sm bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <h3 class="font-bold text-base text-slate-900 dark:text-slate-100">Add Category</h3>
        <button onclick="closeAddCategoryModal()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>
      <form id="form-category" onsubmit="handleAddCategorySubmit(event)" class="space-y-4 py-4 text-xs">
        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Category Name *</label>
          <input type="text" id="cat-name" required placeholder="e.g., Pet Care, Gadgets" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500">
        </div>
        <div>
          <label class="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Badge Color</label>
          <input type="color" id="cat-color" value="#6366f1" class="w-full h-10 p-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 cursor-pointer">
        </div>
        <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
          <button type="button" onclick="closeAddCategoryModal()" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-semibold">Cancel</button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold">Save Category</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: CONFIGURE CATEGORY LIMITS -->
  <!-- ========================================== -->
  <div id="modal-category-limits" onclick="if(event.target === this) closeCategoryLimitsModal()" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
            <i data-lucide="sliders-horizontal" class="w-4 h-4"></i>
          </div>
          <div>
            <h3 class="font-bold text-base text-slate-900 dark:text-slate-100">Category Spending Limits</h3>
            <p class="text-xs text-slate-400">Set monthly spending threshold per category</p>
          </div>
        </div>
        <button type="button" onclick="closeCategoryLimitsModal()" class="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <form id="form-category-limits" onsubmit="handleSaveCategoryLimits(event)" class="space-y-3.5 my-4 text-xs">
        <p class="text-[11px] text-slate-500 dark:text-slate-400">Leave blank or set to 0 for unlimited spending in that category.</p>
        
        <div id="category-limits-inputs" class="space-y-3 max-h-64 overflow-y-auto pr-1">
          <!-- Dynamically populated category inputs -->
        </div>

        <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
          <button type="button" onclick="closeCategoryLimitsModal()" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-semibold">Cancel</button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow-sm transition-all">Save Limits</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: DOUBLE CONFIRM DATA RESET -->
  <!-- ========================================== -->
  <div id="modal-reset-confirm" class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="w-full max-w-sm bg-white dark:bg-slate-900 rounded-3xl border border-rose-200 dark:border-rose-900/60 shadow-2xl p-6 relative text-center">
      <div class="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-950 text-rose-600 flex items-center justify-center mx-auto mb-3">
        <i data-lucide="alert-octagon" class="w-6 h-6"></i>
      </div>
      <h3 class="font-bold text-base text-slate-900 dark:text-slate-100">Permanently Wipe Vault?</h3>
      <p class="text-xs text-slate-500 dark:text-slate-400 mt-2">This will erase all recorded transactions, receipt images, loans, and recurring schedules from this device. This action cannot be reversed.</p>
      
      <div class="mt-4">
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Type <strong class="text-rose-600">DELETE</strong> to confirm:</label>
        <input type="text" id="reset-confirm-input" placeholder="DELETE" class="w-full text-center px-3 py-2 rounded-xl border border-rose-300 dark:border-rose-800 bg-rose-50/50 dark:bg-rose-950/30 text-xs font-mono font-bold uppercase focus:ring-2 focus:ring-rose-500">
      </div>

      <div class="mt-6 flex justify-end gap-2">
        <button onclick="closeDoubleConfirmResetModal()" class="w-1/2 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-semibold text-xs">Cancel</button>
        <button onclick="executeVaultWipe()" class="w-1/2 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs shadow-sm transition-all">Erase All</button>
      </div>
    </div>
  </div>

  <!-- JavaScript Application Engine -->
  <script src="app.js"></script>
</body>
</html>
'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

print("Created updated index.html template with home button and mobile active states.")
