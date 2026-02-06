# Data Quality & Expectations

Implement data quality checks to ensure reliable pipelines. Catch bad data early before it propagates downstream.

## Key Principles

1. **Expectations** - Define rules for valid data
2. **Quarantine Bad Records** - Don't fail jobs, isolate problems
3. **Monitor Quality** - Track metrics over time
4. **Fail Fast** - Validate critical assumptions early
5. **Document Rules** - Make quality rules explicit and visible

## Examples

**✅ Good Patterns:**
```python
from pyspark.sql import functions as F

# Define expectations
def validate_users(df):
    """Validate user data quality."""
    return df.filter(
        (F.col("user_id").isNotNull()) &
        (F.col("email").rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")) &
        (F.col("created_at") <= F.current_timestamp())
    )

# Quarantine bad records
valid_df = validate_users(df)
invalid_df = df.exceptAll(valid_df)

valid_df.write.saveAsTable("catalog.schema.users")
invalid_df.write.saveAsTable("catalog.schema.users_quarantine")

# Delta Live Tables expectations
import dlt

@dlt.table(
    comment="Validated user records"
)
@dlt.expect_all({
    "valid_user_id": "user_id IS NOT NULL",
    "valid_email": "email IS NOT NULL AND email LIKE '%@%'",
    "future_date": "created_at <= current_timestamp()"
})
def users_validated():
    return spark.table("catalog.schema.users_raw")

# Count-based validation
row_count = df.count()
if row_count == 0:
    raise ValueError("Empty DataFrame - expected at least 1 row")

# Range validation
stats = df.select(
    F.min("amount").alias("min_amount"),
    F.max("amount").alias("max_amount")
).collect()[0]

if stats.min_amount < 0:
    raise ValueError(f"Negative amounts found: {stats.min_amount}")
```

**❌ Avoid:**
```python
# Don't silently drop bad data
df = df.filter("email IS NOT NULL")  # Where did bad data go?

# Don't let bad data fail entire job
df.write.saveAsTable("table")  # Fails on constraint violation

# Don't skip validation
# "It worked in dev" - not good enough for production
```

## Cursor Hook

```markdown
# Data Quality & Expectations Rules

When implementing data quality checks in this project, ALWAYS follow these rules:

## Expectation Patterns

1. **Define Expectations Explicitly**
   - Document what constitutes valid data
   - Check null constraints on required fields
   - Validate referential integrity
   - Check value ranges and formats
   - Verify business logic rules

2. **Quarantine Bad Records**
   - NEVER silently drop bad data
   - Write invalid records to quarantine table
   - Include validation timestamp and reason
   - Alert on quarantine volume thresholds
   - Provide mechanism to review and reprocess

3. **Validation Layers**
   - Bronze: Minimal validation, raw data preservation
   - Silver: Strict validation, business rule enforcement
   - Gold: Aggregate validation, consistency checks

## Delta Live Tables Expectations

1. **Expectation Types**
   - `@dlt.expect()`: Log violations, continue processing
   - `@dlt.expect_or_drop()`: Drop violating records
   - `@dlt.expect_or_fail()`: Fail pipeline on violations
   - Use appropriate type based on criticality

2. **Expectation Rules**
   - Name expectations clearly (what they validate)
   - Use SQL expressions for conditions
   - Combine multiple related checks with expect_all
   - Monitor expectation metrics in DLT UI

## Validation Checks

1. **Null Checks**
   - Validate NOT NULL for required fields
   - Check for unexpected nulls in critical columns
   - Distinguish between NULL and empty string
   - Validate nullable fields have defaults

2. **Format Validation**
   - Email: Use regex for format validation
   - Phone: Validate country code and format
   - Date: Check date ranges and formats
   - IDs: Validate format and uniqueness

3. **Range Validation**
   - Check min/max bounds for numeric fields
   - Validate dates are not in future (when applicable)
   - Check enum values against allowed list
   - Validate percentages between 0-100

4. **Referential Integrity**
   - Validate foreign keys exist in parent table
   - Check for orphaned records
   - Validate many-to-one relationships
   - Check for circular references

5. **Business Logic**
   - Total equals sum of parts
   - Status transitions are valid
   - Required combinations present
   - Mutually exclusive conditions

## Monitoring and Alerting

1. **Quality Metrics**
   - Track validation failure rates
   - Monitor quarantine table size
   - Alert on sudden quality degradation
   - Trend quality metrics over time

2. **Logging**
   - Log validation failures with context
   - Include row identifiers for debugging
   - Capture validation rule that failed
   - Timestamp all quality checks

## Code Templates

### Basic Validation with Quarantine
```python
from pyspark.sql import functions as F

def validate_transactions(df):
    """Validate transaction data."""
    return df.filter(
        (F.col("transaction_id").isNotNull()) &
        (F.col("amount") > 0) &
        (F.col("amount") < 1000000) &
        (F.col("currency").isin(["USD", "EUR", "GBP"])) &
        (F.col("transaction_date") <= F.current_date())
    )

# Split valid and invalid
valid_df = validate_transactions(df)
invalid_df = df.exceptAll(valid_df)

