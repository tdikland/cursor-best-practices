# Unity Catalog Patterns

Unity Catalog provides unified governance for data and AI assets across clouds. Proper usage ensures security, discoverability, and compliance.

## Key Principles

1. **Three-Level Namespace** - Always use catalog.schema.table
2. **Managed Tables** - Prefer managed over external tables
3. **Metadata Management** - Use properties, tags, and comments
4. **Access Control** - Implement proper grants and ownership
5. **Volumes for Files** - Use Unity Catalog Volumes for unstructured data

## Examples

**✅ Good Patterns:**
```python
# Always use three-level namespace
df = spark.table("prod_catalog.sales.transactions")

# Create managed tables
df.write.mode("overwrite").saveAsTable("catalog.schema.table")

# Add metadata
spark.sql("""
  COMMENT ON TABLE catalog.schema.customers
  IS 'Customer master data with PII'
""")

spark.sql("""
  ALTER TABLE catalog.schema.customers
  SET TAGS ('pii' = 'true', 'domain' = 'sales')
""")

# Use volumes for files
file_path = "/Volumes/catalog/schema/volume_name/data.parquet"
df.write.parquet(file_path)

# Create views for data access patterns
spark.sql("""
  CREATE OR REPLACE VIEW catalog.schema.active_customers AS
  SELECT * FROM catalog.schema.customers
  WHERE status = 'active'
""")
```

**❌ Avoid:**
```python
# Don't use two-level namespace
df = spark.table("schema.table")  # Missing catalog

# Don't use external tables unnecessarily
df.write.option("path", "s3://bucket/path") \
  .saveAsTable("table")  # Prefer managed

# Don't use DBFS for new data
path = "/dbfs/my-data"  # Use Volumes instead

# Don't skip metadata
# Tables without comments/tags are hard to discover
```

## Cursor Hook

```markdown
# Unity Catalog Best Practices

When working with Unity Catalog in this project, ALWAYS follow these rules:

## Namespace Rules

1. **Three-Level Namespace ALWAYS**
   - NEVER use two-level namespace (schema.table)
   - ALWAYS use full path: catalog.schema.table
   - For temporary data, use workspace-specific catalog or temp views
   - Validate catalog exists before creating tables

2. **Managed vs External Tables**
   - DEFAULT to managed tables: `saveAsTable("catalog.schema.table")`
   - Only use external tables for data you don't own or can't move
   - If external, document why in table comment
   - Never mix managed and external carelessly

## Metadata Management

1. **Always Add Documentation**
   - Add table comments describing purpose and data
   - Document column meanings with COMMENT ON COLUMN
   - Add tags for classification (PII, domain, retention)
   - Use properties for operational metadata

2. **Table Properties and Tags**
   - Tag PII data: `'pii' = 'true'`
   - Tag business domain: `'domain' = 'sales'`
   - Set retention: `'retention_days' = '90'`
   - Document data owner: `'owner' = 'team-name'`

## Storage Patterns

1. **Use Volumes for Files**
   - For unstructured data (CSV, JSON, Parquet files): use Volumes
   - Path format: `/Volumes/catalog/schema/volume_name/file.ext`
   - Don't use DBFS root for new data
   - Don't use external cloud storage paths directly

2. **Table Organization**
   - Group related tables in same schema
   - Use descriptive schema names (not just "default")
   - Create separate catalogs for environments (dev, staging, prod)
   - Use views to create logical data access layers

## Code Templates

### Create Managed Table
```python
df.write.format("delta") \
  .mode("overwrite") \
  .option("comment", "Description of table purpose") \
  .saveAsTable("catalog.schema.table_name")
```

### Add Metadata
```python
spark.sql("""
  ALTER TABLE catalog.schema.table
  SET TAGS ('pii' = 'false', 'domain' = 'analytics')
""")

spark.sql("""
  COMMENT ON TABLE catalog.schema.table
  IS 'Detailed description of what this table contains'
""")

spark.sql("""
  ALTER TABLE catalog.schema.table
  ALTER COLUMN email
  COMMENT 'Customer email address - PII field'
""")
```

### Use Volumes
```python
# Write to volume
output_path = "/Volumes/catalog/schema/raw_files/output.parquet"
df.write.mode("overwrite").parquet(output_path)

# Read from volume
input_path = "/Volumes/catalog/schema/raw_files/input/*.json"
df = spark.read.json(input_path)
```

### Create View with Access Pattern
```python
spark.sql("""
  CREATE OR REPLACE VIEW catalog.schema.customer_summary AS
  SELECT
    customer_id,
    name,
    region,
    total_purchases
  FROM catalog.schema.customers
  WHERE is_active = true
""")
```

## Validation Checklist

Before creating Unity Catalog objects:
- [ ] Using three-level namespace (catalog.schema.object)
- [ ] Table comment describes purpose
- [ ] Appropriate tags applied (PII, domain, etc.)
- [ ] Using managed table unless external required
- [ ] Files stored in Volumes, not DBFS root
- [ ] Schema organization is logical
```

