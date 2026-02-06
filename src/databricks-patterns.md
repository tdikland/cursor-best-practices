# Databricks-Specific Patterns

Leverage Databricks-specific features and best practices for productive development and operations.

## Key Principles

1. **Widgets for Parameters** - Use dbutils.widgets for notebook parameterization
2. **Secret Management** - Use Databricks Secrets, never hardcode credentials
3. **Notebook Organization** - Modular notebooks with %run imports
4. **dbutils Utilities** - Leverage dbutils for file operations and metadata
5. **Workflow Integration** - Design for Databricks Workflows orchestration

## Examples

**✅ Good Patterns:**
```python
# Widgets for parameterization
dbutils.widgets.text("catalog", "dev_catalog", "Catalog Name")
dbutils.widgets.dropdown("env", "dev", ["dev", "staging", "prod"], "Environment")

catalog = dbutils.widgets.get("catalog")
env = dbutils.widgets.get("env")

# Secret management
db_password = dbutils.secrets.get(scope="db_scope", key="password")
api_token = dbutils.secrets.get(scope="api_scope", key="token")

# Use in connection
jdbc_url = f"jdbc:postgresql://host:5432/db?user=admin&password={db_password}"

# Notebook modularity
%run ./common/utils
%run ./common/config

# Use imported functions
transformed_df = apply_common_transformations(df)

# File operations with dbutils
files = dbutils.fs.ls("/Volumes/catalog/schema/volume/")
for file in files:
    if file.name.endswith(".json"):
        process_file(file.path)

# Table metadata
tables = spark.sql("SHOW TABLES IN catalog.schema")
for table in tables.collect():
    print(f"Table: {table.tableName}")
```

**❌ Avoid:**
```python
# Don't hardcode credentials
password = "mypassword123"  # NEVER!

# Don't hardcode environment-specific values
catalog = "prod_catalog"  # Use widgets

# Don't create monolithic notebooks
# 1000+ lines in single notebook is hard to maintain

# Don't use local file paths
path = "/tmp/data.csv"  # Won't work in workflows
```

## Cursor Hook

```markdown
# Databricks-Specific Patterns

When writing Databricks code in this project, ALWAYS follow these Databricks-specific rules:

## Parameterization

1. **Use Widgets**
   - Create widgets for all configurable values
   - Use appropriate widget type (text, dropdown, combobox, multiselect)
   - Provide sensible defaults
   - Document widget purpose in label
   - Remove widgets with dbutils.widgets.removeAll() if needed

2. **Widget Types**
   - text: For flexible string input (table names, paths)
   - dropdown: For limited set of options (environments)
   - combobox: Dropdown with custom value option
   - multiselect: For multiple selections

## Secret Management

1. **Databricks Secrets**
   - ALWAYS use dbutils.secrets.get() for credentials
   - NEVER hardcode passwords, tokens, or API keys
   - NEVER print or log secrets
   - NEVER commit secrets to git
   - Create separate scopes for different credential types

2. **Secret Scopes**
   - Use Azure Key Vault or Databricks-backed scopes
   - Grant appropriate permissions per scope
   - Name scopes descriptively (e.g., "db-prod", "api-keys")
   - Document required secrets in README

## Notebook Organization

1. **Modular Design**
   - Keep notebooks focused (< 300 lines)
   - Extract common code to shared notebooks
   - Use %run to import shared code
   - Organize in folders by function (etl/, utils/, config/)

2. **Code Reuse**
   - Create utility notebooks for common functions
   - Share transformation logic across pipelines
   - Version control shared notebooks
   - Document dependencies clearly

3. **Notebook Structure**
   - Start with docstring describing purpose
   - Define widgets early
   - Import dependencies and shared code
   - Define functions before calling them
   - Include cleanup/teardown at end if needed

## dbutils Utilities

1. **File System Operations**
   - Use dbutils.fs for file operations
   - Works with DBFS, cloud storage, Volumes
   - Better than raw file I/O for distributed systems
   - Returns standardized file information

2. **Notebook Utilities**
   - Use dbutils.notebook.run() for orchestration
   - Pass parameters as dict
   - Handle return values from notebooks
   - Set appropriate timeout values

3. **Metadata Access**
   - Use dbutils.notebook.entry_point for notebook info
   - Get user info with dbutils.notebook.entry_point.getDbutils()
   - Access job context for workflow integration

## Workflow Integration

1. **Design for Workflows**
   - Make notebooks idempotent
   - Use widgets for all parameters
   - Handle failures gracefully
   - Return status/metrics with dbutils.notebook.exit()

2. **Task Dependencies**
   - Define clear inputs and outputs
   - Use task values to pass data between tasks
   - Validate inputs at start of notebook
   - Log progress for monitoring

3. **Error Handling**
   - Catch and log exceptions
   - Use dbutils.notebook.exit("failure") to signal errors
   - Include context in error messages
   - Don't swallow exceptions silently

## Code Templates

### Widget Setup
```python
# Define widgets at notebook start
dbutils.widgets.removeAll()  # Clean slate

dbutils.widgets.text("catalog", "dev_catalog", "Unity Catalog name")
dbutils.widgets.text("schema", "bronze", "Schema name")
dbutils.widgets.dropdown("env", "dev", ["dev", "staging", "prod"], "Environment")
dbutils.widgets.text("date", "", "Processing date (YYYY-MM-DD, empty for today)")

