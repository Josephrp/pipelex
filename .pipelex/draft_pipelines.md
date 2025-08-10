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

Describe the pipeline flow using concise step notation:

```markdown
## Flow

WorkingMemory starts with: {input_name, another_input}

### Step 1: Process input data
LLM[process]: (input_name) → intermediate_result

WorkingMemory now contains: {input_name, another_input, intermediate_result}

### Step 2: Synthesize results with additional context
LLM[synthesize]: (intermediate_result, another_input) → final_output

WorkingMemory now contains: {input_name, another_input, intermediate_result, final_output}
```

### Output Section
```markdown
## Output
Returns: `final_output` - Description of the final result
```

## Pipe Types and Notation

## Operator Notations

**Important**: During drafting, DO NOT write actual prompts or prompt templates. Focus on describing what each operator does and how data flows. Prompts will be written during implementation.

### LLM Operations (including vision, to generate text from text and images)
```markdown
LLM[purpose]: (inputs) → output

Examples:
LLM[summarize]: (long_text) → summary
LLM[analyze]: (document, criteria) → analysis
```

### OCR Operations (to extract text and images from PDF pages, including full page views)
```markdown
OCR: (pdf_document) → pages_list
```

### Image Generation (to generate images from text prompts)
```markdown
ImgGen: (prompt_text) → generated_image
```

### Function Operations (to call external python functions)
```markdown
Func[function_name]: (data) → result
```

### Sequential Processing (to run steps in sequence, use it when steps need results from previous steps)
```markdown
Step 1: Process input data
process_input → result_1

Step 2: Analyze processed results  
analyze(result_1) → result_2

Step 3: Finalize with original context
finalize(result_2, original_input) → final_output
```

### Batch Processing (to process each item in a list independently and in parallel)
```markdown
Process each item in list_of_items:
process_single(item) → processed_item

Collect all results → processed_items_list
```

### Parallel Processing (to run different pipes in parallel from the same memory, use it when steps can be run independently, each with a copy of the working memory)
```markdown
Parallel execution:

Branch A: Process applying pipe A
pipe_a(input) → result_a

Branch B: Process applying pipe B  
pipe_b(input) → result_b

Combine: Merge parallel results
merge(result_a, result_b) → combined_result
```

### Conditional Processing (to run different pipes based on a condition)
```markdown
Route based on expression(input_data):

Case "option_1": Handle option 1
pipe_a(input_data) → result

Case "option_2": Handle option 2
pipe_b(input_data) → result

Default: Handle other cases
pipe_default(input_data) → result
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

### Step 1: Extract content from PDF
OCR: (raw_document) → pages

WorkingMemory: {raw_document, pages}

### Step 2: Summarize each page in parallel
Process each page in pages:
LLM[summarize]: (page) → page_summary

Collect all results → page_summaries

WorkingMemory: {raw_document, pages, page_summaries}

### Step 3: Create comprehensive analysis from summaries
LLM[synthesize]: (page_summaries) → final_analysis

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

### Step 1: Classify query into support category
LLM[classify]: (query) → query_type

WorkingMemory: {query, context, query_type}

### Step 2: Route to appropriate support handler
Route based on query_type:

Case "technical": Technical support handler
LLM[technical_support]: (query, context) → response

Case "billing": Billing support handler
LLM[billing_support]: (query, context) → response

Default: General support handler
LLM[general_support]: (query) → response

WorkingMemory: {query, context, query_type, response}

## Output
Returns: `response`
```

## Best Practices

1. **Name consistently**: Once you name a result (e.g., `analyzed_data`), use that exact name when referencing it later.

2. **Show memory state**: After complex steps, show what's in WorkingMemory to track data flow.

3. **Be explicit about inputs**: For each operator step, clearly indicate which items from WorkingMemory are being used.

4. **Use descriptive names**: Instead of `result_1`, use `extracted_entities` or `summarized_content`.

5. **Concise step descriptions**: Each step should have a clear title that describes what it accomplishes. Avoid repeating the same information in multiple places.

6. **No prompts during drafting**: Focus on describing WHAT each step does, not HOW (the actual prompts). Prompts are implementation details added later.

7. **Block vs Inline references**:
   - Use `@variable_name` notation for block insertions (multi-line content)
   - Use `$variable_name` notation for inline insertions (single values in sentences)

8. **Batch operations**: When processing lists, clearly indicate:
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
- [ ] Each step has a concise, non-repetitive description

## From Draft to Implementation

Once your markdown draft is complete, it can be translated into:
1. A formal TOML pipeline definition with explicit pipe declarations
2. Python structure classes for complex data types (when needed)
3. Validated, executable Pipelex pipeline code

The narrative draft serves as both documentation and a blueprint for implementation, making the pipeline's logic transparent and maintainable.
