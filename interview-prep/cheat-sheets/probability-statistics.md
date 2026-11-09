---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Probability and statistics interview cheat sheet"
description: "Probability, inference, experimentation, and uncertainty revision for senior AI and Data Science interviews."
summary: "Revise probability, estimation, confidence intervals, hypothesis tests, power, experimentation, and causal interpretation."
permalink: "/interview-prep/cheat-sheets/probability-statistics/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 1 · Statistics"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 1 source:** This page integrates the previously prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** Lead Data Scientist, Applied Scientist, AI/ML Engineer  
**Goal:** move from formula recall to correct decisions, assumptions, and business interpretation.

## 1. Thirty-second revision

- Probability models uncertainty; statistics learns about a population from samples.
- Conditional probability is not the same as reversing the condition; use Bayes' theorem.
- A p-value is `P(data this extreme or more | null)`, not the probability that the null is true.
- A confidence interval is a procedure with long-run coverage, not a probability statement about a fixed frequentist parameter.
- Statistical significance does not imply practical value.
- Power rises with sample size, effect size, lower noise, and a less stringent significance threshold.
- Randomization supports causal inference; regression on observational data does not automatically do so.

## 2. Descriptive statistics

| Measure | Formula/meaning | Best use / limitation |
|---|---|---|
| Mean | $\bar{x}=\frac{1}{n}\sum x_i$ | Efficient for symmetric data; sensitive to outliers |
| Median | Middle ordered value | Robust for skewed/heavy-tailed data |
| Mode | Most frequent value | Useful for categorical/discrete data |
| Range | max − min | Very sensitive to extremes |
| Variance | $s^2=\frac{1}{n-1}\sum(x_i-\bar{x})^2$ | Squared spread; unit is squared |
| Standard deviation | $s=\sqrt{s^2}$ | Spread in original units |
| IQR | $Q_3-Q_1$ | Robust middle-50% spread |
| MAD | Median absolute deviation | Robust scale measure |

Use the sample denominator `n - 1` to make sample variance unbiased under standard assumptions.

### Covariance and correlation

$$
\operatorname{Cov}(X,Y)=E[(X-E[X])(Y-E[Y])]
$$

$$
\rho_{X,Y}=\frac{\operatorname{Cov}(X,Y)}{\sigma_X\sigma_Y}
$$

- Pearson correlation measures linear association and is sensitive to outliers.
- Spearman correlation is Pearson correlation of ranks; it captures monotonic association.
- Zero correlation does not generally imply independence.
- Correlation does not identify causation.

## 3. Probability rules

### Core identities

$$
P(A^c)=1-P(A)
$$

$$
P(A\cup B)=P(A)+P(B)-P(A\cap B)
$$

$$
P(A\mid B)=\frac{P(A\cap B)}{P(B)}
$$

If $A$ and $B$ are independent:

$$
P(A\cap B)=P(A)P(B)
$$

Mutually exclusive events cannot occur together. Nontrivial mutually exclusive events are **not** independent.

### Bayes' theorem

$$
P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}
$$

For a binary condition:

$$
P(D\mid +)=\frac{P(+\mid D)P(D)}{P(+\mid D)P(D)+P(+\mid D^c)P(D^c)}
$$

### Solved example: positive medical test

- Prevalence: 1%
- Sensitivity: 95%
- Specificity: 90%, so false-positive rate = 10%

$$
P(D\mid +)=\frac{0.95\times0.01}{0.95\times0.01+0.10\times0.99}
=0.0876
$$

Despite a positive test, the probability of disease is about **8.8%** because the condition is rare. This is the base-rate effect.

## 4. Random variables, expectation, and variance

For a discrete random variable:

$$
E[X]=\sum_x xP(X=x)
$$

Rules:

$$
E[aX+b]=aE[X]+b
$$

$$
\operatorname{Var}(X)=E[X^2]-E[X]^2
$$

