# PySpark Rules

## Write Code Compatible with Serverless Databricks

Serverless Databricks provides a fully managed Spark environment with faster startup times and automatic scaling. However, it has specific constraints that require code to follow certain patterns.

### Key Compatibility Rules

1. **Use DataFrame API Only** - Avoid RDD operations entirely
2. **No Direct SparkContext Access** - Use SparkSession instead
3. **Prefer Built-in Functions** - Avoid Python UDFs when possible
4. **No Custom JARs or Native Libraries** - Use supported libraries only
5. **Avoid Local Filesystem Operations** - Use DBFS, Unity Catalog, or cloud storage
6. **No Broadcast Variables** - Use DataFrame joins instead
7. **Avoid `.collect()` on Large Datasets** - Use `.limit()` or sampling

### Examples

**❌ Not Compatible:**
```python
# RDD operations
rdd = df.rdd.map(lambda x: x[0])

# Direct SparkContext access
sc = spark.sparkContext
broadcast_var = sc.broadcast(large_dict)

# Python UDF with external dependencies
@udf
def complex_transform(value):
    import custom_library  # Not available in serverless
    return custom_library.process(value)
```

**✅ Compatible:**
```python
# Use DataFrame API
from pyspark.sql import functions as F

# Use built-in functions
df = df.withColumn("result", F.upper(F.col("name")))

# Use DataFrame joins instead of broadcast
df_joined = df.join(F.broadcast(small_df), "key")

# Use pandas UDFs for better performance
@pandas_udf("double")
def vectorized_transform(values: pd.Series) -> pd.Series:
    return values * 2
```

### Cursor Hook for Serverless Compatibility

Add this to your project's `.cursorrules` file to ensure all generated PySpark code is serverless-compatible:

```markdown
# PySpark Serverless Databricks Rules

When writing PySpark code for this project, ALWAYS follow these rules to ensure compatibility with Serverless Databricks:

## CRITICAL REQUIREMENTS

1. **DataFrame API ONLY**
   - NEVER use RDD operations (`.rdd`, `.map()`, `.flatMap()`, `.reduceByKey()`, etc.)
   - Always use DataFrame transformations (`select`, `filter`, `withColumn`, `groupBy`, etc.)

2. **No Direct SparkContext Access**
   - NEVER access `spark.sparkContext` or `sc` directly
   - NEVER create broadcast variables with `sc.broadcast()`
   - Use DataFrame operations and `F.broadcast()` for small DataFrame joins

3. **Use Built-in Functions**
   - ALWAYS prefer `pyspark.sql.functions` over Python UDFs
   - Only use pandas UDFs (`@pandas_udf`) if built-in functions are insufficient
   - NEVER use regular `@udf` decorators for complex transformations

4. **No Custom Dependencies**
   - Do NOT import custom JARs or native libraries
   - Only use libraries available in Databricks Runtime
   - Avoid system-level dependencies

5. **Storage Patterns**
   - Use Unity Catalog tables: `spark.table("catalog.schema.table")`
   - Use DBFS paths: `dbfs:/...`
   - NEVER use local filesystem paths (`/tmp/`, `/home/`, etc.)

6. **Data Collection**
   - NEVER use `.collect()` without `.limit()` first
   - Prefer `.toPandas()` only for small result sets
   - Use `.write` operations for large outputs

## Code Examples

When generating PySpark code, follow these patterns:

### Reading Data
```python
# Good
df = spark.table("catalog.schema.table")
df = spark.read.format("delta").load("dbfs:/path/to/data")

# Bad - avoid
df = spark.read.csv("file:///local/path/data.csv")
```

### Transformations
```python
from pyspark.sql import functions as F

# Good - use built-in functions
df = df.withColumn("upper_name", F.upper("name"))
df = df.withColumn("date", F.to_date("timestamp"))

# Bad - avoid Python UDFs
@udf
def upper_case(value):
    return value.upper()
df = df.withColumn("upper_name", upper_case("name"))
```

### Joins
```python
# Good - broadcast small DataFrames
small_df = spark.table("catalog.schema.lookup")
result = large_df.join(F.broadcast(small_df), "key")

# Bad - avoid broadcast variables
lookup_dict = small_df.collect()
broadcast_var = sc.broadcast(lookup_dict)  # Don't do this
```

### Writing Data
```python
# Good
df.write.mode("overwrite").saveAsTable("catalog.schema.output")
df.write.format("delta").save("dbfs:/path/to/output")

# Bad - avoid local writes
df.toPandas().to_csv("/tmp/output.csv")  # Don't do this
```

## Validation Checklist

Before generating PySpark code, verify:
- [ ] No `.rdd` operations
- [ ] No `spark.sparkContext` or `sc` references
- [ ] Only built-in functions or pandas UDFs
- [ ] Storage paths use Unity Catalog or DBFS
- [ ] No `.collect()` without `.limit()`
- [ ] No custom JAR or native library imports

If you generate code that violates these rules, immediately flag it and provide a serverless-compatible alternative.
```

### How to Use This Hook

1. Create a `.cursorrules` file in your project root
2. Copy the hook content above into the file
3. Cursor will automatically apply these rules when generating PySpark code
4. The AI assistant will validate all generated code against these constraints

