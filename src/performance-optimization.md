# Performance Optimization

Optimize PySpark jobs for faster execution and lower costs. Understanding Spark's execution model is key to writing efficient code.

## Key Principles

1. **Cache Wisely** - Use .cache() and .persist() strategically
2. **Partition Pruning** - Filter on partition columns early
3. **Avoid Small Files** - Compact files with OPTIMIZE
4. **Minimize Shuffles** - Reduce data movement across nodes
5. **Leverage AQE** - Use Adaptive Query Execution features

## Examples

**✅ Good Patterns:**
```python
from pyspark.sql import functions as F

# Partition pruning - filter early
df = spark.table("catalog.schema.events") \
    .filter("date = '2024-01-01'")  # Partition column

# Cache for reuse
base_df = spark.table("catalog.schema.large_table") \
    .filter(F.col("status") == "active") \
    .cache()

result1 = base_df.groupBy("category").count()
result2 = base_df.groupBy("region").count()
base_df.unpersist()  # Clean up

# Broadcast small tables
small_dim = spark.table("catalog.schema.dim_small")
large_fact = spark.table("catalog.schema.fact_large")

result = large_fact.join(
    F.broadcast(small_dim),
    "dim_key"
)

# Repartition for balanced processing
df.repartition(200, "user_id") \
  .write.partitionBy("date") \
  .saveAsTable("catalog.schema.output")

# Coalesce after filtering
filtered_df = df.filter("important = true")  # Reduces data
filtered_df.coalesce(10).write.parquet("output")
```

**❌ Avoid:**
```python
# Don't cache everything
df.cache()  # Only used once - wasted memory

# Don't create small files
for date in dates:
    df.filter(f"date = '{date}'").write.mode("append").save(path)

# Don't scan full table when partition exists
df = spark.table("partitioned_table")
result = df.filter("date = '2024-01-01'")  # Filters AFTER full scan

# Don't unnecessary shuffle
df.repartition(1000)  # Too many partitions for small data
```

## Cursor Hook

```markdown
# PySpark Performance Optimization Rules

When writing PySpark code in this project, ALWAYS follow these performance optimization rules:

## Caching and Persistence

1. **Cache Strategically**
   - Only cache DataFrames used multiple times in same job
   - Cache after expensive transformations, before multiple actions
   - Use .persist(StorageLevel.MEMORY_AND_DISK) for large data
   - Always .unpersist() when done to free memory
   - Don't cache DataFrames used only once

2. **Storage Levels**
   - MEMORY_ONLY: Fast but limited by memory
   - MEMORY_AND_DISK: Spills to disk when needed (default for .cache())
   - DISK_ONLY: For very large datasets
   - Add _SER suffix for serialized storage (more CPU, less memory)

## Partitioning

1. **Partition Pruning**
   - ALWAYS filter on partition columns in WHERE clause
   - Do partition filtering BEFORE other operations
   - Use partition columns in join conditions when possible
   - Check query plans to verify partition pruning occurs

2. **Repartition vs Coalesce**
   - Use repartition() when increasing partitions or redistributing data
   - Use coalesce() when reducing partitions (no shuffle for reduction)
   - Repartition on join keys before large joins
   - Coalesce before writing to avoid small files

3. **Partition Size**
   - Target 100MB-1GB per partition
   - Too few partitions = underutilized cluster
   - Too many partitions = excessive overhead
   - Default spark.sql.shuffle.partitions is 200 (adjust as needed)

## Join Optimization

1. **Broadcast Joins**
   - Use F.broadcast() for tables < 10MB
   - Databricks auto-broadcasts < 10MB by default
   - Broadcast dimension tables in star schema
   - Avoid broadcasting large tables (causes OOM)

2. **Join Strategy**
   - Prefer broadcast joins for small tables
   - Use sort-merge join for large tables
   - Repartition both sides on join key if needed
   - Filter before joining to reduce data size

## Shuffle Optimization

1. **Minimize Shuffles**
   - Combine operations that cause shuffles
   - Filter data before shuffle operations
   - Use narrow transformations when possible
   - Check query plan for shuffle operations

2. **Shuffle Operations**
   - groupBy, join, repartition cause shuffles
   - orderBy with global sort causes shuffle
   - distinct, union, intersect cause shuffles
   - Minimize these or combine them efficiently

## File Management

1. **Avoid Small Files**
   - Run OPTIMIZE regularly on Delta tables
   - Use coalesce before writes
   - Set appropriate file size targets
   - Compact after many incremental writes

2. **Optimize Commands**
   - Run OPTIMIZE after bulk loads
   - Use ZORDER BY for frequently filtered columns
   - Schedule regular optimization jobs
   - Monitor file counts and sizes

## Adaptive Query Execution (AQE)

1. **AQE Features**
   - Enabled by default in Databricks Runtime 7+
   - Dynamically adjusts partition count
   - Optimizes skew joins automatically
   - Converts sort-merge to broadcast join when possible

2. **AQE Configuration**
   - spark.sql.adaptive.enabled = true (default)
   - Trust AQE for most optimizations
   - Monitor query plans to verify AQE benefits
   - Override only when necessary

## Code Templates

### Cache for Reuse
```python
from pyspark.sql import functions as F

