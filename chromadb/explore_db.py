import sqlite3

con = sqlite3.connect('./onepal_chroma_db/onepal_chroma_db.db')
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
cursor.close()
con.close()