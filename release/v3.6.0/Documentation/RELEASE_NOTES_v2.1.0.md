# Release Notes — EduLedger ERP v2.1.0

We are pleased to announce **EduLedger ERP Version v2.1.0**. This release introduces major UI layout improvements, sidebar ergonomics, pre-authentication security cleanup, status bar enhancements, and populated realistic demo data for immediate testing and production deployment.

---

## 🌟 Key Highlights in Version 2.1.0

### 💳 1. Fee Collection Table Layout & Amount Column Visibility
- **Fixed Column Width & Stretch Policy**: Column 3 ("Amount (₹)") in the Fee Particulars table now has a spacious minimum width of **165px**, while Column 1 ("Fee Head Description") stretches dynamically to consume remaining space.
- **Zero Text Clipping**: Amount fields displaying large figures (e.g., `₹ 1,25,000.00`) and spinbox controls fit with zero text clipping across all screen resolutions (`1366x768`, `1600x900`, `1920x1080`) and sidebar states.

### 📐 2. Sidebar Startup Auto-Collapse Behavior
- **Default Startup State**: The left navigation sidebar now **always starts in a clean collapsed state** on application launch.
- **Manual Toggle**: Users can expand or collapse the menu on demand by clicking the hamburger menu icon (`☰`).

### 🎨 3. Login Screen Pre-Authentication Cleanup
- **Search Widget Removal**: Removed the Global Search button (`Search everywhere... (Ctrl+K)`) from the login view to ensure search privileges are reserved strictly for authenticated users.
- **Centered Login Card**: Removed top header margin during login mode, perfectly centering the login card in the viewport without blank placeholders or layout shifts.

### 📌 4. Bottom Status Bar User Info Relocation
- **Status Bar Ergonomics**: Relocated active logged-in user information (`Logged in as: System Administrator (Admin)`) from the top header to the **bottom-right corner of the `QStatusBar`**.
- **Dynamic Updates**: Clears on logout and updates dynamically on login with full name and capitalized role in brackets.

### 📊 5. Realistic Demo Data Seeding
- **100 Realistic Students**: Populated 100 students across UG (B.Pharmacy FY/SY/TY/Final Year, B.Sc, B.Com) and PG (M.Pharmacy 1st/2nd Year, M.Sc, M.Com) with unique admission numbers (`ADM/2026/001`–`100`), roll numbers, Indian names, 10-digit mobile numbers, and addresses.
- **350 Receipts**: Populated 350 fee receipts spread over 90 days across all 6 payment modes (Cash, UPI, Card, Cheque, Demand Draft, Net Banking) with discounts, fines, and Indian number-to-words.

---

## 🧪 Quality Assurance & Acceptance Summary

- **QA Audit Score**: **98.2 / 100** (Passed Phase 11 Automated QA Audit).
- **Automated Unit Tests**: Executed `python -m unittest discover tests` — **ALL PASSED**.
- **Commercial Release Recommendation**: **APPROVED FOR PRODUCTION RELEASE** ✅

---

## 📦 Package Deliverables in `release/v2.1.0/`

- **Standalone Executable App**: `release/v2.1.0/CollegeFeeManager/CollegeFeeManager.exe`
- **Client Release Archive**: `release/v2.1.0/CollegeFeeManager_v2.1.0.zip`
- **Developer Source Archive**: `release/v2.1.0/CollegeFeeManager_Source_v2.1.0.zip`
