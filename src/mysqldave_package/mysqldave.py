"""
  Dave Skura
  
  File Description: replaceo
"""
import os
import sys
import mysql.connector 
from datetime import *
import time
from garbledave_package.garbledave import garbledave 
import logging

logging.basicConfig(level=logging.ERROR)

def main():
	mydb = mysql_db('this connection')
	mydb.connect()
	print(mydb.dbstr())


	mydb.export_table_to_csv('this.tsv','information_schema.tables',',')

	#csvfilename = 'testcase1.csv'
	#tblname = 'testcase1'
	#mydb.load_csv_to_table(csvfilename,tblname,True,',')

	mydb.close()


class dbconnection_details: 
	def __init__(self,DSN):
		self.DSN = DSN

		self.DatabaseType='MySQL' 
		self.updated='Feb 28/2023' 

		self.settings_loaded_from_file = False

		self.DB_USERNAME='' 
		self.DB_USERPWD=''
		self.DB_HOST='' 
		self.DB_PORT='' 
		self.DB_NAME='' 
		self.loadSettingsFromFile()

	def loadSettingsFromFile(self):
		try:
			f = open('.schemawiz_config2','r')
			connectionfiledata = f.read()
			connectionstrlines = connectionfiledata.split('\n')
			f.close()
			found_dsn = False
			for connectionline in connectionstrlines:
				logging.info(connectionline)
				connectionstr = garbledave().ungarbleit(connectionline)
				connarr = connectionstr.split(' - ')
				if connarr[0] == self.DSN:
					logging.info('found DSN: ' + self.DSN)

					self.DB_USERNAME	= connarr[1]
					self.DB_USERPWD		= connarr[2]
					self.DB_HOST			= connarr[3] 
					self.DB_PORT			= connarr[4]
					self.DB_NAME			= connarr[5]
					found_dsn = True
					break;

			self.settings_loaded_from_file = True

		except:
			found_dsn = False

		if not found_dsn:
			#saved connection details not found. using defaults
			self.DB_USERNAME='no db user' 
			self.DB_HOST='localhost' 
			self.DB_PORT='3306' 
			self.DB_NAME='no-db-name-given' 
			self.DB_USERPWD='no-password-supplied'

	def dbconnectionstr(self):
		return 'dsn=' + self.DSN + '; usr=' + self.DB_USERNAME + '; svr=' + self.DB_HOST + '; port=' + self.DB_PORT + '; DB Name=' + self.DB_NAME 

	def saveConnectionDefaults(self,DB_USERNAME='unknown',DB_USERPWD='unknown',DB_HOST='unknown',DB_PORT='unknown',DB_NAME='unknown'):

		f = open('.schemawiz_config2','a')
		f.write(garbledave().garbleit(self.DSN + ' - ' + DB_USERNAME + ' - ' + DB_USERPWD + ' - ' + DB_HOST + ' - ' + DB_PORT + ' - ' + DB_NAME )+ '\n')
		f.close()

		self.loadSettingsFromFile()

class tfield:
	def __init__(self):
		self.table_name = ''
		self.column_name = ''
		self.data_type = ''
		self.Need_Quotes = ''
		self.ordinal_position = -1
		self.comment = '' # dateformat in csv [%Y/%m/%d]

