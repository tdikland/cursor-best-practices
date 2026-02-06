# Testing PySpark Code

Proper testing ensures PySpark transformations are correct, maintainable, and reliable. Use testing frameworks designed for Spark.

## Key Principles

1. **Unit Test Transformations** - Test logic without full Spark context when possible
2. **Use Testing Libraries** - Leverage chispa, pytest-spark, or similar
3. **Test Edge Cases** - Nulls, empty DataFrames, duplicates
4. **Fixture Pattern** - Create reusable test data fixtures
5. **Assertion Methods** - Use proper DataFrame comparison methods

## Examples

**✅ Good Testing Patterns:**
```python
import pytest
from chispa.dataframe_comparer import assert_df_equality
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local[2]") \
        .appName("test") \
        .getOrCreate()

def test_transformation_with_schema(spark):
    # Arrange - define schema explicitly
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True)
    ])

    input_data = [(1, "Alice"), (2, "Bob")]
    input_df = spark.createDataFrame(input_data, schema)

    expected_data = [(1, "ALICE"), (2, "BOB")]
    expected_df = spark.createDataFrame(expected_data, schema)

    # Act
    result_df = transform_names(input_df)

    # Assert
    assert_df_equality(result_df, expected_df, ignore_row_order=True)

def test_handles_nulls(spark):
    input_data = [(1, None), (2, "Bob")]
    input_df = spark.createDataFrame(input_data, ["id", "name"])

    result_df = transform_names(input_df)

    # Verify null handling
    null_count = result_df.filter("name IS NULL").count()
    assert null_count == 1

def test_empty_dataframe(spark):
    schema = StructType([StructField("id", IntegerType())])
    empty_df = spark.createDataFrame([], schema)

    result_df = transform_names(empty_df)

    assert result_df.count() == 0
```

**❌ Avoid:**
```python
# Don't test without proper assertions
def test_transformation(spark):
    df = spark.createDataFrame([(1, "test")])
    result = transform(df)
    result.show()  # No assertion!

# Don't compare with collect() for large data
def test_bad_comparison(spark):
    result = transform(df)
    expected = expected_df.collect()
    actual = result.collect()
    assert expected == actual  # Memory issue for large data

# Don't skip edge cases
# Missing tests for: nulls, empty dfs, duplicates
```

## Cursor Hook

```markdown
# PySpark Testing Best Practices

When writing tests for PySpark code in this project, ALWAYS follow these rules:

## Test Structure

1. **Use pytest Framework**
   - Organize tests in `tests/` directory
   - Name test files `test_*.py`
   - Use pytest fixtures for SparkSession
   - Group related tests in classes if needed

2. **Fixture Pattern**
   - Create session-scoped Spark fixture
   - Create reusable data fixtures
   - Clean up resources properly
   - Use appropriate fixture scope (session, module, function)

## Writing Tests

1. **Arrange-Act-Assert Pattern**
   - Arrange: Set up test data with explicit schemas
   - Act: Execute transformation function
   - Assert: Use proper DataFrame comparison methods
   - Keep tests focused on single behavior

2. **Schema Definitions**
   - ALWAYS define schemas explicitly with StructType
   - Don't rely on schema inference in tests
   - Match production schemas exactly
   - Include nullability constraints

3. **DataFrame Comparison**
   - Use `chispa.assert_df_equality()` for DataFrame comparison
   - Use `ignore_row_order=True` when order doesn't matter
   - Use `ignore_column_order=True` if column order flexible
   - Don't use `.collect()` for large DataFrames

4. **Edge Cases to Test**
   - Null values in all relevant columns
   - Empty DataFrames
   - Single row DataFrames
   - Duplicate records
   - Extreme values (min/max)
   - Malformed data

## Code Templates

### Basic Test Setup
```python
import pytest
from chispa.dataframe_comparer import assert_df_equality
from pyspark.sql import SparkSession
from pyspark.sql.types import *

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local[2]") \
        .appName("pytest-pyspark") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

@pytest.fixture
def sample_schema():
    return StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("value", DoubleType(), True)
    ])
```

### Test Transformation
```python
def test_transformation_happy_path(spark, sample_schema):
    # Arrange
    input_data = [
        (1, "Alice", 100.0),
        (2, "Bob", 200.0)
    ]
    input_df = spark.createDataFrame(input_data, sample_schema)

    expected_data = [
        (1, "Alice", 110.0),
        (2, "Bob", 220.0)
    ]
    expected_df = spark.createDataFrame(expected_data, sample_schema)

    # Act
    result_df = apply_markup(input_df, rate=0.10)

    # Assert
    assert_df_equality(result_df, expected_df, ignore_row_order=True)
```

### Test Null Handling
```python
def test_handles_null_values(spark, sample_schema):
    input_data = [
        (1, None, 100.0),
        (2, "Bob", None)
    ]
    input_df = spark.createDataFrame(input_data, sample_schema)

    result_df = apply_markup(input_df, rate=0.10)

    # Verify nulls are handled correctly
    assert result_df.filter("name IS NULL").count() == 1
    assert result_df.filter("value IS NULL").count() == 1
```

### Test Empty DataFrame
```python
def test_empty_dataframe(spark, sample_schema):
    empty_df = spark.createDataFrame([], sample_schema)

    result_df = apply_markup(empty_df, rate=0.10)

    assert result_df.count() == 0
    assert result_df.schema == sample_schema
```

### Test with Multiple Assertions
```python
def test_aggregation_results(spark):
    input_data = [
        ("A", 100),
        ("A", 200),
        ("B", 150)
    ]
    input_df = spark.createDataFrame(input_data, ["group", "value"])

    result_df = aggregate_by_group(input_df)

    # Multiple assertions
    assert result_df.count() == 2
    assert "sum_value" in result_df.columns

    result_dict = {row.group: row.sum_value for row in result_df.collect()}
    assert result_dict["A"] == 300
    assert result_dict["B"] == 150
```

## Validation Checklist

Before committing PySpark tests:
- [ ] Tests use pytest framework
- [ ] SparkSession fixture is session-scoped
- [ ] Schemas defined explicitly with StructType
- [ ] DataFrame comparison uses chispa or similar
- [ ] Edge cases tested (nulls, empty, duplicates)
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Test names clearly describe what they test
```

