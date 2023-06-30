# Show table locks
```
-- show table locks
show open tables 
where In_Use > 0 ;
```

# Find Running Queries
```
-- Find Running Queries
SELECT
    pid
    ,user
    ,db as _schema
    ,time as seconds_duration
    ,last_statement as query 
    ,A.* 
FROM SYS.PROCESSLIST A
WHERE db is not null and command is not null;
```

# stop running query
```
-- stop running query
KILL QUERY PID
```

# show users
```
-- show users
SELECT *
FROM mysql.user;
```
# show current logged in user
```
-- show current logged in user
SELECT current_user();
```
