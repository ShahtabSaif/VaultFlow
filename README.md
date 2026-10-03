<div align="center">

<img src="app/src/main/assets/ic_vault_minimal.png" alt="VaultFlow logo" width="120" />

# VaultFlow

**Local-first personal finance, expense & loan tracker for Android.**

Track income and expenses, manage loans and debts, automate recurring bills, and export clean reports, all stored privately on your own device.

[![Download APK](https://img.shields.io/badge/⬇%20Download%20VaultFlow-APK-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/ShahtabSaif/VaultFlow/releases/latest)
 
![Platform](https://img.shields.io/badge/platform-Android-3DDC84?logo=android&logoColor=white)
![Min SDK](https://img.shields.io/badge/minSdk-24-blue)
![Storage](https://img.shields.io/badge/data-100%25%20on--device-6366f1)
 
</div>

---

## 📥 Download
 
<div align="center">
[![Download APK](https://img.shields.io/badge/Download-Latest%20APK-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/ShahtabSaif/VaultFlow/releases/latest)
 
Button not loading? Use this link: **https://github.com/ShahtabSaif/VaultFlow/releases/latest**
 
</div>
1. Tap the button above to open the **latest release**.
2. Under **Assets**, download the `.apk` file.
3. Open the downloaded file on your Android phone. If prompted, allow **Install unknown apps** for your browser or file manager.
4. Launch **VaultFlow** and follow the [first-time setup](#important-first-time-setup) below.
> Requires **Android 7.0 (API 24)** or higher. Looking for older versions? See all [releases](https://github.com/ShahtabSaif/VaultFlow/releases).
 
---

## ⚠️ Important: First-time setup

> **VaultFlow ships with sample demo data (sample transactions, loans and recurring bills) so you can explore the app right away.**
>
> **Before you start using it for real, you must wipe all vault data from Settings on first use:**
>
> 1. Open the app and go to **Settings**.
> 2. Tap **Wipe All Vault Data** (*Irreversible wipe*).
> 3. Type `DELETE` in the confirmation box.
> 4. Tap **Erase All**.
>
> This clears all demo transactions, receipt images, loans and recurring schedules so you start with a clean vault. Your preferences (name, base currency, budget limits, theme) are kept. **This action cannot be undone**, so if you have real data, back it up first with **Backup JSON Vault**.

---

## ✨ Features

- **📊 Dashboard**: Real-time overview of income, expenses, balance and outstanding debt, with customizable widgets you can show or hide.
- **💸 Transactions**: Log income and expenses with category, payment method, date and notes. Search and filter your history.
- **🧾 Receipt attachments**: Attach receipt photos to transactions. Images are compressed automatically to save space.
- **🤝 Loans & Debts**: Keep separate records of money you owe and money you've lent, with repayment tracking.
- **🔁 Recurring bills & income**: Set up recurring rules that are processed automatically when due (or on demand), and pause or resume them any time.
- **🎯 Budgets**: Set a monthly spending cap and per-category limits, and watch your progress on the dashboard.
- **🏷️ Custom categories**: Use the defaults or add and remove your own spending categories.
- **🌍 Multi-currency**: USD, EUR, GBP, INR, BDT (৳), CAD, AUD and JPY. Pick a base currency and everything converts automatically.
- **📈 Analytics**: Weekly bar chart, spending trend line and category doughnut chart (Chart.js).
- **📄 PDF statements**: Generate a printable financial statement with your name on it.
- **📤 Export & backup**: Export transactions to **CSV**, download a full **JSON vault backup**, and restore from a backup file.
- **🌗 Dark / light theme**: Dark by default, switch any time.
- **📱 Android home-screen widget**: See your vault at a glance and tap **+ Log** to quick-add an expense.
- **🔒 Private by design**: No account, no server. Your data lives on your device (IndexedDB with a localStorage fallback).

---

## 🏗️ How it works

VaultFlow is an Android app that wraps a self-contained web UI inside a native `WebView`:

- **Native layer (Kotlin)**: `MainActivity` hosts the WebView, handles file picking for receipts, saves exports to the device's Downloads folder, manages the Android back button, and powers the home-screen widget (`VaultFlowWidgetProvider`).
- **App layer (HTML/JS)**: `app/src/main/assets/index.html` contains the entire interface and logic (Tailwind CSS, Chart.js, jsPDF).

> **Note:** The UI loads Tailwind CSS, Chart.js and jsPDF from public CDNs, so an internet connection is needed the first time the app loads those libraries. Your financial data itself is never sent anywhere.

---

## 🚀 Getting started

### Prerequisites

- [Android Studio](https://developer.android.com/studio) (latest stable)
- JDK 11 or newer
- An Android emulator or a physical device running **Android 7.0 (API 24)** or higher

### Run locally

1. Clone the repository:
   ```bash
   git clone https://github.com/ShahtabSaif/VaultFlow.git
   ```
2. Open Android Studio, choose **Open**, and select the `VaultFlow` folder.
3. Let Gradle sync finish (allow Android Studio to fix any incompatibilities when prompted).
4. If the build complains about a missing `debug.keystore`, create one (it's git-ignored on purpose):
   ```bash
   keytool -genkeypair -v -keystore debug.keystore -storepass android -alias androiddebugkey \
     -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
   ```
   Or switch the `debug` build type to the default debug signing config in `app/build.gradle.kts`.
5. Press **Run ▶** on an emulator or device.
6. **On first launch, wipe the demo data from Settings** (see [First-time setup](#️-important-first-time-setup)).


---

## 🗂️ Project structure

```
VaultFlow/
├── app/
│   └── src/main/
│       ├── java/com/example/        # MainActivity, home-screen widget, Compose theme
│       ├── assets/index.html        # The complete single-file web UI used by the app
│       └── res/                     # Icons, widget layout, themes, backup rules
├── index.html                       # Single-file build of the UI (same as the assets copy)
├── app.js                           # Source JavaScript for the UI
├── build_vaultflow.py               # Generator script for the single-file UI
├── assemble_single_file.py          # Inlines app.js + icon into index.html and copies it to assets
├── gradle/                          # Version catalog & wrapper
└── .env.example                     # Optional environment config template
```

### Editing the UI

If you change `app.js` or `index.html`, regenerate the single-file build so the Android app picks it up:

```bash
python assemble_single_file.py
```

This inlines the script and logo into `index.html` and writes the result to both the project root and `app/src/main/assets/`.

---

## 💾 Your data & backups

- All data is stored **locally on your device**. There is no cloud sync.
- Use **Settings → Backup JSON Vault** regularly to download a full snapshot.
- Use **Settings → Restore From Backup** to load a `.json` backup (for example after reinstalling or switching phones).
- Uninstalling the app removes its local data, so keep a backup file somewhere safe.

---

## 🛠️ Tech stack

| Layer | Technology |
| --- | --- |
| Platform | Android (Kotlin, `minSdk 24`, `targetSdk 36`) |
| UI | HTML, JavaScript, Tailwind CSS in a WebView |
| Charts | Chart.js 4 |
| PDF export | jsPDF + jsPDF-AutoTable |
| Storage | IndexedDB (localStorage fallback) |
| Build | Gradle (Kotlin DSL) |

---

## 🤝 Contributing

Issues and pull requests are welcome. If you spot a bug or have a feature idea, please [open an issue](https://github.com/ShahtabSaif/VaultFlow/issues).

---

## 👤 Author

Made by **[ShahtabSaif](https://github.com/ShahtabSaif)**.
