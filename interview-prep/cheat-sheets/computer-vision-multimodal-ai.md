---
layout: "week"
status: "approved"
version: "1.0.0"
last_reviewed: "2026-11-11"
imported_on: "2026-11-13"
source_repository: "kogantisasank831-ux/transformer-explainer"
source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"
source_path: "AI_Data_Science_Interview_Cheat_Sheets/Batch_9_Specialized_Modeling/33_Computer_Vision_Multimodal_AI_Interview_Cheat_Sheet.md"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Computer vision and multimodal AI interview cheat sheet"
description: "Interview revision for computer vision, video, OCR, multimodal models, evaluation, deployment, privacy, and safety."
summary: "Revise visual task contracts, CNNs, ViTs, detection and segmentation, multimodal systems, evaluation, deployment, privacy, and safety."
permalink: "/interview-prep/cheat-sheets/computer-vision-multimodal-ai/"
kicker_primary: "Interview revision"
kicker_secondary: "Batch 9 · Computer vision"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---

**Target roles:** AI Engineer, ML Engineer, Applied Scientist, Senior Data Scientist, Computer Vision Engineer, Data Science Lead<br>
**Use:** image/video modeling, vision-language systems, evaluation, deployment, system-design, and project deep-dive interviews<br>
**Interview rule:** define the visual decision, annotation unit, deployment environment, latency/error cost, and evaluation slice before naming an architecture. A larger pretrained model cannot repair ambiguous labels, train-test leakage, invalid augmentation, or unsupported camera conditions.

## 1. Thirty-second revision

- Computer vision tasks include classification, localization, object detection, semantic/instance/panoptic segmentation, keypoints, tracking, OCR, depth, retrieval, captioning, visual question answering, and image-text generation.
- Image tensors usually use `(batch, channels, height, width)` in PyTorch; model preprocessing must match the exact pretrained weights.
- Convolutions share local filters and encode translation-related inductive bias. Receptive field grows with depth, kernel size, stride, dilation, and pooling.
- Vision Transformers split images into patches, embed them as tokens, add positional information, and use attention. Their compute and data needs differ from CNNs.
- Transfer learning normally beats training from scratch when labeled domain data is limited, but source-domain shortcuts and preprocessing mismatch can transfer too.
- Detection predicts classes and boxes; segmentation predicts pixels/masks. IoU, NMS, AP/mAP, Dice, and boundary metrics answer different questions.
- Split by entity, site, patient, video, product, or capture session—not random frames—when adjacent samples leak identity and context.
- Augmentations must preserve labels and geometry. Boxes, masks, keypoints, and images must receive the same spatial transform.
- A dual encoder such as CLIP maps images and text into a shared retrieval space; a vision-language generator uses visual features plus a language model to produce open-ended text.
- Multimodal outputs require task-grounded evaluation: retrieval, localization, OCR, counting, temporal understanding, hallucination, safety, calibration, and abstention.
- Production quality depends on decode/preprocess, resize policy, batch shape, model precision, post-processing, camera drift, throughput, tail latency, and monitoring.
- Treat images/video as sensitive data: faces, documents, screens, location, health information, and metadata create privacy and security risks.

## 2. Frame the visual decision

Write a contract:

> Given **visual input V** captured under **conditions C**, predict or generate **output Y** for **action A** within **latency/cost budget B**, while meeting **quality, safety, privacy, and slice constraints Q**.

Clarify:

- input: still image, document, medical scan, video stream, paired text, or multiple views;
- unit: image, frame, clip, object, pixel, page, study, device, or event;
- action: alert, rank, inspect, count, navigate, summarize, answer, or automate;
- annotation: image label, box, polygon/mask, keypoint, track, caption, or preference;
- capture conditions: camera, lens, resolution, compression, lighting, viewpoint, frame rate, geography, and season;
- deployment: cloud, mobile, browser, vehicle, factory edge, or offline batch;
- error asymmetry: missed defect versus false reject, missed pedestrian versus false alarm;
- abstention and human review;
- intended and excluded populations/environments.

