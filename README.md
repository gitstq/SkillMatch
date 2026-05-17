# SkillMatch

AI Agent Skill Discovery, Matching & Orchestration Engine.

A lightweight CLI tool for intelligently discovering, matching, and managing
AI agent skills. Built with zero external dependencies using only the Python
standard library.

## Features

- **Smart Search**: Hybrid TF-IDF + BM25 matching engine for natural language queries
- **Skill Registry**: Manage skills with full CRUD operations (20+ built-in skills)
- **Security Validation**: Scan skills for dangerous patterns and assess risk levels
- **Skill Installation**: Install and manage skills from registry, local files, or GitHub
- **Inverted Index**: Fast full-text search with tag/capability/framework filtering
- **TUI Interface**: Interactive text UI with ANSI colors and progress bars
- **Zero Dependencies**: Pure Python 3.8+ using only standard library modules

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Initialize configuration
skillmatch init

# Search for skills
skillmatch search "code review"
skillmatch search "testing" --framework claude --top 5

# List skills
skillmatch list --all
skillmatch list

# Install a skill
skillmatch install code-review

# View skill details
skillmatch info code-review

# Uninstall a skill
skillmatch remove code-review

# Validate a skill file
skillmatch validate /path/to/skill.py

# Export registry
skillmatch export --format json
skillmatch export --format yaml --output skills.yaml
```

## License

MIT
