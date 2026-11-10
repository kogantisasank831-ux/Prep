---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-10"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Computer vision and multimodal AI interview cheat sheet"
description: "Visual task framing, data and annotation quality, CNNs, vision transformers, transfer learning, detection, segmentation, VLM evaluation, serving, monitoring, safety, and privacy."
summary: "Revise trustworthy image, video, and vision-language systems from capture and labels through modeling, grounded evaluation, deployment, and incident response."
permalink: "/interview-prep/cheat-sheets/computer-vision-multimodal-ai/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 9 · Computer vision and multimodal AI"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 9 scope:** This review candidate derives from the approved master index and the cited primary documentation. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, Computer Vision Engineer, Applied Scientist, Senior Data Scientist, AI/Data Science Lead  
**Use:** image/video modeling, vision-language systems, model evaluation, system design, deployment, and leadership interviews  
**Interview rule:** define the visual decision, annotation unit, capture process, deployment environment, and cost of a miss before choosing a CNN, vision transformer, detector, segmenter, or vision-language model.

## 1. Thirty-second revision

- Classification predicts one or more labels; detection predicts boxes and classes; segmentation predicts pixels; keypoints predict landmarks; retrieval matches representations.
- Image rows are not automatically independent. Split by patient, device, site, video, object instance, or time when those identities repeat.
- Audit capture conditions, resolution, compression, orientation, metadata, label policy, annotator agreement, rare classes, and duplicate or near-duplicate images.
- Start with a simple transfer-learning baseline. Training from scratch usually needs much more representative labeled data.
- CNNs encode locality and translation structure; vision transformers use patch tokens and attention and often benefit from large-scale pretraining.
- Augmentations must preserve the label and transform boxes, masks, and keypoints consistently.
- Detection needs IoU-aware matching and AP/recall by class, size, and operating threshold—not classification accuracy.
- Segmentation needs overlap and boundary evidence; empty masks and small objects require explicit metric rules.
- Vision-language models add prompt, language, grounding, OCR, hallucination, and cross-modal consistency failure modes.
- Evaluate by capture device, site, lighting, demographics where lawful and relevant, object size, occlusion, and other meaningful slices.
- Production evidence includes preprocessing parity, latency, memory, batch behavior, calibration, abstention, monitoring, rollback, and human review.
- A visually plausible output is not proof that a model used the right pixels or grounded its answer.

## 2. Frame the visual decision

Write a contract:

> At **decision time**, use visual evidence available from **capture source S** to predict **output Y** for **unit U**, enabling **action A** under **latency, safety, and review constraints**.

Record:

- task and output schema: label, score, boxes, masks, keypoints, embedding, caption, or structured answer;
- unit of prediction and stable identity;
- capture device, viewpoint, illumination, resolution, compression, frame rate, and metadata;
- label source, annotation guide, adjudication, uncertainty, and revision process;
- intended and excluded populations and environments;
- false-positive, false-negative, abstention, and delay costs;
- latency, throughput, memory, connectivity, privacy, retention, and review requirements.

Do not choose an architecture until the output can be scored and acted upon.

## 3. Dataset and annotation audit

### Identity and split correctness

Prevent the same underlying evidence from crossing splits:

- adjacent frames from one video;
- repeated photos of one object, patient, document, or location;
- crops or augmentations derived from one original;
- images from the same burst, camera, production lot, or site;
- a near-duplicate downloaded under another filename.

Use group, site, temporal, or external holdouts that match deployment. Perceptual hashes and embedding-based duplicate searches can help, but thresholds need manual validation.

### Annotation quality

Define class ontology, ambiguous cases, occlusion/truncation rules, box tightness, mask boundaries, negative examples, ignored regions, and minimum visible area. Measure disagreement on a representative sample and adjudicate systematically.

For detection and segmentation, audit:

- boxes or masks outside image bounds;
- invalid/empty geometry;
- duplicate annotations;
- missing objects versus true negatives;
- class hierarchy conflicts;
- small-object and crowded-scene consistency;
- changes to the labeling guide over time.

