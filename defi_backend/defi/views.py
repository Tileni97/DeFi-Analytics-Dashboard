# defi/views.py (Updated)
import logging
import requests
from django.core.cache import cache
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import (
    YieldData,
    GovernanceProposal,
    RiskMetric,
    OnChainData,
    RiskScore,
    TechnicalData,
)  # Updated
from .serializers import (
    YieldDataSerializer,
    GovernanceProposalSerializer,
    RiskMetricSerializer,
    OnChainDataSerializer,  # New
    RiskScoreSerializer,  # New
    TechnicalDataSerializer,  # New
)

logger = logging.getLogger(__name__)
CACHE_TIMEOUT = 300  # Cache API responses for 5 minutes


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# Yield Data Endpoints (Existing Code - Do Not Modify)
@api_view(["GET"])
def fetch_yield_data(request):
    """Fetch yield farming data from DeFiLlama API and update database."""
    try:
        url = "https://yields.llama.fi/pools"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json().get("data", [])[:10]  # Limit to top 10
            logger.info(
                f"Fetched {len(data)} yield data entries"
            )  # Log the number of entries
            yield_objects = []

            for item in data:
                yield_objects.append(
                    YieldData(
                        protocol=item["project"],
                        apy=item["apy"],
                        tvl=item["tvlUsd"],
                    )
                )

            YieldData.objects.all().delete()
            YieldData.objects.bulk_create(yield_objects)
            cache.set(
                "yield_data",
                YieldDataSerializer(yield_objects, many=True).data,
                CACHE_TIMEOUT,
            )
            return Response({"message": "Yield data updated successfully!"})
        else:
            logger.error(f"Failed to fetch yield data: {response.status_code}")
            return Response({"error": "Failed to fetch data"}, status=500)
    except Exception as e:
        logger.exception("Error fetching yield data")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_yield_data(request):
    """Get stored yield farming data with pagination and caching."""
    cached_data = cache.get("yield_data")
    if cached_data:
        return Response(cached_data)

    data = YieldData.objects.all().order_by("-tvl")
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = YieldDataSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Governance Data Endpoints (Existing Code - Do Not Modify)
@api_view(["GET"])
def fetch_governance_data(request):
    """Fetch governance data from Snapshot API."""
    try:
        proposals = []

        # Fetch Snapshot governance data
        snapshot_url = "https://hub.snapshot.org/graphql"
        query = """
        {
          proposals(first: 10, where: { space_in: ["aave.eth", "compound-governance.eth"] }) {
            id
            title
            state
            space {
              id
            }
          }
        }
        """
        response = requests.post(snapshot_url, json={"query": query}, timeout=10)
        if response.status_code == 200:
            snapshot_proposals = response.json().get("data", {}).get("proposals", [])
            logger.info(
                f"Snapshot Proposals: {snapshot_proposals}"
            )  # Log Snapshot proposals
            for proposal in snapshot_proposals:
                proposals.append(
                    GovernanceProposal(
                        protocol=proposal["space"]["id"],
                        proposal_id=proposal["id"],
                        title=proposal["title"],
                        status=proposal["state"],
                    )
                )
        else:
            logger.warning(
                f"Failed to fetch Snapshot proposals: {response.status_code}"
            )
            logger.warning(
                f"Snapshot API Response: {response.text}"
            )  # Log the response body

        # Fallback data if no proposals are found
        if not proposals:
            proposals = [
                GovernanceProposal(
                    protocol="Fallback",
                    proposal_id="1",
                    title="Sample Proposal",
                    status="Active",
                )
            ]
            logger.warning("No governance proposals found. Using fallback data.")

        GovernanceProposal.objects.all().delete()
        GovernanceProposal.objects.bulk_create(proposals)
        cache.set(
            "governance_data",
            GovernanceProposalSerializer(proposals, many=True).data,
            CACHE_TIMEOUT,
        )
        return Response({"message": "Governance data updated successfully!"})
    except Exception as e:
        logger.exception("Error fetching governance data")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_governance_data(request):
    """Get stored governance proposals with pagination and caching."""
    cached_data = cache.get("governance_data")
    if cached_data:
        return Response(cached_data)

    data = GovernanceProposal.objects.all().order_by("-created_at")
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = GovernanceProposalSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Risk Metrics Endpoints (Existing Code - Do Not Modify)
@api_view(["GET"])
def fetch_risk_metrics(request):
    """Fetch risk metrics from DeFiLlama API."""
    try:
        url = "https://api.llama.fi/protocols"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            protocols = [p for p in data if isinstance(p.get("tvl"), (int, float))]

            top_protocols = sorted(
                protocols, key=lambda x: float(x["tvl"]), reverse=True
            )[:15]
            risk_objects = []
            for protocol in top_protocols:
                risk_objects.append(
                    RiskMetric(
                        protocol=protocol["name"],
                        category=protocol.get("category", "Other"),
                        tvl=float(protocol.get("tvl", 0)),
                        tvl_change_24h=float(protocol.get("change_1d", 0) or 0),
                        dominance_ratio=float(protocol.get("dominance", 0) or 0),
                        volatility_30d=float(protocol.get("volatility_30d", 0) or 0),
                    )
                )

            RiskMetric.objects.all().delete()
            RiskMetric.objects.bulk_create(risk_objects)
            cache.set(
                "risk_metrics",
                RiskMetricSerializer(risk_objects, many=True).data,
                CACHE_TIMEOUT,
            )
            return Response({"message": "Risk metrics updated successfully!"})
        else:
            logger.error(f"Failed to fetch risk metrics: {response.status_code}")
            return Response({"error": "Failed to fetch risk metrics"}, status=500)
    except Exception as e:
        logger.exception("Error fetching risk metrics")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_risk_metrics(request):
    """Get stored risk metrics with pagination and caching."""
    cached_data = cache.get("risk_metrics")
    if cached_data:
        return Response(cached_data)

    data = RiskMetric.objects.all().order_by("-tvl")
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = RiskMetricSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# New: Fetch On-Chain Data
@api_view(["GET"])
def fetch_on_chain_data(request):
    """Fetch on-chain data from Dune Analytics, DeFiLlama, and Etherscan."""
    try:
        # Example: Fetch transaction volume from Dune Analytics
        dune_url = "https://api.dune.com/api/v1/query/<QUERY_ID>/results"
        dune_response = requests.get(dune_url, timeout=10)
        dune_data = dune_response.json().get("result", {}).get("rows", [])

        # Example: Fetch TVL from DeFiLlama
        defillama_url = "https://api.llama.fi/protocols"
        defillama_response = requests.get(defillama_url, timeout=10)
        defillama_data = defillama_response.json()

        # Example: Fetch wallet balance from Etherscan
        etherscan_url = "https://api.etherscan.io/api?module=account&action=balance&address=<WALLET_ADDRESS>&tag=latest&apikey=<API_KEY>"
        etherscan_response = requests.get(etherscan_url, timeout=10)
        etherscan_data = etherscan_response.json()

        # Save data to database
        OnChainData.objects.all().delete()
        OnChainData.objects.create(
            transaction_volume=dune_data,
            tvl=defillama_data,
            wallet_balance=etherscan_data,
        )

        cache.set(
            "on_chain_data",
            OnChainDataSerializer(OnChainData.objects.first()).data,
            CACHE_TIMEOUT,
        )
        return Response({"message": "On-chain data updated successfully!"})
    except Exception as e:
        logger.exception("Error fetching on-chain data")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_on_chain_data(request):
    """Get stored on-chain data with caching."""
    cached_data = cache.get("on_chain_data")
    if cached_data:
        return Response(cached_data)

    data = OnChainData.objects.first()
    serializer = OnChainDataSerializer(data)
    return Response(serializer.data)


