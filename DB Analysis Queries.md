
```sql
-- list tables 
SELECT 
    table_catalog as idatabase
    ,table_schema as ischema
    ,table_name 
    ,table_rows
    ,(data_length + index_length) as Size_Bytes
FROM information_schema.tables
-- ignore system schemas
WHERE table_schema not in ('information_schema','performance_schema','sys');

```


```sql
-- Schemas by rowcount/size 
SELECT 
    table_catalog as idatabase
    ,table_schema as ischema
    ,sum(table_rows) as rowcount
    ,CASE WHEN sum((data_length + index_length))/1024/1024 > 1 THEN
        round(sum((data_length + index_length))/1024/1024,1)
     ELSE
        '< 1 MB'
     END as size_mb
    ,CASE WHEN sum((data_length + index_length))/1024/1024/1024 > 1 THEN
        round(sum((data_length + index_length))/1024/1024/1024,1)
     ELSE
        '< 1 GB'
     END as size_gb

FROM information_schema.tables
-- ignore system schemas
WHERE table_schema not in ('information_schema','performance_schema','sys')
GROUP BY table_catalog,table_schema;
```

```sql
-- 5 biggest tables by schema counting rows and byte size 

SELECT *
FROM (
    SELECT L.*
        ,rank() OVER (PARTITION BY ischema ORDER BY table_rows desc) as table_rows_rnk 
        ,rank() OVER (PARTITION BY ischema ORDER BY size_bytes desc) as size_bytes_rnk 
    FROM (
        SELECT 
            table_catalog as idatabase
            ,table_schema as ischema
            ,table_name 
            ,sum(table_rows)  as table_rows
            ,sum(data_length + index_length) as size_bytes
        FROM information_schema.tables
        -- ignore system schemas
        WHERE table_schema not in ('information_schema','performance_schema','sys')
        GROUP BY 1,2,3
        ) L
    ) M
WHERE table_rows_rnk <=5 or size_bytes_rnk <= 5


```
