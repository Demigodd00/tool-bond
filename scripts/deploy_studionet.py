"""Deploy ToolBond from the committed source; print verifiable deployment data."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

from eth_account import Account
from eth_utils import to_checksum_address
from genlayer_py import create_client
from genlayer_py.assertions import tx_execution_succeeded
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionStatus


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "ToolBond.py"


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def tx_hex(value: object) -> str:
    rendered = str(value)
    return rendered if rendered.startswith("0x") else "0x" + bytes(value).hex()


def main() -> None:
    if git("status", "--porcelain"):
        raise RuntimeError("working tree must be clean before deploying")
    commit = git("rev-parse", "HEAD").decode().strip()
    source = SOURCE.read_text(encoding="utf-8").replace("\r\n", "\n")
    tracked = git("show", "HEAD:contracts/ToolBond.py").decode().replace("\r\n", "\n")
    if source != tracked:
        raise RuntimeError("deployed source would differ from committed source")
    url = f"https://raw.githubusercontent.com/Demigodd00/tool-bond/{commit}/contracts/ToolBond.py"
    with urllib.request.urlopen(url, timeout=30) as response:
        public = response.read().decode().replace("\r\n", "\n")
    if public != source:
        raise RuntimeError("public committed source differs from local source")

    signer = Account.create()
    client = create_client(chain=studionet, account=signer)
    tx = client.deploy_contract(code=source, account=signer, args=[])
    print(json.dumps({"step": "deploy", "transaction": tx_hex(tx)}), flush=True)
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=tx_hex(tx),
        status=TransactionStatus.FINALIZED,
        interval=5_000,
        retries=120,
        full_transaction=True,
    )
    if (receipt.get("status_name") or receipt.get("statusName")) != TransactionStatus.FINALIZED.value:
        raise RuntimeError("deployment did not finalize")
    if not tx_execution_succeeded(receipt):
        raise RuntimeError("deployment execution failed: " + json.dumps(receipt, default=str))
    if (receipt.get("result_name") or receipt.get("resultName")) not in (None, "AGREE", "MAJORITY_AGREE"):
        raise RuntimeError("deployment did not reach consensus")
    address = None
    for key in ("tx_data_decoded", "data"):
        item = receipt.get(key)
        if isinstance(item, dict) and item.get("contract_address"):
            address = to_checksum_address(str(item["contract_address"]))
            break
    if address is None:
        raise RuntimeError("finalized receipt omitted contract address")
    encoded = client.provider.make_request("gen_getContractCode", [address]).get("result")
    if not isinstance(encoded, str):
        raise RuntimeError("deployed source unavailable")
    deployed = base64.b64decode(encoded, validate=True).decode().replace("\r\n", "\n")
    if deployed != source:
        raise RuntimeError("deployed source differs from committed source")
    schema_response = client.provider.make_request("gen_getContractSchema", [address])
    schema = schema_response.get("result")
    if not isinstance(schema, dict):
        raise RuntimeError("deployed schema unavailable: " + json.dumps(schema_response, default=str))
    methods = schema.get("methods", {})
    if methods.get("create_bond", {}).get("payable") is not True:
        raise RuntimeError("deployed create_bond is not payable")
    print(json.dumps({
        "network": "studionet",
        "chain_id": 61999,
        "status": "VERIFIED",
        "source_commit": commit,
        "source_url": url,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "contract_address": address,
        "explorer": "https://explorer-studio.genlayer.com/address/" + address,
        "deploy_transaction": tx_hex(tx),
        "wallet_policy": "disposable StudioNet-only signer; private key not retained",
        "deployer": signer.address,
        "create_bond_payable": True,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
