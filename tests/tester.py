"""
  Dave Skura
"""
import os

from mysqldave_package.mysqldave import mysql_db 

print('sample program\n')

mydb = mysql_db()
mydb.connect()
print(mydb.dbversion())
print(' - - - - - - - - - - - - - - - - - - - - - - - - - - -  \n')
print('table_count = ' + str(mydb.queryone('SELECT COUNT(*) as table_count FROM INFORMATION_SCHEMA.TABLES')))
print(' - - - - - - - - - - - - - - - - - - - - - - - - - - -  \n')

qry = """
		SELECT table_schema as databasename, COUNT(*) as table_count 
		FROM INFORMATION_SCHEMA.tables 
		GROUP BY table_schema
"""
print(mydb.export_query_to_str(qry,'\t'))


mydb.close()	