### Data provenance

Version the source manifest, usage rights, consent/privacy class, transformations, annotation version, split assignment, and removal requests. Images can carry faces, documents, location clues, and EXIF metadata even when the visible subject seems harmless.

## 4. Task families and evidence

| Task | Output | Useful metrics | Common trap |
|---|---|---|---|
| Single-label classification | one class + probability | macro/micro F1, log loss, calibration | accuracy hides rare-class failure |
| Multi-label classification | independent labels | per-label PR-AUC/F1, mAP, calibration | one global threshold for every label |
| Object detection | boxes, classes, scores | AP/AR across IoU, size and class | evaluating only one easy IoU threshold |
| Semantic segmentation | class per pixel | IoU/Dice by class, boundary metrics | background dominates pixel accuracy |
| Instance segmentation | object masks | mask AP/AR | good boxes with poor boundaries |
| Keypoints/pose | landmark coordinates | normalized distance, PCK/OKS | ignoring missing/occluded landmarks |
| Retrieval | ranked images/text | Recall@K, mAP, NDCG | sampled candidate set inflates quality |
| Caption/VQA/VLM | text or structure grounded in pixels | task rubric, exact/semantic score, grounding, hallucination | fluent text mistaken for visual correctness |

Always pair aggregate metrics with error review and slices aligned to the operating environment.

## 5. Architecture intuition

### Convolutional networks

A convolution applies shared local filters. Weight sharing and local receptive fields give useful inductive bias for images. Deeper layers expand the effective receptive field; residual connections improve optimization.

Know:

- kernel, stride, padding, dilation, pooling, channels, receptive field;
- normalization and activation placement;
- feature pyramids for multiple object scales;
- classification heads versus dense prediction heads.

### Vision transformers

ViTs convert image patches into tokens, add positional information, and apply attention. They can model global relationships directly and transfer well after strong pretraining, but compute grows with token count and high resolution.

Interview trade-off: compare data scale, pretraining, resolution, latency, memory, robustness, interpretability limits, and deployment hardware—not CNN versus ViT as a slogan.

### Detection and segmentation

- Two-stage detectors propose regions then classify/refine them; they can be accurate but add stages.
- One-stage detectors predict dense candidates and are often attractive for low-latency serving.
- Anchor-based and anchor-free designs encode candidate geometry differently.
- Encoder-decoder segmentation combines semantic context with spatial detail; skip connections recover resolution.

### Vision-language models

VLMs align or condition text and visual representations. Common patterns include dual encoders for retrieval, a vision encoder connected to a language model, and models trained for image-text generation or instruction following.

Evaluate model-specific chat templates, image tiling/resizing, maximum image count, OCR ability, grounding, prompt sensitivity, refusal behavior, and token/latency cost. Generalist ability does not remove the need for task-specific evidence.

## 6. Transfer learning and adaptation

Start with a pretrained model and a simple head:

1. reproduce the official preprocessing for the selected weights;
2. train the head with the backbone frozen;
3. unfreeze selected layers or the full backbone with a lower learning rate;
4. compare against a small baseline and the frozen-embedding option;
5. choose by held-out quality, calibration, compute, latency, and stability.

Fine-tuning too aggressively can destroy useful representations; freezing too much can underfit a shifted domain. Layer-wise learning rates, gradual unfreezing, parameter-efficient adaptation, and stronger regularization are options—not automatic requirements.

Pin weights, preprocessing, library version, label map, and checkpoint identity. “ResNet-50” or “a VLM” is not a reproducible model identifier.

## 7. Augmentation, imbalance, and hard examples

Valid augmentations depend on the label mechanism. Horizontal flips may be valid for animals but invalid for text, laterality, or road signs. Color shifts may improve lighting robustness or erase a diagnostic color signal.

Rules:

