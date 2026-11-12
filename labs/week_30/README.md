# Week 30 serving and report lab

The lab separates theoretical packed-weight and worst-context KV estimates from
measured load observations. It reports aggregate token throughput, TTFT and
end-to-end latency percentiles, capacity feasibility and explicit omitted-memory
warnings. A strict report schema requires the roadmap's final evidence and a
versioned package manifest.

```shell
python -m labs.week_30.demo capacity
python -m labs.week_30.demo report
python -m labs.week_30.demo smoke
python -m pytest tests/test_week30_serving.py -q
```

No serving runtime is launched. vLLM or an equivalent must be benchmarked on
the target model, quantisation, hardware, request distribution and concurrency.