$$
\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)
$$

$$
\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)+2\operatorname{Cov}(X,Y)
$$

If $X$ and $Y$ are independent, covariance is zero and their variances add.

### Solved example: expected profit

A campaign produces ₹500 profit with probability 0.30 and loses ₹100 otherwise.

$$
E[X]=0.30(500)+0.70(-100)=₹80
$$

Positive expected value does not describe risk, capital constraints, or tail losses; inspect the distribution too.

## 5. Distributions to know

| Distribution | Parameters | Mean / variance | Common use |
|---|---|---|---|
| Bernoulli | $p$ | $p$ / $p(1-p)$ | One binary outcome |
| Binomial | $n,p$ | $np$ / $np(1-p)$ | Number of successes in fixed independent trials |
| Categorical | class probabilities | — | One outcome among multiple classes |
| Poisson | $\lambda$ | $\lambda$ / $\lambda$ | Event count in an interval under assumptions |
| Exponential | rate $\lambda$ | $1/\lambda$ / $1/\lambda^2$ | Waiting time for Poisson process; memoryless |
| Normal | $\mu,\sigma^2$ | $\mu$ / $\sigma^2$ | Symmetric continuous variation; approximations |
| Uniform | lower, upper | midpoint / $(b-a)^2/12$ | Equal density over interval |
| Beta | $\alpha,\beta$ | $\alpha/(\alpha+\beta)$ | Probability prior/posterior |

Interview checks:

- Poisson assumes independent events and a stable rate in the simplest form.
- Real count data may be overdispersed; negative binomial can be more appropriate.
- Normality of raw data is not always required; many procedures require approximately normal errors or sampling distributions.

## 6. LLN, CLT, and standard error

- **Law of Large Numbers:** the sample average converges to the expected value under suitable conditions.
- **Central Limit Theorem:** the standardized sampling distribution of a sum/mean tends toward normality under suitable conditions, even if individual observations are not normal.

For independent observations with population standard deviation $\sigma$:

$$
SE(\bar{X})=\frac{\sigma}{\sqrt{n}}
$$

Standard deviation describes variation among observations. Standard error describes uncertainty in an estimator. Quadrupling sample size halves the standard error.

## 7. Estimation: bias, variance, MLE, and MAP

An estimator can be evaluated by:

- **bias:** $E[\hat\theta]-\theta$;
- **variance:** variation across repeated samples;
- **consistency:** convergence to the true parameter with more data;
- **efficiency:** low variance among comparable estimators;
- **mean squared error:** $\operatorname{Bias}^2+\operatorname{Variance}$.

### Maximum likelihood

$$
\hat\theta_{MLE}=\arg\max_\theta P(D\mid\theta)
$$

Usually maximize log-likelihood because products become sums and numerical stability improves.

### MAP

$$
\hat\theta_{MAP}=\arg\max_\theta P(D\mid\theta)P(\theta)
$$

MAP adds a prior. MLE is a special case with a flat prior under suitable conditions. Regularization often corresponds to a prior: L2 ↔ Gaussian, L1 ↔ Laplace.

## 8. Confidence intervals

For a mean with unknown population standard deviation:

$$
\bar{x}\pm t_{1-\alpha/2,n-1}\frac{s}{\sqrt{n}}
$$

### Solved example

- $n=100$
- mean = 50
- sample standard deviation = 10
- $SE=10/\sqrt{100}=1$
- 95% critical $t\approx1.984$

$$
CI=50\pm1.984(1)=[48.016,51.984]
$$

Interpretation: if this procedure were repeated many times, about 95% of such intervals would contain the fixed population mean under the assumptions.

For skewed statistics or unclear analytic standard errors, use bootstrap intervals carefully.

## 9. Hypothesis testing

### Workflow

1. Define primary outcome and hypothesis before examining results.
2. Choose significance level $\alpha$.
3. Verify design/test assumptions.
4. Calculate test statistic and p-value.
5. Report effect size and confidence interval.
6. Make a domain/business decision, not merely “significant/not significant.”

