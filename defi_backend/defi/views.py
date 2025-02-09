import logging
import requests
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from datetime import datetime
from .models import (
    YieldData,
    GovernanceProposal,
    RiskMetric,
    OnChainData,
    RiskScore,
    TechnicalData,
)
from .serializers import (
    YieldDataSerializer,
    GovernanceProposalSerializer,
    RiskMetricSerializer,
    OnChainDataSerializer,
    RiskScoreSerializer,
    TechnicalDataSerializer,
)

logger = logging.getLogger(__name__)
CACHE_TIMEOUT = 300  # Cache API responses for 5 minutes


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# Utility function to fetch and cache data
def fetch_and_cache_data(url, model, serializer, cache_key):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"API Response: {response_data}")  # Log the entire API response

            if isinstance(response_data, dict) and "data" in response_data:
                data = response_data["data"]
            else:
                data = response_data

            if not isinstance(data, list):
                logger.error(f"Unexpected data format: {type(data)}")
                return False

            # Log the first few items for debugging
            for i, item in enumerate(data[:5]):
                logger.info(f"Item {i}: {item}")

            objects = []
            model_fields = [f.name for f in model._meta.get_fields()]

            for item in data:
                if not isinstance(item, dict):
                    logger.error(f"Skipping invalid item: {item}")
                    continue

                # Log the item for debugging
                logger.info(f"Processing item: {item}")

                # Filter out fields that are not in the model
                filtered_item = {k: v for k, v in item.items() if k in model_fields}

                # Ensure required fields are populated
                if model == RiskScore:
                    # Map API fields to RiskScore model fields
                    filtered_item["protocol"] = item.get(
                        "name", ""
                    )  # Use "name" as protocol
                    filtered_item["risk_score"] = item.get(
                        "mcap", 0.0
                    )  # Use "mcap" as risk_score
                    filtered_item["audit_status"] = item.get(
                        "audit_note", ""
                    )  # Use "audit_note" as audit_status

                try:
                    objects.append(model(**filtered_item))
                except Exception as e:
                    logger.error(f"Error creating model instance: {e}")

            model.objects.all().delete()
            model.objects.bulk_create(objects)

            serialized_data = serializer(objects, many=True).data
            cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
            return True
        else:
            logger.error(f"Failed to fetch data from {url}: {response.status_code}")
            return False
    except Exception as e:
        logger.exception(f"Error fetching data from {url}")
        return False


