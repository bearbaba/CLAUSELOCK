"""Offline contract-state regression suite with a minimal deterministic GenLayer stub."""
import importlib.util
import json
import pathlib
import sys
import types
import unittest

OWNER = "0x" + "1" * 40
OTHER = "0x" + "2" * 40

class Return:
    def __init__(self, value):
        self.calldata = value

class Runtime:
    def __init__(self):
        self.answer = "PRESERVED"
        self.sequence = None
        self.calls = 0
        self.message = types.SimpleNamespace(sender_address=types.SimpleNamespace(as_hex=OWNER))
        self.vm = types.SimpleNamespace(UserError=ValueError, Return=Return,
                                        run_nondet_unsafe=self.validate)
        self.nondet = types.SimpleNamespace(exec_prompt=self.exec_prompt)
        self.public = types.SimpleNamespace(write=lambda f: f, view=lambda f: f)
        self.Contract = MockContract

    def exec_prompt(self, prompt):
        if self.sequence:
            answer = self.sequence[self.calls % len(self.sequence)]
            self.calls += 1
            return answer
        return self.answer

    def validate(self, leader, validator):
        proposal = leader()
        if not validator(Return(proposal)):
            raise ValueError("simulated consensus disagreement")
        return proposal

class MockContract:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        for name, kind in cls.__annotations__.items():
            if getattr(kind, "__origin__", None) is dict:
                setattr(obj, name, {})
        return obj

runtime = Runtime()
mock = types.ModuleType("genlayer")
mock.gl = runtime
mock.TreeMap = dict
mock.u256 = int
sys.modules["genlayer"] = mock
spec = importlib.util.spec_from_file_location("clauselock", pathlib.Path(__file__).parents[1] / "contracts/clauselock.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

BASE = ("All vendor invoices require approval from two separate reviewers before funds "
        "are released. The second reviewer cannot be bypassed by an amount threshold. "
        "Both independent approvals must be recorded and retained permanently.")
SAFE = ("Every vendor payment requires approval from two distinct finance reviewers, "
        "without exemptions based on amount or employee role. Both separate approval "
        "decisions are recorded permanently before the payment is released.")
WEAK = ("Every vendor payment generally needs two approvals. For invoices below "
        "1000 units, a single finance reviewer may approve the payment and issue "
        "it without a second reviewer. Approval records are kept.")
GUARDS = json.dumps([
    {"id": "TWO_SIGNERS", "text": "Two distinct reviewers must approve every vendor payment without amount exceptions."},
    {"id": "AUDIT_TRAIL", "text": "Both independent approvals must be recorded before release."},
])
RATIONALE = "This amendment refines the vendor authorization workflow."

class ClauseLockTests(unittest.TestCase):
    def setUp(self):
        runtime.message.sender_address.as_hex = OWNER
        runtime.answer = "PRESERVED"
        runtime.sequence = None
        runtime.calls = 0
        self.c = module.ClauseLock()
        self.pid = self.c.create_policy("Payment review policy", BASE, GUARDS)

    def change_actor(self, actor):
        runtime.message.sender_address.as_hex = actor

    def propose(self, text=SAFE):
        self.change_actor(OTHER)
        return self.c.propose_amendment(self.pid, text, RATIONALE)

    def test_preserved_revision_and_history(self):
        proposal = self.propose()
        self.assertEqual(self.c.evaluate_amendment(proposal), "PRESERVED")
        p = json.loads(self.c.get_proposal(proposal))
        self.assertEqual(p["base_version"], 1)
        self.change_actor(OWNER)
        self.assertTrue(json.loads(self.c.activation_eligibility(proposal, OWNER))["allowed"])
        self.assertEqual(self.c.activate_amendment(proposal), 2)
        self.assertEqual(json.loads(self.c.get_version(self.pid, 1))["text"], BASE)
        self.assertEqual(json.loads(self.c.get_version(self.pid, 2))["text"], SAFE)
        self.assertEqual(json.loads(self.c.get_policy(self.pid))["version"], 2)

    def test_weakened_and_uncertain_are_not_activated(self):
        proposal = self.propose(WEAK)
        runtime.answer = "WEAKENED"
        self.assertEqual(self.c.evaluate_amendment(proposal), "WEAKENED")
        self.change_actor(OWNER)
        with self.assertRaisesRegex(ValueError, "not authorized"):
            self.c.activate_amendment(proposal)
        proposal2 = self.propose(SAFE)
        runtime.answer = "UNCERTAIN"
        self.assertEqual(self.c.evaluate_amendment(proposal2), "UNCERTAIN")
        self.change_actor(OWNER)
        with self.assertRaises(ValueError):
            self.c.activate_amendment(proposal2)

    def test_stale_and_replay_protection(self):
        p1 = self.propose(SAFE)
        p2 = self.propose(WEAK)
        self.c.evaluate_amendment(p1)
        self.change_actor(OWNER)
        self.c.activate_amendment(p1)
        with self.assertRaisesRegex(ValueError, "stale"):
            self.c.evaluate_amendment(p2)
        with self.assertRaises(ValueError):
            self.c.activate_amendment(p1)

    def test_owner_only_and_cancel(self):
        proposal = self.propose()
        self.c.evaluate_amendment(proposal)
        with self.assertRaisesRegex(ValueError, "owner only"):
            self.c.activate_amendment(proposal)
        self.c.cancel_proposal(proposal)
        self.change_actor(OWNER)
        with self.assertRaises(ValueError):
            self.c.activate_amendment(proposal)

    def test_validator_disagreement_preserves_state(self):
        proposal = self.propose()
        runtime.sequence = ["PRESERVED", "WEAKENED"]
        runtime.calls = 0
        with self.assertRaisesRegex(ValueError, "consensus disagreement"):
            self.c.evaluate_amendment(proposal)
        state = json.loads(self.c.get_proposal(proposal))
        self.assertEqual(state["decision"], "PENDING")
        self.assertEqual(state["status"], "PROPOSED")
        self.assertEqual(json.loads(self.c.get_policy(self.pid))["version"], 1)

    def test_archive_and_guardrail_validation(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.c.create_policy("Example policy", BASE, json.dumps([
                {"id": "REPEAT", "text": "The first independent approval remains required."},
                {"id": "REPEAT", "text": "The second independent approval remains required."}
            ]))
        self.change_actor(OTHER)
        with self.assertRaisesRegex(ValueError, "owner only"):
            self.c.archive_policy(self.pid)
        self.change_actor(OWNER)
        self.c.archive_policy(self.pid)
        with self.assertRaisesRegex(ValueError, "archived"):
            self.c.propose_amendment(self.pid, SAFE, RATIONALE)

if __name__ == "__main__":
    unittest.main()
