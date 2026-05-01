from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


SUPPORTED_SCOPES = {"cpp", "py", "go", "java"}
SUPPORTED_VALIDATION_LEVELS = {"p0", "p1", "p2"}


@dataclass
class PromptBundle:
    scopes: List[str]
    validation_level: str
    prompt_text: str


class PromptRuleEngine:
    def __init__(self) -> None:
        self._lang_rules: Dict[str, str] = {
            "cpp": (
                "你是 C++ 代码审查专家。重点检查内存安全、对象生命周期、并发竞态、"
                "异常安全与 RAII 一致性。输出必须包含风险等级与修复建议。"
            ),
            "py": (
                "你是 Python 代码审查专家。重点检查类型稳定性、异常处理、依赖安全、"
                "可测试性与性能热点。输出必须包含可落地修复建议。"
            ),
            "go": (
                "你是 Go 代码审查专家。重点检查 goroutine 泄漏、context 传播、error 处理、"
                "接口边界与并发数据竞争。输出必须包含最小改动方案。"
            ),
            "java": (
                "你是 Java 代码审查专家。重点检查线程安全、空指针风险、事务边界、"
                "资源释放与 API 兼容性。输出必须包含回归测试点。"
            ),
        }
        self._plan_prefix: Dict[str, str] = {
            "Plan-A": "策略：稳健优先。先识别高风险缺陷，再做预算与优化建议。",
            "Plan-B": "策略：效率优先。先快速定位核心问题，再补充合规与成本约束。",
        }
        self._template_dir = Path(__file__).resolve().parents[2] / "docs" / "prompts"

    def detect_scopes(self, review_files: List[str]) -> List[str]:
        scopes: List[str] = []
        for path in review_files:
            suffix = Path(path).suffix.lower().lstrip(".")
            if suffix in SUPPORTED_SCOPES and suffix not in scopes:
                scopes.append(suffix)
        return scopes

    def build_prompt(
        self,
        plan_name: str,
        review_files: List[str],
        validation_level: str = "p1",
    ) -> PromptBundle:
        scopes = self.detect_scopes(review_files)
        if not scopes:
            scopes = ["py"]
        level = validation_level.lower()
        if level not in SUPPORTED_VALIDATION_LEVELS:
            level = "p1"

        lang_parts = [self._lang_rules[s] for s in scopes]
        plan_prefix = self._plan_prefix.get(plan_name, "策略：通用审查。")
        reviewed = ", ".join(review_files) if review_files else "未提供文件，使用默认范围"
        template = self._load_level_template(level)
        prompt_text = template.format(
            plan_prefix=plan_prefix,
            review_files=reviewed,
            scopes=", ".join(scopes),
            language_rules=" ".join(lang_parts),
            validation_level=level,
        )
        return PromptBundle(scopes=scopes, validation_level=level, prompt_text=prompt_text)

    def _load_level_template(self, validation_level: str) -> str:
        template_path = self._template_dir / f"{validation_level}.md"
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        # Fallback to built-in template to avoid runtime break.
        return (
            "# 审查提示词模板\n"
            "- 验证等级: {validation_level}\n"
            "- 策略前缀: {plan_prefix}\n"
            "- 审查文件: {review_files}\n"
            "- 语言范围: {scopes}\n"
            "- 语言规则: {language_rules}\n"
        )
