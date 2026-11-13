---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_9_Specialized_Modeling/36_Operations_Research_Scheduling_Optimization_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Operations research, scheduling, and optimization interview cheat sheet"
description: "Interview revision for LP, MILP, CP-SAT, scheduling, routing, uncertainty, infeasibility, evaluation, and production fallback."
summary: "Revise optimization contracts, LP, MILP, CP-SAT, scheduling and routing, infeasibility, heuristics, uncertainty, prediction-plus-optimization, and safe fallback."
permalink: "/interview-prep/cheat-sheets/operations-research-scheduling-optimization/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 9 · Optimization"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** Data Science Lead, Senior Data Scientist, Applied Scientist, Optimization Engineer, ML Engineer, AI Engineer<br>
**Use:** resource allocation, production scheduling, routing, workforce planning, supply chain, pricing, model-system design, and project deep dives<br>
**Interview rule:** define decision variables, objective units, hard/soft constraints, planning horizon, uncertainty, and operational fallback before choosing a solver. A mathematically optimal solution to the wrong or stale model is operationally wrong.

## 1. Thirty-second revision

- Prediction estimates what may happen; optimization chooses what to do under constraints. Many production systems need both.
- A model contains decision variables, parameters/data, objective, constraints, domains, horizon, and assumptions.
- Linear programming (LP) uses continuous variables and linear relationships; mixed-integer linear programming (MILP/MIP) adds integer/binary decisions.
- Integer decisions express assignment, selection, setup, sequencing, logical conditions, and fixed costs but create combinatorial complexity.
- Constraint programming/CP-SAT is strong for discrete feasibility and scheduling/logical constraints; MIP is strong when linear relaxations are informative. Benchmark the formulation.
- Scheduling uses intervals, precedence, resource capacity, calendars, setup/changeover, due dates, and objectives such as makespan, lateness, or cost.
- A feasible solution satisfies constraints. Optimality requires a proof/bound or solver status—not merely finding a good schedule.
- LP relaxation supplies bounds and guides branch-and-bound. A large integrality gap or weak big-M can make MIP slow.
- Hard constraints must never break; soft constraints need explicit penalty/slack and business-approved trade-offs.
- Infeasibility is a result to diagnose: data errors, contradictory constraints, unavailable capacity, or an overly strict policy.
- Stochastic, robust, chance-constrained, and scenario optimization handle uncertainty differently; none knows the true future distribution automatically.
- Production needs validation, warm starts, time limits, acceptable gaps, deterministic fallback, re-optimization triggers, human overrides, and outcome monitoring.

## 2. Decision-model contract

Write:

> Over **horizon H**, choose decisions **x** to optimize **objective f(x; data)** subject to **constraints C**, using data frozen at **cutoff T**, with **solve budget B**, **uncertainty U**, and **fallback/override policy P**.

Clarify:

- who/what consumes the solution;
- decision frequency and horizon;
- continuous, integer, binary, sequence, or route decisions;
- units and scale of every coefficient;
- hard versus soft constraints;
- primary and secondary objectives;
- capacity, safety, policy, and contractual rules;
- uncertain demand, duration, yield, travel time, price, or outages;
- acceptable feasibility/optimality gap;
- response when data is missing or solver times out;
- re-planning and freeze windows;
- whether users can override and why.

Avoid combining incompatible business metrics into one arbitrary weighted score without owner agreement and sensitivity analysis.

## 3. Mathematical-programming foundations

### Linear program

`minimize cᵀx`

subject to:

`Ax ≤ b`<br>
`A_eq x = b_eq`<br>
`l ≤ x ≤ u`

Variables are continuous. LPs have mature algorithms and strong duality under standard conditions.

### Mixed-integer linear program

Add `x_i ∈ Z` or `x_i ∈ {0,1}` for selected variables. Examples:

- open facility or not;
- assign job to machine;
- choose product grade;
- activate fixed setup cost;
- visit customer;
- enforce either/or logic.

MILPs are generally NP-hard; solver performance depends strongly on formulation, bounds, presolve, cuts, branching, symmetry, and warm starts.

### Nonlinear/convex programs

Convex objectives and feasible sets support global optimality guarantees with suitable solvers. Nonlinear non-convex models may converge to local solutions or fail depending on initialization and scaling. Do not label a nonlinear model convex because its variables are continuous.

### Constraint programming

