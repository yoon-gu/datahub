"""`get_entities` tool — batch URN 상세 조회."""

from __future__ import annotations

from typing import Any, Dict, List, Union

from ..lite import get_client
from ..server import mcp


@mcp.tool
def get_entities(urns: Union[str, List[str]]) -> Dict[str, Any]:
    """Get detailed information about one or more entities by their DataHub URNs.

    Accepts a single URN string or a list of URNs. Returns a dict keyed by URN
    with each entity's aspects. Pass a list to compare multiple entities in a
    single call — much more efficient than calling multiple times.

    Response fields vary by entity type. Unknown URNs return an empty aspects dict.
    """
    client = get_client()
    if isinstance(urns, str):
        urn_list = [urns]
    else:
        urn_list = list(urns)

    result: Dict[str, Any] = {}
    for urn in urn_list:
        aspects = client.get_all_aspects(urn)
        result[urn] = {
            "urn": urn,
            "exists": bool(aspects),
            "entity_type": urn.split(":")[2] if urn.startswith("urn:li:") and len(urn.split(":")) >= 3 else None,
            "aspects": aspects,
        }
    return {"result": result}
