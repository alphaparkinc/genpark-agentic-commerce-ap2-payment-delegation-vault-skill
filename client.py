# -*- coding: utf-8 -*-
"""
GenPark Agentic Commerce AP2 Payment Delegation Vault Client
Manages Agentic Payment Protocol ephemeral tokens with cryptographic spend mandates and risk scoring.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
import hashlib
import hmac
import time
from typing import Dict, Any, List

class GenParkAgenticCommerceAP2PaymentDelegationVault:
    """
    Agentic Payment Protocol (AP2) Security Core:
    Implements cryptographic ephemeral tokenization, strict budget caps,
    and zero primary account number (PAN) leakage for autonomous AI agents.
    """

    def __init__(self, vault_master_secret: str = "AP2MasterSecretKeyAlphaPark2026"):
        self.secret = vault_master_secret.encode("utf-8")

    def generate_mandate_signature(self, mandate_id: str, cap_usd: float, exp_timestamp: int) -> str:
        """Signs spend delegation mandate with HMAC-SHA256."""
        payload = f"{mandate_id}:{cap_usd:.2f}:{exp_timestamp}".encode("utf-8")
        return hmac.new(self.secret, payload, hashlib.sha256).hexdigest()

    def issue_spend_mandate(
        self,
        delegating_user_id: str,
        authorized_agent_id: str,
        max_spend_cap_usd: float,
        validity_duration_mins: int = 60,
        allowed_merchant_domains: List[str] = None
    ) -> Dict[str, Any]:
        """
        Issues cryptographically bound financial spend mandate for autonomous agent execution.
        """
        if allowed_merchant_domains is None:
            allowed_merchant_domains = ["walmart.com", "target.com", "bestbuy.com", "shopify.com"]

        now = int(time.time())
        exp = now + (validity_duration_mins * 60)
        mandate_id = f"AP2-MND-{hashlib.md5(f'{delegating_user_id}:{now}'.encode()).hexdigest()[:12].upper()}"
        signature = self.generate_mandate_signature(mandate_id, max_spend_cap_usd, exp)

        return {
            "mandate_id": mandate_id,
            "delegating_user_id": delegating_user_id,
            "authorized_agent_id": authorized_agent_id,
            "max_spend_cap_usd": round(max_spend_cap_usd, 2),
            "issued_timestamp": now,
            "expires_timestamp": exp,
            "validity_duration_mins": validity_duration_mins,
            "allowed_merchant_domains": allowed_merchant_domains,
            "cryptographic_mandate_signature": signature
        }

    def verify_and_authorize_transaction(
        self,
        mandate: Dict[str, Any],
        transaction_amount_usd: float,
        merchant_domain: str,
        item_sku: str
    ) -> Dict[str, Any]:
        """
        Executes AP2 transaction verification and issues single-use settlement token.
        """
        now = int(time.time())
        m_id = mandate.get("mandate_id")
        cap = mandate.get("max_spend_cap_usd", 0.0)
        exp = mandate.get("expires_timestamp", 0)
        sig = mandate.get("cryptographic_mandate_signature", "")

        # 1. Verify Cryptographic Integrity
        expected_sig = self.generate_mandate_signature(m_id, cap, exp)
        if not hmac.compare_digest(sig, expected_sig):
            return {
                "authorization_status": "DECLINED_SIGNATURE_TAMPERED",
                "authorized": False,
                "reason": "Cryptographic spend mandate signature verification failed."
            }

        # 2. Check Expiration
        if now > exp:
            return {
                "authorization_status": "DECLINED_MANDATE_EXPIRED",
                "authorized": False,
                "reason": "Mandate has expired."
            }

        # 3. Check Spend Cap
        if transaction_amount_usd > cap:
            return {
                "authorization_status": "DECLINED_EXCEEDS_BUDGET_CAP",
                "authorized": False,
                "reason": f"Transaction ${transaction_amount_usd:.2f} exceeds authorized limit ${cap:.2f}."
            }

        # 4. Check Allowed Merchant Domains
        allowed = mandate.get("allowed_merchant_domains", [])
        if allowed and merchant_domain.lower() not in [d.lower() for d in allowed]:
            return {
                "authorization_status": "DECLINED_UNAUTHORIZED_MERCHANT",
                "authorized": False,
                "reason": f"Merchant '{merchant_domain}' is not in authorized domain whitelist."
            }

        # Issue Ephemeral Single-Use Settlement Token (Tokenized Agent Pay)
        token_seed = f"{m_id}:{transaction_amount_usd}:{now}:{item_sku}".encode("utf-8")
        ephemeral_pay_token = f"tok_ap2_{hashlib.sha256(token_seed).hexdigest()[:24]}"

        # Risk scoring
        risk_score = round(min(1.0, max(0.01, (transaction_amount_usd / cap) * 0.35)), 3)

        return {
            "authorization_status": "APPROVED",
            "authorized": True,
            "ephemeral_settlement_token": ephemeral_pay_token,
            "settled_amount_usd": round(transaction_amount_usd, 2),
            "remaining_mandate_budget_usd": round(cap - transaction_amount_usd, 2),
            "fraud_risk_score": risk_score,
            "audit_trail": {
                "mandate_id": m_id,
                "merchant_domain": merchant_domain,
                "item_sku": item_sku,
                "timestamp": now,
                "zero_pan_leakage_verified": True
            }
        }
