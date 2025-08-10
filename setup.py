#!/usr/bin/env python3
"""
Setup script for Vinyl Preflight
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="vinyl-preflight",
    version="2.5.0",
    author="Vinyl Preflight Team",
    author_email="your-email@example.com",
    description="Automated validation tool for vinyl record production materials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mvappshub/vinyl-preflight",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Manufacturing",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vinyl-preflight=src.vinyl_preflight_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="vinyl, audio, validation, preflight, manufacturing, quality-control",
    project_urls={
        "Bug Reports": "https://github.com/mvappshub/vinyl-preflight/issues",
        "Source": "https://github.com/mvappshub/vinyl-preflight",
        "Documentation": "https://github.com/mvappshub/vinyl-preflight/blob/main/README.md",
    },
)
