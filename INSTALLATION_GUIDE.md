# Installation & Setup Guide - College Fee Management System v1.0

## System Requirements

- **Operating System**: Microsoft Windows 10 or Windows 11 (64-bit Edition)
- **Processor**: Intel Core i3 / AMD Ryzen 3 or higher
- **RAM**: Minimum 4 GB (8 GB Recommended)
- **Disk Space**: 500 MB free space
- **Display Resolution**: 1366x768 or higher (High DPI / 4K Displays supported)
- **Printer**: Any standard Windows-compatible printer (LaserJet, InkJet, Thermal, or PDF virtual printer)

---

## 1. Quick Installation Steps

1. Extract the client release ZIP file `CollegeFeeManager_v1.0.zip` to your target directory (e.g., `C:\CollegeFeeManager` or `D:\Software\CollegeFeeManager`).
2. Navigate to the extracted `CollegeFeeManager` folder.
3. Double-click **`CollegeFeeManager.exe`** to launch the software.

*(Optional)* Right-click **`CollegeFeeManager.exe`** -> Select **Send to -> Desktop (create shortcut)** for instant access.

---

## 2. Initial Setup & Default Login Credentials

On first startup, the application automatically initializes the SQLite database and seeds default administrative user accounts:

| User Role | Default Username | Default Password | Recommended Usage |
|---|---|---|---|
| **System Administrator** | `admin` | `admin123` | Full access to settings, user management, and database restores. |
| **Fee Collection Operator** | `operator` | `operator123` | Fee collection, student registration, and receipt searching. |

> [!IMPORTANT]
> Change the default administrator password immediately after first login via **Settings & Backup -> User Management**.

---

## 3. Database & Backup Directory Locations

The application creates and manages the following local directories automatically within its root folder:

- **`database/college_fee.db`**: Main SQLite relational database storing all student profiles, fee heads, and receipt ledgers.
- **`backup/`**: Automated timestamped ZIP backup directory created when running manual or automatic backups.
- **`exports/`**: Generated fee receipt PDFs and CSV reports exported from the application.
- **`logs/app.log`**: Application activity and error diagnostic log file.

---

## 4. Troubleshooting & FAQ

#### Q: The application fails to print fee receipts.
**A**: Ensure a default Windows printer is configured in **Windows Control Panel -> Devices and Printers**. The application routes receipts directly through the native Windows Shell printer driver.

#### Q: How do I move the software to a new computer?
**A**:
1. Run a database backup in **Settings & Backup -> Create Database Backup**.
2. Copy the generated `.zip` file from the `backup/` directory to the new computer.
3. Install `CollegeFeeManager.exe` on the new computer and use **Settings & Backup -> Restore Database** to load your data.