# New: Simulate Governance Vote
@api_view(["POST"])
def simulate_governance_vote(request):
    """Simulate a governance vote."""
    try:
        proposal_id = request.data.get("proposal_id")
        vote = request.data.get("vote")  # "FOR" or "AGAINST"

        # Simulate vote logic (e.g., update vote count in database)
        proposal = GovernanceProposal.objects.get(proposal_id=proposal_id)
        if vote == "FOR":
            proposal.for_votes += 1
        elif vote == "AGAINST":
            proposal.against_votes += 1
        proposal.save()

        return Response(
            {"message": f"Vote {vote} recorded for proposal {proposal_id}!"}
        )
    except Exception as e:
        logger.exception("Error simulating governance vote")
        return Response({"error": str(e)}, status=500)


# New: Fetch Risk Scores
@api_view(["GET"])
def fetch_risk_scores(request):
    """Fetch risk scores from CertiK or OpenZeppelin."""
    try:
        certik_url = "https://api.certik.com/v1/protocols/<PROTOCOL>/risks"
        certik_response = requests.get(certik_url, timeout=10)
        certik_data = certik_response.json()

        # Save data to database
        RiskScore.objects.all().delete()
        RiskScore.objects.create(
            protocol=certik_data.get("protocol"),
            risk_score=certik_data.get("risk_score"),
            audit_status=certik_data.get("audit_status"),
        )

        cache.set(
            "risk_scores",
            RiskScoreSerializer(RiskScore.objects.first()).data,
            CACHE_TIMEOUT,
        )
        return Response({"message": "Risk scores updated successfully!"})
    except Exception as e:
        logger.exception("Error fetching risk scores")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_risk_scores(request):
    """Get stored risk scores with caching."""
    cached_data = cache.get("risk_scores")
    if cached_data:
        return Response(cached_data)

    data = RiskScore.objects.first()
    serializer = RiskScoreSerializer(data)
    return Response(serializer.data)


