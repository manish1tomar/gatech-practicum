import pyodbc, os, set_env

# Define connection parameters
db_server = set_env.db_server
database = set_env.database
db_username = set_env.db_username
db_password = set_env.db_password
db_driver = set_env.db_driver

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={db_server};"
    f"DATABASE={database};"
    f"UID={db_username};"
    f"PWD={db_password};"
    #"TrustServerCertificate=yes;"  # Use this if encryption issues might occur
)

# Establish connection
try:
    conn = pyodbc.connect( conn_str )
    print("Connected to SQL Server successfully!")

    # Create a cursor object
    cursor = conn.cursor()

    # Example query
    cursor.execute("SELECT name, database_id, create_date FROM sys.databases;")

    # Fetch and print results
    for row in cursor.fetchall():
        print(row)

    # Close connection
    cursor.close()
    conn.close()

except Exception as e:
    print("Error connecting to SQL Server:", e)
