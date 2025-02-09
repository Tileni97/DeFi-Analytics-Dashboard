# defi/models.py (Updated)
from django.db import models


# Existing Models (Do Not Modify)
class YieldData(models.Model):
    chain = models.CharField(max_length=100)
    project = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50)
    tvlUsd = models.FloatField()
    apyBase = models.FloatField()
    apyReward = models.FloatField(null=True, blank=True)  # Allow NULL values
    apy = models.FloatField()
    rewardTokens = models.JSONField(
        default=list, null=True, blank=True
    )  # Allow NULL values
    pool = models.CharField(max_length=200)
    apyPct1D = models.FloatField(null=True, blank=True)
    apyPct7D = models.FloatField(null=True, blank=True)
    apyPct30D = models.FloatField(null=True, blank=True)
    stablecoin = models.BooleanField(default=False)
    ilRisk = models.CharField(max_length=50, null=True, blank=True)
    exposure = models.CharField(max_length=50, null=True, blank=True)
    predictions = models.JSONField(default=dict, null=True, blank=True)
    poolMeta = models.CharField(max_length=200, null=True, blank=True)
    mu = models.FloatField(null=True, blank=True)
    sigma = models.FloatField(null=True, blank=True)
    count = models.IntegerField(null=True, blank=True)
    outlier = models.BooleanField(default=False)
    underlyingTokens = models.JSONField(default=list, null=True, blank=True)
    il7d = models.FloatField(null=True, blank=True)
    apyBase7d = models.FloatField(null=True, blank=True)
    apyMean30d = models.FloatField(null=True, blank=True)
    volumeUsd1d = models.FloatField(null=True, blank=True)
    volumeUsd7d = models.FloatField(null=True, blank=True)
    apyBaseInception = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project} - {self.symbol}"


class GovernanceProposal(models.Model):
    protocol = models.CharField(max_length=100)
    proposal_id = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    for_votes = models.IntegerField(default=0)
    against_votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocol} - {self.proposal_id}"


class RiskMetric(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    symbol = models.CharField(max_length=50, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    logo = models.URLField(null=True, blank=True)
    audits = models.JSONField(default=list, null=True, blank=True)
    audit_note = models.CharField(max_length=255, null=True, blank=True)
    gecko_id = models.CharField(max_length=255, null=True, blank=True)
    cmcId = models.CharField(max_length=255, null=True, blank=True)
    oracles = models.JSONField(default=list, null=True, blank=True)
    forkedFrom = models.JSONField(default=list, null=True, blank=True)
    chains = models.JSONField(default=list, null=True, blank=True)
    module = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    misrepresentedTokens = models.BooleanField(default=False)
    hallmarks = models.JSONField(default=list, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    chainTvls = models.JSONField(default=dict, null=True, blank=True)
    change_1h = models.FloatField(null=True, blank=True)
    change_1d = models.FloatField(null=True, blank=True)
    change_7d = models.FloatField(null=True, blank=True)
    tokenBreakdowns = models.JSONField(default=dict, null=True, blank=True)
    mcap = models.FloatField(null=True, blank=True)
    # Add other fields as needed

    def __str__(self):
        return self.name or "Unnamed Risk Metric"


# New Models
class OnChainData(models.Model):
    transaction_volume = models.JSONField(default=list)
    tvl = models.JSONField(default=list)
    wallet_balance = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)


class RiskScore(models.Model):
    protocol = models.CharField(max_length=100, default="")  # Allow empty strings
    risk_score = models.FloatField(null=True, blank=True)
    audit_status = models.CharField(max_length=50, default="")  # Allow empty strings
    updated_at = models.DateTimeField(auto_now=True)


class TechnicalData(models.Model):
    uniswap_data = models.JSONField(default=list)
    wallet_transactions = models.JSONField(default=list)
    tenderly_simulation = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