Before deep learning, establish a rule/template/OCR/classical feature baseline where appropriate.

## 3. Data and tensor fundamentals

### Shapes and pixels

For a batch `X ∈ R^(B×C×H×W)`:

- `B`: batch size;
- `C`: channels, often 1, 3, or more spectral bands;
- `H, W`: spatial dimensions.

Libraries may use channel-last `(B, H, W, C)`. Explicitly transpose once at the boundary. Image values may be integers `[0,255]` or normalized floats. Record color space, channel order, alpha handling, EXIF rotation, and resize/crop rule.

### Resize policies

- fixed resize can distort aspect ratio;
- center/random crop discards border information;
- letterboxing preserves aspect ratio but adds padding;
- multi-scale training/inference changes compute and behavior;
- tiling helps high-resolution inspection but creates boundary/duplicate issues.

Pretrained weights usually define expected interpolation, crop size, mean, and standard deviation. Use the weight-specific transform rather than copying an unrelated recipe.

### Data quality checks

- unreadable/truncated files and decode differences;
- duplicate/near-duplicate images;
- conflicting labels or missing objects;
- boxes outside image bounds, negative area, invalid polygons;
- masks with unexpected classes;
- keypoints inconsistent with visibility;
- video timestamps/frame-order errors;
- overlays/watermarks that leak the label;
- metadata or folder names that leak outcome;
- imbalance by site/device/class/context.

Visualize samples after every transform. Numeric schema checks alone will not reveal a horizontally flipped label or a box transformed independently of its image.

## 4. Convolutional neural networks

For input feature map and kernel, a convolution computes a weighted local neighborhood with shared parameters. Important terms:

- kernel/filter size;
- stride;
- padding;
- dilation;
- input/output channels;
- feature-map size;
- receptive field.

For one spatial dimension:

`output = floor((input + 2×padding − dilation×(kernel−1) − 1) / stride + 1)`

### Why CNNs work

- local connectivity reflects nearby pixel structure;
- weight sharing reduces parameters;
- hierarchical layers learn edges, textures, parts, and task features;
- pooling/stride produces spatial tolerance and lower resolution.

### Architecture ideas

- residual connections support gradient flow and identity-like paths;
- depthwise separable convolutions reduce compute;
- feature pyramids combine high-resolution detail with semantic depth;
- encoder-decoder/skip connections support dense prediction;
- normalization and activation choices affect optimization and batch behavior.

CNNs are not perfectly translation invariant. Padding, stride, pooling, boundary effects, and data can change predictions under shifts.

## 5. Vision Transformers and modern backbones

A Vision Transformer commonly:

1. divides an image into fixed-size patches;
2. linearly embeds each patch;
3. adds positional information and optionally a class token;
4. applies transformer blocks;
5. uses a task head or multi-scale decoder.

If image size is `H×W` and patch size `P×P`, the token count is roughly `HW/P²` plus special tokens. Full attention cost grows quadratically with tokens, so high resolution is expensive.

Comparison:

| Dimension | CNN | Vision Transformer |
|---|---|---|
| inductive bias | strong locality/weight sharing | weaker locality unless designed in |
| long-range interaction | grows through depth | direct attention interaction |
| data efficiency | often strong on smaller data | benefits greatly from pretraining/augmentation |
| resolution cost | convolutional spatial cost | token and attention cost can dominate |
| feature hierarchy | natural multi-scale maps | may require hierarchical/window designs |

Model choice should follow accuracy, data, resolution, latency, memory, hardware, and transfer evidence—not fashion.

## 6. Core task families

### Classification and multilabel classification

- single-label softmax assumes mutually exclusive classes;
- multilabel sigmoid predicts independent label scores, though labels may be correlated;
- hierarchical labels need taxonomy-aware evaluation;
- open-set deployment needs unknown/OOD behavior.

