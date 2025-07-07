# SQL Server to S3 CSV Exporter

Export SQL Server data to CSV and upload directly to AWS S3 with a simple Python script.

## Overview

A lightweight Python tool that connects to Microsoft SQL Server, exports your table or query results as a CSV file, and uploads it to your chosen S3 bucket. Perfect for quick backups, data migration, or automation tasks.

## Features

- Connects to SQL Server (MSSQL)
- Supports custom SQL queries or full table exports
- Uploads CSV directly to AWS S3
- Simple configuration

## Requirements

- Python 3.7+
- `pyodbc`
- `pandas`
- `boto3`

Install all requirements with:

```bash
pip install -r requirements.txt
