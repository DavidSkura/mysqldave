-- add comment to table
```
alter table world.city comment = 'this table needs a comment';
```

-- add comment to column
```
alter table world.city MODIFY COLUMN id int comment 'this column needs a comment';
```