Measure per-class precision/recall, macro/micro averages, calibration, and slices—not top-1 accuracy alone.

### Detection

Output class, confidence, and box. Main families:

- two-stage: propose regions, then classify/refine;
- one-stage: dense or anchor-free predictions;
- set-prediction transformers: predict a fixed set and match predictions to targets.

Post-processing may include confidence thresholding, non-maximum suppression, class-aware rules, clipping, and scaling boxes back to original coordinates.

### Segmentation

- semantic: class per pixel;
- instance: separate mask per object;
- panoptic: combines thing instances and stuff regions.

Use IoU/Jaccard, Dice/F1, class-specific metrics, instance AP, panoptic quality, and boundary/size slices as relevant. Pixel accuracy hides rare classes.

### Keypoints, pose, tracking, depth, and optical flow

- keypoints: location plus visibility; evaluate scale-normalized error or task metrics;
- tracking: detection plus identity association over time; identity switches matter;
- depth: absolute/relative scale and valid-region masks matter;
- optical flow: vector error and occlusion boundaries matter.

### OCR and document understanding

OCR includes text detection, recognition, reading order, layout, tables, and key-value extraction. Evaluate character/word error, field exact match, structure, multilingual text, rotation, handwriting, low resolution, and document-level correctness.

## 7. Detection geometry and evaluation

For boxes `A` and `B`:

`IoU = area(A ∩ B) / area(A ∪ B)`

IoU threshold determines whether a prediction matches a target. Matching must handle class, duplicates, difficult/ignored regions, and one-to-one assignment.

### Precision-recall and AP

Sort detections by confidence, mark true/false positives under the matching rule, compute precision-recall, and integrate/interpolate according to the benchmark definition. Mean AP averages across classes and possibly IoU thresholds.

Always state:

- dataset and split;
- IoU thresholds;
- class averaging;
- size/max-detection rules;
- score threshold;
- evaluation implementation/version.

AP is a ranking summary, not an operating-point decision. Production needs recall/precision at the chosen threshold and error cost.

### Non-maximum suppression

NMS keeps high-score boxes and removes strongly overlapping lower-score boxes. It can suppress nearby true objects in crowds. Soft-NMS, class-aware thresholds, or set-prediction architectures may help. Tune on representative density and object-size slices.

## 8. Minimal dependency-free example: box IoU

```python
from __future__ import annotations

from typing import Sequence


def box_iou(box_a: Sequence[float], box_b: Sequence[float]) -> float:
    """Compute IoU for half-open boxes [x1, y1, x2, y2]."""
    if len(box_a) != 4 or len(box_b) != 4:
        raise ValueError("each box must contain four coordinates")
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    if ax2 <= ax1 or ay2 <= ay1 or bx2 <= bx1 or by2 <= by1:
        raise ValueError("boxes must have positive area")

    intersection_width = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    intersection_height = max(0.0, min(ay2, by2) - max(ay1, by1))
    intersection = intersection_width * intersection_height
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - intersection
    return intersection / union


assert box_iou([0, 0, 2, 2], [0, 0, 2, 2]) == 1.0
assert box_iou([0, 0, 1, 1], [2, 2, 3, 3]) == 0.0
assert abs(box_iou([0, 0, 2, 2], [1, 1, 3, 3]) - (1 / 7)) < 1e-12
```

Production evaluation must also define coordinate convention, matching, ignored targets, class handling, and numerical tolerance.

## 9. Training and transfer learning

### Transfer choices

- frozen backbone plus new head: fast baseline, limited adaptation;
- partial unfreezing: adapt upper layers;
- full fine-tuning: highest flexibility and compute/overfit risk;
- parameter-efficient adapters: useful for large multimodal backbones where supported;
- linear probe: measures representation usefulness but not full potential.

Use differential learning rates where justified. Preserve a true holdout and compare against frozen/simple baselines.

