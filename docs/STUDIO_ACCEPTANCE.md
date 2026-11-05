# CLAUSELOCK — Studio-first acceptance guide

Target **GenLayer Studionet 61999**, Python class `ClauseLock` in `contracts/clauselock.py`. Use one owner and one separate proposer wallet. **Record real contract address, tx hashes, GenVM execution, validator consensus and LATEST_FINAL readbacks.** Do not infer results from synthetic examples.

## Sample test fixture

Policy title: `Vendor payment authorization`

Baseline text:

> For every vendor invoice in this organization, at least two distinct finance reviewers must approve the payment before it is released. No employee or threshold-based exception may bypass the second independent approval. Records of both reviewers must be retained.

Protected clauses JSON:

```json
[{"id":"DUAL_APPROVAL","text":"Every vendor payment requires approval from two separate reviewers, with no amount-based exception."},{"id":"AUDIT_TRAIL","text":"Both independent approvals must be recorded and retained before payment."}]
```

### Scenario A — same protection, revised wording

Call `create_policy(title, baseline, guardrails)` as Owner. Read `get_policy(1)` and `get_version(1,1)`.

From a separate proposer wallet, record this candidate amendment (rationale minimum 24 chars):

> Every vendor payment, regardless of its value, requires approval from two different finance reviewers before release. A permanent approval record must capture both separate decisions, and there are no threshold exceptions.

Call `propose_amendment(1, candidate, rationale)` → keep returned proposal ID. Call `evaluate_amendment(id)`. Inspect returned label and `get_proposal(id)`. For a finalized `PRESERVED` outcome, check `activation_eligibility(id, Owner)`, then sign `activate_amendment(id)` as Owner. Confirm version 2 and `get_version(1,2)` at LATEST_FINAL.

### Scenario B — weakened guarantee

Create another proposal against the active version with:

> Every vendor payment usually requires two reviewers, but payments below 1000 units may be released with only one reviewer's approval. A record of approvals should be kept.

Invoke `evaluate_amendment(id)`. The expected semantic judgment is `WEAKENED`; independently verify the actual consensus. Any non-`PRESERVED` outcome must fail `activate_amendment` and leave the active version unchanged.

### Scenario C — stale revision and wallet protection

Propose two candidates against the same version. After one is `PRESERVED` and activated, verify the other cannot be activated against the replaced base. Attempt activation with non-owner wallet and confirm rollback. Cancel an unactivated proposal and check `get_proposal` retains the decision and `CANCELLED` state.

## Evidence requirements

Each successful call: transaction hash + `FINALIZED` + GenVM `SUCCESS` + stored-state readback. AI decisions additionally require the actual consensus result. A finalized rollback is a negative-test result, not successful execution. Compare source and deployment class/schema in Studio.

## Verification scope

This is a standalone policy-integrity primitive without a frontend dependency. Reproduce the signed scenario using the contract source, local tests, actual Studio transactions, validator consensus output and final-state readbacks.