### Errors and power

| Reality / decision | Reject null | Do not reject null |
|---|---|---|
| Null true | Type I error, probability $\alpha$ | Correct |
| Alternative true | Correct; probability = power | Type II error, probability $\beta$ |

Power is $1-\beta$.

### The p-value is not

- the probability the null hypothesis is true;
- the probability the result occurred “by chance”;
- the size or importance of the effect;
- proof that no effect exists when above 0.05.

## 10. Test-selection guide

| Question | Common test | Key assumptions/notes |
|---|---|---|
| One mean versus target | One-sample t-test | Independent data; mean inference |
| Two independent means | Welch's t-test | Prefer Welch when variances/sample sizes differ |
| Paired before/after mean | Paired t-test | Analyze within-pair differences |
| More than two means | ANOVA/Welch ANOVA | Follow with controlled comparisons |
| Two proportions | Two-proportion z-test/Fisher exact | Independence; adequate counts for z approximation |
| Association of categories | Chi-square/Fisher exact | Expected cell counts for chi-square |
| Non-normal independent groups | Mann–Whitney | Tests distribution/rank shift, not automatically medians |
| Non-normal paired data | Wilcoxon signed-rank | Symmetry assumptions for standard interpretation |
| Linear association | Pearson correlation | Linear relationship; outlier sensitivity |
| Monotonic association | Spearman correlation | Rank-based |

Check the experimental unit. Thousands of events from 100 users do not necessarily provide 10,000 independent observations.

## 11. Solved A/B test

Control: 1,000 conversions from 10,000 users = 10.0%  
Treatment: 1,080 conversions from 10,000 users = 10.8%

Absolute lift:

$$
0.108-0.100=0.008=0.8\text{ percentage points}
$$

Relative lift:

$$
\frac{0.108-0.100}{0.100}=8\%
$$

Pooled proportion under the null:

$$
\hat p=\frac{1000+1080}{20000}=0.104
$$

Standard error under the null:

$$
SE=\sqrt{0.104(0.896)(1/10000+1/10000)}\approx0.00432
$$

$$
z=0.008/0.00432\approx1.85
$$

Two-sided p-value is approximately 0.064. A 95% confidence interval for the difference is approximately `[-0.00046, 0.01646]`.

Conclusion: the observed lift is promising but does not cross a conventional two-sided 5% threshold. Report uncertainty and business value; do not say “there is no effect.”

## 12. Sample size and power

For two equally sized groups comparing proportions, a rough planning formula is:

$$
n_{per\ arm}\approx\frac{2\bar p(1-\bar p)(z_{1-\alpha/2}+z_{1-\beta})^2}{\delta^2}
$$

where $\delta$ is the absolute minimum detectable effect.

### Approximate example

Baseline 10%, MDE 1 percentage point, two-sided $\alpha=0.05$, power 80%:

$$
n\approx\frac{2(0.1)(0.9)(1.96+0.84)^2}{0.01^2}\approx14,112
$$

Approximately 14,000 users per arm are required under this simplified calculation. Use an exact/design-aware calculation for implementation and adjust for clustering, attrition, noncompliance, multiple variants, and unequal allocation.

## 13. Multiple testing

Testing many hypotheses increases the chance of false positives.

- Bonferroni controls family-wise error conservatively: use $\alpha/m$.
- Holm is a step-down family-wise procedure and is usually less conservative.
- Benjamini–Hochberg controls expected false discovery rate.
- Pre-register one primary metric; treat exploratory metrics as exploratory.
- Avoid slicing until something “significant” appears.

## 14. Bootstrap and permutation tests

### Bootstrap

Sample observations with replacement, recompute the statistic, and use the empirical distribution for standard errors or intervals.

Appropriate when:

- analytic variance is difficult;
- the sampling unit can be resampled correctly;
- observations are representative and approximately independent at that unit.

For clustered users/sessions or time series, resample clusters/blocks—not individual dependent rows.

### Permutation test

Under exchangeability, shuffle group labels and compare the observed statistic with the null distribution. It tests whether the observed assignment/outcome relationship is unusual under the null.

## 15. Experimentation pitfalls

### Design checklist

- Define eligibility, randomization unit, exposure, outcome window, and analysis population.
- Choose one primary metric and important guardrails.
- Estimate sample size before launch.
- Run an A/A test when validating a new experimentation platform.
- Check sample-ratio mismatch and pre-treatment balance.
- Analyze by intention to treat unless a different estimand was pre-specified.
- Account for novelty, seasonality, interference and repeated measurement.
- Do not stop simply when p-value first falls below 0.05.

### Common biases

| Bias/problem | Example |
|---|---|
| Selection bias | Only highly engaged users see treatment |
| Survivorship bias | Analyze only customers still active |
| Peeking | Stop experiment at first significant day |
| Regression to mean | Select worst performers, then observe improvement |
| Interference | One user's treatment changes another user's outcome |
| Simpson's paradox | Aggregate trend reverses within important subgroups |
| Attrition | Treatment changes who remains observable |
| Instrumentation change | Tracking differs across variants |

## 16. Variance reduction and CUPED

Use a pre-treatment covariate $X$ correlated with outcome $Y$:

$$
\theta=\frac{\operatorname{Cov}(Y,X)}{\operatorname{Var}(X)}
$$

$$
Y_{adj}=Y-\theta(X-E[X])
$$

If assumptions hold, the treatment estimate remains unbiased while variance may fall roughly with the squared correlation $\rho^2$. Only use pre-treatment variables unaffected by treatment.

## 17. Causal inference essentials

### Variables in a causal graph

- **Confounder:** common cause of treatment and outcome; often needs adjustment.
- **Mediator:** lies on the treatment → outcome pathway; adjusting changes the estimand.
- **Collider:** common effect of two variables; conditioning can create spurious association.

### Methods to recognize

| Method | Core idea | Major condition |
|---|---|---|
| Randomized experiment | Treatment independent of potential outcomes by design | Correct randomization, compliance/measurement |
| Regression adjustment | Control measured covariates | No important unmeasured confounding, correct model |
| Propensity methods | Balance measured treatment predictors | Positivity and no unmeasured confounding |
| Difference-in-differences | Compare changes over time | Parallel trends absent treatment |
| Regression discontinuity | Compare near assignment cutoff | No manipulation; continuity near cutoff |
| Instrumental variables | Use exogenous treatment shifter | Relevance, exclusion, independence, monotonicity as applicable |

Prediction answers “what will happen?” Causal inference answers “what would change if we intervene?” A highly predictive variable need not be a valid intervention lever.

## 18. Missing data

| Mechanism | Meaning | Implication |
|---|---|---|
| MCAR | Missingness unrelated to observed/unobserved values | Complete-case analysis may remain unbiased but lose power |
| MAR | Missingness depends on observed information | Model/imputation can use observed predictors |
| MNAR | Missingness depends on unseen value even after observed data | Requires assumptions and sensitivity analysis |

Missingness itself may be informative. Fit preprocessing only on training data, add indicators when justified, and compare imputation strategies using validation—not convenience.

## 19. Bayesian fundamentals

$$
P(\theta\mid D)\propto P(D\mid\theta)P(\theta)
$$

- Prior: beliefs/information before current data.
- Likelihood: how compatible data is with parameter values.
- Posterior: updated parameter distribution.
- Posterior predictive: distribution of future observations integrating parameter uncertainty.
- Credible interval: posterior probability statement conditional on model/prior/data.

For Bernoulli data with Beta prior:

$$
p\sim\operatorname{Beta}(\alpha,\beta),\quad
p\mid D\sim\operatorname{Beta}(\alpha+s,\beta+f)
$$

