from pathlib import Path
import hashlib
import json


CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "ToolBond.py"
SDK = "v0.2.16"
ROOT = "https://raw.githubusercontent.com/example/tool-bond/" + "a" * 40 + "/"
PROMISE = ROOT + "promise.txt"
REQUEST = ROOT + "request.txt"
RESPONSE = ROOT + "response.txt"
BOND = 10**15


def addr(account):
    return "0x" + account.hex()


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def case(contract, case_id=1):
    return json.loads(contract.get_case(case_id))


def setup(vm, deploy, provider, customer):
    vm.warp("2026-10-12T00:00:00Z")
    vm.sender = provider
    contract = deploy(str(CONTRACT), sdk_version=SDK)
    vm.mock_web(PROMISE, {"status": 200, "body": "Return a JSON summary."})
    vm.value = BOND
    case_id = contract.create_bond(addr(customer), PROMISE, digest("Return a JSON summary."), 100, 100, 100)
    vm.value = 0
    return contract, case_id


def respond(vm, contract, case_id, provider, customer):
    vm.sender = customer
    contract.open_request(case_id, REQUEST, digest("Summarize this report."))
    vm.sender = provider
    contract.submit_response(case_id, RESPONSE, digest('{"summary":"Done"}'))


def mock_evidence(vm):
    vm.mock_web(PROMISE, {"status": 200, "body": "Return a JSON summary."})
    vm.mock_web(REQUEST, {"status": 200, "body": "Summarize this report."})
    vm.mock_web(RESPONSE, {"status": 200, "body": '{"summary":"Done"}'})


def test_full_challenge_pass_returns_bond(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    respond(direct_vm, contract, case_id, direct_alice, direct_bob)
    mock_evidence(direct_vm)
    direct_vm.mock_llm("Judge whether the customer's request", '{"label":"PASS"}')
    direct_vm.mock_llm("Judge whether this public response", '{"label":"PASS"}')
    direct_vm.sender = direct_bob
    contract.challenge(case_id)
    contract.assess_scope(case_id)
    assert case(contract)["scope"] == "PASS"
    assert case(contract)["status"] == "SCOPE_PASSED"
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    contract.assess_delivery(case_id)
    assert case(contract)["status"] == "PROVIDER_PAID"
    assert int(contract.credit_of(addr(direct_alice))) == BOND
    with direct_vm.expect_revert("delivery_assessment_closed"):
        contract.assess_delivery(case_id)


def test_confirmed_failure_slashes_to_customer(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    respond(direct_vm, contract, case_id, direct_alice, direct_bob)
    mock_evidence(direct_vm)
    direct_vm.mock_llm("Judge whether the customer's request", '{"label":"PASS"}')
    direct_vm.mock_llm("Judge whether this public response", '{"label":"FAIL"}')
    direct_vm.sender = direct_bob
    contract.challenge(case_id)
    contract.assess_scope(case_id)
    contract.assess_delivery(case_id)
    assert case(contract)["scope"] == "PASS"
    assert case(contract)["delivery"] == "FAIL"
    assert case(contract)["status"] == "CUSTOMER_PAID"
    assert int(contract.credit_of(addr(direct_bob))) == BOND


def test_missing_provider_response_is_failure(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.open_request(case_id, REQUEST, digest("Summarize this report."))
    direct_vm.warp("2026-10-12T00:03:30Z")
    contract.finalize_timeout(case_id)
    assert case(contract)["status"] == "CUSTOMER_PAID"


def test_out_of_scope_request_cannot_take_bond(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    respond(direct_vm, contract, case_id, direct_alice, direct_bob)
    mock_evidence(direct_vm)
    direct_vm.mock_llm("Judge whether the customer's request", '{"label":"FAIL"}')
    direct_vm.sender = direct_bob
    contract.challenge(case_id)
    contract.assess_scope(case_id)
    assert case(contract)["status"] == "PROVIDER_PAID"
    assert case(contract)["scope"] == "FAIL"


def test_tampered_provider_response_fails(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    respond(direct_vm, contract, case_id, direct_alice, direct_bob)
    direct_vm.mock_web(PROMISE, {"status": 200, "body": "Return a JSON summary."})
    direct_vm.mock_web(REQUEST, {"status": 200, "body": "Summarize this report."})
    direct_vm.mock_web(RESPONSE, {"status": 200, "body": "tampered"})
    direct_vm.mock_llm("Judge whether the customer's request", '{"label":"PASS"}')
    direct_vm.sender = direct_bob
    contract.challenge(case_id)
    contract.assess_scope(case_id)
    contract.assess_delivery(case_id)
    assert case(contract)["delivery_evidence"]["response"] == "HASH_MISMATCH"
    assert case(contract)["status"] == "CUSTOMER_PAID"


def test_only_parties_can_submit_and_withdraw(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("customer_required"):
        contract.open_request(case_id, REQUEST, digest("request"))
    with direct_vm.expect_revert("no_credit"):
        contract.withdraw()
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-10-12T00:02:00Z")
    contract.finalize_timeout(case_id)
    assert int(contract.credit_of(addr(direct_alice))) == BOND
    contract.withdraw()
    assert int(contract.credit_of(addr(direct_alice))) == 0
    with direct_vm.expect_revert("no_credit"):
        contract.withdraw()


def test_unassessed_challenge_resolves_without_automatic_slash(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    respond(direct_vm, contract, case_id, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.challenge(case_id)
    direct_vm.warp("2026-10-20T00:00:00Z")
    contract.finalize_timeout(case_id)
    assert case(contract)["status"] == "UNRESOLVED"
    assert int(contract.credit_of(addr(direct_alice))) == BOND
    assert int(contract.customer_wins.get(addr(direct_bob).lower(), 0)) == 0


def test_missing_promise_after_registration_favors_customer(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, case_id = setup(direct_vm, direct_deploy, direct_alice, direct_bob)
    respond(direct_vm, contract, case_id, direct_alice, direct_bob)
    direct_vm.clear_mocks()
    direct_vm.mock_web(PROMISE, {"status": 404, "body": ""})
    direct_vm.mock_web(REQUEST, {"status": 200, "body": "Summarize this report."})
    direct_vm.sender = direct_bob
    contract.challenge(case_id)
    contract.assess_scope(case_id)
    assert case(contract)["scope"] == "PROMISE_MISSING"
    assert case(contract)["status"] == "CUSTOMER_PAID"


def test_invalid_promise_cannot_be_bonded(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-12T00:00:00Z")
    direct_vm.sender = direct_alice
    contract = direct_deploy(str(CONTRACT), sdk_version=SDK)
    direct_vm.mock_web(PROMISE, {"status": 200, "body": "different promise"})
    direct_vm.value = BOND
    with direct_vm.expect_revert("promise_evidence_invalid"):
        contract.create_bond(addr(direct_bob), PROMISE, digest("Return a JSON summary."), 100, 100, 100)
    direct_vm.value = 0
    assert int(contract.count) == 0
