# Beekeeper Studio Database Connection Guide

This guide explains how to connect **Beekeeper Studio** to both your **Local PostgreSQL** database and your **Supabase Cloud PostgreSQL** database so you can view, edit, and query both.

---

## 1. Connecting to Local PostgreSQL

In **Beekeeper Studio**, click **New Connection** and fill in the following parameters:

* **Connection Type**: `PostgreSQL`
* **Host**: `localhost` (or `127.0.0.1`)
* **Port**: `5432`
* **User**: `postgres`
* **Password**: *(Enter the password you set during PostgreSQL installation)*
* **Database Name**: `curato` (or `postgres` if you haven't created `curato` yet)
* **SSL Mode**: `disable` (or `prefer`)

> **Note**: To create the `curato` database locally if it doesn't exist, open query editor in Beekeeper Studio or psql and run:
> ```sql
> CREATE DATABASE curato;
> ```

---

## 2. Connecting to Supabase Cloud PostgreSQL

In **Beekeeper Studio**, click **New Connection** and fill in the following parameters:

* **Connection Type**: `PostgreSQL`
* **Host**: `aws-0-ap-northeast-1.pooler.supabase.com`
* **Port**: `5432`
* **User**: `postgres.zidqwhtdifuuotrirdmp`
* **Password**: `ciRiTIwcMSIqme1B`
* **Database Name**: `postgres`
* **SSL Mode**: `require`

---

## 3. Syncing Data from Supabase to Local PostgreSQL

We have created an automated database clone script in the backend repository. Whenever you want to sync all tables and records from Supabase into your local PostgreSQL database, run:

```bash
cd curato/backend
python scripts/sync_databases.py
```

### Environment Variables (`.env`)
Ensure your `curato/.env` file contains both database URLs:
```env
SUPABASE_DATABASE_URL=postgresql+psycopg://postgres.zidqwhtdifuuotrirdmp:ciRiTIwcMSIqme1B@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
LOCAL_DATABASE_URL=postgresql+psycopg://postgres:YOUR_LOCAL_PASSWORD@localhost:5432/curato
DATABASE_URL=postgresql+psycopg://postgres.zidqwhtdifuuotrirdmp:ciRiTIwcMSIqme1B@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```
*(Replace `YOUR_LOCAL_PASSWORD` with your actual local Postgres password).*
