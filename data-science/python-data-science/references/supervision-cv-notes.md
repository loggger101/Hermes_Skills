---
description: "roboflow supervision 0.30.7 (computer-vision utilities): Detections filtering/NMS, zones, line counting, annotators, run live on synthetic arrays; OpenCV optional, ByteTrack deprecated, silent empty result on bad input"
source_repo: roboflow/supervision (MIT)
tested_version: supervision 0.30.7 pip --target on Windows py3.14 (343 MB with numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2, av 19); synthetic detections and blank images only, no model run
verified_date: "2026-10-05"
---

# supervision: model-agnostic detection utilities

Wraps the output of any detector (Ultralytics, Transformers, Inference, ...) in a `sv.Detections` object and provides filtering, NMS, zones, line counting, tracking and annotators. MIT; 0.30.7 (2026-10-04), Python `>=3.10` (classifiers to 3.14).
It is a post-processing layer: it does not run models itself.

```python
import numpy as np, supervision as sv
det = sv.Detections(xyxy=np.array([[10,10,50,50],[12,11,52,49],[100,100,160,180],[200,20,230,70]], float),
                    confidence=np.array([0.9, 0.6, 0.8, 0.3]), class_id=np.array([0, 0, 1, 1]))
```

## Verified on synthetic data

| Operation | Result |
|---|---|
| `len(det)`, `det.area` | 4; `[1600, 1520, 4800, 1500]` |
| Boolean mask filter `det[det.confidence > 0.5]` | 3 detections; class filter `det[det.class_id == 1]` returns the two class-1 boxes |
| `det.with_nms(threshold=0.5)` | 3 left: the overlapping 0.6 box was suppressed, confidences `[0.9, 0.8, 0.3]` |
| `sv.PolygonZone(polygon).trigger(det)` for a 120x120 square | `[True, True, False, False]`, `zone.current_count == 2` |
| `sv.LineZone` on y = 80 with one tracked object moving from y = 60 to y = 100 | `in_count = 0`, `out_count = 1`: crossing downward counted as "out" (direction depends on the line's start/end order; verify with a known clip) |
| `sv.BoxAnnotator` + `sv.LabelAnnotator` on a 240x320 black image | 3,398 pixels changed |
| `sv.Detections.empty().xyxy.shape` | `(0, 4)` |
| `sv.Detections(xyxy=<4 boxes>, confidence=<1 value>)` | `ValueError: confidence must be a 1D np.ndarray with shape (4,), but got shape (1,)` (length mismatches are caught) |

## Surprises and traps

- **OpenCV is optional.** Importing printed `UserWarning: OpenCV (opencv-python) is not installed; supervision is using its pure NumPy fallback backend instead. Some operations may be slower or behave slightly differently.` Annotators still worked. For production speed and exact drawing behaviour install `opencv-python`; for a pinned, reproducible pipeline decide on one backend and record it.
- **`sv.ByteTrack` is deprecated**: `FutureWarning: The ByteTrack was deprecated since v0.28.0. It will be removed in v0.31.0.` (the current version is 0.30.7, so removal is one minor away). It kept one id (`[1]` on each of 6 frames) for a steadily moving box. Move tracking to the replacement the project points to (its separate `trackers` package) before upgrading to 0.31.
- **Bad input can yield an empty result instead of an error.** `sv.Detections.from_ultralytics(object())` returned an empty `Detections` (shape `(0, 4)`) with no exception. In a pipeline this looks like "nothing detected"; assert that the adapter received the expected result type and count frames with zero detections.
- Annotating a 2-D (grayscale) `uint8` array did not raise; it returned an array of the same shape. Pass 3-channel BGR frames to get coloured boxes.
- The install is heavy (343 MB here) because it pulls scipy, matplotlib and PyAV; fine for analysis boxes, avoid in minimal containers.

## Practical rules

- Convert model output with the matching adapter (`from_ultralytics`, `from_inference`, `from_transformers`), then filter by confidence **before** NMS and by class after.
- Choose zone polygons and line endpoints in the same pixel space as the frames you annotate (resize first or scale the polygon).
- Test counting logic on a short clip with a known answer; the in/out direction convention is easy to invert.
- Record versions: detector weights, supervision, and the OpenCV backend, since annotations and tracker behaviour change between releases.
