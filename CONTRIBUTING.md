# Contributing to Faro Fino MCP Smart Contract Auditor

Thank you for your interest in contributing to the MCP Smart Contract Auditor! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/farofino-mcp.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the server: `python3 -m farofino_mcp`

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- Understanding of smart contract security (helpful but not required)
- Familiarity with async/await in Python (helpful)

### Project Structure

```
farofino-mcp/
├── farofino_mcp/
│   ├── __init__.py       # Package initialization
│   └── __main__.py       # Main server implementation
├── examples/             # Example contracts for testing
├── pyproject.toml        # Python project configuration
├── requirements.txt      # Python dependencies
├── setup.py              # Setup configuration
├── README.md             # Main documentation
└── CONTRIBUTING.md       # This file
```

## Development Workflow

### Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes in the `farofino_mcp/` directory
3. Test your changes: `python3 -m farofino_mcp`
4. Format your code: `black farofino_mcp/` (optional)
5. Commit your changes with clear, descriptive messages

### Development Commands

```bash
# Run the server
python3 -m farofino_mcp

# Format code (optional but recommended)
pip install black
black farofino_mcp/

# Type checking (optional but recommended)
pip install mypy
mypy farofino_mcp/
```

### Testing

Currently, testing is done manually. To test your changes:

1. Run the server: `python3 -m farofino_mcp`
2. Test with MCP protocol messages via stdin/stdout
3. Test with example contracts in the `examples/` directory
4. Test specific functions by importing them in a Python shell

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings to functions and classes
- Use descriptive variable and function names
- Handle errors appropriately with try/except blocks
- Use async/await for I/O operations

## Types of Contributions

### Bug Reports

If you find a bug, please open an issue with:

- A clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Node version, tool versions)

### Feature Requests

We welcome feature requests! Please open an issue with:

- A clear description of the feature
- Use cases and benefits
- Any implementation ideas you have

### Code Contributions

We welcome pull requests for:

1. **New Audit Tool Integrations**
   - Integrating new smart contract analysis tools
   - Improving existing tool integrations
   - Adding support for new contract languages

2. **Pattern Detection Improvements**
   - Adding new vulnerability patterns
   - Improving existing pattern detection
   - Reducing false positives

3. **Documentation**
   - Improving README and guides
   - Adding examples
   - Fixing typos or unclear explanations

4. **Bug Fixes**
   - Fixing reported bugs
   - Improving error handling
   - Enhancing stability

### Pull Request Process

1. Update the README.md if needed
2. Add examples if you're adding new features
3. Test your changes thoroughly
4. Use conventional commit messages (see CI_CD_SETUP.md)
5. Submit the pull request with a clear description of changes

## Adding New Audit Tools

To add a new audit tool integration:

1. Add a new async function in `farofino_mcp/__main__.py` (e.g., `run_new_tool`)
2. Add the tool to the `tools` list in the `main()` function
3. Add a case in the `call_tool` handler
4. Update the `check_tools` function to include the new tool
5. Update the README.md with documentation
6. Add examples if relevant

Example structure:

```python
async def run_new_tool(
    contract_path: str,
    options: Optional[Dict[str, Any]] = None
) -> AuditResult:
    """Run NewTool analysis on a smart contract"""
    try:
        if not file_exists(contract_path):
            return AuditResult(
                success=False,
                error=f"Contract file not found: {contract_path}"
            )
        
        if not command_exists("newtool"):
            return AuditResult(
                success=False,
                error="NewTool is not installed. Install with: pip install newtool"
            )
        
        # Run the tool
        result = subprocess.run(
            ["newtool", contract_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return AuditResult(
            success=True,
            output=result.stdout
        )
    except Exception as e:
        return AuditResult(
            success=False,
            error=f"NewTool analysis failed: {str(e)}"
        )
```

## Adding New Pattern Checks

To add new vulnerability pattern checks to `analyze_contract_patterns`:

```python
if "PATTERN_TO_CHECK" in content:
    findings.append(
        "SEVERITY: Description of the issue and recommendation"
    )
```

Use severity levels:

- `WARNING`: Security vulnerabilities
- `INFO`: Best practices and recommendations
- `ERROR`: Critical security issues

## Code Review Process

All submissions require review. We'll review your PR for:

- Code quality and style
- Functionality and correctness
- Documentation completeness
- Test coverage (when applicable)

## Communication

- GitHub Issues: For bug reports and feature requests
- Pull Requests: For code contributions and reviews
- Discussions: For general questions and ideas

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

If you have questions about contributing, feel free to open an issue with the "question" label.

## Recognition

Contributors will be recognized in the project's README and release notes.

Thank you for contributing to make smart contract auditing more accessible and automated!
