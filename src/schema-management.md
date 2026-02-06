# Schema Management

Proper schema management prevents data quality issues and enables safe evolution of data pipelines over time.

## Key Principles

1. **Explicit Schemas** - Define schemas, don't infer in production
2. **Schema Evolution** - Use mergeSchema and overwriteSchema appropriately
3. **Type Safety** - Use proper data types from the start
4. **Documentation** - Add column comments and constraints
5. **Validation** - Enforce schema at write time

## Examples

**✅ Good Patterns:**
```python
from pyspark.sql.types import *

# Define explicit schema
user_schema = StructType([
    StructField("user_id", LongType(), nullable=False),
    StructField("username", StringType(), nullable=False),
    StructField("email", StringType(), nullable=True),
    StructField("created_at", TimestampType(), nullable=False),
    StructField("metadata", MapType(StringType(), StringType()), nullable=True)
])

# Read with schema
df = spark.read.schema(user_schema).json("path/to/data")

# Schema evolution - adding columns
df_with_new_col = df.withColumn("status", lit("active"))
df_with_new_col.write \
    .format("delta") \
    .option("mergeSchema", "true") \
    .mode("append") \
    .saveAsTable("catalog.schema.users")

# Add column documentation
spark.sql("""
    ALTER TABLE catalog.schema.users
    ALTER COLUMN email
    COMMENT 'User email address for notifications'
""")

# Struct for nested data
address_schema = StructType([
    StructField("street", StringType()),
    StructField("city", StringType()),
    StructField("zip", StringType())
])

schema_with_nested = StructType([
    StructField("id", LongType()),
    StructField("address", address_schema)
])
```

**❌ Avoid:**
```python
# Don't infer schema in production
df = spark.read.json("path")  # Schema changes cause failures

# Don't use string for everything
schema = StructType([
    StructField("date", StringType()),  # Should be DateType
    StructField("amount", StringType())  # Should be DecimalType
])

# Don't ignore nullability
StructField("id", LongType())  # Nullable by default, should be False

# Don't skip mergeSchema when adding columns
df.write.mode("append").saveAsTable("table")  # Fails with schema mismatch
```

## Cursor Hook

```markdown
# Schema Management Best Practices

When working with schemas in this project, ALWAYS follow these rules:

## Schema Definition

1. **Explicit Schema Always**
   - NEVER rely on schema inference for production reads
   - Always define StructType with explicit field types
   - Specify nullability for each field (nullable=True/False)
   - Use appropriate data types (not StringType for everything)

2. **Proper Data Types**
   - Use LongType/IntegerType for IDs and counts
   - Use DecimalType(precision, scale) for money
   - Use DateType for dates, TimestampType for timestamps
   - Use BooleanType for flags, not strings
   - Use ArrayType, MapType, StructType for complex types
   - Use StringType only for actual text data

3. **Nullability**
   - Set nullable=False for required fields (IDs, keys)
   - Set nullable=True for optional fields
   - Be explicit, don't rely on defaults
   - Match nullability to business logic

## Schema Evolution

1. **Adding Columns**
   - Use mergeSchema=true when appending with new columns
   - Add columns to the end for backward compatibility
   - Provide default values with withColumn
   - Document new columns with ALTER COLUMN COMMENT

2. **Changing Types**
   - Avoid changing column types when possible
   - If necessary, create new column and migrate
   - Use type casting explicitly
   - Document breaking changes

3. **Schema Enforcement**
   - Delta Lake enforces schema by default (good!)
   - Use overwriteSchema=true only when intentional
   - Test schema changes in dev environment first
   - Version control schema definitions

## Nested Data

1. **Use Struct Types**
   - Model nested objects as StructType
   - Better than flattening for JSON-like data
   - Maintains data relationships
   - Enables column pruning

2. **Arrays and Maps**
   - Use ArrayType for repeated elements
   - Use MapType for key-value pairs
   - Specify element types explicitly
   - Consider query patterns (arrays easier to explode)

## Documentation

1. **Column Comments**
   - Add comments for all columns
   - Describe meaning, not just restating name
   - Note PII, business rules, or constraints
   - Keep comments up to date

2. **Table Properties**
   - Document data source
   - Note refresh frequency
   - Specify data owner
   - Tag data classification

## Code Templates

### Define Explicit Schema
```python
from pyspark.sql.types import *

