DROP TABLE IF EXISTS restored_1sample7;
CREATE TABLE IF NOT EXISTS restored_1sample7(
	start_date text 		/* eg. 2023-01-31 */  ,
	end_date text 		/* eg. 2023-02-01 */  ,
	subtotal float 		/* eg. 12.49 */  ,
	linenumber integer 		/* eg. 1 */  ,
	name text 		/* eg. brando */  ,
	timestamp text 		/* eg. 2023-02-23 12:30:00 */  
) 
COMMENT="This MySQL table was defined by schemawiz for loading the csv file sample7.csv, delimiter (	)"; 
