# Migration Guide

This document provides guidance for migrating between different versions of Pipelex that introduce breaking changes.

## Version 0.6.11: Concept Definition Syntax Change

### Breaking Change

In version 0.6.11, we changed the syntax for defining concepts in TOML library files. The key name for concept definitions has changed from `Concept` to `definition`.

### What Changed

**Old syntax (before v0.6.11):**
```toml
[concept.MyConceptName]
Concept = "Description of the concept"
refines = "BaseConceptName"
```

**New syntax (v0.6.11+):**
```toml
[concept.MyConceptName]
definition = "Description of the concept"
refines = "BaseConceptName"
```

### Why This Change

This change improves consistency in our TOML schema by:
- Using more descriptive field names (`definition` instead of `Concept`)
- Aligning with the internal `ConceptBlueprint` data structure
- Making the TOML files more self-documenting and intuitive

### Migration Process

#### Automatic Migration

Use the built-in migration command to automatically update your TOML files:

```bash
# Preview changes without applying them
pipelex migrate --dry-run

# Apply the migration to all TOML files
pipelex migrate
```

The migration command will:
- Find all `.toml` files in your configured pipelines directory
- Replace `Concept =` with `definition =` in concept definitions
- Preserve all other formatting and comments
- Create backups of modified files (with `.backup` extension)

#### Manual Migration

If you prefer to migrate manually or need to handle special cases:

1. **Locate your TOML files**: Find all pipeline library files (typically in your configured pipelines directory)
2. **Update concept definitions**: Change `Concept =` to `definition =` in all `[concept.ConceptName]` sections
3. **Validate syntax**: Run `pipelex validate` to ensure your files are correctly formatted

### Examples

#### Simple Concept Definition

**Before:**
```toml
[concept.Article]
Concept = "A written composition on a specific topic"
refines = "Text"
```

**After:**
```toml
[concept.Article]
definition = "A written composition on a specific topic"
refines = "Text"
```

#### Complex Concept with Structure

**Before:**
```toml
[concept.Photo]
Concept = "Photo"
structure = "ImageContent"
refines = "Image"
```

**After:**
```toml
[concept.Photo]
definition = "Photo"
structure = "ImageContent"
refines = "Image"
```

### Validation

After migration, validate your pipeline files:

```bash
# Validate all pipeline files
pipelex validate

# Run a specific pipeline to test
pipelex run your-pipeline-name
```

### Troubleshooting

**Error: "ConceptBlueprint validation failed"**
- Check that all `Concept =` entries have been changed to `definition =`
- Ensure no typos were introduced during migration
- Verify TOML syntax is still valid

**Error: "Failed to load TOML file"**
- Check file permissions
- Ensure TOML syntax is valid (no missing quotes, brackets, etc.)
- Review any custom modifications that might conflict

### Rollback

If you need to rollback the migration:
1. Stop using the new version of Pipelex
2. Restore from the `.backup` files created during migration
3. Or manually change `definition =` back to `Concept =`

---

For additional help or if you encounter issues during migration, please [open an issue](https://github.com/Pipelex/pipelex/issues) on our GitHub repository.