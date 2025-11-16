# Rules Engine System

A production-ready Rules Engine built with Python (FastAPI), PostgreSQL, Kafka, and React. This system allows you to define, manage, and evaluate business rules dynamically.

## Features

- ✅ **Rule Management**: Create, update, version, and manage business rules
- ✅ **Advanced Condition Evaluation**: Support for multiple operators (==, !=, >, <, >=, <=, in, contains, regex, etc.)
- ✅ **Rule Versioning**: Track all rule changes with version history
- ✅ **Audit Logging**: Complete audit trail of all rule evaluations
- ✅ **Explainability**: Detailed explanations of why rules matched or didn't match
- ✅ **Kafka Integration**: Async event processing for high-throughput scenarios
- ✅ **RESTful API**: Comprehensive API for rule management and evaluation
- ✅ **Modern UI**: React + Vite frontend with Tailwind CSS

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React UI  │────▶│  FastAPI     │────▶│ PostgreSQL  │
│   (Vite)    │     │  Backend     │     │  (Port 5433)│
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            │
                            ▼
                    ┌──────────────┐
                    │    Kafka     │
                    │  (Optional)  │
                    └──────────────┘
```

## Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database (port 5433)
- **Kafka** - Event streaming (optional)
- **Redis** - Caching (optional)

### Frontend
- **React 19**
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Setup Instructions

### Prerequisites

1. **PostgreSQL** running on `localhost:5433`
2. **Python 3.10+**
3. **Node.js 18+**
4. **Kafka** (optional, for async processing)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (if not exists):
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the `backend` directory:
```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5433
DB_NAME=rules_engine

# Optional: Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_EVENTS_TOPIC=rule-events
```

6. Create the database:
```sql
CREATE DATABASE rules_engine;
```

7. Run the backend:
```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The UI will be available at `http://localhost:5173`

## API Endpoints

### Rule Management

- `GET /rules` - List all rules (with optional filters: `?active=true&tag=discount`)
- `GET /rules/{rule_id}` - Get a specific rule
- `POST /rules` - Create a new rule
- `PUT /rules/{rule_id}` - Update a rule (creates new version)
- `DELETE /rules/{rule_id}` - Delete a rule
- `GET /rules/{rule_id}/versions` - Get version history

### Evaluation

- `POST /evaluate` - Evaluate all active rules against an event
- `POST /rules/{rule_id}/simulate` - Simulate a single rule

### Audit & Monitoring

- `GET /audit` - Get audit logs (filters: `?event_id=...&rule_id=...&limit=100`)
- `GET /health` - Health check endpoint

## Example Usage

### Creating a Rule

```bash
curl -X POST http://localhost:8000/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "10% off for premium users",
    "priority": 100,
    "conditions": {
      "type": "AND",
      "clauses": [
        {"field": "context.user.tier", "op": "==", "value": "premium"},
        {"field": "event.cart.total", "op": ">=", "value": 1000}
      ]
    },
    "actions": [
      {"type": "apply_discount", "payload": {"percent": 10}}
    ],
    "tags": ["discount", "promo"]
  }'
```

### Evaluating an Event

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "event": {
      "type": "purchase",
      "cart": {"total": 1200},
      "user_id": "u_1"
    },
    "context": {
      "user": {
        "tier": "premium",
        "signup_date": "2024-02-01"
      }
    }
  }'
```

## Condition Operators

The engine supports the following operators:

- `==` - Equals
- `!=` - Not equals
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `in` - Value in list
- `not_in` - Value not in list
- `contains` - String/list contains value
- `regex` - Regular expression match
- `starts_with` - String starts with value
- `ends_with` - String ends with value

## Logical Operators

- `AND` - All clauses must be true
- `OR` - At least one clause must be true
- `NOT` - Negate the result

## Functions

- `days_since(date_field)` - Calculate days since a date

## Project Structure

```
rules_engine/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   ├── evaluator.py      # Condition evaluation engine
│   ├── kafka_client.py   # Kafka integration
│   └── requirements.txt  # Python dependencies
├── src/
│   ├── App.jsx           # Main React component
│   └── components/
│       ├── CreateRuleModal.jsx
│       └── SimulateModal.jsx
├── package.json          # Node.js dependencies
└── README.md
```

## Development

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
npm test
```

### Database Migrations

The system uses SQLAlchemy's `create_all()` for table creation. For production, consider using Alembic for migrations.

## Performance Considerations

- Rules are evaluated in priority order (highest first)
- Use `stop_on_match` to short-circuit evaluation
- Kafka integration allows async processing for high-throughput scenarios
- Consider Redis caching for frequently accessed rules

## Security Notes

- In production, restrict CORS origins
- Implement authentication/authorization
- Sanitize rule inputs to prevent injection
- Mask PII in audit logs

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a PR.
