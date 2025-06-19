# Sonatype IQ Server Raw Report Fetcher

Welcome! This is a **step-by-step, beginner-friendly guide** for using the Sonatype IQ Server Raw Report Fetcher. If you are new to command-line tools, Python, or Sonatype IQ, don't worry—this documentation will walk you through everything, assuming no prior experience.

---

## 📦 What Does This Tool Do?

This tool connects to your Sonatype IQ Server, fetches security scan reports for all your applications, and saves them as CSV files. You can use these CSVs for analysis, compliance, or sharing with your team.

---

## 🚀 Getting Started: Step-by-Step

### 1. **Download the Program**

- Go to the [Releases](../../releases) page of this project.
- Download the latest version for your operating system (Windows, macOS, or Linux).
- Extract the downloaded file (if it is a ZIP or TAR file). You should see a file named `ctbc-raw-report-fetch` (or `ctbc-raw-report-fetch.exe` on Windows).

### 2. **Configure Your Settings**

- Go to the `config` folder in the project directory.
- Copy the file named `.env.example` and rename the copy to `.env`.
- Open `.env` in a text editor (like Notepad, VS Code, or TextEdit).
- Fill in your actual Sonatype IQ Server details:

  ```
  IQ_SERVER_URL=http://your-iq-server:8070
  IQ_USERNAME=your_username
  IQ_PASSWORD=your_password
  ORGANIZATION_ID=your_organization_id   # (optional)
  OUTPUT_DIR=raw_reports                 # (optional)
  ```

  - **IQ_SERVER_URL**: The web address of your Sonatype IQ Server (ask your admin if unsure).
  - **IQ_USERNAME**: Your login username for the IQ Server.
  - **IQ_PASSWORD**: Your password for the IQ Server.
  - **ORGANIZATION_ID**: (Optional) If you want to fetch reports for a specific organization only.
  - **OUTPUT_DIR**: (Optional) Where CSV files will be saved. Default is `raw_reports`.

> **Tip:** If you don't know your organization ID, leave it blank to fetch all applications you have access to.

### 3. **Run the Tool**

- **On macOS/Linux:**
  1. Open the Terminal app.
  2. Navigate to the folder where you extracted the program (e.g., `cd ~/Downloads/ctbc-raw-report-fetch`).
  3. Run:
     ```sh
     ./ctbc-raw-report-fetch
     ```
- **On Windows:**

  1. Open Command Prompt (cmd.exe).
  2. Navigate to the folder (e.g., `cd C:\Users\YourName\Downloads\ctbc-raw-report-fetch`).
  3. Run:
     ```sh
     ctbc-raw-report-fetch.exe
     ```

- The tool will connect to your IQ Server, fetch reports, and save CSV files in the `raw_reports` folder (or the folder you set in `.env`).

---

## 📝 How Configuration Works

You can set configuration in two ways:

1. **Edit the `config/.env` file** (recommended for most users).
2. **Set environment variables** in your shell or system (for advanced users or automation).

**Required settings:**

- `IQ_SERVER_URL` (the address of your IQ Server)
- `IQ_USERNAME` (your username)
- `IQ_PASSWORD` (your password)

**Optional settings:**

- `ORGANIZATION_ID` (limit to one org)
- `OUTPUT_DIR` (where CSVs are saved)

**Example `.env` file:**

```
IQ_SERVER_URL=https://your-iq-server.com
IQ_USERNAME=your-username
IQ_PASSWORD=your-password
OUTPUT_DIR=raw_reports
```

---

## 🛠️ Customizing the Tool (For Advanced Users)

### 1. **Filter Which Applications Are Fetched**

You can change which applications are included by editing the `get_applications()` method in `iq_fetcher/fetcher.py`.

**Example: Only fetch apps with 'prod' in the name:**

```python
apps = self.iq.get_applications(self.config.organization_id)
filtered = [app for app in apps if "prod" in app.name.lower()]
return filtered
```

### 2. **Change What Data Goes Into the CSV**

Edit the consolidation logic in `iq_fetcher/fetcher.py` to add or remove fields in the CSV output.

**Example: Add a custom field:**

