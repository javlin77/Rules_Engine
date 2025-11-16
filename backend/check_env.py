"""
Quick script to check .env file configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Environment Variables Check")
print("=" * 50)

db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "NOT SET")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5433")
db_name = os.getenv("DB_NAME", "rules_engine")
database_url = os.getenv("DATABASE_URL", "NOT SET")

print(f"DB_USER: {db_user}")
print(f"DB_PASSWORD: {'*' * len(db_password) if db_password != 'NOT SET' else 'NOT SET'}")
print(f"DB_HOST: {db_host}")
print(f"DB_PORT: {db_port}")
print(f"DB_NAME: {db_name}")
print(f"DATABASE_URL: {'SET (using this)' if database_url != 'NOT SET' else 'NOT SET'}")

print("\n" + "=" * 50)
print("Connection String Preview:")
print("=" * 50)

if database_url != "NOT SET":
    # Hide password in preview
    if "@" in database_url:
        parts = database_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split("://")[1] if "://" in parts[0] else parts[0]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                print(f"postgresql://{user}:***@{parts[1]}")
            else:
                print(database_url.replace(db_password, "***"))
        else:
            print(database_url.replace(db_password, "***"))
    else:
        print(database_url)
else:
    from urllib.parse import quote_plus
    encoded_password = quote_plus(str(db_password))
    encoded_user = quote_plus(str(db_user))
    print(f"postgresql://{encoded_user}:***@{db_host}:{db_port}/{db_name}")

print("\n" + "=" * 50)
if db_password == "NOT SET" or db_password == "postgres":
    print("[!] WARNING: Using default password 'postgres'")
    print("    Make sure this matches your PostgreSQL password!")
print("=" * 50)

