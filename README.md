# Sonatype IQ Server Raw Report Fetcher

A tool to fetch raw scan reports from all applications in Sonatype IQ Server and export them as CSV files.

---

## 🚀 Quick Start

1. **Download the Executable**

   - Go to the [Releases](../../releases) page
   - Download and extract the latest release for your OS

2. **Configure Settings**

   - Copy `config/.env.example` to `config/.env`
   - Edit `config/.env` with your IQ Server URL, username, and password

3. **Run the Tool**
   - On macOS/Linux: `./ctbc-raw-report-fetch`
   - On Windows: `ctbc-raw-report-fetch.exe`

CSV reports will be saved in the `raw_reports` folder (or as set in `.env`).

---

## ⚙️ Configuration

Edit `config/.env` or set environment variables:

- `IQ_SERVER_URL` (required)
- `IQ_USERNAME` (required)
- `IQ_PASSWORD` (required)
- `ORGANIZATION_ID` (optional)
- `OUTPUT_DIR` (optional, default: `raw_reports`)

Example `.env`:

```
IQ_SERVER_URL=https://your-iq-server.com
IQ_USERNAME=your-username
IQ_PASSWORD=your-password
OUTPUT_DIR=raw_reports
```

---

## 🛠️ Customization

### Filter Applications

Edit `get_applications()` in `main.py` to filter by name, ID, or pattern:

```python
# ...existing code...
apps = self.iq.get_applications(self.config.organization_id)
filtered = [app for app in apps if "prod" in app.name.lower()]
return filtered
# ...existing code...
```

### Change CSV Output

Edit `_save_csv_manual()` in `main.py` to add/remove fields:

```python
# ...existing code...
row = {
    "Package URL": c.get("packageUrl", ""),
    "Display Name": c.get("displayName", ""),
    # Add custom fields here
}
# ...existing code...
```

### Custom File Naming

Edit `_save_as_csv()` in `main.py`:

```python
# ...existing code...
filename = f"{public_id}_{report_id}.csv"
filepath = self.output_path / filename
# ...existing code...
```

### Add Progress Bars

Install `tqdm` and wrap your loop:

```python
from tqdm import tqdm
for app in tqdm(apps, desc="Processing apps"):
    self._fetch_app_report(app, ...)
```

---

## 🧑‍💻 Development & Maintenance

### Install & Run from Source

1. `pip install -r requirements.txt`
2. Copy and edit `config/.env.example` to `config/.env`
3. `python main.py`

### Update Dependencies

- Edit `requirements.txt` and run `pip install -r requirements.txt`

### Debugging

- Set logging to DEBUG in `main.py` for more output
- Use print statements or breakpoints as needed

### Add Features

- Add config options in `Config` (main.py)
- Add new API calls in `IQServerClient`
- Add new output formats in `RawReportFetcher`

### Build Executable

- Install PyInstaller: `pip install pyinstaller`
- Build: `pyinstaller --onefile main.py`
- Output is in `dist/`

---

## 🤝 Contributing

- Fork the repo, create a branch, make changes, and submit a pull request.
- Follow PEP 8, use type hints, and add docstrings.

---

## 📁 Project Structure

```
CTBC_raw_report_fetch/
├── main.py              # Main logic
├── error_handler.py     # Error handling
├── requirements.txt     # Dependencies
├── README.md            # This file
├── config/.env.example  # Config template
└── ...
```

---

For more details, see comments in `main.py` and `error_handler.py`.
