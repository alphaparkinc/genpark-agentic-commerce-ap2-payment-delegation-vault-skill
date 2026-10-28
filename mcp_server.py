# -*- coding: utf-8 -*-
"""
GenPark Agentic Commerce AP2 Payment Delegation Vault MCP Server
Exposes Agentic Payment Protocol tokenization and spend authorization tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GenParkAgenticCommerceAP2PaymentDelegationVault

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-ap2-payment-delegation-vault", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "issue_spend_mandate",
                        "description": "Issues cryptographically bound financial spend mandate for autonomous agent execution.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "delegating_user_id": {"type": "string"},
                                "authorized_agent_id": {"type": "string"},
                                "max_spend_cap_usd": {"type": "number"},
                                "validity_duration_mins": {"type": "integer"}
                            },
                            "required": ["delegating_user_id", "authorized_agent_id", "max_spend_cap_usd"]
                        }
                    },
                    {
                        "name": "verify_and_authorize_transaction",
                        "description": "Executes AP2 transaction verification and issues single-use settlement token.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "mandate": {"type": "object"},
                                "transaction_amount_usd": {"type": "number"},
                                "merchant_domain": {"type": "string"},
                                "item_sku": {"type": "string"}
                            },
                            "required": ["mandate", "transaction_amount_usd", "merchant_domain"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        vault = GenParkAgenticCommerceAP2PaymentDelegationVault()

        if tool_name == "issue_spend_mandate":
            res = vault.issue_spend_mandate(
                delegating_user_id=args.get("delegating_user_id", "USR-ALICE-99"),
                authorized_agent_id=args.get("authorized_agent_id", "AGENT-SHOPPER-X"),
                max_spend_cap_usd=args.get("max_spend_cap_usd", 250.0),
                validity_duration_mins=args.get("validity_duration_mins", 60)
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tool_name == "verify_and_authorize_transaction":
            res = vault.verify_and_authorize_transaction(
                mandate=args.get("mandate", {}),
                transaction_amount_usd=args.get("transaction_amount_usd", 120.0),
                merchant_domain=args.get("merchant_domain", "walmart.com"),
                item_sku=args.get("item_sku", "SKU-TEST-001")
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        v = GenParkAgenticCommerceAP2PaymentDelegationVault()
        m = v.issue_spend_mandate("USER-1", "AGENT-1", 500.0)
        t = v.verify_and_authorize_transaction(m, 320.0, "walmart.com", "SKU-TV")
        print(f"Test Status: {t['authorization_status']}")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