transaction_schema = StructType([
    StructField("transaction_id", LongType(), nullable=False),
    StructField("user_id", LongType(), nullable=False),
    StructField("amount", DecimalType(10, 2), nullable=False),
    StructField("currency", StringType(), nullable=False),
    StructField("transaction_date", DateType(), nullable=False),
    StructField("created_at", TimestampType(), nullable=False),
    StructField("is_refunded", BooleanType(), nullable=False),
    StructField("metadata", MapType(StringType(), StringType()), nullable=True)
])

df = spark.read.schema(transaction_schema).json("/path/to/data")
```

### Nested Schema
```python
address_schema = StructType([
    StructField("street", StringType(), nullable=True),
    StructField("city", StringType(), nullable=True),
    StructField("state", StringType(), nullable=True),
    StructField("zip", StringType(), nullable=True)
])

customer_schema = StructType([
    StructField("customer_id", LongType(), nullable=False),
    StructField("name", StringType(), nullable=False),
    StructField("email", StringType(), nullable=True),
    StructField("address", address_schema, nullable=True),
    StructField("tags", ArrayType(StringType()), nullable=True)
])
```

### Schema Evolution - Adding Column
```python
from pyspark.sql import functions as F

# Add new column with default value
df_with_new_col = existing_df.withColumn(
    "status",
    F.lit("active")
)

# Write with schema merge
df_with_new_col.write \
    .format("delta") \
    .option("mergeSchema", "true") \
    .mode("append") \
    .saveAsTable("catalog.schema.table")

# Document the new column
spark.sql("""
    ALTER TABLE catalog.schema.table
    ALTER COLUMN status
    COMMENT 'Customer account status: active, inactive, or suspended'
""")
```

### Schema Validation
```python
from pyspark.sql.types import *

def validate_schema(df, expected_schema):
    """Validate DataFrame schema matches expected."""
    if df.schema != expected_schema:
        raise ValueError(
            f"Schema mismatch.\n"
            f"Expected: {expected_schema}\n"
            f"Actual: {df.schema}"
        )
    return df

# Use in pipeline
df = spark.read.json("/path/to/data")
validated_df = validate_schema(df, expected_schema)
```

### Add Column Comments
```python
# Create table with column comments
spark.sql("""
    CREATE TABLE catalog.schema.users (
        user_id BIGINT COMMENT 'Unique user identifier',
        email STRING COMMENT 'User email address - PII field',
        created_at TIMESTAMP COMMENT 'Account creation timestamp (UTC)',
        status STRING COMMENT 'Account status: active, inactive, suspended'
    )
    USING DELTA
    COMMENT 'User master table containing account information'
""")

# Add comment to existing column
spark.sql("""
    ALTER TABLE catalog.schema.users
    ALTER COLUMN email
    COMMENT 'User email address - PII field, encrypted at rest'
""")
```

### Reusable Schema Registry
```python
# schemas.py - centralized schema definitions
from pyspark.sql.types import *

class Schemas:
    USER = StructType([
        StructField("user_id", LongType(), False),
        StructField("email", StringType(), True),
        StructField("created_at", TimestampType(), False)
    ])

    TRANSACTION = StructType([
        StructField("txn_id", LongType(), False),
        StructField("user_id", LongType(), False),
        StructField("amount", DecimalType(10, 2), False),
        StructField("txn_date", DateType(), False)
    ])

# Use in code
from schemas import Schemas

df = spark.read.schema(Schemas.USER).json("/path")
```

## Validation Checklist

Before working with schemas:
- [ ] Schema defined explicitly with StructType
- [ ] Appropriate data types used (not all strings)
- [ ] Nullability specified for each field
- [ ] Column comments added for documentation
- [ ] mergeSchema used when adding columns
- [ ] Nested data modeled with StructType
- [ ] Schema definitions version controlled
```

