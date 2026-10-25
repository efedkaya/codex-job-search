"""Behavioral regressions for read-only artifact checks; all people and files are fictional."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "job-search" / "scripts" / "check_materials.py"
SPEC = importlib.util.spec_from_file_location("check_materials", SCRIPT)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def simple_pdf(lines):
    commands = ["BT /F1 12 Tf 72 700 Td"]
    for index, line in enumerate(lines):
        if index:
            commands.append("0 -20 Td")
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"({escaped}) Tj")
    stream = ("\n".join(commands) + "\nET\n").encode("ascii")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
               b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"endstream",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    data = b"%PDF-1.4\n"
    offsets = []
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += str(index).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(data)
    data += b"xref\n0 6\n0000000000 65535 f \n"
    data += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    data += f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return data


class MaterialChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def text(self, content, name="resume.txt"):
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def audit_file(self, path, **checks):
        return CHECK.audit({"files": [{"path": str(path), **checks}]})

    def codes(self, report):
        return [item["code"] for group in ("files", "answers") for record in report[group] for item in record["findings"]]

    def test_supported_text_is_found_without_changing_the_file(self):
        path = self.text("Casey Rivera\ncasey@example.test\nExperience\nResearch Assistant\nEducation")
        before = path.read_bytes()
        report, code = self.audit_file(path, required_text=["casey@example.test", "Research Assistant"],
                                       expected_order=["Experience", "Education"])
        self.assertEqual(code, 0)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(report["files"][0]["sha256"], hashlib.sha256(before).hexdigest())
        self.assertIn("factual grounding", report["not_established"])

    def test_missing_email_is_an_observed_failure(self):
        report, code = self.audit_file(self.text("Casey Rivera"), required_text=["casey@example.test"])
        self.assertEqual(code, 1)
        self.assertIn("missing_required_text", self.codes(report))

    def test_sql_does_not_match_nosql_and_c_sharp_does_not_match_c_plus_plus(self):
        report, code = self.audit_file(self.text("NoSQL and C++"), required_text=["SQL", "C#"])
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report).count("missing_required_text"), 2)

    def test_sentence_punctuation_does_not_hide_required_text(self):
        for ending in [".", ",", ":", ";", "!", "?", ")", "”"]:
            with self.subTest(ending=ending):
                report, code = self.audit_file(self.text("Example Systems" + ending),
                                              required_text=["Example Systems"])
                self.assertEqual(code, 0, report)

    def test_a_technical_namespace_is_not_cut_at_its_period(self):
        report, code = self.audit_file(self.text("Example.Systems and C++17"),
                                      required_text=["Example", "C++"])
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report).count("missing_required_text"), 2)

    def test_unicode_ligatures_spacing_quotes_and_dashes_are_normalized(self):
        report, code = self.audit_file(self.text("oﬃce\nresearch 2024–2025 and ‘reviewed’"),
                                      required_text=["office research", "2024-2025", "'reviewed'"])
        self.assertEqual(code, 0, report)

    def test_diacritics_are_not_erased_to_force_a_name_match(self):
        report, code = self.audit_file(self.text("José Rivera"), required_text=["Jose Rivera"])
        self.assertEqual(code, 1)

    def test_wrong_employer_and_template_placeholder_are_caught(self):
        report, code = self.audit_file(self.text("Dear Wrong Employer, [Company] {{candidate_name}}"),
                                      forbidden_text=["Wrong Employer"])
        self.assertEqual(code, 1)
        self.assertIn("template_placeholder", self.codes(report))
        self.assertIn("forbidden_text_present", self.codes(report))

    def test_normal_brackets_are_not_automatically_placeholders(self):
        report, code = self.audit_file(self.text("Research Assistant [London office]"))
        self.assertEqual(code, 0, report)

    def test_word_order_damage_is_distinguished_from_term_presence(self):
        report, code = self.audit_file(self.text("Education\nExperience"),
                                      required_text=["Experience", "Education"],
                                      expected_order=["Experience", "Education"])
        self.assertEqual(code, 1)
        self.assertNotIn("missing_required_text", self.codes(report))
        self.assertIn("expected_order_not_found", self.codes(report))

    def test_hash_detects_a_changed_attachment_even_when_text_still_matches(self):
        path = self.text("Casey Rivera")
        old_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        path.write_text("Casey Rivera\nRevised", encoding="utf-8")
        report, code = self.audit_file(path, expected_sha256=old_hash, required_text=["Casey Rivera"])
        self.assertEqual(code, 1)
        self.assertIn("file_hash_changed", self.codes(report))

    def test_size_limit_uses_actual_bytes(self):
        report, code = self.audit_file(self.text("éé"), max_bytes=3)
        self.assertEqual(report["files"][0]["bytes"], 4)
        self.assertEqual(code, 1)

    def test_docx_split_runs_and_header_contact_are_read(self):
        path = self.root / "resume.docx"
        namespace = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", f'<w:document {namespace}><w:body><w:p><w:r><w:t>Research </w:t></w:r><w:r><w:t>Assistant</w:t></w:r></w:p></w:body></w:document>')
            archive.writestr("word/header1.xml", f'<w:hdr {namespace}><w:p><w:r><w:t>casey@</w:t></w:r><w:r><w:t>example.test</w:t></w:r></w:p></w:hdr>')
        report, code = self.audit_file(path, required_text=["Research Assistant", "casey@example.test"])
        self.assertEqual(code, 0, report)
        self.assertEqual(report["files"][0]["extractor"], "docx_xml")

    def test_unmeasured_docx_pages_never_pass_a_requested_page_limit(self):
        path = self.root / "resume.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Casey</w:t></w:r></w:p></w:body></w:document>')
        report, code = self.audit_file(path, max_pages=1)
        self.assertEqual(code, 2)
        self.assertTrue(report["files"][0]["not_checked"])

    def test_missing_pdf_tools_are_incomplete_instead_of_a_pass(self):
        path = self.root / "resume.pdf"
        path.write_bytes(simple_pdf(["Casey Rivera"]))
        with patch.object(CHECK.importlib.util, "find_spec", return_value=None), patch.object(CHECK.shutil, "which", return_value=None):
            report, code = self.audit_file(path, required_text=["Casey Rivera"], max_pages=1)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "incomplete")

    @unittest.skipUnless(importlib.util.find_spec("pypdf") or shutil.which("pdftotext"), "No installed PDF text extractor")
    def test_real_pdf_text_is_checked(self):
        path = self.root / "resume.pdf"
        path.write_bytes(simple_pdf(["Casey Rivera", "Research Assistant"]))
        report, code = self.audit_file(path, required_text=["Casey Rivera", "Research Assistant"])
        self.assertEqual(code, 0, report)
        self.assertIn(report["files"][0]["extractor"], {"pypdf", "pdftotext"})

    def test_corrupt_or_disguised_pdf_is_a_failure(self):
        path = self.text("This is not a PDF", "resume.pdf")
        report, code = self.audit_file(path)
        self.assertEqual(code, 1)

    def test_character_and_word_limits_are_separate_and_exact(self):
        report, code = CHECK.audit({"answers": [{"text": "A😀 B", "max_characters": 3, "max_words": 1}]})
        self.assertEqual(code, 1)
        self.assertEqual(report["answers"][0]["characters"], 4)
        self.assertEqual(report["answers"][0]["words"], 2)
        self.assertEqual(len(report["answers"][0]["findings"]), 2)

    def test_exact_limit_is_allowed(self):
        report, code = CHECK.audit({"answers": [{"text": "A B", "max_characters": 3, "max_words": 2}]})
        self.assertEqual(code, 0, report)

    def test_invalid_input_does_not_silently_ignore_checks(self):
        for config in [{}, {"answers": [{"text": "Casey", "max_words": True}]},
                       {"files": [{"path": "relative.txt"}]},
                       {"files": [{"path": "/example.txt", "maximum_words": 4}]}]:
            with self.subTest(config=config), self.assertRaises(CHECK.InputError):
                CHECK.audit(config)

    def test_cli_is_read_only_and_returns_a_structured_failure(self):
        document = self.text("Casey Rivera")
        manifest = self.root / "check.json"
        manifest.write_text(json.dumps({"files": [{"path": str(document), "required_text": ["missing email"]}]}))
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(manifest)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "issues_found")
        self.assertEqual({p.name: p.read_bytes() for p in self.root.iterdir()}, before)


if __name__ == "__main__":
    unittest.main()