# Cache when DataFrame used multiple times
base_df = spark.table("catalog.schema.large") \
    .filter(F.col("date") >= "2024-01-01") \
    .cache()

# Use multiple times
summary1 = base_df.groupBy("category").count()
summary2 = base_df.groupBy("region").sum("amount")

# Clean up
base_df.unpersist()
```

### Partition Pruning
```python
# Good - filter on partition column first
df = spark.table("catalog.schema.partitioned_table") \
    .filter("date = '2024-01-01'") \
    .filter("status = 'active'")

# Verify partition pruning in plan
df.explain()
# Look for "PartitionFilters: [isnotnull(date), (date = 2024-01-01)]"
```

### Broadcast Join
```python
from pyspark.sql import functions as F

# Broadcast small dimension table
dim_table = spark.table("catalog.schema.dim_products")  # Small
fact_table = spark.table("catalog.schema.fact_sales")   # Large

result = fact_table.join(
    F.broadcast(dim_table),
    "product_id"
)
```

### Repartition for Join
```python
# Repartition both sides on join key for large joins
large_df1 = spark.table("catalog.schema.table1") \
    .repartition(200, "join_key")

large_df2 = spark.table("catalog.schema.table2") \
    .repartition(200, "join_key")

result = large_df1.join(large_df2, "join_key")
```

### Coalesce to Avoid Small Files
```python
# After filtering, reduce partitions before writing
filtered_df = spark.table("catalog.schema.large") \
    .filter("important_only = true")  # Reduces to 5% of data

filtered_df.coalesce(20) \
    .write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("catalog.schema.filtered")
```

### Optimize Delta Table
```python
# Compact small files
spark.sql("""
    OPTIMIZE catalog.schema.table
    ZORDER BY (user_id, event_date)
""")

# Check file statistics
spark.sql("""
    DESCRIBE DETAIL catalog.schema.table
""").select("numFiles", "sizeInBytes").show()
```

### Monitor Query Performance
```python
# Enable query logging
spark.conf.set("spark.sql.queryExecutionListeners",
               "org.apache.spark.sql.util.QueryExecutionListener")

# Analyze query plan
df = spark.table("catalog.schema.table") \
    .filter("date = '2024-01-01'") \
    .groupBy("category").count()

# Check physical plan
df.explain("extended")

# Check for shuffles, broadcasts, partition pruning
df.explain("formatted")
```

## Validation Checklist

Before finalizing PySpark code:
- [ ] Cache only DataFrames used multiple times
- [ ] Filter on partition columns early
- [ ] Broadcast joins for small tables (< 10MB)
- [ ] Appropriate partition count (not too many/few)
- [ ] Coalesce before write to avoid small files
- [ ] OPTIMIZE scheduled for Delta tables
- [ ] Query plan reviewed for unnecessary shuffles
- [ ] Unpersist called to free cached memory
```

