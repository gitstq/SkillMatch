"""Setup configuration for SkillMatch."""

from setuptools import setup, find_packages

setup(
    name="skillmatch",
    version="1.0.0",
    description="AI Agent Skill Discovery, Matching & Orchestration Engine",
    long_description=(
        "SkillMatch is a lightweight CLI tool for intelligently discovering, "
        "matching, and managing AI agent skills. Features include TF-IDF + BM25 "
        "hybrid search, skill registry management, security validation, and "
        "interactive TUI. Zero external dependencies - pure Python standard library."
    ),
    author="SkillMatch Team",
    author_email="skillmatch@example.com",
    url="https://github.com/skillmatch/skillmatch",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    entry_points={
        "console_scripts": [
            "skillmatch=skillmatch.cli:main",
        ],
    },
    zip_safe=True,
)
