# Migration Guide

This document provides guidance for migrating between different versions of Pipelex that introduce breaking changes.

## Concepts Migration

### Breaking Change

We changed the syntax for defining concepts in TOML library files. The key name for concept definitions has changed from `Concept` to `definition`.

### What Changed

**Old syntax:**
```toml
[concept.MyConceptName]
Concept = "Description of the concept"
refines = "BaseConceptName"
```

**New syntax:**
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
3. **Validate syntax**: Run `pipelex validate all` to ensure your files are correctly formatted

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
pipelex validate all

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

## Pipes Migration

### Breaking Change

We changed the syntax for defining pipes in TOML library files. The pipe definition format has been restructured to use explicit `type` and `definition` fields instead of the implicit `PipeClassName = "description"` format.

### What Changed

**Old syntax:**
```toml
[pipe.my_pipe_name]
SomePipeClass = "Description of what this pipe does"
```

**New syntax:**
```toml
[pipe.my_pipe_name]
type = "SomePipeClass"
definition = "Description of what this pipe does"
```

### Why This Change

This change improves consistency and clarity by:

- Making the pipe class type explicit and separate from its description
- Aligning pipe definitions with concept definitions (both use `definition`)
- Improving readability and maintainability of TOML files
- Making it easier to parse and validate pipe configurations

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
- Convert `PipeClassName = "description"` to `type = "PipeClassName"` and `definition = "description"`
- Preserve all other formatting and comments
- Create backups of modified files (with `.backup` extension)

#### Manual Migration

If you prefer to migrate manually:

1. **Locate your TOML files**: Find all pipeline library files
2. **Update pipe definitions**: 
   - Find all `[pipe.pipe_name]` sections
   - Replace `PipeClassName = "description"` with:
     - `type = "PipeClassName"`
     - `definition = "description"`
3. **Validate syntax**: Run `pipelex validate all` to ensure your files are correctly formatted

### Examples

#### Simple Pipe Definition

**Before:**
```toml
[pipe.summarize_article]
TextSummarizer = "Summarize the given article into key points"
```

**After:**
```toml
[pipe.summarize_article]
type = "TextSummarizer"
definition = "Summarize the given article into key points"
```

#### Pipe with Additional Configuration

**Before:**
```toml
[pipe.analyze_sentiment]
SentimentAnalyzer = "Analyze the sentiment of the input text"
model = "bert-base-uncased"
threshold = 0.8
```

**After:**
```toml
[pipe.analyze_sentiment]
type = "SentimentAnalyzer"
definition = "Analyze the sentiment of the input text"
model = "bert-base-uncased"
threshold = 0.8
```

### Deprecation Warning

In the transition period, the old syntax will still work but will generate deprecation warnings:

```
WARNING: Pipe 'my_pipe_name' uses deprecated syntax. Please migrate to new format:
replace this syntax:
```
SomePipeClass = "Description"
```
by this:
```
type = "SomePipeClass"
definition = "Description"
```
Old syntax will be removed in v0.3.0.
```

### Validation

After migration, validate your pipeline files:

```bash
# Validate all pipeline files
pipelex validate all

# Run a specific pipeline to test
pipelex run your-pipeline-name
```

---

For additional help or if you encounter issues during migration, please [open an issue](https://github.com/Pipelex/pipelex/issues) on our GitHub repository.