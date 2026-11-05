# CLAUSELOCK

**Policy upgrades without silently weakening protected commitments.**

CLAUSELOCK is a reusable **GenLayer Intelligent Contract** for organizations, DAOs and approval processes that want to preserve important safeguards when policy language changes.

## Product workflow

1. **Lock a policy.** Its owner registers a baseline policy and a set of explicitly protected natural-language guarantees (stable clause IDs).
2. **Propose a revision.** Any proposer submits a candidate, its rationale and a snapshot of the active version.
3. **Assess the meaning.** GenLayer AI consensus compares the full candidate against every frozen guarantee and records `PRESERVED`, `WEAKENED` or `UNCERTAIN`.
4. **Activate safely.** Only the owner can activate a `PRESERVED` proposal; activation requires the exact unchanged base version and writes an immutable version snapshot.
5. **Inspect the history.** Each policy, amendment, decision, eligibility check and active text remains queryable on-chain.

## Why GenLayer matters

Mechanical text diffs do not reveal whether an exception weakens a two-signature rule, whether a clause changes scope or whether an apparently harmless rewrite removes an obligation. CLAUSELOCK uses the **same frozen guarantees and candidate** for a leader AI assessment and an **independent validator reassessment**, comparing the three stable decision labels rather than trusting formatting alone.

### An illustrative policy

Protected guarantee `DUAL_APPROVAL`: Every vendor payment requires approval from **two distinct reviewers**. A revised policy that allows **one reviewer for low-value invoices** weakens this guarantee. A rephrasing that retains two independent approvals preserves it. Ambiguous changes remain `UNCERTAIN` and cannot be activated.

## Contract primitives

| Write call | Effect |
| --- | --- |
| `create_policy(title, baseline_text, protected_clauses_json)` | Locks original obligations with wallet ownership and hash-bound version 1 |
| `propose_amendment(policy_id, candidate_text, rationale)` | Creates a version-bound amendment |
| `evaluate_amendment(proposal_id)` | Runs independent GenLayer AI consensus on protected semantics |
| `activate_amendment(proposal_id)` | Owner-only and `PRESERVED`-only activation; appends a version |
| `cancel_proposal(proposal_id)` | Closes an unactivated proposal |
| `archive_policy(policy_id)` | Owner permanently closes the active policy |

Read calls: `get_policy`, `get_proposal`, `get_version`, `activation_eligibility`, `stats`. Guardrails are immutable. Older assessed proposals cannot silently apply after a new version becomes active; historical versions persist.

## Live Studionet demonstration

**Policy #1 has been upgraded from version 1 to version 2** on [GenLayer Studionet 61999](https://explorer-studio.genlayer.com/address/0x683A1718D50ae65b9eAfa31F06DfB06FC7C9DEED). The signed workflow includes owner-created protected guarantees, a proposer-signed revision, independent AI consensus returning `PRESERVED`, and owner activation. The live `LATEST_FINAL` readback confirms `version=2` and `Proposal #1: ACTIVATED / PRESERVED`. A second amendment attempted to weaken two-reviewer and audit safeguards; GenLayer consensus returned `WEAKENED`, and `activate_amendment(2)` was rejected by on-chain rollback with three validator agreements. The policy remained at version 2.

[**View signed approvals, rejected changes and verified state**](docs/ONCHAIN_EVIDENCE.md).

## Quickstart

Source: [`contracts/clauselock.py`](contracts/clauselock.py). Import it into [GenLayer Studio](https://studio.genlayer.com/) and follow [`docs/STUDIO_ACCEPTANCE.md`](docs/STUDIO_ACCEPTANCE.md). Use separate owner and proposer wallets to demonstrate the authorization boundary.

Run local deterministic tests (Python 3.11+):

```bash
python -m unittest discover -s tests -v
python -m py_compile contracts/clauselock.py
```

These are offline contract-state tests using a mock GenLayer runtime. GenLayer consensus acceptance is established only by actual Studio executions and finalized on-chain readbacks.

## Design boundaries

The contract evaluates semantic compliance against the policy owner's explicit protected guarantees, not legal enforceability. `PRESERVED` is a GenLayer-consensus decision, not an external governance vote or legal opinion. This is a self-contained contract primitive; integration into treasury or proposal executors is a separate application decision.

**CLAUSELOCK · Protect the meaning, not just the wording.**