- transform image and geometry together;
- keep validation/test preprocessing deterministic;
- apply learned or stochastic transforms only inside training;
- review augmented samples and rare-class effects;
- record augmentation parameters with the run;
- test whether gains survive a different site/time/device.

For imbalance, compare class weighting, focal-style loss, balanced sampling, targeted collection, thresholding, and hard-negative mining. Oversampling repeated images can magnify annotation errors and overfitting.

## 8. Detection and segmentation mathematics

For predicted region $P$ and ground-truth region $G$:

$$
\operatorname{IoU}(P,G)=\frac{|P\cap G|}{|P\cup G|}
$$

Dice overlap is:

$$
\operatorname{Dice}(P,G)=\frac{2|P\cap G|}{|P|+|G|}
$$

Detection evaluation must specify:

- how predictions match ground truth;
- IoU threshold or range;
- confidence threshold and non-maximum suppression policy;
- maximum detections;
- treatment of ignored/crowd regions;
- class, object-size, and image-level aggregation.

AP summarizes a precision-recall curve under a defined protocol. It is not one universal number; changing IoU, candidate limits, class averaging, or dataset changes the meaning.

For segmentation, report per-class IoU/Dice, macro/weighted aggregation, boundary quality where important, and explicit behavior for images where both prediction and truth are empty.

## 9. Evaluation design

Use a locked evaluation manifest with exact preprocessing and label versions. Compare:

- simple baseline and current production model;
- overall quality and confidence intervals;
- class, site, device, lighting, blur, compression, viewpoint, scale, occlusion, and time slices;
- calibration and selective performance under abstention;
- robustness to plausible corruptions without claiming synthetic tests equal field performance;
- latency distribution, throughput, memory, energy/cost, and failure rate on target hardware;
- human-review workload and downstream decision impact.

For VLMs, define a rubric with visual evidence requirements. Separate OCR, object recognition, spatial relation, counting, grounding, reasoning, safety, and unsupported-detail errors. Preserve image, prompt, model, generation config, and output identity.

## 10. Serving architecture

A production path often includes:

1. validate media type, dimensions, size, frame count, and decompression limits;
2. remove or intentionally retain metadata under policy;
3. decode and apply versioned preprocessing;
4. batch dynamically within latency limits;
5. run model and deterministic postprocessing;
6. calibrate/threshold/abstain;
7. return a versioned output schema and trace identity;
8. route uncertain or high-impact cases to review;
9. monitor inputs, outputs, slices, latency, and outcomes.

Optimize only after measuring the bottleneck. Candidate techniques include resizing policy, mixed precision, compilation, quantization, pruning, distillation, batching, model cascades, and hardware-specific runtimes. Re-evaluate quality and geometry after every export or quantization change.

## 11. Monitoring and drift

Monitor:

- decode failures, invalid media, resolution/aspect ratio, blur, brightness, compression, camera/source mix;
- embedding and prediction distributions by meaningful slice;
- class/box/mask counts and confidence/abstention rates;
- delayed label quality and reviewer disagreement;
- latency, memory, accelerator utilization, queueing and fallback use;
- preprocessing/model/postprocessing versions and online/offline parity.

Input drift does not prove performance drift. Confirm with labels, review samples, controlled shadow evaluation, or another accepted proxy. Keep privacy-safe thumbnails or derived diagnostics only when policy allows.

## 12. Safety, security, and privacy

- Treat image bytes, filenames, metadata, OCR text, captions, and linked URLs as untrusted input.
- Bound pixels, frames, file size, decompression ratio, processing time, and downstream tokens.
- Isolate decoders and patch vulnerable media libraries promptly.
- Enforce tenant authorization before retrieval, inference, storage, or display.
- Test adversarial patches and corruptions only within an approved threat model; do not overclaim robustness from one benchmark.
- Redact or avoid retaining faces, documents, location, and other sensitive content unless necessary and authorized.
- For multimodal agents, visual text can contain prompt injection. It remains data, not trusted instructions.

