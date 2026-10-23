"""Grade the bank's small standard-library exercises in CPython or Pyodide.

This is a browser practice checker, not a secure code-execution service.
The caller owns worker lifetime and execution timeouts.
"""

import ast
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
import inspect
import io
import sys
from types import ModuleType
from typing import Literal, TypedDict


class Check(TypedDict):
    label: str
    code: str


class Exercise(TypedDict):
    id: str
    checks: list[Check]


class CheckResult(TypedDict):
    label: str
    passed: bool
    detail: str


class RunResult(TypedDict):
    status: Literal["checked"]
    question_id: str
    passed: int
    total: int
    results: list[CheckResult]
    output: str


class BoundedOutput(io.StringIO):
    """Retain a small diagnostic prefix instead of unbounded print output."""

    def write(self, text: str) -> int:
        remaining = max(0, 4000 - self.tell())
        super().write(text[:remaining])
        return len(text)


def raises(
    error_type: type[Exception], function: Callable[..., object], *args: object
) -> bool:
    """Support declarative exception cases in trusted question checks."""
    try:
        function(*args)
    except error_type:
        return True
    except Exception:
        return False
    return False


async def grade_submission(source: str, exercise: Exercise) -> RunResult:
    """Execute one submission and report the five named observable checks."""
    if not isinstance(source, str) or len(source) > 20_000:
        raise ValueError("submission must be at most 20,000 characters")
    checks = exercise["checks"]
    if len(checks) != 5:
        raise ValueError("an exercise requires five checks")
    module_name = "_assessment_submission"
    module = ModuleType(module_name)
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    output = BoundedOutput()
    results: list[CheckResult] = []
    try:
        with redirect_stdout(output), redirect_stderr(output):
            try:
                exec(compile(source, "submission.py", "exec"), module.__dict__)
            except (Exception, SystemExit, KeyboardInterrupt) as error:
                message = f"{type(error).__name__}: {str(error)[:300]}"
                results = [
                    {"label": check["label"], "passed": False, "detail": message}
                    for check in checks
                ]
            else:
                for check in checks:
                    # These checks are trusted repository content, not learner input.
                    context = {**module.__dict__, "raises": raises}
                    try:
                        code = compile(
                            check["code"],
                            "check.py",
                            "exec",
                            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
                        )
                        value = eval(code, context)
                        if inspect.isawaitable(value):
                            await value
                    except (Exception, SystemExit, KeyboardInterrupt) as error:
                        results.append(
                            {
                                "label": check["label"],
                                "passed": False,
                                "detail": f"{type(error).__name__}: {str(error)[:300]}",
                            }
                        )
                    else:
                        results.append(
                            {
                                "label": check["label"],
                                "passed": True,
                                "detail": "Passed",
                            }
                        )
    finally:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
    return {
        "status": "checked",
        "question_id": exercise["id"],
        "passed": sum(row["passed"] for row in results),
        "total": len(checks),
        "results": results,
        "output": output.getvalue(),
    }
