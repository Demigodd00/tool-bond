# ToolBond

ToolBond is a standalone GenLayer Intelligent Contract for a **single named customer's, single invocation** tool warranty. A provider locks native-asset collateral and points to a full-commit, SHA-256-bound public promise. The customer locks a request reference; the provider locks a response reference. A challenge triggers two independent on-chain assessments: whether the request is in scope, then whether the response fulfills the promise. The result controls who can withdraw the bond.

This repository intentionally contains **no frontend, dashboard, policy explorer, or user-facing app**. The contribution is the contract and its protocol/tests.

## Contract mechanism

1. `create_bond` checks that the provider's public promise is independently retrievable and SHA-256 correct, then escrows the exact attached bond for a named customer. Promise URL/hash and time windows are immutable.
2. The customer calls `open_request` with a full-commit raw GitHub URL and SHA-256. The provider calls `submit_response` with a similarly locked response.
3. The customer may `challenge`. `assess_scope` and `assess_delivery` are separate public transactions; any account can drive them. GenLayer validators refetch evidence and independently compare the substantive labels and evidence states. A confirmed in-scope failure or invalid provider response credits the customer. An out-of-scope/unclear request or a passing/unclear delivery credits the provider.
4. `finalize_timeout` handles missed requests, missed responses, no challenge, and unassessed challenges. Credits are pull-withdrawn with state zeroed before transfer.

See [the protocol](docs/PROTOCOL.md) for exact outcomes and limitations.

## Source and validation

- Contract: [`contracts/ToolBond.py`](contracts/ToolBond.py)
- Direct tests: [`tests/direct/test_tool_bond.py`](tests/direct/test_tool_bond.py)
- Runner: pinned in the contract's first line; no `latest` runner alias
- `genvm-lint check contracts/ToolBond.py --json`
- `pytest tests/direct -q`

The contract does not execute tools, authenticate off-chain runtime behavior, or guarantee that a URL represents a real invocation. Parties must publish non-sensitive evidence and choose a specific, testable promise. It is an adjudication and collateral mechanism, not a sandbox, insurance product, or legal determination.
