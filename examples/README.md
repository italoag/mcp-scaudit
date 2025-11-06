# Example Contracts

This directory contains example smart contracts for testing the MCP Smart Contract Auditor.

## SimpleToken.sol

A basic ERC20-like token contract that demonstrates:
- Token transfers
- Approval mechanism
- Balance tracking
- Safe arithmetic (using Solidity 0.8+)

This is a relatively safe contract that should pass most security checks.

## Usage

To audit these contracts, use the MCP server tools:

```bash
# Start the MCP server
npx farofino-mcp

# Then use the tools through your MCP client:
# 1. Read the contract
read_contract with contract_path="examples/SimpleToken.sol"

# 2. Run pattern analysis
pattern_analysis with contract_path="examples/SimpleToken.sol"

# 3. Run Slither (if installed)
slither_audit with contract_path="examples/SimpleToken.sol"
```

## Creating Your Own Test Contracts

You can create your own test contracts and place them in this directory or anywhere on your filesystem. The audit tools accept absolute or relative paths.

### Tips for Testing

1. **Start Simple**: Begin with pattern_analysis which requires no external tools
2. **Install Tools**: For comprehensive analysis, install Slither, Aderyn, and Mythril
3. **Compare Results**: Run multiple tools on the same contract to get different perspectives
4. **Test Edge Cases**: Create contracts with known vulnerabilities to verify detection
