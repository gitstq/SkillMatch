"""Utility functions for SkillMatch.

Provides ANSI color output, progress bars, file operations,
version comparison, and network request helpers. All implemented
using only Python standard library.
"""

import os
import sys
import re
import json
import time
import math
import shutil
import hashlib
from datetime import datetime


# ---------------------------------------------------------------------------
# ANSI Color Output
# ---------------------------------------------------------------------------

class Colors:
    """ANSI color codes for terminal output.

    Provides color constants and helper methods for colored terminal text.
    Colors are automatically disabled when output is not a TTY.
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    _enabled = None

    @classmethod
    def enabled(cls):
        """Check if colored output should be enabled.

        Returns:
            bool: True if output is a TTY and supports colors.
        """
        if cls._enabled is None:
            cls._enabled = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        return cls._enabled

    @classmethod
    def set_enabled(cls, value):
        """Manually enable or disable colored output.

        Args:
            value: Boolean to enable or disable colors.
        """
        cls._enabled = bool(value)

    @classmethod
    def colorize(cls, text, color):
        """Wrap text with an ANSI color code.

        Args:
            text: The text to colorize.
            color: ANSI color code string.

        Returns:
            str: Colorized text, or plain text if colors are disabled.
        """
        if not cls.enabled():
            return text
        return f"{color}{text}{cls.RESET}"

    @classmethod
    def red(cls, text):
        """Return text in red.

        Args:
            text: The text to colorize.

        Returns:
            str: Red-colored text.
        """
        return cls.colorize(text, cls.RED)

    @classmethod
    def green(cls, text):
        """Return text in green.

        Args:
            text: The text to colorize.

        Returns:
            str: Green-colored text.
        """
        return cls.colorize(text, cls.GREEN)

    @classmethod
    def yellow(cls, text):
        """Return text in yellow.

        Args:
            text: The text to colorize.

        Returns:
            str: Yellow-colored text.
        """
        return cls.colorize(text, cls.YELLOW)

    @classmethod
    def blue(cls, text):
        """Return text in blue.

        Args:
            text: The text to colorize.

        Returns:
            str: Blue-colored text.
        """
        return cls.colorize(text, cls.BLUE)

    @classmethod
    def cyan(cls, text):
        """Return text in cyan.

        Args:
            text: The text to colorize.

        Returns:
            str: Cyan-colored text.
        """
        return cls.colorize(text, cls.CYAN)

    @classmethod
    def magenta(cls, text):
        """Return text in magenta.

        Args:
            text: The text to colorize.

        Returns:
            str: Magenta-colored text.
        """
        return cls.colorize(text, cls.MAGENTA)

    @classmethod
    def bold(cls, text):
        """Return text in bold.

        Args:
            text: The text to bold.

        Returns:
            str: Bold text.
        """
        return cls.colorize(text, cls.BOLD)

    @classmethod
    def dim(cls, text):
        """Return text in dim (faint) style.

        Args:
            text: The text to dim.

        Returns:
            str: Dim text.
        """
        return cls.colorize(text, cls.DIM)


# ---------------------------------------------------------------------------
# Progress Bar
# ---------------------------------------------------------------------------

class ProgressBar:
    """A simple text-based progress bar using ANSI codes.

    Displays a progress bar in the terminal with percentage and optional
    status message. Uses carriage return to update in-place.

    Attributes:
        total: Total number of items/steps.
        width: Character width of the progress bar.
    """

    def __init__(self, total, width=40, prefix="", suffix=""):
        """Initialize the progress bar.

        Args:
            total: Total number of steps.
            width: Width of the bar in characters.
            prefix: Text to display before the bar.
            suffix: Text to display after the bar.
        """
        self.total = total
        self.width = width
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self.start_time = time.time()

    def update(self, current, status=""):
        """Update the progress bar display.

        Args:
            current: Current progress value.
            status: Optional status message to display.
        """
        self.current = min(current, self.total)
        if self.total == 0:
            percent = 100.0
        else:
            percent = 100.0 * self.current / self.total
        filled = int(self.width * self.current / max(self.total, 1))
        bar = "█" * filled + "░" * (self.width - filled)

        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = elapsed / self.current * (self.total - self.current)
            eta_str = f" ETA: {eta:.1f}s"
        else:
            eta_str = ""

        line = (
            f"\r{self.prefix} |{bar}| {percent:5.1f}% "
            f"({self.current}/{self.total}){eta_str}"
        )
        if status:
            line += f" {status}"
        sys.stdout.write(line)
        sys.stdout.flush()

    def finish(self):
        """Complete the progress bar and print a newline."""
        self.update(self.total)
        sys.stdout.write("\n")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# File Operations
# ---------------------------------------------------------------------------

def ensure_dir(path):
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to create.

    Returns:
        str: The path that was ensured.
    """
    if not os.path.exists(path):
        os.makedirs(path, mode=0o755)
    return path


