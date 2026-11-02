"""
HeatShield AI — Validated Occupational Safety Knowledge Base

Curated, source-referenced occupational heat-safety guidance.
Every topic entry cites authoritative public-health sources
(OSHA / NIOSH / CDC) and carries a validation marker so the
platform can distinguish reviewed guidance from unreviewed
content.
"""

from app.knowledge.safety_knowledge import (
    KB_VERSION,
    KNOWLEDGE_TOPICS,
    get_topic,
    list_topics,
    search_knowledge,
    validate_knowledge_base,
)

__all__ = [
    "KB_VERSION",
    "KNOWLEDGE_TOPICS",
    "get_topic",
    "list_topics",
    "search_knowledge",
    "validate_knowledge_base",
]
