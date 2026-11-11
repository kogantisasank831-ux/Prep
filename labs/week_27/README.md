# Week 27 LoRA lab

The lab freezes a two-by-two base matrix and manually optimises low-rank A and B
adapters. It exposes rank, alpha/rank scaling, gradient clipping, parameter
counts and optional simulated signed 4-bit base quantisation.

```shell
python -m labs.week_27.demo smoke
python -m labs.week_27.demo smoke --qlora
python -m pytest tests/test_week27_lora.py -q
```

This is a numerical teaching model, not an LLM fine-tune. Its tiny dimensions
make adapter parameter efficiency unrealistic; real target-module selection,
tokenisation, kernels, paged optimisers and hardware memory must be measured in
the actual framework.

