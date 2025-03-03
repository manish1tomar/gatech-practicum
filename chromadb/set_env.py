import pyodbc
SERVER = 'fcssqldb.database.windows.net'
DATABASE = 'FCSDB'
USERNAME = 'raman'
PASSWORD = 'ManRam@2025'
conn_str = 'DRIVER={SQL Server};SERVER=fcssqldb.database.windows.net;DATABASE=FCSDB;UID=raman;PWD=ManRam@2025'

'''
print(pyodbc.drivers())
conn = pyodbc.connect(conn_str)
print("Connected to SQL Server successfully!")
cursor = conn.cursor()
cursor.execute(f"select Subject, CreditsNeeded, EarnedCredit from [dbo].[Student_Credits] where StudentID in ( 248630 ) order by StudentID asc, CreditsNeeded desc, Subject;")
rows = str(cursor.fetchall())
columns = [column[0] for column in cursor.description]

header = "\t".join(columns)
result_string = header + "\n" + "\n".join("\t".join(str(value) for value in row) for row in rows)
print(result_string)

cursor.close()
conn.close()
'''