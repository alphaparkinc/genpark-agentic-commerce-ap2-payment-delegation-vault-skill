# -*- coding: utf-8 -*-
"""
Example usage of GenParkAgenticCommerceAP2PaymentDelegationVault
Demonstrates issuance of cryptographic spend mandate and transaction execution.
"""

from client import GenParkAgenticCommerceAP2PaymentDelegationVault

def main():
    vault = GenParkAgenticCommerceAP2PaymentDelegationVault()

    print("================================================================")
    print("GenPark Agentic Commerce AP2 Delegation Vault - Live Runs")
    print("================================================================\n")

    # Step 1: Issue Spend Mandate
    mandate = vault.issue_spend_mandate(
        delegating_user_id="USER-ELIZABETH-901",
        authorized_agent_id="AGENT-SHOPPING-PROXY-01",
        max_spend_cap_usd=400.00,
        validity_duration_mins=45,
        allowed_merchant_domains=["target.com", "walmart.com"]
    )
    print(f"Issued Mandate ID      : {mandate['mandate_id']}")
    print(f"Authorized Spend Cap   : ${mandate['max_spend_cap_usd']:.2f}")
    print(f"Signature (HMAC-SHA256): {mandate['cryptographic_mandate_signature'][:32]}...\n")

    # Step 2: Attempt Legitimate Transaction
    tx1 = vault.verify_and_authorize_transaction(
        mandate=mandate,
        transaction_amount_usd=348.00,
        merchant_domain="walmart.com",
        item_sku="SKU-WH1000XM5"
    )
    print("[Transaction 1: Valid Checkout at Walmart ($348.00)]")
    print(f"  Authorization Status   : {tx1['authorization_status']}")
    print(f"  Settlement Pay Token   : {tx1['ephemeral_settlement_token']}")
    print(f"  Remaining Mandate Cap  : ${tx1['remaining_mandate_budget_usd']:.2f}")
    print(f"  Fraud Risk Score       : {tx1['fraud_risk_score']}\n")

    # Step 3: Attempt Overspending Transaction
    tx2 = vault.verify_and_authorize_transaction(
        mandate=mandate,
        transaction_amount_usd=550.00,
        merchant_domain="walmart.com",
        item_sku="SKU-OLED-TV"
    )
    print("[Transaction 2: Overspend Attempt ($550.00 vs $400 Cap)]")
    print(f"  Authorization Status   : {tx2['authorization_status']}")
    print(f"  Decline Reason         : {tx2['reason']}\n")

if __name__ == "__main__":
    main()
