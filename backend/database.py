import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Default to PostgreSQL on localhost:5433 if DATABASE_URL not set
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Default PostgreSQL connection for port 5433
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "rules_engine")
    
    # URL-encode password to handle special characters
    encoded_password = quote_plus(str(db_password))
    encoded_user = quote_plus(str(db_user))
    
    DATABASE_URL = f"postgresql://{encoded_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