### Augmentation

Potential transforms:

- crop/resize/flip/rotate;
- color jitter, blur, noise, compression;
- cutout, MixUp, CutMix;
- copy-paste for detection/segmentation;
- temporal sampling for video.

Validate label preservation. Flipping text, traffic direction, laterality, or medical anatomy may change the label. Do not augment validation/test data except a predeclared test-time procedure.

### Losses and imbalance

- cross-entropy/focal loss for classification;
- box regression and classification losses for detection;
- cross-entropy, Dice, focal/Tversky-style losses for segmentation;
- contrastive losses for paired modalities.

Loss weighting changes optimization, not necessarily calibrated probabilities. Evaluate rare/small classes and threshold behavior separately.

## 10. Multimodal architectures

### Early, late, and intermediate fusion

- early fusion combines raw/low-level features;
- intermediate fusion joins learned representations;
- late fusion combines independent model outputs.

The right fusion depends on alignment, missing modalities, compute, and whether cross-modal interaction is needed.

### Dual encoders

An image encoder and text encoder map paired inputs to a shared embedding space. Contrastive training raises similarity for true pairs and lowers it for mismatched pairs. Good for:

- image-text retrieval;
- zero-shot classification using text prompts;
- semantic search and deduplication.

Limitations include prompt sensitivity, weak fine-grained grounding, dataset bias, and similarity that does not guarantee factual description.

### Vision-language generators

A visual encoder produces visual tokens/features; an adapter/projector and language model condition text generation. Fusion can use concatenated tokens, cross-attention, resampling, or other connectors.

Tasks include captioning, VQA, document QA, chart understanding, grounded description, image-to-code, and multimodal agents.

Key distinctions:

- image-to-text specialist versus general instruction/chat model;
- base/pretrained versus instruction-tuned checkpoint;
- single image versus multi-image/video context;
- global understanding versus box/mask grounding;
- perception error versus language reasoning/hallucination.

Use the exact processor/chat template expected by the checkpoint. Image resizing, placeholder tokens, frame sampling, and prompt formatting are part of the model contract.

### Video

Video introduces temporal sampling, motion, audio, long context, repeated frames, and event boundaries. Uniform frame sampling can miss brief events; dense sampling increases cost. Evaluate temporal order, action localization, long-range consistency, and latency.

## 11. Evaluation beyond one benchmark

Build a matrix:

| Axis | Example slices |
|---|---|
| visual quality | blur, darkness, glare, compression, occlusion |
| geometry | small/large objects, crowding, viewpoint, crop edge |
| capture domain | site, device, camera generation, geography, season |
| people | skin tone, age, mobility aids, clothing, intersectional groups |
| language/text | script, font, handwriting, multilingual, rotated text |
| multimodal | missing image, contradictory text, multiple images, long video |
| operations | latency, memory, batch size, thermal/edge constraints |

For generative/VLM systems:

- task accuracy and rubric-based human evaluation;
- grounded object/region evidence;
- hallucinated objects/attributes/text;
- OCR exactness and counting;
- answer refusal/abstention;
- consistency under irrelevant prompt/image changes;
- adversarial instructions embedded in images/documents;
- safety and privacy leakage;
- citation/region traceability where promised.

LLM-as-judge can scale review but needs calibration against humans, blind randomized comparisons, judge-version pinning, order-bias checks, and disagreement analysis.

## 12. Data splits and leakage

High-risk leakage patterns:

- adjacent video frames across train/test;
- same patient/product/object/site captured multiple times;
- near duplicates or crops of the same image;
- synthetic variants of one source crossing splits;
- label-bearing filename, watermark, background, device, or capture protocol;
- post-event images used to predict an earlier event.

Use group/time/site splits matching deployment. Hold out a camera, region, facility, or product family when claiming generalization there. Keep pretraining overlap and benchmark contamination as explicit limitations.

