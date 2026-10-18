# Intelligent Contracts submission correction

**Original contribution date:** 12/10/2026

**Correction date:** 19/10/2026

**Title:** ToolBond — Bonded AI Tool Warranty Intelligent Contract

**Notes / Description:**

ToolBond is a standalone GenLayer Intelligent Contract, not a user-facing app. A provider creates a payable, per-invocation bond for a named customer against a SHA-256-verified public promise. The customer and provider lock request and response references. A challenge triggers separate validator judgments on request scope and delivery; validators independently refetch the full-commit evidence and compare substantive labels and verification states. Deterministic deadlines and pull withdrawals govern escrow settlement. The corrected StudioNet deployment exposes `create_bond.payable=true`; its source matches the public commit, and ten direct tests pass. No live funded bond or settlement has yet been demonstrated. ToolBond does not execute tools or prove private off-chain behavior.

**Evidence links:**

1. Repository: https://github.com/Demigodd00/tool-bond
2. Exact corrected contract source: https://github.com/Demigodd00/tool-bond/blob/7dd3b7425e3926e0c399b527a3db32db738678ab/contracts/ToolBond.py
3. Corrected GenLayer Explorer deployment: https://explorer-studio.genlayer.com/address/0x41816cc5D6752AA43dE1c7F8dA2C52b432ceAa8e
4. Corrected deployment transaction: https://explorer-studio.genlayer.com/tx/0x371775d1bdab21fec5d3bbe3ee17d3454228d8e02bdc3e6b1d8e6b6ace083bd0
5. Deployment and schema-readback record: https://github.com/Demigodd00/tool-bond/blob/main/deployments/studionet.json
6. Protocol and limitations: https://github.com/Demigodd00/tool-bond/blob/main/docs/PROTOCOL.md
7. Direct tests, including payable-schema regression: https://github.com/Demigodd00/tool-bond/blob/main/tests/direct/test_tool_bond.py

**Steward response draft:**

Thank you for catching the payable-schema mismatch. I changed `create_bond` to `@gl.public.write.payable` and redeployed the matching public source. The corrected StudioNet contract is https://explorer-studio.genlayer.com/address/0x41816cc5D6752AA43dE1c7F8dA2C52b432ceAa8e . Its live `gen_getContractSchema` response now reports `create_bond.payable=true`; `gen_getContractCode` matches the source pinned at commit `7dd3b7425e3926e0c399b527a3db32db738678ab`. The deployment transaction finalized with successful leader execution. The old non-payable address is superseded. I have not yet demonstrated a live funded bond or settlement, so this evidence addresses the specific schema blocker rather than claiming full escrow proof.

Do not claim stewardship approval or a live funded warranty. The human submits the Portal response.
