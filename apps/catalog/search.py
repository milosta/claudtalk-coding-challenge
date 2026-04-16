from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import QuerySet


def build_search(queryset: QuerySet, q: str) -> QuerySet:
    """Apply Postgres full-text search to the queryset, ranking by relevance."""
    if not q:
        return queryset
    query = SearchQuery(q, config="english")
    return (
        queryset.annotate(rank=SearchRank("search_vector", query))
        .filter(search_vector=query)
        .order_by("-rank")
    )