# New: Fetch Technical Data
@api_view(["GET"])
def fetch_technical_data(request):
    """Fetch technical data from The Graph, Etherscan, and Tenderly."""
    try:
        # Example: Fetch Uniswap data from The Graph
        the_graph_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
        the_graph_query = """
        {
          swaps(first: 10) {
            id
            amountUSD
            timestamp
          }
        }
        """
        the_graph_response = requests.post(
            the_graph_url, json={"query": the_graph_query}, timeout=10
        )
        the_graph_data = the_graph_response.json().get("data", {}).get("swaps", [])

        # Example: Fetch wallet transactions from Etherscan
        etherscan_url = "https://api.etherscan.io/api?module=account&action=txlist&address=<WALLET_ADDRESS>&startblock=0&endblock=99999999&sort=asc&apikey=<API_KEY>"
        etherscan_response = requests.get(etherscan_url, timeout=10)
        etherscan_data = etherscan_response.json().get("result", [])

        # Example: Simulate transaction using Tenderly
        tenderly_url = "https://api.tenderly.co/api/v1/simulate"
        tenderly_payload = {
            "network_id": "1",
            "from": "<FROM_ADDRESS>",
            "to": "<TO_ADDRESS>",
            "input": "<INPUT_DATA>",
        }
        tenderly_response = requests.post(
            tenderly_url,
            json=tenderly_payload,
            headers={"X-Access-Key": "<API_KEY>"},
            timeout=10,
        )
        tenderly_data = tenderly_response.json()

        # Save data to database
        TechnicalData.objects.all().delete()
        TechnicalData.objects.create(
            uniswap_data=the_graph_data,
            wallet_transactions=etherscan_data,
            tenderly_simulation=tenderly_data,
        )

        cache.set(
            "technical_data",
            TechnicalDataSerializer(TechnicalData.objects.first()).data,
            CACHE_TIMEOUT,
        )
        return Response({"message": "Technical data updated successfully!"})
    except Exception as e:
        logger.exception("Error fetching technical data")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_technical_data(request):
    """Get stored technical data with caching."""
    cached_data = cache.get("technical_data")
    if cached_data:
        return Response(cached_data)

    data = TechnicalData.objects.first()
    serializer = TechnicalDataSerializer(data)
    return Response(serializer.data)