# Get widget values
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
env = dbutils.widgets.get("env")
date = dbutils.widgets.get("date") or str(date.today())

print(f"Processing {catalog}.{schema} for {env} environment on {date}")
```

### Secret Management
```python
# Retrieve secrets
db_host = dbutils.secrets.get(scope="database", key="host")
db_user = dbutils.secrets.get(scope="database", key="username")
db_password = dbutils.secrets.get(scope="database", key="password")

# Use in connection (password not exposed in logs)
jdbc_url = f"jdbc:postgresql://{db_host}:5432/mydb"
connection_properties = {
    "user": db_user,
    "password": db_password,
    "driver": "org.postgresql.Driver"
}

df = spark.read.jdbc(jdbc_url, "table_name", properties=connection_properties)

# For APIs
api_token = dbutils.secrets.get(scope="external-api", key="token")
headers = {"Authorization": f"Bearer {api_token}"}
```

### Modular Notebooks
```python
# Main notebook: etl/process_sales.py
"""
Sales Data Processing Pipeline

Processes daily sales data from raw to gold layer.
Requires: catalog, schema, date widgets
"""

# Import shared code
%run ../utils/common_functions
%run ../utils/validation_rules
%run ../config/table_config

# Get parameters
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# Use imported functions
raw_df = read_raw_sales(catalog, schema)
validated_df = validate_sales_data(raw_df)
final_df = apply_business_rules(validated_df)

# Write output
write_to_gold_layer(final_df, catalog, schema)
```

### dbutils File Operations
```python
# List files in Volume
files = dbutils.fs.ls("/Volumes/catalog/schema/raw_data/")

# Filter and process
json_files = [f for f in files if f.name.endswith(".json")]
print(f"Found {len(json_files)} JSON files")

for file_info in json_files:
    print(f"Processing {file_info.path}")
    df = spark.read.json(file_info.path)
    process_and_save(df)

    # Move to processed folder
    dbutils.fs.mv(
        file_info.path,
        f"/Volumes/catalog/schema/processed/{file_info.name}"
    )

# Check if path exists
if dbutils.fs.ls("/Volumes/catalog/schema/output/"):
    print("Output directory exists")
```

### Notebook Orchestration
```python
# Parent notebook: orchestrate_pipeline.py

try:
    # Run bronze layer
    bronze_result = dbutils.notebook.run(
        path="./etl/bronze_layer",
        timeout_seconds=3600,
        arguments={
            "catalog": "prod_catalog",
            "date": "2024-01-01"
        }
    )
    print(f"Bronze layer result: {bronze_result}")

    # Run silver layer (depends on bronze)
    silver_result = dbutils.notebook.run(
        path="./etl/silver_layer",
        timeout_seconds=3600,
        arguments={
            "catalog": "prod_catalog",
            "date": "2024-01-01"
        }
    )
    print(f"Silver layer result: {silver_result}")

    # Success
    dbutils.notebook.exit("SUCCESS")

except Exception as e:
    print(f"Pipeline failed: {str(e)}")
    dbutils.notebook.exit(f"FAILURE: {str(e)}")
```

### Error Handling and Logging
```python
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_with_error_handling():
    """Process data with proper error handling."""
    try:
        # Get parameters
        catalog = dbutils.widgets.get("catalog")
        table_name = dbutils.widgets.get("table_name")

        logger.info(f"Starting processing for {catalog}.{table_name}")
        start_time = datetime.now()

        # Process
        df = spark.table(f"{catalog}.{table_name}")
        result_df = transform_data(df)
        result_df.write.saveAsTable(f"{catalog}.{table_name}_processed")

        # Log success metrics
        duration = (datetime.now() - start_time).total_seconds()
        row_count = result_df.count()
        logger.info(f"Completed in {duration}s, processed {row_count} rows")

        # Return success
        result = {
            "status": "SUCCESS",
            "rows_processed": row_count,
            "duration_seconds": duration
        }
        dbutils.notebook.exit(str(result))

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)

        # Return failure with context
        result = {
            "status": "FAILURE",
            "error": str(e),
            "table": f"{catalog}.{table_name}"
        }
        dbutils.notebook.exit(str(result))

# Run
process_with_error_handling()
```

### Table Metadata and Management
```python
# Get table metadata
table_name = "catalog.schema.table"

# Describe table details
detail = spark.sql(f"DESCRIBE DETAIL {table_name}").collect()[0]
print(f"Format: {detail.format}")
print(f"Location: {detail.location}")
print(f"Num files: {detail.numFiles}")
print(f"Size: {detail.sizeInBytes / 1e9:.2f} GB")

# Get table history
history = spark.sql(f"DESCRIBE HISTORY {table_name}").limit(5)
history.show(truncate=False)

# Get table properties
properties = spark.sql(f"SHOW TBLPROPERTIES {table_name}")
properties.show(truncate=False)

# List all tables in schema
tables = spark.sql("SHOW TABLES IN catalog.schema")
for table in tables.collect():
    print(f"Table: {table.tableName}, Is Temp: {table.isTemporary}")
```

## Validation Checklist

For Databricks notebooks:
- [ ] Widgets defined for all parameters
- [ ] Secrets used for credentials (never hardcoded)
- [ ] Shared code extracted to utility notebooks
- [ ] File operations use dbutils.fs
- [ ] Error handling with try/except
- [ ] Status returned with dbutils.notebook.exit()
- [ ] Notebook is idempotent (safe to rerun)
- [ ] Dependencies clearly documented
```