# Yield Data Endpoints
@api_view(["GET"])
def fetch_yield_data(request):
    """Fetch yield farming data from DeFiLlama API and update database."""
    try:
        url = "https://yields.llama.fi/pools"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json().get("data", [])[:10]  # Limit to top 10
            logger.info(f"Fetched {len(data)} yield data entries")
            yield_objects = []

            for item in data:
                yield_objects.append(
                    YieldData(
                        chain=item.get("chain"),
                        project=item.get("project"),
                        symbol=item.get("symbol"),
                        tvlUsd=item.get("tvlUsd"),
                        apyBase=item.get("apyBase"),
                        apyReward=item.get("apyReward"),  # Can be NULL
                        apy=item.get("apy"),
                        rewardTokens=item.get(
                            "rewardTokens", []
                        ),  # Default to empty list if missing
                        pool=item.get("pool"),
                        apyPct1D=item.get("apyPct1D"),
                        apyPct7D=item.get("apyPct7D"),
                        apyPct30D=item.get("apyPct30D"),
                        stablecoin=item.get("stablecoin", False),
                        ilRisk=item.get("ilRisk"),
                        exposure=item.get("exposure"),
                        predictions=item.get(
                            "predictions", {}
                        ),  # Default to empty dict if missing
                        poolMeta=item.get("poolMeta"),
                        mu=item.get("mu"),
                        sigma=item.get("sigma"),
                        count=item.get("count"),
                        outlier=item.get("outlier", False),
                        underlyingTokens=item.get(
                            "underlyingTokens", []
                        ),  # Default to empty list if missing
                        il7d=item.get("il7d"),
                        apyBase7d=item.get("apyBase7d"),
                        apyMean30d=item.get("apyMean30d"),
                        volumeUsd1d=item.get("volumeUsd1d"),
                        volumeUsd7d=item.get("volumeUsd7d"),
                        apyBaseInception=item.get("apyBaseInception"),
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
    cached_data = cache.get("yield_data")
    if cached_data:
        return Response(cached_data)

    data = YieldData.objects.all().order_by("-tvl")
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = YieldDataSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Governance Data Endpoints
@api_view(["GET"])
def fetch_governance_data(request):
    """Fetch governance data from Snapshot API."""
    try:
        url = "https://hub.snapshot.org/graphql"
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
        response = requests.post(url, json={"query": query}, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", {}).get("proposals", [])
            proposals = []
            for proposal in data:
                proposals.append(
                    GovernanceProposal(
                        protocol=proposal["space"]["id"],
                        proposal_id=proposal["id"],  # String value
                        title=proposal["title"],
                        status=proposal["state"],
                    )
                )

            GovernanceProposal.objects.all().delete()
            GovernanceProposal.objects.bulk_create(proposals)
            cache.set(
                "governance_data",
                GovernanceProposalSerializer(proposals, many=True).data,
                CACHE_TIMEOUT,
            )
            return Response({"message": "Governance data updated successfully!"})
        else:
            logger.error(f"Failed to fetch governance data: {response.status_code}")
            return Response({"error": "Failed to fetch data"}, status=500)
    except Exception as e:
        logger.exception("Error fetching governance data")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_governance_data(request):
    cached_data = cache.get("governance_data")
    if cached_data:
        return Response(cached_data)

    data = GovernanceProposal.objects.all().order_by("-created_at")
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = GovernanceProposalSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Risk Metrics Endpoints
@api_view(["GET"])
def fetch_risk_metrics(request):
    url = "https://api.llama.fi/protocols"
    if fetch_and_cache_data(url, RiskMetric, RiskMetricSerializer, "risk_metrics"):
        return Response({"message": "Risk metrics updated successfully!"})
    else:
        return Response({"error": "Failed to fetch data"}, status=500)


@api_view(["GET"])
def get_risk_metrics(request):
    cached_data = cache.get("risk_metrics")
    if cached_data:
        return Response(cached_data)

    # Default ordering field
    ordering_field = request.query_params.get("ordering", "-mcap")

    # Validate that the ordering field exists in the model
    valid_fields = [f.name for f in RiskMetric._meta.get_fields()]
    if ordering_field.lstrip("-") not in valid_fields:
        return Response(
            {"error": f"Invalid ordering field: {ordering_field}"}, status=400
        )

    # Order by the validated field
    data = RiskMetric.objects.all().order_by(ordering_field)
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = RiskMetricSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# On-Chain Data Endpoints
@api_view(["GET"])
def fetch_on_chain_data(request):
    data = {}
    try:
        # Fetch TVL data
        tvl_url = "https://api.llama.fi/charts"
        tvl_response = requests.get(tvl_url, timeout=10)
        if tvl_response.status_code == 200:
            data["tvl"] = tvl_response.json()
    except Exception as e:
        logger.error(f"TVL data fetch failed: {e}")

    try:
        # Fetch DeFi market data
        cg_url = "https://api.coingecko.com/api/v3/global/defi"
        cg_response = requests.get(
            cg_url, headers={"x-cg-api-key": settings.COINGECKO_API_KEY}, timeout=10
        )
        if cg_response.status_code == 200:
            data["market"] = cg_response.json()
    except Exception as e:
        logger.error(f"CoinGecko data fetch failed: {e}")

    if not data:
        return Response({"error": "All data fetches failed"}, status=500)

    # Process whatever data we successfully retrieved
    try:
        OnChainData.objects.update_or_create(
            id=1,
            defaults={
                "transaction_volume": data.get("market", {})
                .get("data", {})
                .get("trading_volume_24h", 0),
                "tvl": data.get("tvl", []),
                "wallet_balance": data.get("market", {})
                .get("data", {})
                .get("market_cap", 0),
            },
        )
        return Response({"message": "On-chain data updated successfully!"})
    except Exception as e:
        logger.exception("Error saving on-chain data")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_on_chain_data(request):
    cached_data = cache.get("on_chain_data")
    if cached_data:
        return Response(cached_data)

    data = OnChainData.objects.first()
    serializer = OnChainDataSerializer(data)
    return Response(serializer.data)


# Simulate Governance Vote
@api_view(["POST"])
def simulate_governance_vote(request):
    try:
        proposal_id = request.data.get("proposal_id")
        vote = request.data.get("vote")  # "FOR" or "AGAINST"

        # Check if the proposal exists
        try:
            proposal = GovernanceProposal.objects.get(proposal_id=proposal_id)
        except GovernanceProposal.DoesNotExist:
            return Response({"error": "Proposal not found"}, status=404)

        # Update the vote count
        if vote == "FOR":
            proposal.for_votes += 1
        elif vote == "AGAINST":
            proposal.against_votes += 1
        else:
            return Response(
                {"error": "Invalid vote type. Use 'FOR' or 'AGAINST'."}, status=400
            )

        proposal.save()

        return Response(
            {"message": f"Vote {vote} recorded for proposal {proposal_id}!"}
        )
    except Exception as e:
        logger.exception("Error simulating governance vote")
        return Response({"error": str(e)}, status=500)


# Risk Scores Endpoints
@api_view(["GET"])
def fetch_risk_scores(request):
    url = "https://api.llama.fi/protocols"
    if fetch_and_cache_data(url, RiskScore, RiskScoreSerializer, "risk_scores"):
        return Response({"message": "Risk scores updated successfully!"})
    else:
        return Response({"error": "Failed to fetch data"}, status=500)


@api_view(["GET"])
def get_risk_scores(request):
    cached_data = cache.get("risk_scores")
    if cached_data:
        return Response(cached_data)

    data = RiskScore.objects.all().order_by("-risk_score")
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = RiskScoreSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Technical Data Endpoints
@api_view(["GET"])
def fetch_technical_data(request):
    try:
        price_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_vol=true"
        price_response = requests.get(price_url, timeout=10)
        price_data = price_response.json()

        protocols_url = "https://api.llama.fi/protocols"
        protocols_response = requests.get(protocols_url, timeout=10)
        protocol_data = protocols_response.json()

        TechnicalData.objects.update_or_create(
            id=1,
            defaults={
                "uniswap_data": protocol_data,
                "wallet_transactions": price_data,
                "tenderly_simulation": {},
            },
        )
        return Response({"message": "Technical data updated successfully!"})
    except Exception as e:
        logger.exception("Error fetching technical data")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_technical_data(request):
    cached_data = cache.get("technical_data")
    if cached_data:
        return Response(cached_data)

    data = TechnicalData.objects.first()
    serializer = TechnicalDataSerializer(data)
    return Response(serializer.data)
