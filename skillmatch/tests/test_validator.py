"""Tests for the Skill Security Validator.

Tests cover file validation, content validation, skill metadata validation,
risk level assessment, and suggestion generation.
"""

import unittest
import tempfile
import os

from skillmatch.models import Skill, ValidationResult
from skillmatch.validator import SkillValidator


class TestSkillValidator(unittest.TestCase):
    """Test cases for the SkillValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = SkillValidator()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_temp_file(self, content):
        """Write content to a temporary file and return the path.

        Args:
            content: String content to write.

        Returns:
            str: Path to the temporary file.
        """
        path = os.path.join(self.temp_dir, "test_skill.py")
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_safe_code(self):
        """Test that safe code gets 'safe' risk level."""
        code = '''
def hello():
    """Say hello."""
    name = input("What is your name? ")
    print(f"Hello, {name}!")
    return name
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertEqual(result.risk_level, "safe")
        self.assertTrue(result.is_safe())

    def test_file_write_detection(self):
        """Test detection of file write operations."""
        code = '''
def save_data(data):
    with open("output.txt", "w") as f:
        f.write(data)
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertIn(result.risk_level, ("low", "medium", "high"))
        self.assertGreater(len(result.warnings), 0)

    def test_command_execution_detection(self):
        """Test detection of command execution."""
        code = '''
import subprocess
def run_cmd(cmd):
    subprocess.run(cmd, shell=True)
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertEqual(result.risk_level, "high")

    def test_eval_detection(self):
        """Test detection of eval() usage."""
        code = '''
def execute(user_input):
    result = eval(user_input)
    return result
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertEqual(result.risk_level, "high")

    def test_network_request_detection(self):
        """Test detection of network requests."""
        code = '''
from urllib.request import urlopen
def fetch(url):
    return urlopen(url).read()
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertIn(result.risk_level, ("low", "medium", "high"))

    def test_dangerous_import_detection(self):
        """Test detection of dangerous imports."""
        code = '''
import pickle
def deserialize(data):
    return pickle.loads(data)
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertEqual(result.risk_level, "high")

    def test_sudo_detection(self):
        """Test detection of sudo usage."""
        code = '''
import os
os.system("sudo rm -rf /")
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertEqual(result.risk_level, "high")

    def test_validate_content(self):
        """Test validating content string directly."""
        result = self.validator.validate_content("print('hello world')")
        self.assertEqual(result.risk_level, "safe")

    def test_validate_nonexistent_file(self):
        """Test validating a nonexistent file."""
        result = self.validator.validate_file("/nonexistent/path/file.py")
        self.assertEqual(result.risk_level, "safe")
        self.assertGreater(len(result.warnings), 0)

    def test_validate_skill_safe(self):
        """Test validating a safe Skill object."""
        skill = Skill(
            name="safe-skill",
            description="A safe skill",
            install_cmd="echo hello",
            risk_level="safe",
        )
        result = self.validator.validate_skill(skill)
        self.assertEqual(result.risk_level, "safe")

    def test_validate_skill_with_pip(self):
        """Test validating a skill with pip install command."""
        skill = Skill(
            name="pip-skill",
            description="A skill with pip install",
            install_cmd="pip install some-package",
            risk_level="safe",
        )
        result = self.validator.validate_skill(skill)
        self.assertIn(result.risk_level, ("low", "medium", "high"))

    def test_validate_skill_with_sudo(self):
        """Test validating a skill with sudo in install command."""
        skill = Skill(
            name="sudo-skill",
            description="A skill requiring sudo",
            install_cmd="sudo pip install some-package",
            risk_level="safe",
        )
        result = self.validator.validate_skill(skill)
        self.assertEqual(result.risk_level, "high")

    def test_validate_skill_with_curl_pipe(self):
        """Test validating a skill with curl|sh pattern."""
        skill = Skill(
            name="curl-skill",
            description="A skill with curl pipe",
            install_cmd="curl http://example.com/script.sh | sh",
            risk_level="safe",
        )
        result = self.validator.validate_skill(skill)
        self.assertEqual(result.risk_level, "high")

    def test_result_is_safe(self):
        """Test ValidationResult.is_safe() method."""
        safe_result = ValidationResult(risk_level="safe")
        self.assertTrue(safe_result.is_safe())

        low_result = ValidationResult(risk_level="low")
        self.assertTrue(low_result.is_safe())

        medium_result = ValidationResult(risk_level="medium")
        self.assertFalse(medium_result.is_safe())

        high_result = ValidationResult(risk_level="high")
        self.assertFalse(high_result.is_safe())

    def test_result_invalid_risk_level(self):
        """Test that invalid risk level raises ValueError."""
        with self.assertRaises(ValueError):
            ValidationResult(risk_level="invalid")

    def test_result_to_dict(self):
        """Test ValidationResult serialization."""
        result = ValidationResult(
            risk_level="medium",
            warnings=["warning1"],
            suggestions=["suggestion1"],
            details={"key": "value"},
        )
        d = result.to_dict()
        self.assertEqual(d["risk_level"], "medium")
        self.assertEqual(d["warnings"], ["warning1"])
        self.assertEqual(d["suggestions"], ["suggestion1"])
        self.assertEqual(d["details"], {"key": "value"})

    def test_multiple_risks_highest_wins(self):
        """Test that the highest risk level is used when multiple are found."""
        code = '''
import subprocess
import pickle

def dangerous(data):
    result = eval(data)
    subprocess.run(["rm", "-rf", "/"])
    pickle.loads(data)
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertEqual(result.risk_level, "high")

    def test_suggestions_generated(self):
        """Test that suggestions are generated for detected risks."""
        code = '''
import subprocess
subprocess.run(["ls"])
'''
        path = self._write_temp_file(code)
        result = self.validator.validate_file(path)
        self.assertGreater(len(result.suggestions), 0)


if __name__ == "__main__":
    unittest.main()