# Write valid data
valid_df.write.format("delta") \
    .mode("append") \
    .saveAsTable("catalog.schema.transactions")

# Quarantine invalid with metadata
invalid_with_reason = invalid_df.withColumn(
    "quarantine_timestamp", F.current_timestamp()
).withColumn(
    "validation_failed", F.lit("Amount, currency, or date validation failed")
)

invalid_with_reason.write.format("delta") \
    .mode("append") \
    .saveAsTable("catalog.schema.transactions_quarantine")
```

### Delta Live Tables Expectations
```python
import dlt
from pyspark.sql import functions as F

@dlt.table(
    comment="Bronze layer - raw events with minimal validation"
)
@dlt.expect_all({
    "valid_timestamp": "event_timestamp IS NOT NULL",
    "valid_user": "user_id IS NOT NULL"
})
def events_bronze():
    return spark.readStream.table("catalog.schema.events_raw")

@dlt.table(
    comment="Silver layer - validated events"
)
@dlt.expect_all_or_drop({
    "valid_event_type": "event_type IN ('click', 'view', 'purchase')",
    "reasonable_timestamp": "event_timestamp BETWEEN '2020-01-01' AND current_date()",
    "valid_email": "email RLIKE '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}$'"
})
def events_silver():
    return dlt.read_stream("events_bronze")

@dlt.table(
    comment="Gold layer - aggregated metrics"
)
@dlt.expect_or_fail("positive_counts", "event_count > 0")
def events_daily_summary():
    return dlt.read("events_silver").groupBy(
        F.col("event_date"),
        F.col("event_type")
    ).agg(
        F.count("*").alias("event_count")
    )
```

### Referential Integrity Check
```python
from pyspark.sql import functions as F

# Check for orphaned records
orders = spark.table("catalog.schema.orders")
customers = spark.table("catalog.schema.customers")

orphaned_orders = orders.join(
    customers,
    orders.customer_id == customers.customer_id,
    "left_anti"
)

if orphaned_orders.count() > 0:
    print(f"WARNING: Found {orphaned_orders.count()} orphaned orders")
    orphaned_orders.write.mode("overwrite") \
        .saveAsTable("catalog.schema.orphaned_orders_quarantine")
```

### Range and Format Validation
```python
from pyspark.sql import functions as F

def validate_customer_data(df):
    """Comprehensive customer validation."""
    return df.filter(
        # Required fields
        (F.col("customer_id").isNotNull()) &
        (F.col("email").isNotNull()) &

        # Email format
        (F.col("email").rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")) &

        # Date ranges
        (F.col("registration_date") >= F.lit("2020-01-01")) &
        (F.col("registration_date") <= F.current_date()) &

        # Enum values
        (F.col("status").isin(["active", "inactive", "suspended"])) &

        # Numeric ranges
        (F.col("age").between(18, 120)) &

        # Optional phone format (null or valid)
        (
            F.col("phone").isNull() |
            F.col("phone").rlike(r"^\+?[1-9]\d{1,14}$")
        )
    )
```

### Aggregate Validation
```python
from pyspark.sql import functions as F

# Validate totals match
order_summary = spark.table("catalog.schema.order_summary")
order_details = spark.table("catalog.schema.order_details")

# Sum of details should equal summary total
detail_totals = order_details.groupBy("order_id") \
    .agg(F.sum("line_amount").alias("detail_total"))

mismatches = order_summary.alias("s").join(
    detail_totals.alias("d"),
    "order_id"
).filter(
    F.abs(F.col("s.order_total") - F.col("d.detail_total")) > 0.01
)

if mismatches.count() > 0:
    raise ValueError(f"Found {mismatches.count()} orders with total mismatches")
```

### Quality Metrics
```python
from pyspark.sql import functions as F

def calculate_quality_metrics(source_df, valid_df, invalid_df):
    """Calculate and log data quality metrics."""
    total_count = source_df.count()
    valid_count = valid_df.count()
    invalid_count = invalid_df.count()

    metrics = {
        "total_records": total_count,
        "valid_records": valid_count,
        "invalid_records": invalid_count,
        "quality_rate": valid_count / total_count if total_count > 0 else 0,
        "timestamp": F.current_timestamp()
    }

    # Log metrics
    metrics_df = spark.createDataFrame([metrics])
    metrics_df.write.format("delta") \
        .mode("append") \
        .saveAsTable("catalog.schema.quality_metrics")

    # Alert if quality drops below threshold
    if metrics["quality_rate"] < 0.95:
        print(f"WARNING: Quality rate {metrics['quality_rate']:.2%} below threshold")

    return metrics
```

## Validation Checklist

For every data pipeline:
- [ ] Required fields validated for NOT NULL
- [ ] Format validation for emails, phones, dates
- [ ] Range checks for numeric and date fields
- [ ] Enum values validated against allowed lists
- [ ] Invalid records quarantined with reason
- [ ] Referential integrity validated
- [ ] Business logic rules enforced
- [ ] Quality metrics tracked and monitored
- [ ] Alerts configured for quality degradation
```

