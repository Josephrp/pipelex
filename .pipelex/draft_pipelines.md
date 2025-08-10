# Drafting Pipelex Pipelines

This guide explains how to draft pipelines in natural language using markdown notation before translating them into formal Pipelex definitions.

## Core Concept: WorkingMemory

Every pipeline execution maintains a `WorkingMemory` that acts as a shared data space. When a pipeline starts, the initial inputs are placed in this memory. As each pipe executes, its output is added to the memory with a specific name (the `result` name). Subsequent pipes can access any data in the memory by referencing these names.

**Key Rules**: 
- When a pipe produces an output with name `X`, any later pipe can use `X` as an input. The names must match exactly.
- Controller pipes (PipeSequence, PipeParallel, PipeCondition) automatically inherit the input requirements of their nested operators - you don't need to specify their inputs explicitly.

## Drafting Workflow

1. **Start with the goal**: What does this pipeline accomplish?
2. **Define inputs**: What data does it need to start?
3. **Narrate the flow**: Describe each step and how data flows through WorkingMemory
4. **Specify outputs**: What final result emerges?

## Pipeline Draft Structure

### Header
```markdown
# Pipeline: [pipeline_name]
Domain: [domain_name]
Purpose: [What this pipeline does]
```

### Inputs Section
```markdown
## Inputs
- `input_name` : Description of what this input represents
- `another_input` : Another input description
```

### Flow Section

Describe the pipeline flow narratively, using a pseudo-code style that shows how data moves through WorkingMemory:

```markdown
## Flow

WorkingMemory starts with: {input_name, another_input}

### Step 1: [Description]
Use `input_name` to generate `intermediate_result`
→ LLM[process]: (input_name) → intermediate_result
   Purpose: Processes the input data

WorkingMemory now contains: {input_name, another_input, intermediate_result}

### Step 2: [Description]
Combine `intermediate_result` and `another_input` to create `final_output`
→ LLM[synthesize]: (intermediate_result, another_input) → final_output
   Purpose: Synthesizes the intermediate result with additional context

WorkingMemory now contains: {input_name, another_input, intermediate_result, final_output}
```

### Output Section
```markdown
## Output
Returns: `final_output` - Description of the final result
```

## Pipe Types and Notation

### Sequential Processing (PipeSequence)
```markdown
Step 1: process_input → result_1
Step 2: analyze(result_1) → result_2
Step 3: finalize(result_2, original_input) → final_output
```

### Parallel Processing (PipeParallel)
```markdown
Parallel:
  Branch A: process_method_a(input) → result_a
  Branch B: process_method_b(input) → result_b
Combine: merge(result_a, result_b) → combined_result
```

### Conditional Processing (PipeCondition)
```markdown
If expression(input_data):
  Case "option_1": pipe_a(input_data) → result
  Case "option_2": pipe_b(input_data) → result
  Default: pipe_default(input_data) → result
```

### Batch Processing
```markdown
For each item in `list_of_items`:
  process_single(item) → processed_item
Collect all → processed_items_list
```

## Operator Notations

**Important**: During drafting, DO NOT write actual prompts or prompt templates. Focus on describing what each operator does and how data flows. Prompts will be written during implementation.

### LLM Operations
```markdown
LLM[purpose]: (inputs) → output
Example: LLM[summarize]: (long_text) → summary
```

Describe the purpose without the actual prompt:
```markdown
LLM[analyze]: (document, criteria) → analysis
  Purpose: Analyzes the document based on provided criteria
```

### OCR Operations
```markdown
OCR: (pdf_document) → pages_list
Each page contains text and images
```

### Image Generation
```markdown
ImgGen: (prompt_text) → generated_image
```

### Function Operations
```markdown
Func[calculate_metrics]: (data) → metrics
```

## Memory Flow Examples

### Example 1: Document Analysis Pipeline
```markdown
# Pipeline: analyze_document
Domain: document_analysis
Purpose: Extract and analyze key information from documents

## Inputs
- `raw_document` : PDF document to analyze

## Flow

WorkingMemory: {raw_document}

### Step 1: Extract content
OCR: (raw_document) → pages
WorkingMemory: {raw_document, pages}

### Step 2: Summarize each page
For each page in pages:
  LLM[summarize]: (page) → page_summary
Collect all → page_summaries
WorkingMemory: {raw_document, pages, page_summaries}

### Step 3: Create final analysis
LLM[synthesize]: (page_summaries) → final_analysis
  Purpose: Creates comprehensive analysis from all page summaries
WorkingMemory: {raw_document, pages, page_summaries, final_analysis}

## Output
Returns: `final_analysis`
```

### Example 2: Conditional Processing
```markdown
# Pipeline: smart_responder
Domain: customer_service
Purpose: Route and respond to customer queries

## Inputs
- `query` : Customer question
- `context` : Available context information

## Flow

WorkingMemory: {query, context}

### Step 1: Classify query type
LLM[classify]: (query) → query_type
  Purpose: Classifies the query into a category
WorkingMemory: {query, context, query_type}

### Step 2: Route based on type
If query_type:
  Case "technical": 
    LLM[technical_support]: (query, context) → response
      Purpose: Provides technical support based on query and context
  Case "billing":
    LLM[billing_support]: (query, context) → response
      Purpose: Handles billing-related queries with available context
  Default:
    LLM[general_support]: (query) → response
      Purpose: Provides general assistance for unclassified queries

WorkingMemory: {query, context, query_type, response}

## Output
Returns: `response`
```

## Best Practices

1. **Name consistently**: Once you name a result (e.g., `analyzed_data`), use that exact name when referencing it later.

2. **Show memory state**: After complex steps, show what's in WorkingMemory to track data flow.

3. **Be explicit about inputs**: For each operator step, clearly indicate which items from WorkingMemory are being used. Controller pipes will automatically inherit these requirements.

4. **Use descriptive names**: Instead of `result_1`, use `extracted_entities` or `summarized_content`.

5. **No prompts during drafting**: Focus on describing WHAT each step does (its purpose), not HOW (the actual prompts). Prompts are implementation details added later.

6. **Block vs Inline references**:
   - Use `@variable_name` notation for block insertions (multi-line content)
   - Use `$variable_name` notation for inline insertions (single values in sentences)

7. **Batch operations**: When processing lists, clearly indicate:
   - What list is being iterated (`batch_over`)
   - What each item is called during processing (`batch_as`)
   - What the collected results are named

## Validation Checklist

Before finalizing your draft:

- [ ] Every input used by an operator pipe exists in WorkingMemory (either from initial inputs or previous steps)
- [ ] Every result name is unique (no overwriting unless intentional)
- [ ] The final output exists in WorkingMemory
- [ ] Names are consistent throughout (no typos or variations)
- [ ] The flow clearly shows data transformation from inputs to outputs
- [ ] Each LLM step has a clear purpose (but no actual prompts yet)

## From Draft to Implementation

Once your markdown draft is complete, it can be translated into:
1. A formal TOML pipeline definition with explicit pipe declarations
2. Python structure classes for complex data types (when needed)
3. Validated, executable Pipelex pipeline code

The narrative draft serves as both documentation and a blueprint for implementation, making the pipeline's logic transparent and maintainable.
