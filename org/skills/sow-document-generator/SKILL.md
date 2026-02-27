---
name: sow-document-generator
description: Use when creating or filling a Statement of Work (SOW) document from the project SOW template with prompted field inputs and file outputs. Do not use for generic proposal writing, contract legal review, or non-SOW documents.
version: 0.1.2
owner: Alvaro Bezerra
---

# Purpose

Generate a fully filled Statement of Work from a canonical project template by collecting required inputs section-by-section and writing both Markdown and DOCX artifacts.

# When to use

- The user asks to create, fill, or update an SOW from the project template.
- Required SOW fields must be collected interactively before generation.
- The workflow must output files (not only chat text), including `.md` and `.docx`.
- The workflow must default missing fee details (`daily`, `600€`, `5 days/week`) and fixed payment method (`wired transfer / on-chain`).

# When NOT to use

- The request is for a different artifact (PRD, roadmap, ticket, agenda, invoice-only).
- The user asks for legal advice, legal validation, or contract interpretation.
- No template-based SOW generation is requested.

# Inputs

- Template file: `templates/new_statement_of_work_template.md`
- Field schema: `templates/field_schema.yaml`
- Contractor defaults: `project-context/sow/contractor_profile.yaml`
- Runtime values via:
  - interactive mode (`--interactive`), or
  - structured input file (`--input <yaml/json>`)

# Outputs

- Filled Markdown SOW in `docs-output/sow` (or custom `--output-dir`):
  - `{timestamp}_{client_slug}_{project_slug}_sow.md`
- Filled DOCX SOW in same folder:
  - `{timestamp}_{client_slug}_{project_slug}_sow.docx`
- When the user requests Notion output (page content), tables must use Notion block syntax:
  - Use `<table>...</table>` with table rows/cells.
  - Do not use markdown pipe tables (`| ... |`) for Notion content.
- After generating output artifacts, always ask whether to send/publish the generated SOW to Notion.

# Workflow

1. Confirm the request is SOW template filling.
2. Load contractor defaults from `project-context/sow/contractor_profile.yaml`.
3. Run collection in this strict order:
   - Contractor profile override check
   - Prepared For / Date Issued
   - Introduction and Background
   - Period of Performance
   - Scope of Work
   - Fee Schedule
   - Bill To
   - Legal and invoice/custom clause overrides
   - Execution and signature block values
4. Validate required fields, date order, fee rows, and unresolved placeholders.
5. Render Markdown from `templates/new_statement_of_work_template.md`.
6. Convert rendered Markdown to DOCX.
7. Save both artifacts under `docs-output/sow` unless `--output-dir` is provided.
8. Use `DD/MM/YYYY` date format in prompts and output.
9. If partial data is provided, ask only missing fields to complete generation quickly.
10. If output target is Notion, emit fee schedule and other tabular content using Notion `<table>` blocks instead of pipe tables.
11. Immediately after successful generation, ask: "Do you want me to send this to Notion now?"

# Examples

- Input example: `examples/example-input.md`
- Output example: `examples/example-output.md`
