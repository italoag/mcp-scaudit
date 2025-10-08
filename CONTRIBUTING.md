# Contributing to MCP Smart Contract Auditor

Thank you for your interest in contributing to the MCP Smart Contract Auditor! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/mcp-scaudit.git`
3. Install dependencies: `npm install`
4. Build the project: `npm run build`

## Development Setup

### Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn
- TypeScript knowledge
- Understanding of smart contract security (helpful but not required)

### Project Structure

```
mcp-scaudit/
├── src/
│   └── index.ts          # Main server implementation
├── dist/                 # Built output (generated)
├── examples/             # Example contracts for testing
├── package.json          # Project dependencies
├── tsconfig.json         # TypeScript configuration
├── README.md            # Main documentation
└── CONTRIBUTING.md      # This file
```

## Development Workflow

### Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes in the `src/` directory
3. Build the project: `npm run build`
4. Test your changes manually
5. Commit your changes with clear, descriptive messages

### Building

```bash
npm run build        # Compile TypeScript to JavaScript
npm run watch        # Watch mode for development
```

### Testing

Currently, testing is done manually. To test your changes:

1. Build the project: `npm run build`
2. Run the server: `node dist/index.js`
3. Test with MCP protocol messages via stdin/stdout
4. Test with example contracts in the `examples/` directory

### Code Style

- Use TypeScript strict mode
- Follow the existing code style
- Add JSDoc comments for public functions
- Use descriptive variable and function names
- Handle errors appropriately

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
3. Ensure the build succeeds: `npm run build`
4. Update the CHANGELOG if you're adding significant features
5. Submit the pull request with a clear description of changes

## Adding New Audit Tools

To add a new audit tool integration:

1. Add a new function in `src/index.ts` (e.g., `runNewTool`)
2. Add the tool to the `tools` array with proper schema
3. Add a case in the `CallToolRequestSchema` handler
4. Update the `check_tools` function to include the new tool
5. Update the README.md with documentation
6. Add examples if relevant

Example structure:

```typescript
async function runNewTool(
  contractPath: string,
  options?: { /* tool-specific options */ }
): Promise<AuditResult> {
  // Implementation
}
```

## Adding New Pattern Checks

To add new vulnerability pattern checks to `analyzeContractPatterns`:

```typescript
if (content.includes("PATTERN_TO_CHECK")) {
  findings.push(
    "SEVERITY: Description of the issue and recommendation"
  );
}
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
