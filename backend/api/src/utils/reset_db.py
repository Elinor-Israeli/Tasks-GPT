import os
from models import init_db  # adjust if your init_db is elsewhere

db_path = "todo.db"

if os.path.exists(db_path):
    os.remove(db_path)
    print("Database deleted.")
else:
    print("No existing database found.")

# Recreate the schema
init_db()
print("Fresh database initialized.")
