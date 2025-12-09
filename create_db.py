import csv
import os
import sqlite3

db_dir = 'db'

# Create the db directory if it doesn't exist
os.makedirs(db_dir, exist_ok=True)

# Connect to SQLite database inside db directory
db_path = os.path.join(db_dir, 'soil_pollution.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print(f"Database created at: {db_path}")

# Read CSV file
csv_file = 'inputs/soil_pollution_diseases.csv'
with open(csv_file, 'r') as f:
    reader = csv.reader(f)
    
    # Get headers from first row
    headers = next(reader)
    
    # Create table with columns from CSV headers
    columns = ', '.join([f'"{header}" TEXT' for header in headers])
    cursor.execute(f'CREATE TABLE IF NOT EXISTS soil_pollution_diseases ({columns})')
    
    # Insert data
    placeholders = ', '.join(['?' for _ in headers])
    insert_query = f'INSERT INTO soil_pollution_diseases VALUES ({placeholders})'
    
    row_count = 0
    for row in reader:
        cursor.execute(insert_query, row)
        row_count += 1
    
    conn.commit()
    print(f"Imported {row_count} rows successfully!")

# Verify the import
cursor.execute('SELECT * FROM soil_pollution_diseases LIMIT 5')
print("\nFirst 5 rows:")
for row in cursor.fetchall():
    print(row)

conn.close()