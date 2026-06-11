from backend.tools.approval import check_authority, route_parallel
from backend.tools.base import ToolDefinition, ToolRegistry
from backend.tools.cpq import generate_quote, validate_config
from backend.tools.knowledge_base import search as kb_search
from backend.tools.salesforce import get_opportunity


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="salesforce.get_opportunity",
            description="Fetch CRM opportunity and rep history",
            parameters={"type": "object", "properties": {"opportunity_id": {"type": "string"}}, "required": ["opportunity_id"]},
            handler=lambda opportunity_id: get_opportunity(opportunity_id),
        )
    )
    registry.register(
        ToolDefinition(
            name="knowledge_base.search",
            description="Search policy documents for pricing and channel rules",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            handler=lambda query: kb_search(query),
        )
    )
    registry.register(
        ToolDefinition(
            name="cpq.validate_config",
            description="Validate product configuration for a deal",
            parameters={"type": "object", "properties": {"opportunity": {"type": "object"}}, "required": ["opportunity"]},
            handler=lambda opportunity: validate_config(opportunity),
        )
    )
    registry.register(
        ToolDefinition(
            name="cpq.generate_quote",
            description="Generate wholesale quote after approval",
            parameters={
                "type": "object",
                "properties": {
                    "opportunity": {"type": "object"},
                    "approved_discount": {"type": "number"},
                },
                "required": ["opportunity"],
            },
            handler=lambda opportunity, approved_discount=None: generate_quote(opportunity, approved_discount),
        )
    )
    registry.register(
        ToolDefinition(
            name="approval.route_parallel",
            description="Route deal to multiple approvers simultaneously",
            parameters={
                "type": "object",
                "properties": {
                    "approvers": {"type": "array", "items": {"type": "string"}},
                    "deal_context": {"type": "object"},
                },
                "required": ["approvers", "deal_context"],
            },
            handler=lambda approvers, deal_context: route_parallel(approvers, deal_context),
        )
    )
    return registry