class mysql_db:
	def __init__(self,DSN='default',DB_USERPWD='no-password-supplied',DB_SCHEMA='no-schema-supplied'):
		self.DSN = DSN.replace('_','')
		self.delimiter = ''
		self.delimiter_replace = '^~^'
		self.enable_logging = False
		self.max_loglines = 500
		self.db_conn_dets = dbconnection_details(self.DSN)
		self.dbconn = None
		self.cur = None

		if DB_USERPWD != 'no-password-supplied':
			self.db_conn_dets.DB_USERPWD = DB_USERPWD			#if you pass in a password it overwrites the stored pwd

		if DB_SCHEMA != 'no-schema-supplied':
			self.db_conn_dets.DB_SCHEMA = DB_SCHEMA			#if you pass in a schema it overwrites the stored schema

	def getbetween(self,srch_str,chr_strt,chr_end,srch_position=0):
		foundit = 0
		string_of_interest = ''
		for i in range(srch_position,len(srch_str)):
			if (srch_str[i] == chr_strt ):
				foundit += 1

			if (srch_str[i] == chr_end ):
				foundit -= 1
			if (len(string_of_interest) > 0 and (foundit == 0)):
				break
			if (foundit > 0):
				string_of_interest += srch_str[i]
			
		return string_of_interest[1:]

	def getfielddefs(self,dbname,tablename):
		tablefields = []
		sql = """
SELECT  column_name
    ,CAST(data_type as char(255)) as data_type
	,CASE 
        WHEN lower(data_type) in ('date','timestamp') THEN 'QUOTE'
        WHEN lower(data_type) in ('char','varchar','text','mediumtext','longtext') THEN 'QUOTE'
        WHEN lower(data_type) in ('blob','mediumblob','longblob','json') THEN 'QUOTE'
        ELSE
            'NO QUOTE'
    END as Need_Quotes    
    ,ordinal_position
    ,CAST(column_comment as char(255)) as column_comment

FROM INFORMATION_SCHEMA.COLUMNS isc
WHERE upper(table_schema) = upper('""" + dbname + """') and 
    upper(table_name) = upper('""" + tablename + """')
ORDER BY ordinal_position
		"""

		data = self.query(sql)
		for row in data:
			fld = tfield()
			fld.table_name = tablename
			fld.column_name = row[0]
			fld.data_type = row[1]
			fld.Need_Quotes = row[2]
			fld.ordinal_position = row[3]
			fld.comment = row[4]

			tablefields.append(fld)

		return tablefields

	def dbstr(self):
		return self.db_conn_dets.dbconnectionstr()

	def dbversion(self):
		return self.queryone('SELECT VERSION()')

	def clean_column_name(self,col_name):

		col = col_name.replace(' ','_')
		new_column_name = ''
		for i in range(0,len(col)):
			if 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'.find(col[i]) > -1:
				new_column_name += col[i]

		return new_column_name

	def clean_text(self,ptext): # remove optional double quotes
		text = ptext.replace(self.delimiter_replace,self.delimiter).strip()
		if (text[:1] == '"' and text[-1:] == '"'):
			return text[1:-1]
		else:
			return text

	def count_chars(self,data,exceptchars=''):
		chars_in_hdr = {}
		for i in range(0,len(data)):
			if data[i] != '\n' and exceptchars.find(data[i]) == -1:
				if data[i] in chars_in_hdr:
					chars_in_hdr[data[i]] += 1
				else:
					chars_in_hdr[data[i]] = 1
		return chars_in_hdr

	def count_alpha(self,alphadict):
		count = 0
		for ch in alphadict:
			if 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.find(ch) > -1:
				count += alphadict[ch]
		return count

	def count_nbr(self,alphadict):
		count = 0
		for ch in alphadict:
			if '0123456789'.find(ch) > -1:
				count += alphadict[ch]
		return count

	def logquery(self,logline,duration=0.0):
		if self.enable_logging:
			startat = (datetime.now())
			startdy = str(startat.year) + '-' + ('0' + str(startat.month))[-2:] + '-' + str(startat.day)
			starttm = str(startat.hour) + ':' + ('0' + str(startat.minute))[-2:] + ':' + ('0' + str(startat.second))[-2:]
			start_dtm = startdy + ' ' + starttm
			preline = start_dtm + '\nduration=' + str(duration) + '\n'

			log_contents=''
			try:
				f = open('.querylog','r')
				log_contents = f.read()
				f.close()
			except:
				pass

			logs = log_contents.splitlines()
			
			logs.insert(0,preline + logline + '\n ------------ ')
			f = open('.querylog','w+')
			numlines = 0
			for line in logs:
				numlines += 1
				f.write(line + '\n')
				if numlines > self.max_loglines:
					break

			f.close()

	def savepwd(self,pwd):
		self.db_conn_dets.savepwd(pwd)
		self.db_conn_dets.DB_USERPWD = pwd

	def saveConnectionDefaults(self,DB_USERNAME,DB_USERPWD,DB_HOST,DB_PORT,DB_NAME):
		self.db_conn_dets.saveConnectionDefaults(DB_USERNAME,DB_USERPWD,DB_HOST,DB_PORT,DB_NAME)

	def useConnectionDetails(self,DB_USERNAME,DB_USERPWD,DB_HOST,DB_PORT,DB_NAME):

		self.db_conn_dets.DB_USERNAME = DB_USERNAME
		self.db_conn_dets.DB_USERPWD = DB_USERPWD			
		self.db_conn_dets.DB_HOST = DB_HOST				
		self.db_conn_dets.DB_PORT = DB_PORT				
		self.db_conn_dets.DB_NAME = DB_NAME					
		self.db_conn_dets.DB_SCHEMA = ''
		self.connect()

	def is_an_int(self,prm):
			try:
				if int(prm) == int(prm):
					return True
				else:
					return False
			except:
					return False

	def export_query_to_str(self,qry,szdelimiter=','):
		self.execute(qry)
		f = ''
		sz = ''
		for k in [i[0] for i in self.cur.description]:
			sz += k + szdelimiter
		f += sz[:-1] + '\n'

		for row in self.cur:
			sz = ''
			for i in range(0,len(self.cur.description)):
				sz += str(row[i])+ szdelimiter

			f += sz[:-1] + '\n'

		return f

	def export_query_to_csv(self,qry,csv_filename,szdelimiter=','):
		self.execute(qry)
		f = open(csv_filename,'w')
		sz = ''
		for k in [i[0] for i in self.cur.description]:
			sz += k + szdelimiter
		f.write(sz[:-1] + '\n')

		for row in self.cur:
			sz = ''
			for i in range(0,len(self.cur.description)):
				sz += str(row[i])+ szdelimiter

			f.write(sz[:-1] + '\n')
				

	def export_table_to_csv(self,csvfile,tblname,szdelimiter=','):
		if not self.does_table_exist(tblname):
			raise Exception('Table does not exist.  Create table first')

		self.export_query_to_csv('SELECT * FROM ' + tblname,csvfile,szdelimiter)


	def handledblquotes(self,rowwithquotes):
		newstr = ''
		quotecount = 0
		cvtmode = False
		for i in range (0,len(rowwithquotes)):
			if rowwithquotes[i] == '"':
				quotecount += 1
			
			if (quotecount % 2) == 1:
				cvtmode = True 
			else:
				cvtmode = False

			if cvtmode and rowwithquotes[i] == self.delimiter:
				newstr += self.delimiter_replace
			elif rowwithquotes[i] != '"':
				newstr += rowwithquotes[i]
			
		return newstr


	def load_csv_to_table(self,csvfile,tblname,withtruncate=True,szdelimiter=',',fields='',withextrafields={}):
		self.delimiter = szdelimiter
		table_fields = self.getfielddefs(self.db_conn_dets.DB_NAME,tblname)

		if not self.does_table_exist(tblname):
			raise Exception('Table does not exist.  Create table first')


		if withtruncate:
			self.execute('TRUNCATE TABLE ' + tblname)


		f = open(csvfile,'r')
		hdrs = f.read(1000).split('\n')[0].strip().split(szdelimiter)
		f.close()		

		isqlhdr = 'INSERT INTO ' + tblname + '('

		if fields != '':
			isqlhdr += fields	+ ') VALUES '	
		else:
			for i in range(0,len(hdrs)):
				isqlhdr += self.clean_column_name(hdrs[i]) + ','
			isqlhdr = isqlhdr[:-1] + ') VALUES '

		skiprow1 = 0
		batchcount = 0
		ilines = ''

		with open(csvfile) as myfile:
			for line in myfile:
				if line.strip()!='':
					if skiprow1 == 0:
						skiprow1 = 1
					else:
						batchcount += 1
						unquotedline = self.handledblquotes(line.rstrip("\n"))
						row = unquotedline.split(szdelimiter)
						newline = "("
						for var in withextrafields:
							newline += "'" + withextrafields[var]  + "',"

						for j in range(0,len(row)):
							#print(table_fields[j].data_type.strip().lower())
							#print(table_fields[j].comment)
							#print(self.getbetween(table_fields[j].comment,'[',']'))

							if row[j].lower() == 'none' or row[j].lower() == 'null':
								newline += "NULL,"
							else:
								if table_fields[j].data_type.strip().lower() == 'date':
									dt_fmt = self.getbetween(table_fields[j].comment,'[',']')
									if dt_fmt.strip() != '':
										newline += "str_to_date('" + self.clean_text(row[j]) + "','" + dt_fmt + "'),"
									else:
										newline += "'" + self.clean_text(row[j]) + "',"

								elif table_fields[j].data_type.strip().lower() == 'timestamp':
									dt_fmt = self.getbetween(table_fields[j].comment,'[',']')
									if dt_fmt.strip() != '':
										newline += "str_to_date('" + self.clean_text(row[j]) + "','" + dt_fmt + "'),"
									else:
										newline += "'" + self.clean_text(row[j]) + "',"

								elif table_fields[j].Need_Quotes == 'QUOTE':
									newline += "'" + self.clean_text(row[j]).replace("'",'').replace('"','') + "',"
								else:
									val = self.clean_text(row[j]).replace("'",'').replace('"','')
									if val == '':
										newline += "NULL,"
									else:
										newline += val + ","

							
						ilines += newline[:-1] + '),'
						
						if batchcount > 500:
							qry = isqlhdr + ilines[:-1]
							#print(qry)
							#sys.exit(0)
							batchcount = 0
							ilines = ''
							self.execute(qry)

		if batchcount > 0:
			qry = isqlhdr + ilines[:-1]
			batchcount = 0
			ilines = ''
			self.execute(qry)

	def does_table_exist(self,tblname):
		self.connect()

		if tblname.find('.') > -1:
			this_schema = tblname.split('.')[0]
			this_tbl = tblname.split('.')[1]
		else:
			this_schema = self.db_conn_dets.DB_NAME
			this_tbl = tblname

		sql = """
SELECT count(*)  
FROM information_schema.tables
WHERE upper(table_schema) = upper('""" + this_schema + """') and upper(table_name)=upper('""" + this_tbl + """')
		"""
		if self.queryone(sql) == 0:
			return False
		else:
			return True


	def close(self):
		if self.dbconn.is_connected():
			self.dbconn.close()

	def ask_for_database_details(self):
		print('Asking about DSN: ' +  self.DSN)
		self.db_conn_dets.DB_HOST = input('DB_HOST (localhost): ') or 'localhost'
		self.db_conn_dets.DB_PORT = input('DB_PORT (3306): ') or '3306'
		self.db_conn_dets.DB_NAME = input('DB_NAME (): ') or ''
		self.db_conn_dets.DB_USERNAME = input('DB_USERNAME (dave): ') or 'dave'
		self.db_conn_dets.DB_USERPWD = input('DB_USERPWD: ') or '4165605869'

	def connect(self):
		connects_entered = False

		if self.db_conn_dets.DB_USERPWD == 'no-password-supplied':
			self.ask_for_database_details()
			connects_entered = True

		try:
			self.dbconn = mysql.connector.connect(
					host=self.db_conn_dets.DB_HOST,
					user=self.db_conn_dets.DB_USERNAME,
					passwd=self.db_conn_dets.DB_USERPWD,
					database=self.db_conn_dets.DB_NAME,
					autocommit=True
			)
			self.cur = self.dbconn.cursor()

			if connects_entered:
				user_response_to_save = input('Save this connection locally? (y/n) :')
				# only if successful connect after user prompted and got Y do we save pwd
				if user_response_to_save.upper()[:1] == 'Y':
					self.saveConnectionDefaults(self.db_conn_dets.DB_USERNAME,self.db_conn_dets.DB_USERPWD,self.db_conn_dets.DB_HOST,self.db_conn_dets.DB_PORT,self.db_conn_dets.DB_NAME)

		except Exception as e:
			if self.db_conn_dets.settings_loaded_from_file:
				os.remove('.schemawiz_config2')

			raise Exception(str(e))

	def query(self,qry):
		if not self.dbconn.is_connected():
			self.connect()

		self.execute(qry)
		all_rows_of_data = self.cur.fetchall()
		return all_rows_of_data

	def commit(self):
		#mysql is autocommit so do nothing here
		committed = True
		#self.dbconn.commit()

	def execute(self,qry):
		try:
			begin_at = time.time() * 1000
			if not self.dbconn.is_connected():
				self.connect()
			self.cur.execute(qry)

			end_at = time.time() * 1000

			duration = end_at - begin_at
			self.logquery(qry,duration)
		except Exception as e:
			raise Exception("SQL ERROR:\n\n" + str(e))

	def queryone(self,select_one_fld):
		try:
			if not self.dbconn.is_connected():
				self.connect()
			self.execute(select_one_fld)
			retval=self.cur.fetchone()
			return retval[0]
		except Exception as e:
			raise Exception("SQL ERROR:\n\n" + str(e))

if __name__ == '__main__':
	main()
