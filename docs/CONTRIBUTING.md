# Contributing to VideoWall

Thank you for considering contributing to VideoWall! This document outlines the process for contributing to the project.

## Code of Conduct

Please be respectful and inclusive in all interactions with the project.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported
- Use the bug report template
- Include detailed steps to reproduce
- Include screenshots if relevant
- Include system information (OS, Python version, etc.)

### Suggesting Features

- Check if the feature has already been suggested
- Use the feature request template
- Describe the feature in detail
- Explain the use case for the feature

### Pull Requests

1. Fork the repository
2. Create a branch for your feature or bug fix
3. Make your changes
4. Add tests for your changes
5. Run the tests
6. Update documentation if needed
7. Submit a pull request

## Development Process

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/videowall.git
cd videowall

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Running Tests

```bash
pytest
```

### Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style. Use the following tools to ensure your code meets our standards:

```bash
# Format code with Black
black videowall tests

# Sort imports with isort
isort videowall tests

# Check for issues with flake8
flake8 videowall tests
```

### Pre-commit Checks

Before committing, please run:

```bash
# Run tests
pytest

# Format code
black videowall tests
isort videowall tests
flake8 videowall tests
```

## Documentation

Please update the documentation when making changes that affect user-facing functionality.

## Pull Request Process

1. Update the README.md or documentation with details of changes
2. Update the CHANGELOG.md
3. The PR should work on macOS (we will test it on other platforms if applicable)
4. The PR must pass all tests
5. A maintainer will review and merge your PR

## Release Process

1. Update version number in videowall/__init__.py
2. Update CHANGELOG.md
3. Create a tag for the new version
4. Build the release artifacts
5. Create a GitHub release

## License

By contributing to VideoWall, you agree that your contributions will be licensed under the project's MIT license.