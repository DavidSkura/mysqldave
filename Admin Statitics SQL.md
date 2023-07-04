
```sql
-- Check the Statistics in the MySQL database
SELECT * 
FROM INFORMATION_SCHEMA.STATISTICS 
WHERE table_name = 'city' AND table_schema = 'world';
```


```sql
-- Generate the Statistics for the table in the MySQL database
ANALYZE TABLE city;
```

### Generate stats for a table with Histogram of columns 
A histogram is an approximation of the data distribution for a column. 
It can tell you with a reasonably accuray whether your data is skewed or not, 
which in turn will help the database server understand the nature of data it contains

```sql
-- Generate stats for a table with Histogram of columns
ANALYZE TABLE city UPDATE HISTOGRAM ON Name,District WITH 16 BUCKETS;
```