CP models variables with domains and global constraints such as all-different, no-overlap, cumulative capacity, and logical implications. Propagation removes infeasible values. CP-SAT combines SAT, CP, and integer techniques and uses integer coefficients.

## 4. Variables, parameters, and modeling patterns

### Assignment

Binary `x_ij=1` if worker/machine `i` handles task `j`.

Typical constraints:

- each task assigned exactly once: `Σ_i x_ij=1`;
- capacity: `Σ_j demand_j x_ij ≤ capacity_i`;
- qualification: fix invalid `x_ij=0`.

### Selection and fixed charge

Binary `y_i` indicates opening/activation. Link flow `x_i` with:

`x_i ≤ M_i y_i`

Use the smallest valid bound `M_i`. Loose big-M weakens relaxation and can cause numerical issues. Indicator constraints or native logical constructs may be better.

### Piecewise linear cost

Model tariffs, discounts, or penalties with breakpoints, SOS2/native piecewise constructs, or segment variables. Confirm continuity, convexity, and boundary behavior.

### Logical conditions

- implication: if A then B;
- either/or;
- exactly/at-most/at-least K;
- mutually exclusive choices;
- prerequisites.

Prefer native Boolean/indicator constraints when supported rather than opaque large-M formulas.

### Multi-objective decisions

- weighted sum;
- lexicographic priority;
- epsilon-constraint: optimize one objective while bounding another;
- Pareto frontier/scenario comparison.

Normalize units and show sensitivity. A small weight can dominate when metric scales differ.

## 5. LP duality and sensitivity

Dual variables/shadow prices quantify the marginal objective change for a small relaxation of a constraint under the valid sensitivity range.

Use them to ask:

- what is one additional unit of capacity worth?
- which constraints bind?
- where should expansion occur?
- is a business constraint expensive?

Caveats:

- shadow prices can change beyond the allowable range;
- integer models do not inherit LP dual interpretation directly;
- degeneracy can produce multiple valid duals;
- inaccurate coefficients yield misleading sensitivity.

Reduced costs describe how much an objective coefficient must improve before a nonbasic variable enters an LP solution.

## 6. How MIP solvers search

### LP relaxation

Drop integrality to obtain a bound. For minimization, the LP relaxation is a lower bound.

### Branch-and-bound

1. solve a relaxation;
2. if fractional, branch on a variable/decision;
3. compute node bounds;
4. prune infeasible nodes or those unable to beat incumbent;
5. continue until gap/time/node limit.

Cuts tighten relaxations without removing integer-feasible solutions. Heuristics find incumbents quickly. Presolve simplifies the model.

### Status and gap

Record:

- feasible/infeasible/unbounded;
- optimal or feasible under limit;
- incumbent objective;
- best bound;
- absolute/relative gap;
- wall time, nodes, iterations;
- numerical warnings.

A time-limited feasible solution can be operationally acceptable if the gap and constraint validation meet predeclared criteria.

## 7. Scheduling model

### Core entities

- jobs/orders/tasks;
- operations with duration;
- machines/resources/crews;
- release times;
- due dates;
- precedence;
- setup/changeover;
- calendars and downtime;
- inventory/material;
- batching and campaign rules.

### Objectives

- makespan: finish all work as early as possible;
- total/maximum lateness or tardiness;
- weighted tardiness;
- setup/changeover cost;
- energy or overtime;
- throughput/profit;
- work-in-process/inventory;
- stability versus previous schedule.

These objectives conflict. Define business priority and acceptable trade-offs.

### Interval/CP formulation

An operation has start, duration, and end; optional intervals represent alternative assignments. Constraints:

- no-overlap on unary machine;
- cumulative capacity on multi-capacity resource;
- precedence `start_B ≥ end_A`;
- alternative machine selection;
- calendar/unavailability;
- sequence-dependent setup;
- synchronization.

### Time-indexed MIP

Binary `x_(j,t)=1` when job `j` starts at time `t`. It can be strong and intuitive but explodes with horizon granularity.

### Disjunctive/precedence MIP

Pairwise binary variables decide order on a machine, linked to start times with bounds. It avoids time discretization but can have many binaries and weak big-M constraints.

Choose formulation through data scale and benchmark evidence.

## 8. Sequence-dependent setup and campaign planning

Changeover depends on predecessor and successor—for example color, product grade, tooling, allergen, or cleaning.

Model options:

- circuit/route over tasks on each machine;
- pairwise precedence binaries;
- transition matrix in sequence variables;
- state/resource formulation;
- aggregate campaign before detailed scheduling.

