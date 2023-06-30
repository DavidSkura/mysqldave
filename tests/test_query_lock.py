"""
  Dave Skura
"""
import os
import readchar
from mysqldave_package.mysqldave import mysql_db 

print('sample program\n')

mydb = mysql_db()
mydb.connect()
print(mydb.dbversion())

mydb.execute('LOCK TABLE world.city WRITE;')

qry = """
SELECT *
FROM  world.city;

"""
print(mydb.export_query_to_str(qry,'\t'))
print('Waiting...')
rnk_nbr = readchar.readchar()
mydb.execute('UNLOCK TABLES;')


mydb.close()	


