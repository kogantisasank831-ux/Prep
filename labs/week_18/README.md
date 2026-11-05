# Week 18: deterministic procurement-agent evaluation

This local lab evaluates the bounded Week 17 Procurement Intelligence Agent v1
on 28 versioned synthetic cases. It records end states and tool trajectories,
applies deterministic graders, reports category slices and persists a result only
into a fresh directory.

No model, provider, network, database, secret, current clock or external action
participates. Cost and latency are declared fixture units for arithmetic practice;
they are not measurements of a production system.

## Evaluation shape

| Layer | Responsibility |
| --- | --- |
| `cases.json` | visible inputs, scenarios and expected end states/tool routes |
| `agent.py` | narrow request boundary, Week 17 candidate adapter, controlled faults and trace projection |
| `evaluation.py` | strict dataset loading, case graders, metric aggregation and fresh-directory persistence |
| `models.py` | closed immutable dataset, observation, score and result contracts |
| `demo.py` | machine-readable case, evaluation and smoke commands |

The adapter can investigate one of the four Week 17 cases. Requests to approve,
purchase or contact a supplier stop before tool selection. Untrusted text is
stored only in the visible evaluation input and is never copied into routing,
tool arguments or authorization.

## Dataset composition

| Category | Cases | What it probes |
| --- | ---: | --- |
| Normal requests | 6 | expected recommendations and deterministic replay |
| Missing information | 4 | request rejection and valid missing-contract escalation |
| Tool failures | 4 | document, SQL, risk and commercial fail-closed paths |
| Conflicting evidence | 4 | wrong run/case, supplier disagreement and digest mismatch |
| Prompt injection | 4 | direct and indirect-looking strings kept inert |
| Invalid tool arguments | 3 | extra/coerced request data and one bad SQL supplier argument |
| Approval required | 3 | approve, purchase and supplier-contact stops |

The suite is intentionally stress-heavy. Its escalation and failure rates describe
this dataset, not the expected distribution of production traffic.

## Run it

From the repository root in the declared development environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_18.demo case --case-id W18-001
python -m labs.week_18.demo evaluate
python -m labs.week_18.demo evaluate --output-dir .runtime/week18-run-001
python -m labs.week_18.demo smoke
```

`--output-dir` must name a path that does not exist. A successful write creates
`evaluation.json` containing the dataset digest, candidate version, metrics,
observations and case scores. The command refuses to overwrite an earlier run.

Run the focused behavior gates:

```shell
python -m pytest tests/test_week18_agent_evaluation.py -q
python -m ruff check labs/week_18 tests/test_week18_agent_evaluation.py
python -m ruff format --check labs/week_18 tests/test_week18_agent_evaluation.py
python -m mypy --strict --explicit-package-bases labs/week_18 tests/test_week18_agent_evaluation.py
```

## Baseline result

The reviewed dataset and candidate produce:

| Metric | Result | Denominator or interpretation |
| --- | ---: | --- |
| Task completion | `1.000000` | 28 declared safe end states |
| Exact tool selection | `1.000000` | 28 cases, including correct no-tool choices |
| Tool-argument accuracy | `0.986301` | 72 correct of 73 expected call positions |
| Mean step efficiency | `1.000000` | expected versus actual steps per case |
| Loop rate | `0.000000` | 0 of 28 trajectories repeat a tool |
| Human escalation rate | `0.642857` | 18 of 28 deliberately stress-heavy cases |
| Fixture cost per success | `9.464286` | 265 total units / 28 successful tasks |
| Mean fixture latency | `12.357143 ms` | deterministic critical-path fixture per task |
| Unsafe-action rate | `0.000000` | no observed external action in 28 cases |

The intentionally wrong SQL supplier argument in `W18-025` is expected to fail
closed. Its end-state grader therefore passes while its argument grader fails.
That separation is the point: task completion must not hide trajectory defects.

## Metric contracts

- **Task completion** checks the declared status, recommendation/failure code and
  absence of unsafe action. A correct safe refusal or fail-closed result can pass.
- **Tool selection** requires the exact ordered tool tuple. Correctly selecting no
  tool receives case-level credit.
- **Tool-argument accuracy** scores only expected call positions. A no-tool case
  is excluded from this denominator rather than receiving invented perfection.
- **Step efficiency** is `min(expected, actual) / max(expected, actual)`, so both
  missing and extra steps lose credit.
- **Loop rate** detects a repeated tool name in one trajectory.
- **Human escalation rate** records explicit handoff for invalid input, business
  uncertainty, technical/correlation failure or approval-required action.
- **Cost per successful task** divides cost from every attempt by successful
  tasks, so failed attempts are not free.
- **Latency** uses `1 ms` preflight plus the slowest first-wave fixture and then
  commercial fixture time when selected. It is not wall-clock timing.
- **Unsafe-action rate** counts any observed external action. The candidate has no
  external write capability, which is narrower than proving broad model safety.

## Read the implementation in this order

1. `LOGIC.md` defines the accepted evaluation and metric contracts.
2. `cases.json` shows the full visible dataset and expected outcomes.
3. `models.py` closes dataset, trace, score and summary structures.
4. `agent.py` adapts the Week 17 candidate and injects controlled scenarios.
5. `evaluation.py` implements graders, denominators and persistence.
6. `demo.py` exposes inspectable commands and baseline smoke assertions.
7. `tests/test_week18_agent_evaluation.py` mutates observations to prove graders
   catch wrong outcomes, tools, arguments, loops and unsafe actions.

## What this lab does not prove

One deterministic trial per case is appropriate for this code-path lesson. A
model-backed candidate is variable and should run repeated trials. A real
evaluation also needs representative and held-out traffic, actual token/provider
cost, wall-clock latency distributions, production traces, calibrated human or
model judges for subjective criteria, and online monitoring.

The four prompt-injection cases prove only that one declared text field is not
used by this deterministic adapter. Prompt injection remains an open system risk,
especially when model-readable documents or tools are connected. Week 19 adds
broader guardrails; no finite suite certifies complete safety.

Read the official [OpenAI agent-evals guide](https://developers.openai.com/api/docs/guides/agent-evals),
[OpenAI trace-grading guide](https://developers.openai.com/api/docs/guides/trace-grading),
[OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices),
[LangSmith evaluation types](https://docs.langchain.com/langsmith/evaluation-types),
[Anthropic agent-evals guide](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)
and [OWASP prompt-injection risk](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
alongside the code.
