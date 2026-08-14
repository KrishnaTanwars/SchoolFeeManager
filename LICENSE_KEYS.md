# EduLedger ERP — Authorized Production License Keys

Below is the list of authorized production license keys pre-configured in the Windows Installer Setup (`SchoolFeeERP_Setup_v2.4.0.exe` / `installer.iss`).

---

## 🔑 Pre-Authorized Production Keys

| Key # | Authorized License Key | Purpose |
| :---: | :--------------------- | :------ |
| **1** | `EDU-ABCD-1234-EFGH-5678` | Client License Key 1 |
| **2** | `ERP-2026-EDUL-EDGER-2026` | Client License Key 2 |
| **3** | `EDU-2026-8888-9999-7777` | Client License Key 3 |
| **4** | `ERP-2026-PROD-KEYS-9999` | Client License Key 4 |
| **5** | `EDU-PROD-2026-MAIN-KEY1` | Client License Key 5 |

---

## ⚙️ License Key Validation Rules

In addition to the pre-authorized keys above, any custom key that satisfies the algorithmic validation rules will also pass installation verification:

1. **Prefix**: Must start with `EDU-` or `ERP-`.
2. **Length**: Minimum length of 19 characters (e.g. `EDU-XXXX-XXXX-XXXX-XXXX`).
3. **Algorithmic Rule**: Either `(Sum mod 13 == 0)` or `(Hash mod 97 == 12)`.