```python
consolidated_row = {
    "No.": len(consolidated_data) + 1,
    "Application": app_id,
    "Organization": org_id,
    # Add custom fields here
}
```

### 3. **Change the CSV File Name**

Edit the `_save_as_csv()` method in `iq_fetcher/fetcher.py`.

**Example:**

```python
filename = f"{public_id}_{report_id}.csv"
filepath = self.output_path / filename
```

### 4. **Add Progress Bars**

To see a progress bar as the tool runs, install the `tqdm` package and wrap your loop:

```python
from tqdm import tqdm
for app in tqdm(apps, desc="Processing apps"):
    self._fetch_app_report(app, ...)
```

---

## 🧑‍💻 For Developers: Running from Source

If you want to run or modify the tool as Python source code:

1. **Install dependencies:**
   - If you use [uv](https://github.com/astral-sh/uv):
     ```sh
     uv sync
     ```
   - Or with pip:
     ```sh
     pip install -r requirements.txt
     ```
2. **Copy and edit the `.env` file** as above.
3. **Run the tool:**
   ```sh
   python -m iq_fetcher.cli
   ```

---

## 🔄 Updating or Debugging

- **Update dependencies:**
  - Edit `pyproject.toml` and run `uv sync`, or update `requirements.txt` and run `pip install -r requirements.txt`.
- **Debugging:**
  - Set logging to DEBUG in `iq_fetcher/utils.py` for more output.
  - Use print statements or breakpoints as needed.
- **Add new features:**
  - Add config options in `Config` (`iq_fetcher/config.py`).
  - Add new API calls in `IQServerClient` (`iq_fetcher/client.py`).
  - Add new output formats in `RawReportFetcher` (`iq_fetcher/fetcher.py`).

---

## 🏗️ Building an Executable (For Distribution)

1. **Install PyInstaller:**
   - With uv: `uv add pyinstaller`
   - Or with pip: `pip install pyinstaller`
2. **Build the executable:**
   ```sh
   pyinstaller --onefile iq_fetcher/cli.py
   ```
   - The output will be in the `dist/` folder.

---

## 🤝 Contributing

- Fork the repo, create a branch, make your changes, and submit a pull request.
- Please follow [PEP 8](https://peps.python.org/pep-0008/) style, use type hints, and add docstrings to your code.

---

## 📁 Project Structure (What’s in Each Folder?)

```
CTBC_raw_report_fetch/
├── iq_fetcher/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line entry point
│   ├── config.py            # Configuration management
│   ├── client.py            # IQ Server API client
│   ├── fetcher.py           # Core report fetching logic
│   └── utils.py             # Utilities, logging, error handling
├── config/
│   ├── .env.example         # Configuration template
│   └── .env                 # Your configuration (not in git)
├── pyproject.toml           # Project dependencies (uv)
├── uv.lock                  # Locked dependencies
├── README.md                # This file
└── scripts/
    └── build_macos.sh       # Build script for macOS
```

---

## ❓ Frequently Asked Questions (FAQ)

**Q: I get a 'Permission denied' error when running the executable.**

- On macOS/Linux, you may need to make the file executable:
  ```sh
  chmod +x ctbc-raw-report-fetch
  ```

**Q: The tool says it can't connect to the server.**

- Double-check your `IQ_SERVER_URL`, username, and password in `.env`.
- Make sure your computer can reach the IQ Server (try opening the URL in a browser).

**Q: Where are my CSV files?**

- By default, they are in the `raw_reports` folder in the same directory as the program. You can change this in `.env`.

**Q: How do I get my Organization ID?**

- Ask your Sonatype IQ Server administrator, or leave it blank to fetch all applications you have access to.

**Q: Can I run this on a schedule?**

- Yes! Use a cron job (Linux/macOS) or Task Scheduler (Windows) to run the executable automatically.

---

## 🆘 Need Help?

- If you get stuck, open an issue on GitHub or ask your IT/security team for help.
- For Sonatype IQ Server documentation, see [Sonatype Docs](https://help.sonatype.com/iqserver).

---

**Enjoy automated, reliable report fetching!**
