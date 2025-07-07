# SQL Server to S3 CSV Exporter

Export SQL Server data to CSV and upload directly to AWS S3 with a simple Python script.

---

## Overview

A lightweight Python tool to connect to Microsoft SQL Server, export your table or query results as a CSV file, and upload it to your chosen AWS S3 bucket. Perfect for fast backups, data migrations, and automation.

---

## Features

- Connects to SQL Server (MSSQL)
- Exports entire tables or custom query results
- Uploads CSV to AWS S3
- Simple configuration (see `.env.sample`)
- Progress bar and error tracking
- Optional: Email and Sentry notifications

---

## Requirements

- Python 3.7 or newer  
- See `requirements.txt` for dependencies (includes: pyodbc, pymssql, pandas, boto3, etc.)

---

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/aliabbas-2012/sqlserver-to-s3-csv.git
    cd sqlserver-to-s3-csv
    ```

2. **Create a Python virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv_sql_s3
    source venv_sql_s3/bin/activate   # On Windows: venv_sql_s3\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Set up configuration:**  
   Copy `.env.sample` to `.env` and edit with your environment-specific credentials/settings.

---

## Usage

Run the exporter:

```bash
python main.py
