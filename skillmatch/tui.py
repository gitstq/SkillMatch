"""Text-based User Interface for SkillMatch.

Provides a simple interactive TUI using ANSI escape codes for colored
output. No external dependencies required - uses only standard library
modules. Supports skill browsing, searching, installation, and
information display with progress indicators.
"""

import sys

from skillmatch.utils import Colors, ProgressBar


class TUI:
    """Simple text-based user interface for SkillMatch.

    Provides formatted output for skill listings, search results,
    installation progress, and validation reports. Uses ANSI escape
    codes for colored terminal output.

    Attributes:
        colors: Colors utility class reference.
        width: Terminal width for text wrapping (default: 80).
    """

    def __init__(self, width=80):
        """Initialize the TUI.

        Args:
            width: Terminal width for text formatting (default: 80).
        """
        self.colors = Colors
        self.width = width

    def _separator(self, char="-"):
        """Print a horizontal separator line.

        Args:
            char: Character to use for the separator line.
        """
        print(char * self.width)

    def _bold_header(self, text):
        """Print a bold header with separators.

        Args:
            text: Header text to display.
        """
        self._separator()
        print(self.colors.bold(text))
        self._separator()

    # ------------------------------------------------------------------
    # Skill Listing
    # ------------------------------------------------------------------

    def print_skill_list(self, skills, title="Installed Skills"):
        """Display a formatted list of skills.

        Args:
            skills: List of Skill objects to display.
            title: Section title string.
        """
        self._bold_header(f" {title} ({len(skills)}) ")

        if not skills:
            print(self.colors.yellow("  No skills found."))
            print()
            return

        for i, skill in enumerate(skills, 1):
            installed_marker = self.colors.green("[installed]") if skill.installed else ""
            risk_color = {
                "safe": self.colors.green,
                "low": self.colors.cyan,
                "medium": self.colors.yellow,
                "high": self.colors.red,
            }.get(skill.risk_level, self.colors.dim)

            print(f"  {i}. {self.colors.bold(skill.name)} {installed_marker}")
            print(f"     {self.colors.dim('Version:')} {skill.version}  "
                  f"{self.colors.dim('Author:')} {skill.author}  "
                  f"{self.colors.dim('Risk:')} {risk_color(skill.risk_level)}")
            desc = skill.description[:60] + ("..." if len(skill.description) > 60 else "")
            print(f"     {self.colors.dim(desc)}")
            if skill.tags:
                tags_str = " ".join(f"[{t}]" for t in skill.tags[:5])
                print(f"     {self.colors.cyan(tags_str)}")
            print()

    # ------------------------------------------------------------------
    # Skill Detail
    # ------------------------------------------------------------------

    def print_skill_info(self, skill):
        """Display detailed information about a skill.

        Args:
            skill: Skill object to display.
        """
        self._bold_header(f" Skill: {skill.name} ")

        risk_color = {
            "safe": self.colors.green,
            "low": self.colors.cyan,
            "medium": self.colors.yellow,
            "high": self.colors.red,
        }.get(skill.risk_level, self.colors.dim)

        info_lines = [
            (self.colors.bold("Name:"), skill.name),
            (self.colors.bold("Version:"), skill.version),
            (self.colors.bold("Author:"), skill.author),
            (self.colors.bold("Risk Level:"), risk_color(skill.risk_level.upper())),
            (self.colors.bold("Source:"), skill.source),
            (self.colors.bold("Installed:"), self.colors.green("Yes") if skill.installed else self.colors.red("No")),
        ]

        if skill.install_path:
            info_lines.append((self.colors.bold("Install Path:"), skill.install_path))
        if skill.created_at:
            info_lines.append((self.colors.bold("Created:"), skill.created_at))
        if skill.updated_at:
            info_lines.append((self.colors.bold("Updated:"), skill.updated_at))

        for label, value in info_lines:
            print(f"  {label:20s} {value}")

        print()
        print(f"  {self.colors.bold('Description:')}")
        for line in self._wrap_text(skill.description, indent=4):
            print(line)

        if skill.tags:
            print()
            print(f"  {self.colors.bold('Tags:')}")
            tags_str = ", ".join(self.colors.cyan(t) for t in skill.tags)
            print(f"    {tags_str}")

        if skill.capabilities:
            print()
            print(f"  {self.colors.bold('Capabilities:')}")
            for cap in skill.capabilities:
                print(f"    {self.colors.green('+')} {cap}")

        if skill.framework_support:
            print()
            print(f"  {self.colors.bold('Framework Support:')}")
            fw_str = ", ".join(self.colors.blue(fw) for fw in skill.framework_support)
            print(f"    {fw_str}")

        if skill.install_cmd:
            print()
            print(f"  {self.colors.bold('Install Command:')}")
            print(f"    {self.colors.yellow(skill.install_cmd)}")

        print()
        self._separator()

    # ------------------------------------------------------------------
    # Search Results
    # ------------------------------------------------------------------

    def print_search_results(self, results, query=""):
        """Display formatted search results.

        Args:
            results: List of SearchResult objects to display.
            query: Original search query string.
        """
        if query:
            self._bold_header(f' Search Results for: "{query}" ({len(results)}) ')
        else:
            self._bold_header(f" Search Results ({len(results)}) ")

        if not results:
            print(self.colors.yellow("  No matching skills found."))
            print(self.colors.dim("  Try different keywords or broader search terms."))
            print()
            return

        for i, result in enumerate(results, 1):
            skill = result.skill
            score_bar = self._score_bar(result.score)
            matched = ", ".join(result.matched_fields) if result.matched_fields else "fulltext"

            print(f"  {i}. {self.colors.bold(skill.name)} "
                  f"{self.colors.dim(f'v{skill.version}')}")
            print(f"     Score: {score_bar} {result.score:.4f}")
            print(f"     Matched: {self.colors.dim(matched)}")
            desc = skill.description[:70] + ("..." if len(skill.description) > 70 else "")
            print(f"     {self.colors.dim(desc)}")
            if skill.tags:
                tags_str = " ".join(f"[{t}]" for t in skill.tags[:4])
                print(f"     {self.colors.cyan(tags_str)}")
            print()

    def _score_bar(self, score, width=20):
        """Create a visual score bar using block characters.

        Args:
            score: Score value between 0 and 1.
            width: Character width of the bar.

        Returns:
            str: ANSI-colored score bar string.
        """
        filled = int(width * min(score, 1.0))
        bar = self.colors.green("█" * filled) + self.colors.dim("░" * (width - filled))
        return bar

    # ------------------------------------------------------------------
    # Validation Results
    # ------------------------------------------------------------------

    def print_validation(self, result, target=""):
        """Display validation results with color-coded risk levels.

        Args:
            result: ValidationResult object to display.
            target: Name or path of the validated target.
        """
        if target:
            self._bold_header(f" Validation: {target} ")
        else:
            self._bold_header(" Validation Results ")

        risk_display = {
            "safe": (self.colors.green, "SAFE"),
            "low": (self.colors.cyan, "LOW RISK"),
            "medium": (self.colors.yellow, "MEDIUM RISK"),
            "high": (self.colors.red, "HIGH RISK"),
        }
        color_fn, label = risk_display.get(
            result.risk_level, (self.colors.dim, "UNKNOWN")
        )

        print(f"  Risk Level: {color_fn(label)}")
        print()

        if result.warnings:
            print(f"  {self.colors.bold('Warnings:')}")
            for warning in result.warnings:
                print(f"    {self.colors.yellow('!')} {warning}")
            print()

        if result.suggestions:
            print(f"  {self.colors.bold('Suggestions:')}")
            for suggestion in result.suggestions:
                print(f"    {self.colors.green('>')} {suggestion}")
            print()

        if result.details:
            print(f"  {self.colors.bold('Details:')}")
            for category, detail in result.details.items():
                risk_c = {
                    "safe": self.colors.green,
                    "low": self.colors.cyan,
                    "medium": self.colors.yellow,
                    "high": self.colors.red,
                }.get(detail["risk_level"], self.colors.dim)
                print(f"    [{category}] {risk_c(detail['risk_level'])} "
                      f"- {detail['match_count']} match(es)")
                print(f"      {detail['description']}")
            print()

        self._separator()

    # ------------------------------------------------------------------
    # Installation Progress
    # ------------------------------------------------------------------

    def print_install_progress(self, name, success=True, message=""):
        """Display installation progress message.

        Args:
            name: Name of the skill being installed.
            success: Whether the installation was successful.
            message: Additional message to display.
        """
        if success:
            print(f"  {self.colors.green('>>')} {self.colors.bold('Installed:')} {name}")
        else:
            print(f"  {self.colors.red('>>')} {self.colors.bold('Failed:')} {name}")
        if message:
            print(f"     {self.colors.dim(message)}")

    def print_uninstall_progress(self, name, success=True, message=""):
        """Display uninstallation progress message.

        Args:
            name: Name of the skill being uninstalled.
            success: Whether the uninstallation was successful.
            message: Additional message to display.
        """
        if success:
            print(f"  {self.colors.green('>>')} {self.colors.bold('Uninstalled:')} {name}")
        else:
            print(f"  {self.colors.red('>>')} {self.colors.bold('Failed:')} {name}")
        if message:
            print(f"     {self.colors.dim(message)}")

    # ------------------------------------------------------------------
    # Init / Setup
    # ------------------------------------------------------------------

    def print_init_success(self, config_dir):
        """Display initialization success message.

        Args:
            config_dir: Path to the created configuration directory.
        """
        self._bold_header(" SkillMatch Initialized ")
        print(f"  Configuration directory: {self.colors.cyan(config_dir)}")
        print(f"  Registry: {self.colors.cyan(config_dir + '/registry.json')}")
        print(f"  Skills directory: {self.colors.cyan(config_dir + '/skills/')}")
        print()
        search_cmd = 'skillmatch search "<query>"'
        print(f"  {self.colors.green('Ready to use!')} Run "
              f"{self.colors.bold(search_cmd)} to find skills.")
        print()

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def print_export_success(self, format_type, output_path):
        """Display export success message.

        Args:
            format_type: Export format (json or yaml).
            output_path: Path to the exported file.
        """
        print(f"  {self.colors.green('>>')} Exported skills in {format_type.upper()} format")
        print(f"     {self.colors.cyan(output_path)}")

    # ------------------------------------------------------------------
    # Error Messages
    # ------------------------------------------------------------------

    def print_error(self, message):
        """Display an error message.

        Args:
            message: Error message to display.
        """
        print(f"  {self.colors.red('Error:')} {message}", file=sys.stderr)

    def print_warning(self, message):
        """Display a warning message.

        Args:
            message: Warning message to display.
        """
        print(f"  {self.colors.yellow('Warning:')} {message}")

    def print_success(self, message):
        """Display a success message.

        Args:
            message: Success message to display.
        """
        print(f"  {self.colors.green(message)}")

    # ------------------------------------------------------------------
    # Help / Banner
    # ------------------------------------------------------------------

    def print_banner(self):
        """Display the SkillMatch ASCII banner."""
        banner = r"""
  ____       _       _ _        ____  _       _ _        _   ____            _           
 |  _ \ __ _(_)_ __ | (_) ___  |  _ \| | __ _| | |_  ___| | / ___| _   _ ___| |_ ___ _ __ 
 | |_) / _` | | '_ \| | |/ __| | |_) | |/ _` | | __|/ _ \ | \___ \| | | / __| __/ _ \ '__|
 |  __/ (_| | | | | | | | (__  |  __/| | (_| | | |_|  __/ |  ___) | |_| \__ \ ||  __/ |   
 |_|   \__,_|_|_| |_|_|_|\___| |_|   |_|\__,_|_|\__|\___|_| |____/ \__,_|___/\__\___|_|   
"""
        print(self.colors.cyan(banner))
        print(self.colors.dim(f"  v1.0.0 - AI Agent Skill Discovery, Matching & Orchestration"))
        print()

    # ------------------------------------------------------------------
    # Interactive Menu
    # ------------------------------------------------------------------

    def print_menu(self):
        """Display the interactive menu options."""
        self._bold_header(" SkillMatch Interactive Menu ")
        options = [
            ("1", "Search skills"),
            ("2", "List all skills"),
            ("3", "List installed skills"),
            ("4", "Install a skill"),
            ("5", "View skill details"),
            ("6", "Uninstall a skill"),
            ("7", "Validate a skill"),
            ("0", "Exit"),
        ]
        for num, desc in options:
            print(f"  {self.colors.bold(f'[{num}]')} {desc}")
        print()

    def prompt(self, message="> "):
        """Display a prompt and read user input.

        Args:
            message: Prompt message to display.

        Returns:
            str: User input string.
        """
        try:
            return input(self.colors.bold(message)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return ""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _wrap_text(self, text, indent=0, max_width=None):
        """Wrap text to fit within the terminal width.

        Args:
            text: Text to wrap.
            indent: Number of spaces for indentation.
            max_width: Maximum line width (defaults to self.width).

        Yields:
            str: Wrapped text lines.
        """
        width = max_width or self.width
        effective_width = width - indent
        if effective_width < 20:
            effective_width = 20

        prefix = " " * indent
        words = text.split()
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= effective_width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    yield prefix + current_line
                current_line = word

        if current_line:
            yield prefix + current_line
