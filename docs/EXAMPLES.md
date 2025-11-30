# Markdown Merger Examples

This document provides practical examples of using Markdown Merger for common tasks.

---

## Example 1: Basic Documentation Merge

**Scenario**: You have a documentation folder with multiple markdown files and want to create a single reference document.

### Input Structure
```
docs/
├── introduction.md
├── getting-started.md
├── configuration.md
├── api-reference.md
└── troubleshooting.md
```

### Steps

1. **Open Markdown Merger**

2. **Add the docs folder**:
   - Click "📁 Add Folder"
   - Select the `docs/` folder

3. **Select preset**:
   - Choose "documentation" from the preset dropdown

4. **Configure output**:
   - Set output to `docs/complete-guide.md`

5. **Start merge**

### Result

```markdown
# Table of Contents
- [introduction](#introduction)
- [getting-started](#getting-started)
- [configuration](#configuration)
- [api-reference](#api-reference)
- [troubleshooting](#troubleshooting)

---

# introduction

Welcome to our project...

---

# getting-started

To get started, first install...

---

[...more sections...]
```

---

## Example 2: AI Knowledge Base Creation

**Scenario**: You're building a RAG (Retrieval Augmented Generation) system and need to prepare your markdown content for ingestion.

### Input Structure
```
knowledge-base/
├── products/
│   ├── product-a.md
│   ├── product-b.md
│   └── product-c.md
├── policies/
│   ├── return-policy.md
│   ├── shipping-policy.md
│   └── privacy-policy.md
└── faq/
    ├── general-faq.md
    ├── technical-faq.md
    └── billing-faq.md
```

### Steps

1. **Add the knowledge-base folder**

2. **Select the "ai_knowledge_base" preset**
   - This enables:
     - Document metadata
     - Semantic markers
     - Chunk hints
     - Table of contents

3. **Open Advanced Settings**:
   - Enable "Extract Keywords"
   - Set "Include File Path" to true

4. **Set output path**

5. **Start merge**

### Result

```markdown
# Table of Contents
- [product-a](#product-a)
- [product-b](#product-b)
...

---

<!-- DOC_META: {"source": "products/product-a.md", "index": 1, "size": 2048, "modified": "2025-11-30", "keywords": ["Product A", "Features", "Specifications"]} -->
<document id="doc_0001" source="product-a.md">
<!-- CHUNK_BOUNDARY: doc_0001 -->

## product-a
*Source: `knowledge-base/products/product-a.md`*
*Document 1 of 9*

# Product A

Product A is our flagship offering...

## Features

- Feature 1
- Feature 2
- Feature 3

## Specifications

| Spec | Value |
|------|-------|
| Size | Large |
| Color | Blue |

</document>

---

<!-- DOC_META: {"source": "products/product-b.md", "index": 2, ...} -->
<document id="doc_0002" source="product-b.md">
...
</document>
```

### Why This Works for AI

- **Semantic markers** (`<document>...</document>`) help chunking algorithms identify document boundaries
- **Metadata comments** provide structured information for indexing
- **Chunk hints** suggest optimal split points for RAG systems
- **Keywords** improve search and retrieval

---

## Example 3: Blog Post Archive

**Scenario**: You have years of blog posts and want to create a single archive file.

### Input Structure
```
blog/
├── 2023/
│   ├── 01-january-update.md
│   ├── 02-new-features.md
│   └── ...
├── 2024/
│   ├── 01-year-in-review.md
│   ├── 02-roadmap.md
│   └── ...
└── 2025/
    └── ...
```

### Steps

1. **Add the blog folder**

2. **Configure sorting**:
   - Open Advanced Settings
   - Set Sort Order to "natural" (handles numbers correctly)
   - Set Sort Ascending to true

3. **Configure structure**:
   - Header style: `### {name}`
   - Include file path: yes
   - Separator: `---`

4. **Configure content**:
   - Strip front matter: yes (blog posts often have YAML metadata)
   - Normalize whitespace: yes

5. **Set output and merge**

### Result

