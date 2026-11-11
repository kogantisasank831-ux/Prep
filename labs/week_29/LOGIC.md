# Week 29 logic

All candidates must produce exactly one output for every frozen example. The
default excludes declared contamination. Exact match is normalised by one
published rule; classification metrics use a declared positive label;
perplexity is exponentiated mean token negative log-likelihood. Candidate gains
are paired against the base on the same examples and bootstrapped with a fixed
seed. Human votes remain separate preference evidence.

Exact match, perplexity, resampling and preference each answer a different
question. No single metric is promoted to overall model truth.

