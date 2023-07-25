@echo off
REM
REM  Dave Skura, 2023
REM

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump" -u dave -p -t  -T. ossn ossn_users --fields-terminated-by=','
mysql -u dbadmin -p mysql -h localhost -e "SELECT concat(app_contact_name,',',app_contact2_name,',',branch_phone,',',buyer_phone,',',builder_sales_phone,',',app_city) as line FROM atable" >filename.csv
REM "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u dave ossn -h localhost -e "SELECT * INTO OUTFILE 'F:\\git\\mysql_basics\\ossn_users.csv' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n' FROM ossn_users;"
REM "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" -u dave ossn -h localhost -e "SELECT * FROM ossn_users" > ossn_users.tsv
