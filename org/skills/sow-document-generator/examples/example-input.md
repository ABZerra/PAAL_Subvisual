# Example Input: sow-document-generator

Generate a new Statement of Work using the project template.

Constraints:
- Ask for all required fields section-by-section.
- Keep signature lines blank.
- Write outputs to the default folder.

Structured input file example (`--input sample.json`):

```json
{
  "prepared_for": "Acme Corp",
  "date_issued": "02/03/2026",
  "prepared_by_name": "Roberto Machado",
  "prepared_by_role": "CEO",
  "client_legal_name": "Acme Corp, Inc.",
  "project_title": "Website Redesign and Development",
  "project_summary": "website redesign and development services",
  "start_date": "10/03/2026",
  "end_date": "10/04/2026",
  "non_working_days": ["19/03/2026"],
  "project_description": "Complete redesign and frontend/backend implementation.",
  "deliverables": [
    "Website redesign",
    "Website development",
    "QA and launch support"
  ],
  "fee_schedule": [
    {
      "fee_type": "daily",
      "role": "Product Manager",
      "fee": "600€",
      "allocation": "5 days/week",
      "duration": "4 weeks",
      "estimation": "6800 EUR"
    },
    {
      "fee_type": "daily",
      "role": "Developer",
      "fee": "600€",
      "allocation": "5 days/week",
      "duration": "4 weeks",
      "estimation": "13600 EUR"
    }
  ],
  "project_cost_total": "20400 EUR",
  "cost_resume_title": "Website Redesign + Development, 4 weeks",
  "cost_resume_value": "20400 EUR",
  "bill_to": {
    "client": "Acme Corp, Inc.",
    "address": "100 Market Street, San Francisco, CA",
    "email": "finance@acme.com"
  },
  "execution": {
    "company_signing_date": "02/03/2026",
    "client_name": "Acme Corp, Inc.",
    "client_signing_date": "02/03/2026",
    "client_address": "100 Market Street, San Francisco, CA"
  },
  "overrides": {
    "invoice_model": "Monthly fee"
  }
}
```
