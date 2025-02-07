# defi/models.py (Updated)
from django.db import models


# Existing Models (Do Not Modify)
class YieldData(models.Model):
    protocol = models.CharField(max_length=100)
    apy = models.FloatField()
    tvl = models.FloatField()  # Total Value Locked
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocol} - {self.apy}%"


class GovernanceProposal(models.Model):
    protocol = models.CharField(max_length=100)
    proposal_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50)  # Active, Pending, Closed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocol} - {self.proposal_id}"


class RiskMetric(models.Model):
    protocol = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default="Other")
    tvl = models.FloatField(default=0)
    tvl_change_24h = models.FloatField(default=0)
    dominance_ratio = models.FloatField(default=0)
    volatility_30d = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocol} ({self.category})"


# New Models
class OnChainData(models.Model):
    transaction_volume = models.JSONField(default=list)
    tvl = models.JSONField(default=list)
    wallet_balance = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)


class RiskScore(models.Model):
    protocol = models.CharField(max_length=100)
    risk_score = models.FloatField()
    audit_status = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)


class TechnicalData(models.Model):
    uniswap_data = models.JSONField(default=list)
    wallet_transactions = models.JSONField(default=list)
    tenderly_simulation = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
