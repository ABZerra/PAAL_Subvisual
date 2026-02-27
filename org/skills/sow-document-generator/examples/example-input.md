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
  "date_issued": "2026-03-02",
  "client_legal_name": "Acme Corp, Inc.",
  "project_title": "Website Redesign and Development",
  "project_summary": "website redesign and development services",
  "start_date": "2026-03-10",
  "end_date": "2026-04-10",
  "non_working_days": ["2026-03-19"],
  "project_description": "Complete redesign and frontend/backend implementation.",
  "deliverables": [
    "Website redesign",
    "Website development",
    "QA and launch support"
  ],
  "fee_schedule": [
    {
      "team": "Product",
      "role": "Product Manager",
      "fee": "850 EUR/day",
      "schedule": "2 days/week",
      "duration": "4 weeks",
      "cost_estimation": "6800 EUR"
    },
    {
      "team": "Engineering",
      "role": "Developer",
      "fee": "850 EUR/day",
      "schedule": "4 days/week",
      "duration": "4 weeks",
      "cost_estimation": "13600 EUR"
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
    "company_signing_date": "2026-03-02",
    "client_name": "Acme Corp, Inc.",
    "client_signing_date": "2026-03-02",
    "client_address": "100 Market Street, San Francisco, CA"
  },
  "overrides": {
    "payment_method": "Wired transfer",
    "invoice_model": "Monthly fee"
  }
}
```
