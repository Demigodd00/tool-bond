# Intelligent Contracts submission text

**Contribution date:** 12/10/2026

**Title:** ToolBond — Bonded AI Tool Warranty Intelligent Contract

**Notes / Description:**

ToolBond is a standalone GenLayer Intelligent Contract, not a user-facing app. A tool provider escrows a per-invocation bond for a named customer against an immutable, SHA-256-verified public promise. The customer commits a request reference and the provider commits a response reference. A timely challenge invokes two separately stored GenLayer consensus judgments: whether the request is within the frozen promise, and whether the response fulfills it. Validators independently refetch the full-commit GitHub evidence, check exact hashes, and compare substantive labels plus source-verification states. Deterministic deadlines resolve missing requests, missing responses, unchallenged responses, and unassessed challenges. A proven in-scope failure or missing provider evidence credits the customer; no proven breach returns the bond to the provider. Pull withdrawals prevent double payouts. The contract does not execute tools or prove private off-chain behavior. Source is deployed on StudioNet; nine direct tests pass. No live funded case has been run yet.

**Evidence links:**

1. Repository: https://github.com/Demigodd00/tool-bond
2. Tracked contract source at deployment commit: https://github.com/Demigodd00/tool-bond/blob/268e1220e3e7f1d3ca3b1e7ce38ce17e62784266/contracts/ToolBond.py
3. GenLayer Explorer: https://explorer-studio.genlayer.com/address/0x2144D5B9D3094F501dB1779719AB3396bE1609e7
4. Deployment record: https://github.com/Demigodd00/tool-bond/blob/main/deployments/studionet.json
5. Protocol and limitations: https://github.com/Demigodd00/tool-bond/blob/main/docs/PROTOCOL.md
6. Direct tests: https://github.com/Demigodd00/tool-bond/blob/main/tests/direct/test_tool_bond.py

Do not claim stewardship approval or a live claim settlement. The repository is public and contains no frontend or project dashboard.
