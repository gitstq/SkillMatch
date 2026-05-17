"""Skill Security Validator for SkillMatch.

Analyzes skill scripts and definitions for potentially dangerous operations
including file system writes, network requests, command execution, and other
risky behaviors. Provides risk level assessment and sandbox execution
suggestions.
"""

import os
import re


class SkillValidator:
    """Validates skill safety by analyzing source code for dangerous patterns.

    Scans skill scripts for patterns that indicate potentially risky operations
    such as file system manipulation, network access, code execution, and
    environment variable access. Assigns a risk level and generates
    actionable mitigation suggestions.

    Attributes:
        risk_patterns: Dictionary mapping risk categories to regex patterns.
    """

    # Risk categories and their associated code patterns
    RISK_PATTERNS = {
        "file_write": {
            "patterns": [
                r"\bopen\s*\([^)]*[\'\"]w[\'\"]",
                r"\bopen\s*\([^)]*[\'\"]a[\'\"]",
                r"\bos\.(remove|unlink|makedirs|mkdir|rmdir|rename|replace)",
                r"\bshutil\.(rmtree|copy|move|copytree)",
                r"\bpathlib.*\.write",
                r"\bwith\s+open\s*\([^)]*[\'\"]w",
                r"\bfile_put_contents\b",
                r"\bos\.chmod\b",
                r"\bos\.chown\b",
            ],
            "risk_level": "medium",
            "description": "File system write operations detected",
        },
        "file_read_sensitive": {
            "patterns": [
                r"\bos\.path\.expanduser\s*\(\s*[\'\"]~",
                r"/etc/(passwd|shadow|hosts|ssh/)",
                r"\bos\.environ\b",
                r"\bgetenv\b",
                r"\bdotenv\b",
                r"\bconfigparser\b",
            ],
            "risk_level": "low",
            "description": "Access to sensitive file paths or environment variables",
        },
        "network_request": {
            "patterns": [
                r"\burllib\.request\b",
                r"\brequests\.(get|post|put|delete|patch|head)\b",
                r"\bhttpx\.(get|post|put|delete|patch|head)\b",
                r"\baiohttp\b",
                r"\bsocket\b",
                r"\burlopen\b",
                r"\bfetch\s*\(",
                r"\bXMLHttpRequest\b",
            ],
            "risk_level": "medium",
            "description": "Network request capabilities detected",
        },
        "command_execution": {
            "patterns": [
                r"\bos\.system\s*\(",
                r"\bsubprocess\.(run|call|Popen|check_output|check_call)",
                r"\beval\s*\(",
                r"\bexec\s*\(",
                r"\bcompile\s*\(",
                r"\b__import__\s*\(",
                r"\bimportlib\.(import_module|reload)",
                r"\bglobals\s*\(\s*\)",
                r"\blocals\s*\(\s*\)",
            ],
            "risk_level": "high",
            "description": "Command execution or dynamic code evaluation detected",
        },
        "dangerous_imports": {
            "patterns": [
                r"\bimport\s+(ctypes|ctypes\.windll)",
                r"\bfrom\s+ctypes\s+import\b",
                r"\bimport\s+pickle\b",
                r"\bfrom\s+pickle\s+import\b",
                r"\bimport\s+marshal\b",
                r"\bfrom\s+marshal\s+import\b",
                r"\bimport\s+shelve\b",
                r"\bimport\s+signal\b",
            ],
            "risk_level": "high",
            "description": "Dangerous module imports detected",
        },
        "privilege_escalation": {
            "patterns": [
                r"\bos\.setuid\b",
                r"\bos\.setgid\b",
                r"\bos\.seteuid\b",
                r"\bos\.setegid\b",
                r"\bsudo\b",
                r"\bsu\s+",
                r"\bchmod\s+777\b",
                r"\bchmod\s+[0-7]{3,4}\b",
            ],
            "risk_level": "high",
            "description": "Privilege escalation patterns detected",
        },
        "data_exfiltration": {
            "patterns": [
                r"\burllib\.request\.Request\b",
                r"\brequests\.post\s*\([^)]*(?:data|json|files)",
                r"\bbase64\.(b64encode|encodebytes)\b",
                r"\bjson\.dumps\b.*?(?:password|secret|token|key|credential)",
            ],
            "risk_level": "high",
            "description": "Potential data exfiltration patterns detected",
        },
    }

    # Risk level ordering for comparison
    RISK_ORDER = {"safe": 0, "low": 1, "medium": 2, "high": 3}

    def __init__(self):
        """Initialize the validator with default risk patterns."""
        self.risk_patterns = self.RISK_PATTERNS

    def validate_file(self, file_path):
        """Validate a skill file for security risks.

        Reads the file content and scans it for dangerous patterns.

        Args:
            file_path: Path to the skill file to validate.

        Returns:
            ValidationResult: Validation result with risk level and details.
        """
        from skillmatch.models import ValidationResult

        if not os.path.exists(file_path):
            return ValidationResult(
                risk_level="safe",
                warnings=[f"File not found: {file_path}"],
                suggestions=["Verify the file path is correct."],
            )

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except IOError as e:
            return ValidationResult(
                risk_level="safe",
                warnings=[f"Could not read file: {e}"],
                suggestions=["Check file permissions."],
            )

        return self._analyze_content(content, file_path)

    def validate_content(self, content):
        """Validate skill content string for security risks.

        Args:
            content: String content to analyze.

        Returns:
            ValidationResult: Validation result with risk level and details.
        """
        return self._analyze_content(content, "<string>")

    def _analyze_content(self, content, source):
        """Analyze content for security risk patterns.

        Args:
            content: Text content to scan.
            source: Source identifier for reporting.

        Returns:
            ValidationResult: Detailed validation result.
        """
        from skillmatch.models import ValidationResult

        warnings = []
        suggestions = []
        max_risk = 0
        details = {}

        for category, config in self.risk_patterns.items():
            matches = []
            for pattern in config["patterns"]:
                found = re.findall(pattern, content)
                if found:
                    matches.extend(found)

            if matches:
                risk_level = config["risk_level"]
                risk_value = self.RISK_ORDER.get(risk_level, 0)
                max_risk = max(max_risk, risk_value)

                warning = f"[{category.upper()}] {config['description']}"
                warnings.append(warning)

                details[category] = {
                    "risk_level": risk_level,
                    "match_count": len(matches),
                    "description": config["description"],
                }

                # Generate suggestions based on category
                cat_suggestions = self._get_suggestions(category)
                suggestions.extend(cat_suggestions)

        # Determine overall risk level
        if max_risk == 0:
            overall_risk = "safe"
        elif max_risk == 1:
            overall_risk = "low"
        elif max_risk == 2:
            overall_risk = "medium"
        else:
            overall_risk = "high"

        # Add general suggestion if any risk found
        if overall_risk != "safe":
            suggestions.append(
                "Consider running this skill in a sandboxed environment "
                "with restricted file system and network access."
            )

        return ValidationResult(
            risk_level=overall_risk,
            warnings=warnings,
            suggestions=suggestions,
            details=details,
        )

    def _get_suggestions(self, category):
        """Get mitigation suggestions for a risk category.

        Args:
            category: Risk category identifier string.

        Returns:
            list: List of suggestion strings.
        """
        suggestions_map = {
            "file_write": [
                "Use a sandboxed directory for file write operations.",
                "Implement path validation to prevent directory traversal.",
                "Consider using a virtual filesystem or temporary directory.",
            ],
            "file_read_sensitive": [
                "Restrict access to only necessary configuration files.",
                "Use environment variables with prefix filtering.",
                "Avoid logging sensitive information.",
            ],
            "network_request": [
                "Restrict network access to approved domains only.",
                "Implement request timeout and size limits.",
                "Validate and sanitize all URL parameters.",
            ],
            "command_execution": [
                "Avoid eval() and exec() - use safer alternatives.",
                "Validate and sanitize all command inputs.",
                "Use allowlists for permitted commands.",
                "Run commands in a containerized environment.",
            ],
            "dangerous_imports": [
                "Avoid importing ctypes, pickle, and marshal for untrusted data.",
                "Use json instead of pickle for serialization.",
                "Implement input validation for all deserialized data.",
            ],
            "privilege_escalation": [
                "Never run with elevated privileges unless absolutely necessary.",
                "Use principle of least privilege for all operations.",
                "Implement proper permission checks before sensitive operations.",
            ],
            "data_exfiltration": [
                "Audit all outbound network requests.",
                "Implement content filtering for sensitive data.",
                "Use encryption for any data transmission.",
                "Log all external communications for audit purposes.",
            ],
        }
        return suggestions_map.get(category, [])

    def validate_skill(self, skill):
        """Validate a Skill object for security risks.

        Checks the skill's install command and metadata for risk indicators.

        Args:
            skill: Skill object to validate.

        Returns:
            ValidationResult: Validation result.
        """
        from skillmatch.models import ValidationResult

        warnings = []
        suggestions = []
        max_risk = 0

        # Check install command for risks
        if skill.install_cmd:
            cmd_warnings = self._check_install_command(skill.install_cmd)
            warnings.extend(cmd_warnings["warnings"])
            suggestions.extend(cmd_warnings["suggestions"])
            max_risk = max(max_risk, cmd_warnings["risk_value"])

        # Check declared risk level
        declared_risk = self.RISK_ORDER.get(skill.risk_level, 0)
        if declared_risk > max_risk:
            max_risk = declared_risk

        # Determine overall risk
        if max_risk == 0:
            overall_risk = "safe"
        elif max_risk == 1:
            overall_risk = "low"
        elif max_risk == 2:
            overall_risk = "medium"
        else:
            overall_risk = "high"

        return ValidationResult(
            risk_level=overall_risk,
            warnings=warnings,
            suggestions=suggestions,
        )

    def _check_install_command(self, cmd):
        """Check an install command for risky patterns.

        Args:
            cmd: Installation command string.

        Returns:
            dict: Dictionary with warnings, suggestions, and risk_value.
        """
        warnings = []
        suggestions = []
        risk_value = 0

        # Check for pip install with --user flag (low risk)
        if "pip install" in cmd and "--user" in cmd:
            risk_value = max(risk_value, 1)
            warnings.append("Install command uses pip with --user flag")

        # Check for pip install without constraints (medium risk)
        if "pip install" in cmd and "--user" not in cmd:
            risk_value = max(risk_value, 2)
            warnings.append("Install command uses pip without --user isolation")
            suggestions.append("Consider using --user flag or virtual environment")

        # Check for curl/wget piped to shell (high risk)
        if re.search(r"curl.*\|.*sh", cmd) or re.search(r"wget.*\|.*sh", cmd):
            risk_value = max(risk_value, 3)
            warnings.append("Install command pipes remote content to shell")
            suggestions.append("Download and review scripts before execution")

        # Check for sudo (high risk)
        if "sudo" in cmd:
            risk_value = max(risk_value, 3)
            warnings.append("Install command requires sudo privileges")
            suggestions.append("Review why elevated privileges are needed")

        # Check for git clone (low risk)
        if "git clone" in cmd:
            risk_value = max(risk_value, 1)
            warnings.append("Install command clones from git repository")
            suggestions.append("Verify the repository source is trusted")

        return {
            "warnings": warnings,
            "suggestions": suggestions,
            "risk_value": risk_value,
        }
