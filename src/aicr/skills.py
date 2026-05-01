from __future__ import annotations

from typing import Callable, Dict


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: Dict[str, Callable[[str], str]] = {}

    def register(self, name: str, fn: Callable[[str], str]) -> None:
        self._skills[name] = fn

    def run(self, name: str, payload: str) -> str:
        skill = self._skills.get(name)
        if not skill:
            return f"Skill not found: {name}"
        return skill(payload)