Validate:

- first/last setup;
- forbidden transitions;
- cleaning duration/resource;
- setup carryover across shifts/horizon;
- minimum/maximum campaign length;
- material/inventory feasibility;
- rework and breakdown.

An asymmetric transition matrix must not be silently symmetrized.

## 9. Routing and network optimization

### Shortest path and flow

- shortest path minimizes additive path cost;
- maximum flow maximizes feasible flow through capacities;
- minimum-cost flow combines capacity and cost;
- matching assigns pairs;
- facility location chooses sites and flows.

### Vehicle routing

VRP extends traveling salesperson with capacity, time windows, pickups/deliveries, multiple depots, skills, breaks, and heterogeneous fleets.

Common failures:

- incorrect travel-time matrix/time zone;
- asymmetric travel ignored;
- infeasible time windows;
- service time omitted;
- route starts/ends wrong;
- vehicle capacity units mismatch;
- traffic uncertainty;
- re-optimization instability.

Use domain-specific routing APIs/solvers where suitable, but independently validate returned routes and constraints.

## 10. Minimal dependency-free example: assignment optimization

```python
from __future__ import annotations

from itertools import permutations
from typing import Sequence


def solve_assignment(costs: Sequence[Sequence[float]]) -> tuple[list[int], float]:
    """Solve a tiny square assignment problem by exhaustive search."""
    size = len(costs)
    if size == 0 or any(len(row) != size for row in costs):
        raise ValueError("cost matrix must be nonempty and square")

    best_assignment: tuple[int, ...] | None = None
    best_cost = float("inf")
    for assignment in permutations(range(size)):
        total = sum(costs[worker][task] for worker, task in enumerate(assignment))
        if total < best_cost:
            best_cost = total
            best_assignment = assignment

    if best_assignment is None:
        raise RuntimeError("no assignment found")
    return list(best_assignment), best_cost


assignment, objective = solve_assignment(
    [
        [9.0, 2.0, 7.0],
        [6.0, 4.0, 3.0],
        [5.0, 8.0, 1.0],
    ]
)
assert assignment == [1, 0, 2]
assert objective == 9.0
assert len(set(assignment)) == 3
```

This is `O(n!)` and educational only. Production assignment uses Hungarian/min-cost-flow/MIP/CP algorithms and must validate all constraints.

## 11. Infeasibility and debugging

### First distinguish

- data/schema error;
- genuinely impossible demand;
- contradictory hard rules;
- unit/index/sign mistake;
- missing variable option;
- too-tight horizon/bounds;
- numerical issue;
- solver/model unsupported construct.

Techniques:

- independently validate input units and domains;
- start with a small known-feasible instance;
- add constraints incrementally;
- introduce diagnostic slack with very high penalty;
- request an irreducible infeasible subsystem/conflict refiner where supported;
- inspect presolve and solver logs;
- test boundary scenarios;
- compare constraint counts and generated coefficients;
- validate a candidate solution outside the solver.

Never solve infeasibility by silently relaxing safety, legal, quality, or contractual constraints.

### Unboundedness

The objective can improve indefinitely because a bound/link/constraint is missing or signs are wrong. It can also be a valid mathematical result. Trace variables in an improving direction.

### Numerical stability

- scale coefficients and units;
- avoid very large big-M;
- use tight variable bounds;
- avoid nearly dependent constraints;
- choose tolerances deliberately;
- check post-solve residuals.

“Optimal” is relative to solver feasibility/integrality tolerances.

## 12. Heuristics and metaheuristics

Exact solvers may be too slow or formulation may be complex.

### Constructive/local search

- greedy assignment/dispatching;
- earliest due date, shortest processing time;
- insertion;
- swap, relocate, 2-opt/3-opt;
- large neighborhood search;
- ruin-and-recreate.

### Metaheuristics

- simulated annealing;
- tabu search;
- genetic/evolutionary algorithms;
- ant colony;
- variable neighborhood search.

Use when:

- time budget is tight;
- exact gap is less important;
- problem has custom nonlinear simulation;
- solution repair is easy.

Evaluate feasibility rate, objective versus bound/baseline, stability, runtime distribution, and robustness across seeds. A heuristic's lack of optimality proof must be explicit.

Hybrid strategies:

- heuristic warm start for MIP/CP;
- solver repairs heuristic solution;
- decomposition/master-subproblem;
- large-neighborhood search using CP/MIP subproblems;
- ML predicts branching, warm start, demand, or candidate subset.