## 13. Production and optimization

Pipeline:

`ingest/decode → validate → resize/normalize → model → post-process → business rules → action/logging`

Measure each stage:

- decode and data-transfer latency;
- preprocessing CPU/GPU utilization;
- batch formation and shape padding;
- model latency/throughput/memory;
- post-processing/NMS;
- end-to-end p50/p95/p99 and failure rate.

Optimization options:

- smaller backbone/resolution;
- quantization or mixed precision;
- pruning/distillation;
- compilation/export to supported runtime;
- dynamic batching;
- tiling only when required;
- cascades: cheap detector then expensive verifier;
- edge/cloud split with privacy and connectivity controls.

Re-evaluate accuracy and slices for every exported/quantized artifact. Runtime operator support and preprocessing parity are part of correctness.

### Monitoring

- input schema/decode failures;
- resolution/aspect/color/brightness distributions;
- embedding or model-score drift;
- class/object/count and confidence distributions;
- human-review disagreement and delayed outcomes;
- camera/site slice performance;
- latency, memory, thermal throttling, queueing;
- sample-based visual audits with privacy controls.

## 14. Safety, privacy, and security

- minimize collection and retention;
- strip unnecessary metadata;
- protect faces, license plates, documents, screens, and health imagery;
- enforce access and deletion throughout derived datasets/embeddings;
- review biometric and surveillance use with responsible owners;
- test printed/embedded prompt injection for multimodal agents;
- validate file type, size, decompression, parser, and media-decoder boundaries;
- prevent untrusted model output from directly controlling tools;
- document synthetic-media and generation risks;
- provide appeal/human review for consequential decisions.

Adversarial patches, distribution shift, and camera tampering require layered controls; a single robustness score is not a security guarantee.

## 15. Library map

| Tool | Best fit | Verify before use |
|---|---|---|
| torchvision | PyTorch datasets, transforms, models, detection/segmentation ops | exact weight transforms and API stability |
| timm | broad image backbones and pretrained weights | checkpoint preprocessing, license, export support |
| OpenCV | image/video processing and classical CV | color/coordinate conventions and codec behavior |
| Albumentations | synchronized augmentation for images/boxes/masks | label preservation and parameter/version semantics |
| Hugging Face Transformers | vision and multimodal processors/models | checkpoint class, processor, chat template, remote-code trust |
| MMDetection/MMSegmentation | configurable detection/segmentation research stacks | config/version compatibility and deployment path |
| Ultralytics | end-to-end detection/segmentation/pose workflows | license, model/version, benchmark and export target |
| ONNX Runtime/TensorRT/Core ML/TFLite | deployment runtimes | supported ops, precision parity, hardware benchmark |

A model zoo is a starting point, not evidence for the user's domain.

## 16. Rapid interview questions

**Why use transfer learning?**<br>
Pretraining supplies useful visual features and optimization initialization when domain labels are limited. Validate domain shift and preprocessing.

**Why not random-split video frames?**<br>
Adjacent frames share nearly identical content and identity, producing severe leakage.

**What is receptive field?**<br>
The input region that can affect an activation. The theoretical and effective receptive fields can differ.

**IoU versus Dice?**<br>
Both measure overlap; Dice is `2×intersection/(sum of areas)` and is monotonically related to IoU for one mask pair, but benchmark aggregation can differ.

**Why can mAP improve while production worsens?**<br>
AP averages rankings/thresholds and classes; the selected operating point, latency, small critical objects, or site shift may worsen.

**CNN versus ViT?**<br>
Compare inductive bias, data/pretraining, resolution, latency/memory, and evidence on the target workload.

**What does CLIP-style training learn?**<br>
Aligned image/text embeddings through contrastive objectives; it is useful for retrieval/zero-shot transfer but does not guarantee grounded generation.

**How do you evaluate a VLM?**<br>
Use task-specific correctness plus grounding, hallucination, OCR/counting, robustness, safety, slices, latency/cost, and human review.

