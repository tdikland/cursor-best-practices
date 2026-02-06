# Delta Lake Best Practices

Delta Lake is the foundation of Databricks lakehouse architecture. Following these best practices ensures optimal performance and reliability.

## Key Principles

1. **Regular Optimization** - Compact small files with OPTIMIZE
2. **Data Skipping** - Use Z-ORDERING or Liquid Clustering
3. **File Cleanup** - Run VACUUM to remove old versions
4. **Enable Features** - Use Change Data Feed, Deletion Vectors
5. **Efficient Merges** - Proper MERGE syntax for upserts

## Examples

**✅ Good Patterns:**
```python
# Write with partitioning
df.write.format("delta") \
  .partitionBy("date") \
  .mode("overwrite") \
  .saveAsTable("catalog.schema.events")

# Optimize and Z-ORDER
spark.sql("""
  OPTIMIZE catalog.schema.events
  ZORDER BY (user_id, event_type)
""")

# Enable table features
spark.sql("""
  ALTER TABLE catalog.schema.events
  SET TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.deletedFileRetentionDuration' = 'interval 7 days'
  )
""")

# Efficient MERGE for upserts
from delta.tables import DeltaTable

delta_table = DeltaTable.forName(spark, "catalog.schema.target")
delta_table.alias("target").merge(
    updates_df.alias("updates"),
    "target.id = updates.id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

**❌ Avoid:**
```python
# Don't write many small files
for row in data:
    df = spark.createDataFrame([row])
    df.write.format("delta").mode("append").save(path)

# Don't skip optimization
# Never optimize = poor read performance

# Don't use overwrite when merge is appropriate
df.write.mode("overwrite").saveAsTable("table")  # Loses history
```

## Cursor Hook

```markdown
# Delta Lake Best Practices for Databricks

When working with Delta Lake tables in this project, ALWAYS follow these rules:

## Table Operations

1. **Writing Data**
   - Always specify format explicitly: `.format("delta")`
   - Use `saveAsTable()` for managed tables, not `.save()`
   - Include proper partitioning for large tables: `.partitionBy("date", "region")`
   - Use meaningful table properties and comments

2. **Optimization**
   - After large writes, suggest OPTIMIZE: `OPTIMIZE catalog.schema.table`
   - For high-cardinality filter columns, use ZORDER: `ZORDER BY (col1, col2)`
   - For Databricks Runtime 13.3+, consider Liquid Clustering for evolving access patterns
   - Run VACUUM periodically: `VACUUM catalog.schema.table RETAIN 168 HOURS`

3. **Merge Operations**
   - ALWAYS use MERGE instead of delete+insert patterns
   - Use proper join conditions to minimize data scans
   - Consider whenNotMatchedBySource for deletions
   - Include all necessary columns in merge condition

4. **Table Features**
   - Enable Change Data Feed for CDC use cases
   - Use Deletion Vectors for frequent deletes (DBR 12.2+)
   - Set appropriate retention periods
   - Enable column mapping for schema evolution

## Code Templates

### Write with Partitioning
```python
df.write.format("delta") \
  .partitionBy("date") \
  .option("overwriteSchema", "true") \
  .mode("overwrite") \
  .saveAsTable("catalog.schema.table")
```

### Optimize Table
```python
spark.sql("""
  OPTIMIZE catalog.schema.table
  ZORDER BY (frequently_filtered_col)
""")
```

### MERGE Pattern
```python
from delta.tables import DeltaTable

target = DeltaTable.forName(spark, "catalog.schema.target")
target.alias("t").merge(
    source_df.alias("s"),
    "t.id = s.id AND t.date = s.date"
).whenMatchedUpdate(set={
    "status": "s.status",
    "updated_at": "current_timestamp()"
}).whenNotMatchedInsert(values={
    "id": "s.id",
    "date": "s.date",
    "status": "s.status",
    "updated_at": "current_timestamp()"
}).execute()
```

### Enable Features
```python
spark.sql("""
  ALTER TABLE catalog.schema.table
  SET TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.enableDeletionVectors' = 'true',
    'delta.deletedFileRetentionDuration' = 'interval 7 days'
  )
""")
```

## Validation Rules

Before writing Delta code, verify:
- [ ] Table name uses three-level namespace
- [ ] Format is explicitly set to "delta"
- [ ] Partitioning strategy is appropriate (not too granular)
- [ ] MERGE is used for upserts, not overwrite
- [ ] Optimization strategy is considered for large tables
```