## 13. Decomposition and large problems

### Benders decomposition

Separate complicating master decisions from a subproblem; add feasibility/optimality cuts iteratively. Useful for facility/assignment with continuous recourse.

### Dantzig-Wolfe/column generation

Master chooses from patterns/routes; pricing generates promising columns. Common in crew/vehicle scheduling and cutting stock.

### Lagrangian relaxation

Dualize difficult constraints into the objective, solve easier subproblems, update multipliers. Produces bounds and heuristic solutions.

### Rolling horizon

Optimize a window, freeze near-term decisions, advance with updated data. It controls scale and uncertainty but may create myopic choices and boundary artifacts.

Document decomposition convergence, bounds, stopping, and solution repair.

## 14. Uncertainty

### Deterministic scenarios

Run base/upside/downside or stress cases. Easy to explain but not probabilistically complete.

### Stochastic programming

Optimize expected objective over scenarios, often with first-stage decisions before uncertainty and recourse afterward. Scenario quality and probability matter; size grows quickly.

### Robust optimization

Optimize against an uncertainty set, balancing protection and conservatism. Budgeted sets can control worst-case severity.

### Chance constraints

Require a constraint to hold with specified probability under distributional assumptions/approximations.

### Distributionally robust optimization

Optimize against a family of distributions near observed data. The ambiguity set/radius is a consequential choice.

Evaluate out-of-sample cost, feasibility/violation rate, tail risk, and sensitivity. Do not call one forecast scenario “stochastic optimization.”

## 15. Prediction plus optimization

Common pipeline:

`forecast/ML → calibrated scenarios/parameters → optimizer → simulation/replay → action → outcome feedback`

Risks:

- optimizing noisy point predictions;
- optimizer exploits model errors (“optimizer's curse”);
- prediction metric does not match decision value;
- feature/decision feedback changes data;
- covariate shift after policy change.

Better:

- decision-focused metrics;
- prediction intervals/scenarios;
- robust constraints;
- conservative bounds for critical parameters;
- end-to-end backtesting;
- perturbation/sensitivity analysis;
- causal evaluation of deployed policy.

Prescriptive ML and reinforcement learning can learn policies, but hard constraints, off-policy evaluation, exploration safety, and distribution shift remain.

## 16. Validation and production integration

### Model validation

- dimensional/unit analysis;
- known tiny instances with expected optimum;
- randomized property tests;
- independent constraint checker;
- compare solver/formulations/baselines;
- sensitivity and stress scenarios;
- historical replay;
- shadow use with planners/operators.

### Production controls

- immutable input snapshot and cutoff;
- data-quality gate;
- model/config/solver version;
- reproducible run ID and seed;
- time limit, gap, and termination status;
- warm start and previous-plan reference;
- post-solve feasibility checker;
- fallback schedule/rule;
- approval/override with reason;
- re-optimization and freeze policy;
- audit trail and rollback.

### Monitoring

- solve success, feasibility, gap, runtime and nodes;
- constraint slack/binding frequency;
- objective components;
- override/rejection rate;
- schedule churn/stability;
- realized cost, service, throughput, lateness, setup, downtime;
- forecast error and parameter drift;
- data freshness and missing capacity;
- fallback usage.

Objective value is not realized business value. Compare planned versus actual and separate model, execution, and external causes.

## 17. Library and solver map

| Tool | Best fit | Boundary |
|---|---|---|
| SciPy optimize/HiGHS | LP/MILP and continuous optimization APIs | compact modeling; inspect status/gap |
| OR-Tools | CP-SAT, routing, assignment, flows | integer coefficients for CP-SAT; API-specific modeling |
| Pyomo | algebraic modeling with many external solvers | solver installed/licensed separately |
| PuLP | approachable LP/MIP modeling | scale/features depend on chosen solver |
| CVXPY | disciplined convex modeling and some mixed-integer support | accepted problem class and installed solver |
| Gurobi/CPLEX/Xpress | commercial high-performance optimization | licensing, deployment and reproducibility |
| SCIP | open-source optimization suite | build/version and supported interfaces |
| MiniZinc | high-level constraint modeling across solvers | backend capabilities and translation |
| Timefold/OptaPlanner-style tools | planning/heuristic constraint solving | score semantics and termination |

Modeling layer and solver are different. Record both versions, parameters, licenses, and deployment environment.

## 18. Rapid interview questions

**LP versus MILP?**<br>
LP variables are continuous with linear relationships; MILP adds integer/binary decisions and combinatorial search.

**MIP versus CP-SAT?**<br>
MIP benefits from strong linear relaxations; CP-SAT excels at discrete logic and scheduling. Formulation and benchmark decide.

**What is a feasible solution?**<br>
One satisfying every hard constraint within defined tolerances, regardless of objective quality.

**What is optimality gap?**<br>
Difference between incumbent and best bound, absolute or relative, showing how far the current solution could be from proven optimum.

**Why is big-M risky?**<br>
Too large weakens relaxation and harms numerical stability; too small removes valid solutions.

**What is a shadow price?**<br>
For an LP, the marginal objective impact of relaxing a constraint within a valid sensitivity region.

**How do you diagnose infeasibility?**<br>
Validate data/units, simplify, add constraints incrementally, inspect conflicts/IIS, use diagnostic slacks, and never silently relax protected constraints.

**Why can a better forecast worsen optimization?**<br>
Aggregate prediction metrics may improve while errors near binding constraints or high-value decisions worsen.

**When use a heuristic?**<br>
When exact solve time/formulation is impractical and a fast feasible solution with measured quality is sufficient.

**How do you productionize a solver?**<br>
Version inputs/model/solver, validate output independently, set time/gap/fallback, log status/overrides, replay, stage, monitor, and rollback.

## 19. Lead-level case: production grade scheduling

Structure the answer:

1. Define orders/grades, lines, horizon, frozen window, inventory, due dates, rates, transition matrix, maintenance, and operator authority.
2. Separate hard safety/quality/material/resource constraints from soft lateness, campaign, inventory, and stability preferences.
3. Reconcile units and build deterministic input contracts with point-in-time demand and capacity.
4. Establish current dispatching/manual baseline and tiny-instance test suite.
5. Compare CP-SAT interval/sequence formulation with MIP disjunctive/time-indexed alternatives on representative workloads.
6. Use lexicographic or owner-approved objective trade-offs: feasibility/safety, service, changeover, throughput/profit, schedule stability.
7. Add tight bounds, symmetry breaking, warm start from current plan, time limit, and acceptable gap.
8. Validate every returned schedule independently; diagnose infeasibility with conflict/slack reports that planners can understand.
9. Backtest realized production, grade transition/yield, lateness, inventory, downtime, and forecast uncertainty; run stress scenarios.
10. Deploy decision support first, capture overrides/reasons, freeze near-term tasks, re-optimize on material events, and retain manual/fallback plan.
11. Measure realized margin/service and execution adherence—not only solver objective—and use causal discipline before attributing impact.

## 20. Final checklist

- [ ] I define variables, data cutoff, objective units, hard/soft constraints, horizon, and fallback.
- [ ] I distinguish LP, MILP, convex/nonlinear optimization, CP/CP-SAT, and heuristics.
- [ ] I model assignment, activation, logic, capacity, and multi-objective trade-offs.
- [ ] I can explain LP relaxation, branch-and-bound, cuts, incumbent, bound, and gap.
- [ ] I understand interval, time-indexed, and disjunctive scheduling formulations.
- [ ] I handle sequence-dependent setup, calendars, resources, routing, and re-planning.
- [ ] I diagnose infeasible, unbounded, time-limited, and numerical outcomes.
- [ ] I compare deterministic, stochastic, robust, and chance-constrained approaches.
- [ ] I validate solutions outside the solver and against historical/operational evidence.
- [ ] I design versioning, status/gap logging, human override, monitoring, fallback, and rollback.

## 21. Primary references

- [Google OR-Tools documentation](https://developers.google.com/optimization)
- [OR-Tools CP-SAT guide](https://developers.google.com/optimization/cp/cp_solver)
- [OR-Tools scheduling recipes](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/scheduling.md)
- [OR-Tools employee scheduling](https://developers.google.com/optimization/scheduling/employee_scheduling)
- [Pyomo documentation](https://pyomo.readthedocs.io/en/stable/)
- [SciPy mixed-integer linear programming API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)
- [CVXPY documentation](https://www.cvxpy.org/)
- [MiniZinc documentation](https://docs.minizinc.dev/)
- [HiGHS documentation](https://highs.dev/)
- [Boyd and Vandenberghe, Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/)
- [Bertsimas and Tsitsiklis, Introduction to Linear Optimization](https://athenasc.com/linoptbook.html)
