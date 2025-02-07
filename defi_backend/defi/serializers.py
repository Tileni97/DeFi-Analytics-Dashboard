# defi/serializers.py (Updated)
from rest_framework import serializers
from .models import (
    YieldData,
    GovernanceProposal,
    RiskMetric,
    OnChainData,
    RiskScore,
    TechnicalData,
)


# Existing Serializers (Do Not Modify)
class YieldDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = YieldData
        fields = "__all__"


class GovernanceProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernanceProposal
        fields = "__all__"


class RiskMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskMetric
        fields = "__all__"


# New Serializers
class OnChainDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnChainData
        fields = "__all__"


class RiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScore
        fields = "__all__"


class TechnicalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalData
        fields = "__all__"
