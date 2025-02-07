# defi/urls.py
from django.urls import path
from .views import (
    fetch_yield_data,
    get_yield_data,
    fetch_governance_data,
    get_governance_data,
    fetch_risk_metrics,
    get_risk_metrics,
    fetch_on_chain_data,  # New
    get_on_chain_data,  # New
    simulate_governance_vote,  # New
    fetch_risk_scores,  # New
    fetch_technical_data,  # New
)

urlpatterns = [
    path("fetch-yield/", fetch_yield_data),
    path("yield-data/", get_yield_data),
    path("fetch-governance/", fetch_governance_data),
    path("governance-data/", get_governance_data),
    path("fetch-risk/", fetch_risk_metrics),
    path("risk-metrics/", get_risk_metrics),
    path("fetch-on-chain/", fetch_on_chain_data),  # New
    path("on-chain-data/", get_on_chain_data),  # New
    path("simulate-vote/", simulate_governance_vote),  # New
    path("fetch-risk-scores/", fetch_risk_scores),  # New
    path("fetch-technical/", fetch_technical_data),  # New
]
