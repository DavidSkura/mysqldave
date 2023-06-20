# using mysqladmin 

mysqladmin -uUSERNAME -pPASSWORD pr

mysqladmin -uUSERNAME -pPASSWORD kill pid

# using psql

mysql -uusername -p  -hhostname

mysql> SHOW processlist;

mysql> show full processlist;

mysql> kill 9255451;

# in sql

select * from jos_users, jos_comprofiler;

CALL mysql.rds_kill(9255451);

