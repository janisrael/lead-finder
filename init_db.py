import sqlite3

# Connect (or create if not exists)
conn = sqlite3.connect("places.db")
cursor = conn.cursor()

# Create a table (example schema — customize as needed)
cursor.execute("""
CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    phone TEXT,
    website TEXT,
    rating REAL,
    types TEXT,
    status TEXT
)
""")

# Save and close
conn.commit()
conn.close()

print("✅ Database and table created successfully.")