where $s$ and $f$ are successes and failures.

## 20. Common traps

| Trap | Correct reasoning |
|---|---|
| “p = 0.03 means 97% chance treatment works” | Frequentist p-value does not give posterior probability |
| “Not significant means equal” | It may mean insufficient precision; use equivalence/non-inferiority design if needed |
| “Large sample fixes bias” | It reduces variance, not systematic bias |
| “CLT means raw data becomes normal” | Sampling distribution of normalized sums/means approaches normal |
| “Correlation is causation after controlling variables” | Adjustment needs a valid causal identification strategy |
| “More observations means more independent data” | Repeated/clustered rows need cluster-aware analysis |
| “Use normality test, then choose test mechanically” | Consider estimand, design, robustness and sample size |
| “Average treatment effect applies to everyone” | Effects may be heterogeneous; subgroup work needs correction/validation |

## 21. Rapid interview questions and answers

1. **Independence versus zero correlation?** Independence generally implies zero covariance when moments exist; zero correlation only rules out linear association.
2. **Why does variance use `n-1`?** Estimating the mean consumes one degree of freedom; Bessel's correction makes sample variance unbiased under standard assumptions.
3. **Confidence versus credible interval?** Frequentist CI describes long-run procedure coverage; Bayesian credible interval gives posterior probability conditional on model/prior/data.
4. **Type I versus Type II error?** Type I rejects a true null; Type II fails to reject a false null.
5. **What increases power?** Larger effect, sample, allocation efficiency, lower variance, or higher alpha; design/variance reduction can help.
6. **When use Welch's t-test?** For two independent means, especially when variance or sample size may differ; it does not assume equal variances.
7. **Why not peek daily?** Repeated unplanned testing inflates false-positive probability; use fixed horizon or valid sequential methods.
8. **Absolute versus relative lift?** From 10% to 11% is +1 percentage point absolute and +10% relative.
9. **Why can Simpson's paradox occur?** Group proportions/confounding differ, so weighted aggregate association can reverse subgroup associations.
10. **What does randomization buy?** In expectation it balances measured and unmeasured pre-treatment factors, supporting causal identification.

## 22. Lead-level case

**Question:** A new agent-assist feature appears to reduce handling time by 8%. Design the experiment and decide whether to launch.

**Strong answer structure:**

1. Define the decision: launch to which agents/use cases and under what safety constraints.
2. Choose randomization unit. Agent-level randomization may avoid contamination; account for clustered tickets.
3. Primary metric: handling time with a robust definition; consider median/quantiles and task mix.
4. Guardrails: resolution quality, reopen/escalation rate, customer satisfaction, compliance errors, hallucination/tool-error rate, and agent workload.
5. Set eligibility, exposure, analysis unit, attribution window, MDE, alpha, power and duration before launch.
6. Stratify or block by team/experience if appropriate; check sample-ratio mismatch and balance.
7. Use intention-to-treat; account for clustering/repeated observations and heavy-tailed time data.
8. Examine effect size and confidence interval, not only p-value; inspect pre-specified heterogeneous effects.
9. Estimate net value: saved time minus inference, review, error and change-management costs.
10. Launch gradually only if quality/safety guardrails pass; continue monitoring novelty decay and model drift.

## 23. Final revision checklist

- [ ] I can apply conditional probability and Bayes' theorem.
- [ ] I know expectation, variance, covariance and key distributions.
- [ ] I can distinguish standard deviation from standard error.
- [ ] I can interpret confidence intervals and p-values correctly.
- [ ] I can select a statistical test from the design and estimand.
- [ ] I can calculate and explain lift, uncertainty, power and MDE.
- [ ] I understand multiple testing, bootstrap and clustered observations.
- [ ] I can identify confounders, mediators and colliders.
- [ ] I can design and critique an end-to-end experiment.
