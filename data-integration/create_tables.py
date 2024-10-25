import sqlite3
import argparse

# 0. Set up command-line arguments using argparse
parser = argparse.ArgumentParser(description="Create a new DB for a Patient Registry.")
parser.add_argument('db_file_location', type=str, help="Path to the SQlite DB file containing contact and patient data.")
args = parser.parse_args()
db_file = args.db_file_location

# 1. Create a connection to the SQLite database (it will create a file if it doesn’t exist)
conn = sqlite3.connect(db_file)

# 2. Create a cursor object to execute SQL commands
cursor = conn.cursor()

# 3. Drop existing tables to start fresh
cursor.execute("DROP TABLE IF EXISTS Link_Table")
cursor.execute("DROP TABLE IF EXISTS Contacts")
cursor.execute("DROP TABLE IF EXISTS Patients")

# 4. Define and execute SQL statements to create the tables
# Create Contacts Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Contacts (
    parent_name TEXT,
    email TEXT UNIQUE,
    resides_in_spain BOOLEAN,
    country TEXT,
    creation_date TEXT,
    region_id TEXT,
    contact_uuid TEXT PRIMARY KEY
)
''')

# Create Patients Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Patients (
    rett_name TEXT,
    rett_surname TEXT,
    date_of_birth TEXT,
    gender TEXT,
    diagnosis_type TEXT,
    creation_date TEXT,
    age INTEGER,
    age_group TEXT,
    region_id TEXT,
    persona_rett_uuid TEXT PRIMARY KEY
)
''')

# Create Link Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Link_Table (
    relationship_uuid TEXT PRIMARY KEY,
    relationship TEXT,
    contact_uuid TEXT,
    persona_rett_uuid TEXT,
    FOREIGN KEY (contact_uuid) REFERENCES Contacts (contact_uuid),
    FOREIGN KEY (persona_rett_uuid) REFERENCES Patients (persona_rett_uuid)
)
''')

# 5. Commit the changes and close the connection
conn.commit()
conn.close()

print("Database schema reset successfully.")