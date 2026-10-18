# ToolBond

ToolBond is a standalone GenLayer Intelligent Contract for a **single named customer's, single invocation** tool warranty. A provider locks native-asset collateral and points to a full-commit, SHA-256-bound public promise. The customer locks a request reference; the provider locks a response reference. A challenge triggers two independent on-chain assessments: whether the request is in scope, then whether the response fulfills the promise. The result controls who can withdraw the bond.

This repository intentionally contains **no frontend, dashboard, policy explorer, or user-facing app**. The contribution is the contract and its protocol/tests.

## Contract mechanism

1. Payable `create_bond` checks that the provider's public promise is independently retrievable and SHA-256 correct, then escrows the exact attached bond for a named customer. Promise URL/hash and time windows are immutable.
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

## StudioNet deployment

- [Corrected contract in GenLayer Explorer](https://explorer-studio.genlayer.com/address/0x41816cc5D6752AA43dE1c7F8dA2C52b432ceAa8e)
- [Exact deployed source at a full commit](https://github.com/Demigodd00/tool-bond/blob/7dd3b7425e3926e0c399b527a3db32db738678ab/contracts/ToolBond.py)
- [Deployment record](deployments/studionet.json)

The corrected deployment finalized with leader execution `SUCCESS`. Its source was fetched back from the chain and matched against the public commit; its on-chain schema reports `create_bond.payable=true`. The previous non-payable deployment is [archived](deployments/studionet-original.json) and should not be used as evidence for bond creation. This corrected instance has **not** yet exercised a live funded warranty; contract behavior is verified by ten direct tests. Do not present deployment alone as proof of a funded case or settled real-world claim.
