# using mysql to restore from mysqldump

	mysql -u  database_username  database_name -p < database_backup_file.sql

## Restore a Single MySQL Database From a Full MySQL Dump File. 

	mysql -u database_username --one-database database_name1 -p < all_databases_backup_file.sql


# Export and Import a MySQL Database in One Command 

	mysqldump -u database_username database_name -p | mysql -h remote_host -u remote_database_username remote_database_name -p
