"""Compatibility wrapper for the split skill tools package."""

from .skill_tools import (
    SkillToolExecutor,
    get_shared_executor,
    get_skill_tools,
    register_shared_executor,
)

__all__ = [
    "SkillToolExecutor",
    "get_skill_tools",
    "register_shared_executor",
    "get_shared_executor",
]
