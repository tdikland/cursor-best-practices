# Incremental Processing Patterns

Incremental processing allows you to efficiently process only new or changed data. Essential for scalable data pipelines.

## Key Principles

1. **Auto Loader for Ingestion** - Use cloudFiles for incremental file ingestion
2. **Watermarking** - Apply watermarks for streaming aggregations
3. **MERGE for Updates** - Use MERGE operations for incremental updates
4. **Checkpointing** - Maintain checkpoints for fault tolerance
5. **Idempotency** - Ensure pipelines can safely rerun

## Examples

**✅ Good Patterns:**
```python
# Auto Loader for incremental file ingestion
df = spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", "/path/to/schema") \
    .option("cloudFiles.inferColumnTypes", "true") \
    .load("s3://bucket/raw/")

# Streaming with watermark
events_df = spark.readStream.table("catalog.schema.events") \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        window("event_time", "5 minutes"),
        "user_id"
    ).count()

# Incremental batch with MERGE
from delta.tables import DeltaTable

target = DeltaTable.forName(spark, "catalog.schema.target")

# Read only new data
new_data = spark.read.table("catalog.schema.source") \
    .filter("load_date > (SELECT MAX(load_date) FROM catalog.schema.target)")

# Merge incrementally
target.alias("t").merge(
    new_data.alias("s"),
    "t.id = s.id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()

# Checkpointed streaming query
query = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .outputMode("append") \
    .table("catalog.schema.output")
```

**❌ Avoid:**
```python
# Don't reprocess all data every time
df = spark.table("huge_table")  # Full scan!
df.write.mode("overwrite").saveAsTable("output")

# Don't skip checkpoints
df.writeStream.format("delta").table("output")  # No checkpoint!

# Don't use append mode with deduplication
# This creates duplicates on failure/restart
```

## Cursor Hook

```markdown
# Incremental Processing Best Practices

When implementing incremental processing in this project, ALWAYS follow these rules:

## Auto Loader Patterns

1. **Use cloudFiles for File Ingestion**
   - Use format "cloudFiles" for incremental file processing
   - Always specify cloudFiles.format (json, csv, parquet, etc.)
   - Set schemaLocation for schema tracking
   - Use schema inference with cloudFiles.inferColumnTypes
   - Configure cloudFiles.maxFilesPerTrigger for rate limiting

2. **Schema Evolution**
   - Store schema in dedicated location
   - Use schemaHints for known columns
   - Handle schema evolution with mergeSchema
   - Monitor schema changes with notifications

## Streaming Patterns

1. **Watermarking**
   - ALWAYS use watermarks for time-based aggregations
   - Set appropriate watermark delay based on late data tolerance
   - Apply watermark before windowing operations
   - Use event time, not processing time

2. **Checkpointing**
   - ALWAYS specify checkpointLocation for streaming queries
   - Use reliable storage (cloud storage, not local)
   - One checkpoint location per query
   - Don't delete checkpoints unless intentional reset

3. **Output Modes**
   - Use "append" for most cases (new rows only)
   - Use "update" for aggregations with watermarks
   - Use "complete" only for small result sets
   - Understand mode implications for downstream consumers

## Batch Incremental Patterns

1. **Incremental Reads**
   - Filter data based on high-water mark
   - Store last processed timestamp/id
   - Use >= for timestamp comparisons (handle duplicates)
   - Consider overlapping windows for late arrivals

2. **MERGE Operations**
   - Use MERGE for upserts in batch incremental
   - Include proper join conditions
   - Consider whenNotMatchedBySource for deletions
   - Optimize merge condition columns

3. **Idempotency**
   - Design pipelines to handle reruns safely
   - Use unique keys for deduplication
   - Handle partial failures gracefully
   - Make operations commutative when possible

## Code Templates

### Auto Loader Basic
```python
df = spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", "/Volumes/cat/schema/checkpoint/schema") \
    .option("cloudFiles.inferColumnTypes", "true") \
    .option("cloudFiles.maxFilesPerTrigger", "1000") \
    .load("/Volumes/catalog/schema/volume/raw/")

query = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/Volumes/cat/schema/checkpoint/query") \
    .outputMode("append") \
    .table("catalog.schema.bronze_table")
```

### Streaming with Watermark
```python
events = spark.readStream \
    .table("catalog.schema.events") \
    .withWatermark("event_time", "1 hour")

windowed = events.groupBy(
    window("event_time", "10 minutes", "5 minutes"),
    "user_id"
).agg(
    count("*").alias("event_count"),
    max("value").alias("max_value")
)

query = windowed.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .outputMode("update") \
    .table("catalog.schema.windowed_events")
```

### Incremental Batch with Watermark
```python
from pyspark.sql import functions as F

# Get last processed timestamp
last_processed = spark.sql("""
    SELECT COALESCE(MAX(processed_at), '1970-01-01') as max_ts
    FROM catalog.schema.target
""").collect()[0]['max_ts']

# Read incremental data
incremental_df = spark.table("catalog.schema.source") \
    .filter(F.col("created_at") >= last_processed)

# Process and write
processed_df = transform(incremental_df) \
    .withColumn("processed_at", F.current_timestamp())

processed_df.write.format("delta") \
    .mode("append") \
    .saveAsTable("catalog.schema.target")
```

### Incremental MERGE
```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F

# Get incremental data
last_id = spark.sql("SELECT MAX(id) FROM catalog.schema.target").collect()[0][0]
incremental_df = spark.table("catalog.schema.source") \
    .filter(F.col("id") > last_id)

# Merge
target = DeltaTable.forName(spark, "catalog.schema.target")
target.alias("t").merge(
    incremental_df.alias("s"),
    "t.business_key = s.business_key"
).whenMatchedUpdate(set={
    "value": "s.value",
    "updated_at": "current_timestamp()"
}).whenNotMatchedInsert(values={
    "business_key": "s.business_key",
    "value": "s.value",
    "created_at": "current_timestamp()",
    "updated_at": "current_timestamp()"
}).execute()
```

### Idempotent Processing
```python
# Read with deduplication window
incremental_df = spark.table("catalog.schema.source") \
    .filter("created_at >= current_date() - interval 1 day")

# Deduplicate within window
from pyspark.sql.window import Window

window_spec = Window.partitionBy("id").orderBy(F.col("created_at").desc())
deduped_df = incremental_df \
    .withColumn("rn", F.row_number().over(window_spec)) \
    .filter("rn = 1") \
    .drop("rn")

# Use MERGE to handle reruns safely
target = DeltaTable.forName(spark, "catalog.schema.target")
target.alias("t").merge(
    deduped_df.alias("s"),
    "t.id = s.id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

## Validation Checklist

For incremental processing pipelines:
- [ ] Checkpoint location specified for streaming
- [ ] Watermark applied for time-based operations
- [ ] Schema location configured for Auto Loader
- [ ] High-water mark tracked for batch incremental
- [ ] MERGE used instead of delete+insert
- [ ] Pipeline is idempotent (safe to rerun)
- [ ] Late data handling strategy defined
```

