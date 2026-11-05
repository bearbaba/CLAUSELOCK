# CLAUSELOCK — Signed Studionet evidence

**Network:** GenLayer Studionet 61999  
**Deployed contract:** [0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED](https://explorer-studio.genlayer.com/address/0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED)

This ledger records signed transaction results and independently checked persisted `LATEST_FINAL` state from the **Policy #1, Proposal #1 and Proposal #2** workflow.

## Signed lifecycle

| Step | Method | Signer | GenVM result | Returned value | Evidence |
| --- | --- | --- | --- | --- | --- |
| Create policy | `create_policy` | Owner `0x4C7c…8Dcb` | FINALIZED · SUCCESS · Accepted | Policy ID `1` | [Transaction](https://explorer-studio.genlayer.com/tx/0x8b6646626304775e7397b4a538976e0f2fb1bec063137da42290e91bbeffc78d) |
| Propose wording-preserving amendment | `propose_amendment(1, …)` | Proposer `0x60Bf…eBff` | FINALIZED · SUCCESS · Accepted | Proposal ID `1` | [Transaction](https://explorer-studio.genlayer.com/tx/0x54c630444bb0877e0fc60b7b48ae337ee4916dbb91ee29e5b3ebe3042aa3573c) |
| Evaluate protected meaning | `evaluate_amendment(1)` | Proposer `0x60Bf…eBff` | FINALIZED · SUCCESS · Accepted | `PRESERVED` | [Transaction](https://explorer-studio.genlayer.com/tx/0x683c6022a04323b0ef313ee8a2f5fb69af3c4a59c57b2e101a1604412e20e350) |
| Activate approved version | `activate_amendment(1)` | Owner `0x4C7c…8Dcb` | FINALIZED · SUCCESS · Accepted | Policy version `2` | [Transaction](https://explorer-studio.genlayer.com/tx/0x775ac328b602464455bc5a0f6d80cd7868e1f08fab3b533627394fb4e1f8e09f) |

## Semantic safeguard assessment — Proposal #2

After version 2 was activated, the Owner submitted a new amendment that would allow **one reviewer for invoices below 1,000 units** and require only that reviewer's record. This conflicts with both frozen protected guarantees.

| Step | Method | Signer | GenVM result | Returned value | Evidence |
| --- | --- | --- | --- | --- | --- |
| Create weaker amendment | `propose_amendment(1, …)` | Owner `0x4C7c…8Dcb` | FINALIZED · SUCCESS · Accepted | Proposal ID `2` | [Transaction](https://explorer-studio.genlayer.com/tx/0x506703b6bff9e402f1f07a5193b65c2f8526bb465e7fdb9d8159e72b04ce6dc5) |
| Assess safeguard weakening | `evaluate_amendment(2)` | Owner `0x4C7c…8Dcb` | FINALIZED · SUCCESS · Accepted | `WEAKENED` | [Transaction](https://explorer-studio.genlayer.com/tx/0x2ab0001945765fce2518238dd3d8dafc6131e60b11179c7c16271147644b3f85) |

### Enforcement — rejected activation of weakened policy

The Owner signed `activate_amendment(2)` after GenLayer evaluated the second proposal as `WEAKENED`.

- [On-chain transaction](https://explorer-studio.genlayer.com/tx/0x15d0a6dd7cf993dc98ebb81cd3fd3d7c033b445b88ab8b2def6a2e5a905951ba)
- Transaction status: **FINALIZED**; consensus result: **Accepted**.
- GenVM execution: **ERROR / Rollback**, intentionally rejecting the disallowed state transition.
- Exact rollback message: `proposal not authorized for activation`.
- Validator responses: three `Agree` results on the same rollback; two other validators cancelled after quorum.
- This is an **expected security-enforcement outcome**, not a successful activation.

The effective policy version is independently checked by the read-only `LATEST_FINAL` verification workflow.

The equivalence principle output for the second assessment was also **`WEAKENED`**. This demonstrates semantic classification of an explicit exception to the two-reviewer requirement. Contract-level enforcement is determined by `activate_amendment`, which requires an assessed `PRESERVED` verdict.

### Scope and authorization

- Policy Owner: `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`.
- Proposal author: `0x60Bfdf6315294c7856Acdc0B80D7Bd40217DEBff`.
- Protected guarantees: `DUAL_APPROVAL` (two distinct approvals without amount-based exceptions) and `AUDIT_TRAIL` (retain both approvals).
- The revised policy retains independent approval requirements across payment amounts, plus permanent audit records.
- The `evaluate_amendment` transaction returned `PRESERVED` with equivalence output `PRESERVED` and Consensus `Accepted`.

### Independent latest-final readback

[Read-only deployment and state verification](https://github.com/bearbaba/CLAUSELOCK/actions/runs/42035764726), successful re-run after activation on Nov 5, 2026:

```json
{"policies":1,"proposals":1}
{"policy_id":1,"owner":"0x4c7cb73ac8f8999af21cfc9ff4cf2333a9508dcb","version":2,"guardrails":["DUAL_APPROVAL","AUDIT_TRAIL"]}
{"proposal_id":1,"base_version":1,"status":"ACTIVATED","decision":"PRESERVED"}
```

The automated read-only preflight also verified a normalized deployed-source match, required ABI schema, and a successful `LATEST_FINAL` read. The initial policy and active version are retained in the versioned contract state.

## Reviewer walkthrough

Import the [deployed contract](https://studio.genlayer.com/?import-contract=0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED), read `get_policy(1)` and `get_proposal(1)`, then inspect `get_version(1,1)` and `get_version(1,2)` to compare the original and activated texts. The contract's runtime uses independent GenLayer validator evaluation; historical records and current activation eligibility remain readable.

