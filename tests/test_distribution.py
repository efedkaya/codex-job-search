"""Safety and reproducibility checks; fixtures contain no real candidate data."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

MODULE = Path(__file__).resolve().parents[1] / "tools" / "distribute.py"
SPEC = importlib.util.spec_from_file_location("distribute", MODULE)
distribute = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(distribute)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / "public"
        self.root.mkdir()
        self.files = ["distribution.json", "README.md", "skills/job-search/SKILL.md", "skills/job-search/references/profile.template.json"]
        self.write("README.md", "Read the [skill](skills/job-search/SKILL.md).\n")
        self.write("skills/job-search/SKILL.md", "# Job search\n[Profile](references/profile.template.json)\n")
        self.write("skills/job-search/references/profile.template.json", "{}\n")
        self.manifest()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def manifest(self):
        self.write("distribution.json", json.dumps({"version": "0.1.0", "files": self.files}))

    def test_unlisted_private_files_never_read_packaged_or_installed(self):
        private = self.write("skills/job-search/profile.json", "not public")
        self.write("tracker.json", "not public")
        private.chmod(0)
        self.addCleanup(private.chmod, 0o600)
        archive = Path(self.temporary.name).resolve() / "release.zip"
        distribute.package(archive, self.root)
        with zipfile.ZipFile(archive) as package:
            self.assertEqual(set(package.namelist()), set(self.files))
            self.assertTrue(all(not name.startswith("/") and ".." not in Path(name).parts for name in package.namelist()))
        installed = Path(self.temporary.name).resolve() / "installed"
        self.assertEqual(distribute.install(installed, self.root), "installed")
        self.assertFalse((installed / "job-search/profile.json").exists())
        self.assertEqual(distribute.install(installed, self.root), "unchanged")
        self.assertTrue(private.exists())

    def test_reproducible_archive(self):
        first, second = [Path(self.temporary.name).resolve() / name for name in ("one.zip", "two.zip")]
        distribute.package(first, self.root)
        (self.root / "README.md").touch()
        distribute.package(second, self.root)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_rejects_traversal_absolute_windows_and_duplicate_paths(self):
        for bad in ("../outside.txt", "/outside.txt", "a/../README.md", "a//b", "a/./b", "C:" + "\\" + "outside.txt", "README.md", "nested.zip", "bad\nname"):
            with self.subTest(path=bad):
                self.files.append(bad)
                self.manifest()
                with self.assertRaises(ValueError):
                    distribute.check(self.root)
                self.files.pop()

    def test_rejects_private_names_but_accepts_templates_and_fiction(self):
        for name in ("application-answers.json", "PROFILE_CONTEXT.md", "employer-targets.json", "company-coverage.json", "search-plan.json", "candidate-evidence.json", "application-links.json", "profile.json", "tracker.json", "search_state.json", "discoveries.json", "vacancies.json", "run_metrics.json", "candidate-brief.json", ".tracker.lock", ".vacancies.lock", ".search_state.lock", "nested/SEARCH_STATE.JSON", "nested/VACANCIES.JSON", ".env", ".env.local", "secrets.json", "credentials.txt"):
            with self.subTest(name=name):
                self.write(name, "{}")
                self.files.append(name)
                self.manifest()
                with self.assertRaises(ValueError):
                    distribute.check(self.root)
                self.files.pop()
        self.files += ["profile.template.json", "credentials_fictional.json"]
        for name in self.files[-2:]:
            self.write(name, "{}")
        self.manifest()
        distribute.check(self.root)

    def test_symlink_file_and_directory_rejected(self):
        source = self.root / "README.md"
        source.unlink()
        source.symlink_to(self.root / "distribution.json")
        with self.assertRaises(ValueError):
            distribute.check(self.root)
        source.unlink()
        source.write_text("ok")
        (self.root / "link").symlink_to(self.root / "skills", target_is_directory=True)
        self.files.append("link/job-search/SKILL.md")
        self.manifest()
        with self.assertRaises(ValueError):
            distribute.check(self.root)

    def test_rejects_candidate_evidence_and_private_directories(self):
        for name in ("evidence.json", "applications/app_123/resume.txt", "sources/resume.txt", "nested/Applications/app_123/resume.txt", "nested/SOURCES/resume.txt"):
            with self.subTest(name=name):
                self.write(name, "fictional private candidate state")
                self.files.append(name)
                self.manifest()
                with self.assertRaises(ValueError):
                    distribute.check(self.root)
                self.files.pop()
        public = ["evidence.template.json", "evidence_fictional.json", "applications.md", "sources.md"]
        for name in public:
            self.write(name, "{}")
        self.files += public
        self.manifest()
        distribute.check(self.root)

    def test_existing_different_install_is_preserved(self):
        parent = Path(self.temporary.name).resolve() / "installed"
        distribute.install(parent, self.root)
        target = parent / "job-search/SKILL.md"
        target.write_text("my existing skill")
        with self.assertRaises(ValueError):
            distribute.install(parent, self.root)
        self.assertEqual(target.read_text(), "my existing skill")
        self.assertIn("Job search", (self.root / "skills/job-search/SKILL.md").read_text())

    def test_credential_and_machine_path_detection(self):
        samples = ["/" + "Users" + "/fictional-person/work", "/" + "home" + "/fictional-person/work", "C:" + "\\" + "Users" + "\\fictional-person", "ghp_" + "a" * 32, "sk-" + "a" * 24, "-----BEGIN " + "PRIVATE KEY-----"]
        for sample in samples:
            with self.subTest(sample=sample):
                self.write("README.md", sample)
                with self.assertRaises(ValueError):
                    distribute.check(self.root)

    def test_missing_and_escaping_markdown_links_rejected(self):
        self.write("unlisted.md", "This does not ship")
        for target in ("missing.md", "../outside.md", "file:private.txt", "//example.com", "unlisted.md"):
            with self.subTest(target=target):
                self.write("README.md", f"[link]({target})")
                with self.assertRaises(ValueError):
                    distribute.check(self.root)
        self.write("README.md", "[web](https://example.com) [section](#section)")
        distribute.check(self.root)

    def test_output_and_install_symlinks_rejected(self):
        destination = Path(self.temporary.name).resolve() / "release.zip"
        destination.symlink_to(self.root / "README.md")
        with self.assertRaises(ValueError):
            distribute.package(destination, self.root)
        parent = Path(self.temporary.name).resolve() / "installed"
        parent.mkdir()
        (parent / "job-search").symlink_to(self.root / "skills/job-search", target_is_directory=True)
        with self.assertRaises(ValueError):
            distribute.install(parent, self.root)


if __name__ == "__main__":
    unittest.main()
