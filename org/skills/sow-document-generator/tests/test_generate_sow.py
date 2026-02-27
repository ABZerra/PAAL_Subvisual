from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "generate_sow.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("generate_sow", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load generate_sow module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGenerateSow(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def contractor_defaults(self) -> dict:
        return {
            "company_name": "Subvisual, Lda.",
            "company_address": "Address line",
            "country": "Portugal",
            "phone": "+351 900000000",
            "email": "contact@subvisual.com",
            "website": "subvisual.com",
            "prepared_by_name": "Roberto Machado",
            "prepared_by_role": "CEO",
            "payment": {
                "company_name": "Subvisual Lda.",
                "bank_name": "Bank",
                "iban": "PT50 0000 0000 0000 0000 00",
                "swift": "SWIFTPTPL",
                "wallet": "subvisual.eth",
            },
        }

    def base_raw_payload(self) -> dict:
        return {
            "prepared_for": "Acme Corp",
            "date_issued": "01/03/2026",
            "prepared_by_name": "Roberto Machado",
            "prepared_by_role": "CEO",
            "client_legal_name": "Acme Corp, Inc.",
            "project_title": "Website Redesign",
            "project_summary": "website redesign and development",
            "start_date": "10/03/2026",
            "end_date": "10/04/2026",
            "non_working_days": ["19/03/2026"],
            "project_description": "Redesign and implementation.",
            "deliverables": ["Design", "Development"],
            "fee_schedule": [
                {
                    "team": "1",
                    "fee_type": "daily",
                    "role": "Product Manager",
                    "fee": "600€",
                    "allocation": "5 days/week",
                    "duration": "4 weeks",
                    "estimation": "6800 EUR",
                }
            ],
            "project_cost_total": "6800 EUR",
            "cost_resume_title": "Website Redesign, 4 weeks",
            "cost_resume_value": "6800 EUR",
            "bill_to": {
                "client": "Acme Corp, Inc.",
                "address": "100 Market Street",
                "email": "finance@acme.com",
            },
            "execution": {
                "company_signing_date": "01/03/2026",
                "client_name": "Acme Corp, Inc.",
                "client_signing_date": "01/03/2026",
                "client_address": "100 Market Street",
            },
        }

    def schema(self) -> dict:
        return {
            "required_fields": [
                "prepared_for",
                "date_issued",
                "client_legal_name",
                "project_summary",
                "project_title",
                "start_date",
                "end_date",
                "deliverables",
                "fee_schedule",
                "bill_to_client",
                "bill_to_address",
                "bill_to_email",
                "company_signing_date",
                "client_signatory_name",
                "client_signing_date",
                "client_address",
            ],
            "required_fee_row_fields": [
                "team",
                "fee_type",
                "role",
                "fee",
                "allocation",
                "duration",
                "estimation",
            ],
        }

    def test_happy_path_render_has_no_placeholders(self) -> None:
        payload = self.mod.normalize_payload(self.base_raw_payload(), self.contractor_defaults())
        template = (
            "Client {{client_legal_name}}\n"
            "Summary {{project_summary}}\n"
            "{{deliverables_numbered}}\n"
            "{{fee_schedule_rows}}\n"
            "{{statement_of_confidentiality}}\n"
        )
        markdown = self.mod.render_and_validate(template, payload, self.schema())
        self.assertIn("Acme Corp, Inc.", markdown)
        self.assertNotRegex(markdown, r"{{\s*[a-z0-9_]+\s*}}")

    def test_missing_required_field_fails_validation(self) -> None:
        raw = self.base_raw_payload()
        raw["prepared_for"] = ""
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        with self.assertRaises(ValueError) as ctx:
            self.mod.validate_payload(payload, self.schema())
        self.assertIn("prepared_for", str(ctx.exception))

    def test_invalid_date_range_fails_validation(self) -> None:
        raw = self.base_raw_payload()
        raw["start_date"] = "01/05/2026"
        raw["end_date"] = "01/04/2026"
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        with self.assertRaises(ValueError) as ctx:
            self.mod.validate_payload(payload, self.schema())
        self.assertIn("start_date must be <=", str(ctx.exception))

    def test_iso_date_input_is_normalized_to_ddmmyyyy(self) -> None:
        raw = self.base_raw_payload()
        raw["date_issued"] = "2026-03-01"
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        self.assertEqual(payload["date_issued"], "01/03/2026")

    def test_dynamic_fee_rows_render(self) -> None:
        raw = self.base_raw_payload()
        raw["fee_schedule"] = [
            {
                "team": "1",
                "fee_type": "daily",
                "role": "Product Manager",
                "fee": "600€",
                "allocation": "5 days/week",
                "duration": "4 weeks",
                "estimation": "6800 EUR",
            },
            {
                "team": "1",
                "fee_type": "daily",
                "role": "Product Designer",
                "fee": "600€",
                "allocation": "5 days/week",
                "duration": "4 weeks",
                "estimation": "6800 EUR",
            },
            {
                "team": "1",
                "fee_type": "daily",
                "role": "Developer",
                "fee": "600€",
                "allocation": "5 days/week",
                "duration": "4 weeks",
                "estimation": "13600 EUR",
            },
        ]
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        rows = self.mod.format_fee_schedule_rows(payload["fee_schedule"])
        self.assertEqual(rows.count("\n"), 2)
        self.assertIn("Product Designer", rows)
        self.assertIn("Developer", rows)
        self.assertIn("| 1 | Developer | 600€ | 5 days/week | 4 weeks | 13600 EUR |", rows)

    def test_daily_fee_defaults_are_applied(self) -> None:
        raw = self.base_raw_payload()
        raw["fee_schedule"] = [
            {
                "team": "1",
                "fee_type": "daily",
                "role": "Product Manager",
                "duration": "4 weeks",
                "estimation": "12000 EUR",
            }
        ]
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        row = payload["fee_schedule"][0]
        self.assertEqual(row["fee"], "600€")
        self.assertEqual(row["allocation"], "5 days/week")

    def test_fee_totals_row_is_computed(self) -> None:
        raw = self.base_raw_payload()
        raw["fee_schedule"] = [
            {
                "team": "1",
                "fee_type": "daily",
                "role": "Product Manager",
                "fee": "600€",
                "allocation": "5 days/week",
                "duration": "4 weeks",
                "estimation": "6800 EUR",
            },
            {
                "team": "1",
                "fee_type": "daily",
                "role": "Developer",
                "fee": "600€",
                "allocation": "5 days/week",
                "duration": "4 weeks",
                "estimation": "13600 EUR",
            },
        ]
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        totals = self.mod.format_fee_totals_row(payload["fee_schedule"])
        self.assertEqual(
            totals,
            "| Project Costs | 2 members (minimum) | 1200€ | 10 days/week | 8 weeks | TOTAL 20400 EUR |",
        )

    def test_pipe_separated_fee_rows_are_parsed(self) -> None:
        raw = self.base_raw_payload()
        raw["fee_schedule"] = [
            "- Engineering | Developer 1 | 650 EUR/day | 4 days/week | 3 months | 31200 EUR",
            "- Engineering | Developer 2 | 650 EUR/day | 4 days/week | 3 months | 31200 EUR",
            "- Design | Product Designer | 650 EUR/day | 4 days/week | 3 months | 31200 EUR",
            "- Product | Product Manager | 650 EUR/day | 4 days/week | 3 months | 31200 EUR"
        ]
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        rows = self.mod.format_fee_schedule_rows(payload["fee_schedule"])
        totals = self.mod.format_fee_totals_row(payload["fee_schedule"])
        self.assertIn("| Engineering | Developer 1 | 650 EUR/day | 4 days/week | 3 months | 31200 EUR |", rows)
        self.assertEqual(
            totals,
            "| Project Costs | 4 members (minimum) | 2600 EUR/day | 16 days/week | 12 months | TOTAL 124800 EUR |",
        )

    def test_free_form_fee_sentence_is_coerced_to_table_row(self) -> None:
        raw = self.base_raw_payload()
        raw["fee_schedule"] = "600 per day to all"
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        self.mod.validate_payload(payload, self.schema())
        rows = self.mod.format_fee_schedule_rows(payload["fee_schedule"])
        totals = self.mod.format_fee_totals_row(payload["fee_schedule"])
        self.assertIn("| 1 | All roles | 600€/day | 5 days/week | to be defined | to be defined |", rows)
        self.assertEqual(
            totals,
            "| Project Costs | 1 members (minimum) | 600€/day | 5 days/week | - | TOTAL - |",
        )

    def test_legal_override_replaces_default(self) -> None:
        raw = self.base_raw_payload()
        raw["overrides"] = {
            "statement_of_confidentiality": "Custom confidentiality text."
        }
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        self.assertEqual(payload["statement_of_confidentiality"], "Custom confidentiality text.")

    def test_default_legal_text_is_used_without_override(self) -> None:
        payload = self.mod.normalize_payload(self.base_raw_payload(), self.contractor_defaults())
        self.assertEqual(
            payload["statement_of_confidentiality"],
            self.mod.DEFAULT_CONFIDENTIALITY_TEXT,
        )

    def test_payment_method_is_fixed(self) -> None:
        raw = self.base_raw_payload()
        raw["overrides"] = {"payment_method": "cash"}
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        self.assertEqual(payload["payment_method"], "wired transfer / on-chain")

    def test_contractor_override_applies_to_this_payload(self) -> None:
        raw = self.base_raw_payload()
        raw["contractor_profile_overrides"] = {
            "company_name": "Custom Co",
            "payment": {"iban": "CUSTOM-IBAN"},
        }
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        self.assertEqual(payload["company_name"], "Custom Co")
        self.assertEqual(payload["payment_iban"], "CUSTOM-IBAN")

    def test_prepared_by_can_be_overridden_per_document(self) -> None:
        raw = self.base_raw_payload()
        raw["prepared_by_name"] = "Ana Silva"
        raw["prepared_by_role"] = "Head of Delivery"
        payload = self.mod.normalize_payload(raw, self.contractor_defaults())
        self.assertEqual(payload["prepared_by_name"], "Ana Silva")
        self.assertEqual(payload["prepared_by_role"], "Head of Delivery")

    def test_write_outputs_respects_custom_output_dir(self) -> None:
        payload = self.mod.normalize_payload(self.base_raw_payload(), self.contractor_defaults())
        template = "# Statement of Work\n\n**Signature:**\n\n**Date:** {{client_signing_date}}\n"
        markdown = self.mod.render_and_validate(template, payload, self.schema())
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path, docx_path = self.mod.write_outputs(markdown, payload, Path(tmpdir))
            self.assertTrue(markdown_path.exists())
            self.assertTrue(docx_path.exists())
            self.assertEqual(markdown_path.parent, Path(tmpdir))
            self.assertEqual(docx_path.parent, Path(tmpdir))

    def test_signature_line_remains_blank(self) -> None:
        payload = self.mod.normalize_payload(self.base_raw_payload(), self.contractor_defaults())
        template = (
            "**Client:** {{client_signatory_name}}\n"
            "**Signature:**\n"
            "**Date:** {{client_signing_date}}\n"
        )
        markdown = self.mod.render_and_validate(template, payload, self.schema())
        self.assertIn("**Signature:**", markdown)
        self.assertNotIn("{{client_signing_date}}", markdown)

    def test_regression_render_matches_expected_snippet(self) -> None:
        payload = self.mod.normalize_payload(self.base_raw_payload(), self.contractor_defaults())
        template = (
            "### Prepared For\n{{prepared_for}}\n"
            "### Date Issued\n{{date_issued}}\n"
            "{{deliverables_numbered}}\n"
        )
        markdown = self.mod.render_and_validate(template, payload, self.schema())
        expected = (
            "### Prepared For\nAcme Corp\n"
            "### Date Issued\n01/03/2026\n"
            "1. Design\n2. Development\n"
        )
        self.assertEqual(markdown, expected)


if __name__ == "__main__":
    unittest.main()
