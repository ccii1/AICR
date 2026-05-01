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
            "cpp": self._cpp_rules(),
            "py": self._python_rules(),
            "go": self._go_rules(),
            "java": self._java_rules(),
        }
        self._plan_prefix: Dict[str, str] = {
            "Plan-A": "策略：稳健优先。先识别高风险缺陷，再做预算、性能和可维护性建议。",
            "Plan-B": "策略：效率优先。先快速定位最可能阻断上线的问题，再补充治理和优化建议。",
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
        scopes = self.detect_scopes(review_files) or ["py"]
        level = validation_level.lower()
        if level not in SUPPORTED_VALIDATION_LEVELS:
            level = "p1"

        reviewed = ", ".join(review_files) if review_files else "未提供变更文件，按通用范围做预审。"
        template = self._load_level_template(level)
        prompt_text = template.format(
            plan_prefix=self._plan_prefix.get(plan_name, "策略：默认审查策略。"),
            review_files=reviewed,
            scopes=", ".join(scopes),
            language_rules="\n\n".join(self._lang_rules[scope] for scope in scopes),
            validation_level=level,
        )
        return PromptBundle(scopes=scopes, validation_level=level, prompt_text=prompt_text)

    def _load_level_template(self, validation_level: str) -> str:
        template_path = self._template_dir / f"{validation_level}.md"
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        return (
            "# 审查提示词\n"
            "- 验证等级: {validation_level}\n"
            "- 策略: {plan_prefix}\n"
            "- 审查文件: {review_files}\n"
            "- 语言范围: {scopes}\n\n"
            "## 语言专项规则\n\n"
            "{language_rules}\n"
        )

    def _cpp_rules(self) -> str:
        return (
            "### C++ 审查规则\n"
            "你是资深 C++ 代码审查工程师。重点关注会导致崩溃、未定义行为、资源泄漏、并发竞态、"
            "ABI 兼容问题和长期维护困难的问题，而不是停留在表面风格。\n"
            "\n"
            "必须优先检查以下内容：\n"
            "1. 对象生命周期是否清晰，包括栈对象、堆对象、智能指针、引用、裸指针和临时对象的有效期。\n"
            "2. 是否存在越界访问、悬垂引用、use-after-free、double free、未初始化读取、空指针解引用等内存安全问题。\n"
            "3. 资源管理是否符合 RAII；锁、文件句柄、套接字、线程、事务性资源是否能在异常路径和早返回路径上正确释放。\n"
            "4. 并发代码是否存在 data race、死锁、锁顺序不一致、条件变量误用、原子操作语义错误、可见性问题。\n"
            "5. 异常安全级别是否合理；构造函数、析构函数、move/copy 操作、容器扩容和回滚路径是否破坏不变量。\n"
            "6. 接口设计是否引入不必要拷贝、对象切片、悬垂视图、错误的 const 语义、危险的隐式转换或模板实例化风险。\n"
            "\n"
            "输出时不要只说“建议优化”。请明确指出问题证据、触发条件、潜在后果、最小修复方向，以及是否建议补充 "
            "ASan/TSan/UBSan、单元测试或并发回归测试。"
        )

    def _python_rules(self) -> str:
        return (
            "### Python 审查规则\n"
            "你是资深 Python 代码审查工程师。重点关注运行时正确性、异常边界、类型稳定性、依赖安全、"
            "可测试性和性能热点，而不是把注意力放在格式化层面。\n"
            "\n"
            "必须优先检查以下内容：\n"
            "1. 类型和数据结构是否稳定，是否存在返回值形态漂移、可选值未判空、字典字段假定过强、隐式类型转换问题。\n"
            "2. 异常处理是否清晰，是否有吞异常、过宽捕获、错误日志缺失、重试条件不当、资源清理遗漏等问题。\n"
            "3. I/O、网络、文件、数据库、子进程调用是否具备超时、失败分支和明确的错误传播策略。\n"
            "4. 状态管理是否安全，尤其是默认可变参数、全局变量、缓存、副作用初始化、懒加载共享对象和线程/协程间共享状态。\n"
            "5. 性能是否会在真实数据规模下退化，例如重复扫描、N+1 风格访问、无界内存增长、低效字符串拼接和不必要序列化。\n"
            "6. 代码是否容易测试，是否把外部依赖和纯逻辑分离，是否存在难以 mock 或难以覆盖的隐式环境耦合。\n"
            "\n"
            "输出时请区分功能错误、稳定性风险和工程性债务，并给出可落地的修复建议。若问题与 typing、边界输入、编码、"
            "并发模型或依赖版本相关，要明确点出。"
        )

    def _go_rules(self) -> str:
        return (
            "### Go 审查规则\n"
            "你是资深 Go 代码审查工程师。重点关注并发正确性、context 传播、error 处理、资源生命周期、"
            "接口边界和可观测性，而不是只看代码是否“像 Go”。\n"
            "\n"
            "必须优先检查以下内容：\n"
            "1. goroutine 是否可能泄漏，是否有无法退出的 worker、未消费 channel、错误的 select 分支或阻塞发送/接收。\n"
            "2. context 是否贯穿请求链路，取消、超时、deadline 是否被正确传递，是否有后台任务忽略上游取消信号。\n"
            "3. error 处理是否完整，是否存在吞错、包装丢失、部分失败未回滚、返回 nil error 但状态不一致等问题。\n"
            "4. 共享状态是否存在 data race；map、slice、缓存、连接池和结构体字段是否在并发路径上被不安全访问。\n"
            "5. 资源是否被正确关闭，包括 response body、文件句柄、ticker、timer、数据库 rows、事务和锁。\n"
            "6. 接口和 package 边界是否清晰，是否引入过度抽象、错误的零值语义、隐藏副作用或难以测试的耦合。\n"
            "\n"
            "输出时请给出最小改动方案，明确说明问题在高并发、取消、网络抖动或部分失败场景下会如何暴露。"
        )

    def _java_rules(self) -> str:
        return (
            "### Java 审查规则\n"
            "你是资深 Java 代码审查工程师。重点关注线程安全、空值语义、事务边界、资源管理、异常传播、"
            "框架集成副作用和 API 兼容性，而不是只讨论命名或样式。\n"
            "\n"
            "必须优先检查以下内容：\n"
            "1. 并发代码是否线程安全，包括共享可变状态、锁粒度、不可变对象使用、并发容器选择和发布可见性。\n"
            "2. 是否存在空指针风险，特别是外部输入、DTO 映射、Optional 使用、集合元素、框架注入对象和延迟初始化字段。\n"
            "3. 事务边界是否正确，异常类型是否会触发预期回滚，跨库/跨服务操作是否可能出现部分提交和数据不一致。\n"
            "4. 资源生命周期是否完整，包括 stream、连接、线程池、事务对象、文件句柄和第三方客户端的关闭与复用。\n"
            "5. API 设计和实现是否破坏兼容性，例如序列化字段变动、泛型擦除误用、反射调用副作用、公共接口行为变化。\n"
            "6. 框架相关代码是否存在隐蔽问题，例如 Spring 代理失效、自调用绕过事务、懒加载异常、配置绑定不一致等。\n"
            "\n"
            "输出时请明确指出问题属于功能正确性、数据一致性、性能/容量还是工程稳定性问题，并补充建议的回归测试点。"
        )