def read_json_file(path):
    """Read and parse a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        dict/list: Parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(path, data, indent=2):
    """Write data to a JSON file.

    Args:
        path: Path to the JSON file.
        data: Data to serialize (must be JSON-serializable).
        indent: Indentation level for pretty printing.
    """
    ensure_dir(os.path.dirname(path) if os.path.dirname(path) else ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def file_hash(path, algorithm="sha256"):
    """Calculate the hash of a file.

    Args:
        path: Path to the file.
        algorithm: Hash algorithm name (default: sha256).

    Returns:
        str: Hexadecimal hash string.
    """
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def safe_remove(path):
    """Safely remove a file or directory.

    Args:
        path: Path to the file or directory to remove.

    Returns:
        bool: True if removal was successful, False otherwise.
    """
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except (OSError, IOError):
        return False


# ---------------------------------------------------------------------------
# Version Comparison
# ---------------------------------------------------------------------------

def parse_version(version_str):
    """Parse a semantic version string into a tuple of integers.

    Args:
        version_str: Version string (e.g., "1.2.3").

    Returns:
        tuple: Tuple of version components as integers.
    """
    parts = re.split(r"[.\-]", version_str)
    result = []
    for part in parts:
        match = re.match(r"(\d+)", part)
        if match:
            result.append(int(match.group(1)))
        else:
            result.append(0)
    while len(result) < 3:
        result.append(0)
    return tuple(result[:3])


def compare_versions(v1, v2):
    """Compare two version strings.

    Args:
        v1: First version string.
        v2: Second version string.

    Returns:
        int: -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2.
    """
    p1 = parse_version(v1)
    p2 = parse_version(v2)
    if p1 < p2:
        return -1
    elif p1 > p2:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Text Processing
# ---------------------------------------------------------------------------

def tokenize(text):
    """Tokenize text into lowercase words.

    Splits text on non-alphanumeric characters and filters out
    common stop words and very short tokens.

    Args:
        text: Input text to tokenize.

    Returns:
        list: List of lowercase word tokens.
    """
    # Split on non-alphanumeric characters
    tokens = re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", text.lower())
    # Filter out very short tokens
    return [t for t in tokens if len(t) > 1]


def normalize_text(text):
    """Normalize text for search and matching.

    Converts to lowercase, collapses whitespace, and removes
    special characters.

    Args:
        text: Input text to normalize.

    Returns:
        str: Normalized text string.
    """
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Timestamp Helpers
# ---------------------------------------------------------------------------

def now_iso():
    """Return the current UTC time in ISO 8601 format.

    Returns:
        str: ISO format timestamp string.
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(timestamp):
    """Parse an ISO 8601 timestamp string.

    Args:
        timestamp: ISO format timestamp string.

    Returns:
        datetime: Parsed datetime object, or None if parsing fails.
    """
    try:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Network Helpers (using urllib)
# ---------------------------------------------------------------------------

def fetch_url(url, timeout=30):
    """Fetch content from a URL using urllib.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        str: Response body as string.

    Raises:
        Exception: If the request fails for any reason.
    """
    from urllib.request import urlopen, Request
    from urllib.error import URLError

    headers = {
        "User-Agent": "SkillMatch/1.0.0",
        "Accept": "application/json, text/plain, */*",
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except URLError as e:
        raise Exception(f"Failed to fetch {url}: {e}")


def is_github_url(url):
    """Check if a URL is a valid GitHub repository URL.

    Args:
        url: URL string to check.

    Returns:
        bool: True if the URL appears to be a GitHub URL.
    """
    pattern = r"^https?://github\.com/[a-zA-Z0-9\-_.]+/[a-zA-Z0-9\-_.]+"
    return bool(re.match(pattern, url))


def parse_github_url(url):
    """Parse a GitHub URL to extract owner and repo name.

    Args:
        url: GitHub repository URL.

    Returns:
        tuple: (owner, repo) or (None, None) if parsing fails.
    """
    pattern = r"^https?://github\.com/([a-zA-Z0-9\-_.]+)/([a-zA-Z0-9\-_.]+)"
    match = re.match(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None


# ---------------------------------------------------------------------------
# Config Path Helpers
# ---------------------------------------------------------------------------

def get_config_dir():
    """Get the SkillMatch configuration directory path.

    Returns:
        str: Path to ~/.skillmatch/
    """
    home = os.path.expanduser("~")
    return os.path.join(home, ".skillmatch")


def get_registry_path():
    """Get the path to the registry JSON file.

    Returns:
        str: Path to ~/.skillmatch/registry.json
    """
    return os.path.join(get_config_dir(), "registry.json")


def get_skills_dir():
    """Get the directory where installed skills are stored.

    Returns:
        str: Path to ~/.skillmatch/skills/
    """
    return os.path.join(get_config_dir(), "skills")


def get_index_path():
    """Get the path to the search index file.

    Returns:
        str: Path to ~/.skillmatch/index.json
    """
    return os.path.join(get_config_dir(), "index.json")