```markdown
### 01-january-update
*Source: `blog/2023/01-january-update.md`*
*Document 1 of 50*

Happy New Year! Here's our January update...

---

### 02-new-features
*Source: `blog/2023/02-new-features.md`*
*Document 2 of 50*

We're excited to announce new features...

---

[...more posts in chronological order...]
```

---

## Example 4: Research Notes Compilation

**Scenario**: You have research notes scattered across multiple folders and want to compile them for a paper.

### Input

Mixed markdown files with various formatting, front matter, and different heading levels.

### Configuration

```json
{
  "header_style": "## {name}",
  "include_file_path": true,
  "include_doc_index": false,
  "separator_style": "***",
  "separator_blank_lines": 3,
  "generate_toc": true,
  "toc_depth": 3,
  "adjust_header_level": 1,
  "strip_front_matter": true,
  "normalize_whitespace": true,
  "max_consecutive_blanks": 2
}
```

### Key Settings Explained

- **adjust_header_level: 1**: Shifts all headers down one level, so `# Heading` becomes `## Heading`. This prevents conflicts with the document title headers.
- **separator_blank_lines: 3**: Adds more visual separation between notes
- **toc_depth: 3**: Creates a detailed table of contents

---

## Example 5: Code Documentation

**Scenario**: You have markdown documentation alongside code in multiple packages.

### Input Structure
```
packages/
├── core/
│   ├── README.md
│   └── docs/
│       ├── api.md
│       └── examples.md
├── utils/
│   ├── README.md
│   └── docs/
│       └── helpers.md
└── cli/
    ├── README.md
    └── docs/
        └── commands.md
```

### Configuration

Use the "documentation" preset with these modifications:

- **Include patterns**: `*.md`
- **Exclude patterns**: `CHANGELOG.md`, `LICENSE.md`
- **Sort order**: alphabetical
- **Recursive**: true

### Result

Creates a unified API reference with all package documentation combined.

---

## Example 6: Minimal Merge

**Scenario**: You just want to concatenate files with no extras.

### Configuration

Use the "basic" preset:

```json
{
  "header_style": "## {name}",
  "generate_toc": false,
  "add_metadata": false,
  "add_semantic_markers": false,
  "strip_front_matter": true
}
```

### Result

Just the content with minimal headers:

```markdown
## file1

Content of file 1...

---

## file2

Content of file 2...
```

---

## Example 7: Custom Separator and Header

**Scenario**: You need a specific format for your output.

### Custom Header Template

```
=== {name} ===
```

### Custom Separator

```
<!-- ========================== -->
```

### Result

```markdown
=== document-one ===
*Document 1 of 3*

Content here...

<!-- ========================== -->

=== document-two ===
*Document 2 of 3*

More content...
```

---

## Example 8: Processing 1000+ Files

**Scenario**: You have a large documentation project with over 1000 markdown files.

### Recommended Settings

1. **Disable non-essential features**:
   - Extract keywords: OFF (slow for large sets)
   - Detect duplicates: OFF (unless needed)

2. **Use simpler TOC**:
   - TOC depth: 1 (just document names)
   - TOC style: plain (no links)

3. **Optimize output**:
   - Normalize whitespace: ON (reduces file size)
   - Max consecutive blanks: 1

4. **Monitor progress**:
   - Keep the log panel visible
   - Note any warnings or errors

### Performance Tips

- Process in batches if experiencing memory issues
- Close other applications during large merges
- Use SSD for faster I/O

---

## Saving and Reusing Configurations

### Save Your Settings

1. Configure everything as desired
2. File → Save Configuration
3. Choose a descriptive name: `my-ai-knowledge-base.json`

### Load for Future Use

1. File → Load Configuration
2. Select your saved `.json` file
3. All settings are restored instantly

### Share Configurations

Configuration files are portable. You can:
- Share with team members
- Include in project repositories
- Create templates for different use cases

---

## Tips for Best Results

1. **Preview before merging**: Use the preview pane to check formatting
2. **Test with subset first**: Try 5-10 files before processing thousands
3. **Check the log**: Review for warnings about duplicates or errors
4. **Validate output**: Open the merged file in your markdown editor
5. **Backup important data**: Enable backup option for safety

---

*Have a use case not covered here? Open an issue and we'll add it!*
