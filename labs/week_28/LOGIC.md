# Week 28 logic

Exact duplicate instruction-response pairs are removed before splitting. All
examples from one source remain in one partition. The chat template makes role
boundaries explicit, and the loss mask gives weight only to assistant response
tokens. Padding receives zero attention and zero loss. Vocabulary is fitted on
training examples, so validation-only tokens become `<unk>`.

The exact lookup scores training memorisation but should fail on unseen held-out
instructions. That contrast is a teaching baseline, not model evaluation.