**What is NMS failure in crowds?**<br>
Overlapping true objects may suppress one another; tune or use alternative post-processing/modeling and evaluate density slices.

**How do you handle unseen camera conditions?**<br>
Collect representative validation, use safe augmentations/domain adaptation if justified, monitor input shift, abstain/fallback, and stage rollout.

## 17. Lead-level case: visual defect inspection

Structure the answer:

1. Define defect taxonomy, severity, product/unit, inspection stage, action, line speed, and false-reject versus miss cost.
2. Audit cameras, lighting, fixtures, resolution, synchronization, operator labels, repair feedback, and site variation.
3. Split by production lot/time/line/site to prevent near-duplicate and context leakage.
4. Establish rule/classical CV and pretrained classification/detection/segmentation baselines.
5. Choose annotation granularity based on required action and explainability; measure reviewer agreement.
6. Evaluate recall at the reject/review capacity, per-defect and small-object performance, calibration, latency, and site slices.
7. Test lighting, blur, contamination, camera shift, unseen product variants, and adversarial/accidental occlusion.
8. Design edge inference with deterministic preprocessing, artifact signing/versioning, queue backpressure, safe manual inspection fallback, and audit images.
9. Shadow and canary by line; verify exported precision/runtime parity; monitor drift and delayed quality outcomes.
10. Use active learning only with controlled sampling and label governance; retain rollback and change review.

The business metric is escaped defects and inspection cost under safety/quality constraints—not offline mAP alone.

## 18. Final checklist

- [ ] I define input, output, annotation unit, action, capture conditions, and latency/error cost.
- [ ] I state tensor shapes, color/coordinate conventions, and weight-specific preprocessing.
- [ ] I can explain CNNs, residuals, receptive field, ViT patches, and attention cost.
- [ ] I distinguish classification, detection, segmentation, keypoints, tracking, OCR, and video tasks.
- [ ] I can explain IoU, AP/mAP, Dice, NMS, calibration, and operating thresholds.
- [ ] I prevent entity/site/video-frame and near-duplicate leakage.
- [ ] I validate augmentations for images, boxes, masks, keypoints, and semantics.
- [ ] I distinguish dual-encoder retrieval from vision-language generation.
- [ ] I evaluate grounding, hallucination, OCR/counting, robustness, safety, slices, and operations.
- [ ] I design preprocessing parity, export validation, monitoring, fallback, and rollback.

## 19. Primary references

- [Torchvision documentation](https://docs.pytorch.org/vision/stable/)
- [Torchvision models and pretrained weights](https://docs.pytorch.org/vision/stable/models.html)
- [Torchvision detection and segmentation operators](https://docs.pytorch.org/vision/stable/ops.html)
- [PyTorch transfer-learning tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- [PyTorch object-detection fine-tuning tutorial](https://docs.pytorch.org/tutorials/intermediate/torchvision_tutorial.html)
- [Hugging Face multimodal chat templates](https://huggingface.co/docs/transformers/en/chat_templating_multimodal)
- [Hugging Face image-text-to-text task guide](https://huggingface.co/docs/transformers/tasks/image_text_to_text)
- [He et al., Deep Residual Learning for Image Recognition](https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html)
- [Dosovitskiy et al., An Image Is Worth 16x16 Words](https://research.google/pubs/an-image-is-worth-16x16-words-transformers-for-image-recognition-at-scale/)
- [Carion et al., End-to-End Object Detection with Transformers](https://ai.meta.com/research/publications/end-to-end-object-detection-with-transformers/)
- [Radford et al., Learning Transferable Visual Models From Natural Language Supervision](https://proceedings.mlr.press/v139/radford21a.html)
- [Kirillov et al., Segment Anything](https://openaccess.thecvf.com/content/ICCV2023/html/Kirillov_Segment_Anything_ICCV_2023_paper.html)
