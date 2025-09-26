# Database Setup Guide

## Issue: PostgreSQL Authentication

The error `FATAL: Peer authentication failed for user "pgvector_admin"` indicates PostgreSQL authentication issues.

## Quick Fix

1. **Test your database connection first**:
   ```bash
   python test_db_connection.py
   ```

2. **If connection fails, try these solutions**:

### Option 1: Use Password Authentication
Edit PostgreSQL configuration to allow password authentication:

```bash
# Find pg_hba.conf location
sudo -u postgres psql -c "SHOW hba_file;"

# Edit the file (Ubuntu/Debian example)
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

Change this line:
```
local   all             all                                     peer
```

To:
```
local   all             all                                     md5
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Option 2: Create Database User with Proper Permissions

```bash
# Connect as postgres superuser
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE USER your_db_user WITH PASSWORD 'your_password';
ALTER USER your_db_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
\q
```

### Option 3: Use Environment Variables for Connection

Set these in your `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_NAME=rag_database
```

## Manual Database Setup

If automated setup fails, run these commands manually:

```bash
# 1. Create database
createdb -h localhost -U your_user rag_database

# 2. Connect and create extension
psql -h localhost -U your_user -d rag_database

# 3. In psql prompt:
CREATE EXTENSION IF NOT EXISTS vector;

# 4. Run the initialization script
\i database/init_db.sql

# 5. Exit
\q
```

## Verify Setup

```bash
# Test connection
python test_db_connection.py

# If successful, run the main application
python agno_rag_agent.py
```

## Common Issues

1. **PostgreSQL not running**: `sudo systemctl start postgresql`
2. **pgvector not installed**: `sudo apt install postgresql-15-pgvector`
3. **Wrong credentials**: Check your `.env` file
4. **Database doesn't exist**: Create it manually as shown above