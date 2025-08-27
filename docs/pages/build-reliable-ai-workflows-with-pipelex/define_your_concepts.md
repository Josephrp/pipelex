# Defining Your Concepts

Concepts are the foundation of reliable AI workflows. They define what flows through your pipes—not just as data types, but as meaningful pieces of knowledge with clear boundaries and validation rules.

## Writing Concept Definitions

Every concept starts with a natural language definition. This definition serves two audiences: developers who build with your pipeline, and the LLMs that process your knowledge.

### Basic Concept Definition

The simplest way to define a concept is with a descriptive sentence:

```toml
[concept]
Invoice = "A commercial document issued by a seller to a buyer"
Employee = "A person employed by an organization"
ProductReview = "A customer's evaluation of a product or service"
```

Those concepts will be Text-based by default. If you want to use sutrctured output, you need to create a Python class for the concept, or declare the structure directly in the concept definition. 

**Key principles for concept definitions:**

1. **Define what it is, not what it's for**
   ```toml
   # ❌ Wrong: includes usage context
   TextToSummarize = "Text that needs to be summarized"
   
   # ✅ Right: defines the essence
   Article = "A written composition on a specific topic"
   ```

2. **Use singular forms**
   ```toml
   # ❌ Wrong: plural form
   Invoices = "Commercial documents from sellers"
   
   # ✅ Right: singular form
   Invoice = "A commercial document issued by a seller to a buyer"
   ```

3. **Avoid unnecessary adjectives**
   ```toml
   # ❌ Wrong: includes subjective qualifier
   LongArticle = "A lengthy written composition"
   
   # ✅ Right: neutral definition
   Article = "A written composition on a specific topic"
   ```

### Organizing Related Concepts

