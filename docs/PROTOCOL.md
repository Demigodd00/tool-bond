# ToolBond protocol

## Roles and evidence

The provider creates one bond for one preselected customer. Each case is independent, so the same contract can host repeated warranties without rewriting policy or conflating evidence. `create_bond` accepts 0.001–1 native token and three bounded time windows (60 seconds–30 days). Request and response references use raw GitHub URLs pinned to 40-character commit IDs and exact SHA-256 digests. The provider promise is fetched and hashed during creation; request and response are fetched and hashed during adjudication. Each source is limited to 6,000 bytes. These are **public** documents; secrets or private customer data must not be published.

The named on-chain customer controls the request and challenge. The named on-chain provider controls the response. The contract does not infer identity from GitHub authorship or an off-chain signature. Whoever controls a party's wallet may submit that party's URL/hash reference.

## Decision and settlement

`assess_scope` asks whether the customer's request is covered by the frozen promise. If the promise has disappeared or its hash changed after registration, the customer wins. If the request is missing/tampered, or the substantive result is FAIL/UNCLEAR, the provider wins. Only PASS advances to `assess_delivery`.

`assess_delivery` asks whether the response satisfies that in-scope request. A missing/tampered provider response or substantive FAIL gives the customer the bond. PASS/UNCLEAR returns it to the provider. An UNCLEAR result is *not* represented as a proven breach.

These labels are judged separately with independently re-fetched source content, not a single summary prompt. Validators compare the label, assessment dimension, and source verification states under the equivalence principle. Hash and source-state checks are deterministic. A result is stored before crediting either party. The contract uses pull payments; withdrawal clears credit before transferring value.

## Deadlines

- No request by request deadline: provider may reclaim the bond.
- No response by response deadline: customer receives the bond.
- No challenge by challenge deadline: provider may reclaim the bond.
- No completed assessment by seven days after challenge: case becomes `UNRESOLVED`; the bond is returned to the provider. This is expressly *not* a PASS verdict. Off-chain disputes remain possible, but the contract does not slash without a confirmed result.

Deadlines are evaluated from on-chain transaction time. Anyone can call `finalize_timeout` after the relevant deadline. A settlement may be withdrawn once; duplicate settlement and withdrawal are rejected.

## Threat model and limitations

- URL/hash pinning protects the exact bytes that validators see; it does not prove that the provider actually ran a tool or that the customer honestly described the task. GenLayer cannot observe a private API call from these public documents alone.
- Customer-authored requests can be adversarial or out of scope; a scope assessment protects the provider from those. Missing customer request evidence also favors the provider.
- The provider must keep its registered promise available. Its disappearance favors the customer. Missing/tampered provider response favors the customer only after scope passes.
- The LLM can return UNCLEAR or validators can fail to reach consensus. The former favors the provider; the latter leaves the case open until the assessment deadline, after which it is marked UNRESOLVED. No claim is made that subjective adjudication is infallible.
- The bond is per invocation, not a pooled fund. This avoids overcommitting collateral across multiple claims.
- The contract does not charge a customer fee, issue a transferable reputation token, inspect executable code, or offer an end-user product interface.
