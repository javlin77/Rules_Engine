# Quick Start Guide

## Prerequisites Check

1. **PostgreSQL** must be running on `localhost:5433`
2. **Python 3.10+** installed
3. **Node.js 18+** installed

## Step-by-Step Setup

### 1. Database Setup

**Easiest Method (Recommended):** Use the Python script:
```bash
cd backend
python create_database.py
```

This will automatically create the database using your `.env` settings.

**Alternative Methods:**

**Option A: Using psql command line**
```bash
psql -U postgres -h localhost -p 5433 -c "CREATE DATABASE rules_engine;"
```

**Option B: Using pgAdmin (GUI)**
1. Open pgAdmin
2. Connect to your PostgreSQL server (localhost:5433)
3. Right-click on "Databases" → "Create" → "Database"
4. Name: `rules_engine`
5. Click "Save"

**Option C: Using SQL directly**
1. Connect to PostgreSQL (any method)
2. Run: `CREATE DATABASE rules_engine;`

### 2. Backend Setup

```bash
cd backend

# Activate virtual environment (if exists)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the example below or create manually
```

Create `backend/.env`:
```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5433
DB_NAME=rules_engine
```

### 3. Create Database (if not done in step 1)

```bash
python create_database.py
```

### 4. Initialize Database Tables

```bash
python init_db.py --seed
```

This creates tables and adds sample rules.

### 5. Test Connection

```bash
python test_connection.py
```

### 6. Start Backend Server

```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

Backend will be at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 7. Frontend Setup

In a new terminal:

```bash
# From project root
npm install
npm run dev
```

Frontend will be at: http://localhost:5173

## Verify Everything Works

1. Open http://localhost:5173
2. You should see the Rules Engine UI
3. Click "Create Rule" to add a new rule
4. Use "Quick Test" button to evaluate a sample event
5. Check "Audit Logs" tab to see evaluation history

## Example: Create Your First Rule

1. Click "Create Rule"
2. Use this example:

**Name:** `High Value Purchase Alert`

**Conditions:**
```json
{
  "type": "AND",
  "clauses": [
    { "field": "event.amount", "op": ">=", "value": 5000 }
  ]
}
```

**Actions:**
```json
[
  { "type": "alert", "payload": { "message": "High value purchase detected" } }
]
```

**Tags:** `alert, high-value`

3. Click "Create Rule"
4. Test it with "Quick Test" button

## Troubleshooting

### Database Connection Failed

- Check PostgreSQL is running: `pg_isready -h localhost -p 5433`
- Verify credentials in `backend/.env`
- Ensure database exists: `psql -U postgres -h localhost -p 5433 -l`

### Backend Won't Start

- Check Python version: `python --version` (should be 3.10+)
- Verify dependencies: `pip list | grep fastapi`
- Check port 8000 is available

### Frontend Won't Start

- Check Node version: `node --version` (should be 18+)
- Clear cache: `rm -rf node_modules package-lock.json && npm install`
- Check port 5173 is available

### Kafka Errors

Kafka is optional! The system works without it. If you see Kafka errors, you can ignore them or set up Kafka separately.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Check out example rules in the database after running `init_db.py --seed`