Group concepts that naturally belong together in the same domain. A domain acts as a namespace for a set of related concepts and pipes, helping you organize and reuse your pipeline components. You can learn more about them in [Kick off a Knowledge Pipeline Project](kick-off-a-knowledge-pipeline-project.md#what-are-domains).

```toml
# pipelex_libraries/pipelines/finance.toml
domain = "finance"
description = "Financial document processing"

[concept]
Invoice = "A commercial document issued by a seller to a buyer"
Receipt = "Proof of payment for goods or services"
PurchaseOrder = "A buyer's formal request to purchase goods or services"
PaymentTerms = "Conditions under which payment is to be made"
LineItem = "An individual item or service listed in a financial document"
```

## Adding Structure with Python Models

While text definitions help LLMs understand your concepts, Python models ensure structured, validated outputs. This combination gives you the best of both worlds: AI flexibility with software reliability.

**Important**: If you don't create a Python class for a concept, it defaults to text-based content. Only create Python models when you need structured output with specific fields.

### Creating Your First Structured Model

For each concept that needs structured output, create a corresponding Python class:

```python
# pipelex_libraries/pipelines/finance.py
from datetime import datetime
from typing import List, Optional
from pydantic import Field
from pipelex.core.stuffs.stuff_content import StructuredContent

class Invoice(StructuredContent):
    invoice_number: str
    issue_date: datetime
    due_date: datetime
    vendor_name: str
    customer_name: str
    total_amount: float = Field(ge=0, description="Total invoice amount")
    currency: str = Field(default="USD", description="Three-letter currency code")
    line_items: List[str] = Field(default_factory=list)
```

The model name must match the concept name exactly: `Invoice` concept → `Invoice` class.

### Basic Validation Examples

Use Pydantic's validation features to ensure data quality:

```python
from pydantic import field_validator
from pipelex.core.stuffs.stuff_content import StructuredContent

class Employee(StructuredContent):
    name: str
    email: str
    department: str
    years_of_experience: int = Field(ge=0, le=50, description="Years of work experience")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

class ProductReview(StructuredContent):
    product_name: str
    reviewer_name: str
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: str
    verified_purchase: bool = False
```

### Working with Optional Fields

Not all data is always available. Use Optional fields with sensible defaults:

```python
from typing import Optional
from datetime import datetime
from pipelex.core.stuffs.stuff_content import StructuredContent

class Meeting(StructuredContent):
    title: str
    scheduled_date: datetime
    duration_minutes: int = Field(ge=15, le=480, description="Meeting duration")
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    is_recurring: bool = False
```

### Linking Concepts to Models

The connection between TOML definitions and Python models happens automatically through naming:

```toml
# pipelex_libraries/pipelines/hr.toml
domain = "hr"

[concept]
Employee = "A person employed by an organization"
Meeting = "A scheduled gathering of people for discussion"
PerformanceReview = "An evaluation of an employee's work performance"
Department = "An organizational unit within a company"  # No Python model => text-based
```

```python
# pipelex_libraries/pipelines/hr.py
from pipelex.core.stuffs.stuff_content import StructuredContent
from datetime import datetime
from typing import List, Optional

# Only define models for concepts that need structure
class Employee(StructuredContent):
    name: str
    email: str
    department: str
    hire_date: datetime

class Meeting(StructuredContent):
    title: str
    scheduled_date: datetime
    duration_minutes: int
    attendees: List[str]

class PerformanceReview(StructuredContent):
    employee_name: str
    review_period: str
    rating: int = Field(ge=1, le=5)
    strengths: List[str]
    areas_for_improvement: List[str]

# Note: Department concept has no Python model, so it's text-based
```

## Concept Refinement and Inheritance

Sometimes concepts build on each other. A `Contract` is a kind of `Document`. A `NonCompeteClause` is a specific part of a `Contract`. Pipelex lets you express these relationships.

### Declaring Concept Refinement

Use the `refines` field to indicate when one concept is a more specific version of another:

```toml
[concept]
Document = "A written or printed record"

[concept.Contract]
definition = "A legally binding agreement between parties"
refines = "Text"

[concept.ContractLogo]
definition = "A logo associated with a contract"
refines = "Image"
```

### Why Refinement Matters

Concept refinement helps in two ways:

1. **Semantic clarity**: Makes relationships between concepts explicit
2. **Pipeline flexibility**: Pipes accepting general concepts can work with refined ones
3. **Validation**: You can only refine Native concepts **for now** (Text, Image, PDF, TextAndImages, Number, Page)

For example, a pipe that processes `Document` can also process `Contract` or `EmploymentContract`:

```toml
[pipe.extract_key_points]
type = "PipeLLM"
description = "Extract main points from any document"
inputs = { doc = "Document" }  # Can accept Document, Contract, or EmploymentContract
output = "KeyPoints"
```

## Native Concepts and Their Structures

Pipelex includes several built-in native concepts that cover common data types in AI workflows. These concepts come with predefined structures and are automatically available in all pipelines.

### Available Native Concepts

Here are all the native concepts you can use out of the box:

| Concept | Description | Content Class Name |
|---------|-------------|---------------|
| `Text` | A text | `TextContent` |
| `Image` | An image | `ImageContent` |
| `PDF` | A PDF document | `PDFContent` |
| `TextAndImages` | A text combined with images | `TextAndImagesContent` |
| `Number` | A number | `NumberContent` |
| `Page` | The content of a document page with text, images, and optional page view | `PageContent` |
| `Dynamic` | A dynamic concept that can adapt to context | `DynamicContent` |
| `LlmPrompt` | A prompt for an LLM | *No specific implementation* |
| `Anything` | A concept that can represent any type of content | *No specific implementation* |

### Native Concept Structures

Each native concept has a corresponding Python structure that defines its data model:

#### TextContent
```python
class TextContent(StuffContent):
    text: str
```

#### ImageContent
```python
class ImageContent(StuffContent):
    url: str
    source_prompt: Optional[str] = None
    caption: Optional[str] = None
    base_64: Optional[str] = None
```

#### PDFContent
```python
class PDFContent(StuffContent):
    url: str
```

#### NumberContent
```python
class NumberContent(StuffContent):
    number: Union[int, float]
```

#### TextAndImagesContent
```python
class TextAndImagesContent(StuffContent):
    text: Optional[TextContent]
    images: Optional[List[ImageContent]]
```

#### PageContent
```python
class PageContent(StructuredContent):
    text_and_images: TextAndImagesContent
    page_view: Optional[ImageContent] = None
```

#### DynamicContent
```python
class DynamicContent(StuffContent):
    # Dynamic content that can adapt to context
    # Structure is flexible and determined at runtime
    pass
```

**Note**: `LlmPromptContent` and `AnythingContent` are referenced in the native concept definitions but do not have actual implementations in the current codebase. They are handled through the generic content system.

### Using Native Concepts

Native concepts can be used directly in your pipeline definitions without any additional setup:

```toml
[pipe.analyze_document]
type = "PipeLLM"
description = "Analyze a PDF document"
inputs = { document = "PDF" }
output = "Text"
prompt_template = "Analyze this document and provide a summary"

[pipe.process_image]
type = "PipeLLM"
description = "Describe an image"
inputs = { photo = "Image" }
output = "Text"
prompt_template = "Describe what you see in this image"

[pipe.extract_from_page]
type = "PipeLLM"
description = "Extract information from a document page"
inputs = { page_content = "Page" }
output = "ExtractedInfo"
prompt_template = "Extract key information from this page content"
```

### Refining Native Concepts

You can create more specific concepts by refining native ones:

```toml
[concept.Invoice]
definition = "A commercial document issued by a seller to a buyer"
refines = "PDF"

[concept.ProductPhoto]
definition = "A photograph of a product for marketing purposes"
refines = "Image"

[concept.ContractPage]
definition = "A page from a legal contract document"
refines = "Page"
```

When you refine a native concept, your refined concept inherits the structure of the native concept but can be used in more specific contexts. This allows for better semantic clarity while maintaining compatibility with pipes that accept the base native concept.

With well-defined concepts—both in natural language and code—your pipelines gain clarity, reliability, and maintainability. Next, we'll see how to build pipes that transform these concepts.