## 13. Minimal IoU example

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    x1: float
    y1: float
    x2: float
    y2: float

    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)


def intersection_over_union(left: Box, right: Box) -> float:
    intersection = Box(
        x1=max(left.x1, right.x1),
        y1=max(left.y1, right.y1),
        x2=min(left.x2, right.x2),
        y2=min(left.y2, right.y2),
    ).area()
    union = left.area() + right.area() - intersection
    return intersection / union if union > 0.0 else 0.0
```

Production evaluation still needs matching rules, confidence thresholds, classes, ignored regions, and aggregation. This function establishes only box overlap.

## 14. Common failure modes

- Randomly splitting frames from the same video.
- Using preprocessing that does not match pretrained weights.
- Applying a crop or flip to the image but not to boxes/masks.
- Treating unannotated objects as negatives without checking annotation completeness.
- Reporting overall accuracy for rare or safety-critical classes.
- Tuning confidence/NMS thresholds on the final test set.
- Ignoring small objects, empty masks, or crowded scenes.
- Comparing AP values produced by different protocols.
- Believing attention maps or saliency alone prove causality.
- Serving a converted model without numerical and task-level parity tests.
- Letting a VLM answer from prior knowledge when the task requires image grounding.
- Retaining sensitive visual data or metadata without a documented need.

## 15. Rapid interview questions

**Why use transfer learning?** It reuses representations learned from large datasets, reducing task-specific data and training needs; validate domain shift and preprocessing compatibility.

**CNN or ViT?** Compare inductive bias, pretraining, data, resolution, compute, latency, robustness, and target evidence. Neither family wins universally.

**Why can image-level random splitting leak?** Multiple files can show the same subject, event, device, scene, or adjacent video frames, letting the model memorize identity or background.

**What does IoU measure?** Spatial overlap divided by union. It says nothing about class correctness, confidence calibration, or operating cost.

**Why can high AP still fail users?** The evaluation may miss the deployment slice, object size, threshold, latency, annotation policy, or downstream action that matters.

**How do you evaluate a VLM?** Use a task-specific visual-evidence rubric, grounding and hallucination checks, slice/robustness tests, deterministic identities, human calibration, and serving evidence.

## 16. Design case: visual inspection service

For a factory defect-inspection system, cover:

1. defect taxonomy, part/line/camera identity, action, review and cost matrix;
2. collection and annotation across products, shifts, sites and rare defects;
3. grouped/temporal split plus new-line external holdout;
4. simple rule and transfer-learning baselines;
5. classification versus localization requirement and threshold policy;
6. edge/cloud architecture, latency, offline fallback and versioned preprocessing;
7. calibration, abstention and reviewer workflow;
8. slice metrics, false-negative audit, capacity and cost;
9. drift/relabel/retraining triggers, shadow release and rollback;
10. privacy, retention, access, incident and deletion controls.

## 17. Interview checklist

- [ ] I can distinguish classification, detection, segmentation, keypoints, retrieval, and VLM tasks.
- [ ] I can design identity-safe visual splits and an annotation audit.
- [ ] I can explain CNN, ViT, transfer learning, augmentation, IoU, Dice, AP, and calibration.
- [ ] I can evaluate small objects, empty masks, slices, robustness, and human-review load.
- [ ] I can design preprocessing parity, serving, monitoring, security, and rollback.
- [ ] I can explain why fluent multimodal output is not the same as grounded visual evidence.

## References

- PyTorch, [Transfer Learning for Computer Vision Tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- TorchVision, [Models and pre-trained weights](https://docs.pytorch.org/vision/stable/models.html)
- TorchVision, [Object detection finetuning tutorial](https://docs.pytorch.org/tutorials/intermediate/torchvision_tutorial.html)
- Hugging Face Transformers, [Image-text-to-text](https://huggingface.co/docs/transformers/tasks/image_text_to_text)

Model families, APIs, and benchmark conventions evolve. Pin the exact model, weights, preprocessing, evaluation protocol, and runtime used for every claim.
