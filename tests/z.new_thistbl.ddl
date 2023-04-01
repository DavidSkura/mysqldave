DROP TABLE IF EXISTS new_thistbl;
CREATE TABLE IF NOT EXISTS new_thistbl(
	subtotal float 		/* eg. 12.49 */  ,
	linenumber float 		/* eg. 1.0 */  ,
	total float 		/* eg. 132.49 */  
) 
COMMENT="This MySQL table was defined by schemawiz for loading the csv file thistbl.csv, delimiter (	)"; 
