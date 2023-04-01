@echo off
REM
REM  Dave Skura, 2023
REM
REM  pip install zetl

echo  Backing up tables in MySQL

call py -m zetl.mysql_extract "SELECT * FROM sample7" sample7.csv
call py -m zetl.mysql_extract "SELECT * FROM sample8" sample8.csv
call py -m zetl.mysql_extract "SELECT * FROM thistbl" thistbl.csv





