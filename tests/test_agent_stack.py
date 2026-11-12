from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agent_stack", ROOT / "scripts" / "agent-stack.py")
assert SPEC and SPEC.loader
agent_stack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_stack)


class ManifestIntegrityTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        skill = root / "skills" / "demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
        digest = agent_stack.sha256_directory(skill)
        (root / "agent-stack.yaml").write_text(
            "skills:\n"
            "  -\n"
            '    name: "demo"\n'
            '    path: "skills/demo"\n'
            "    files: 1\n"
            f'    sha256: "{digest}"\n'
            "connectors:\n",
            encoding="utf-8",
        )
        return root

    def test_matching_manifest_passes(self) -> None:
        self.assertEqual(agent_stack.verify_manifest_integrity(self.make_repo()), [])

    def test_changed_skill_fails(self) -> None:
        root = self.make_repo()
        (root / "skills" / "demo" / "SKILL.md").write_text("tampered\n", encoding="utf-8")
        errors = agent_stack.verify_manifest_integrity(root)
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_path_outside_skills_fails(self) -> None:
        root = self.make_repo()
        manifest = (root / "agent-stack.yaml").read_text(encoding="utf-8")
        (root / "agent-stack.yaml").write_text(
            manifest.replace('path: "skills/demo"', 'path: "../demo"'), encoding="utf-8"
        )
        errors = agent_stack.verify_manifest_integrity(root)
        self.assertTrue(any("escapes" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
