from django.urls import path
from .views import (
    fetch_yield_data,
    get_yield_data,
    fetch_governance_data,
    get_governance_data,
    fetch_risk_metrics,
    get_risk_metrics,
    fetch_on_chain_data,
    get_on_chain_data,
    simulate_governance_vote,  # Add this import
    fetch_risk_scores,
    get_risk_scores,
    fetch_technical_data,
    get_technical_data,
)

urlpatterns = [
    path("fetch-yield/", fetch_yield_data),
    path("yield-data/", get_yield_data),
    path("fetch-governance/", fetch_governance_data),
    path("governance-data/", get_governance_data),
    path("fetch-risk/", fetch_risk_metrics),
    path("risk-metrics/", get_risk_metrics),
    path("fetch-on-chain/", fetch_on_chain_data),
    path("on-chain-data/", get_on_chain_data),
    path("simulate-vote/", simulate_governance_vote),  # Add this line
    path("fetch-risk-scores/", fetch_risk_scores),
    path("risk-scores/", get_risk_scores),
    path("fetch-technical/", fetch_technical_data),
    path("technical-data/", get_technical_data),
]
