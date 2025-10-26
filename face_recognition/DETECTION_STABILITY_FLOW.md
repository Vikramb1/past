# Detection Stability Flow Diagram

## Visual Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Face Detected in Frame                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │ Check: Already tracked?     │
         │ (existing person_XXX)       │
         └────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
       YES                 NO
        │                   │
        ▼                   ▼
┌───────────────┐    ┌─────────────────────────────┐
│ Update Stats  │    │ NEW: Check if candidate?    │
│ Return ID     │    │ (similarity check)          │
│ ✅ Done       │    └────────┬────────────────────┘
└───────────────┘             │
                    ┌─────────┴─────────┐
                    │                   │
                  MATCH               NEW
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐   ┌──────────────────┐
        │ Increment count   │   │ Create candidate │
        │ count = N + 1     │   │ count = 1        │
        └────────┬──────────┘   └────────┬─────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ Check: count >= 5?     │
                └────────┬───────────────┘
                         │
               ┌─────────┴─────────┐
               │                   │
              NO                  YES
               │                   │
               ▼                   ▼
     ┌──────────────────┐   ┌─────────────────────┐
     │ Return None      │   │ ✅ Stability reached│
     │ (not saved yet)  │   │ Delete candidate    │
     └──────────────────┘   └──────────┬──────────┘
                                       │
                                       ▼
                          ┌────────────────────────┐
                          │ Quality Check enabled? │
                          └────────┬───────────────┘
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                        YES                 NO
                         │                   │
                         ▼                   ▼
            ┌──────────────────────┐  ┌───────────────┐
            │ Collect 5 frames     │  │ Save          │
            │ Select best quality  │  │ immediately   │
            │ Save best frame      │  └───────┬───────┘
            └──────────┬───────────┘          │
                       │                      │
                       └──────────┬───────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │ Upload to        │
                        │ Supabase         │
                        └─────────┬────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │ Add to registry  │
                        │ Return person_ID │
                        │ ✅ Complete      │
                        └──────────────────┘
```

## Timeline Example (30 FPS)

```
Time:     0ms    33ms   66ms   100ms  133ms  166ms  200ms  233ms  266ms  300ms
Frame:    1      2      3      4      5      6      7      8      9      10
          │      │      │      │      │      │      │      │      │      │
          ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
Stage 1:  New    +1     +1     +1     ✅     Q1     Q2     Q3     Q4     Q5
         (1/5)  (2/5)  (3/5)  (4/5)  (5/5)
                                       │
                                  STABILITY
                                   REACHED
                                       │
Stage 2:                               └─────────────────────────────────►
                                              Quality Collection
                                              (if enabled)
                                                                           │
                                                                          SAVE
                                                                        (person_027)
```

## State Transitions

### Detection Candidate Lifecycle

```
[Non-existent] 
      │
      │ First detection
      ▼
[Candidate: count=1] ──► [Candidate: count=2] ──► ... ──► [Candidate: count=5]
      │                        │                                    │
      │ Not seen for 2s        │ Not seen for 2s                  │ Stability reached
      ▼                        ▼                                    ▼
[Cleaned up]           [Cleaned up]                        [Quality/Save Stage]
                                                                    │
                                                                    ▼
                                                            [Tracked Person]
                                                            (person_XXX in registry)
```

## Code Flow

### Main Loop (face_engine.py)
```python
for face_encoding, face_location in detected_faces:
    person_id, is_new = face_tracker.track_face(
        frame, 
        face_encoding, 
        face_location
    )
    # person_id will be None during stability/quality collection
    # person_id will be "person_XXX" once saved or for existing people
```

### Track Face Method (face_tracker.py)
```python
def track_face(encoding, ...):
    # Step 1: Check existing people
    is_duplicate, existing_id = _is_duplicate(encoding)
    if is_duplicate:
        return existing_id, False  # Recognized person
    
    # Step 2: Check/create candidate
    candidate_id = _check_detection_candidate(encoding)
    if candidate_id is None:
        candidate_id = _add_detection_candidate(encoding)
        return None, False  # Frame 1/5
    
    # Step 3: Increment and check threshold
    self.detection_candidates[candidate_id]['count'] += 1
    if count < DETECTION_STABILITY_FRAMES:
        return None, False  # Frame 2-4/5
    
    # Step 4: Stability reached, proceed to save
    del self.detection_candidates[candidate_id]
    return _handle_quality_or_save(...)  # Frame 5/5
```

## Performance Characteristics

### Memory Usage Over Time

```
Memory
  │
  │     Candidate      Candidate
  │       added        removed
  │         ▼             ▼
  │        ┌─────────────┐
  │        │             │
  │ ───────┘             └──────────  (Baseline)
  │
  └───────────────────────────────►  Time
     0s    1s    2s    3s    4s    5s

Typical: 1-5 candidates active at once (~5-25 KB)
Peak: 10-20 candidates in crowded scene (~10-100 KB)
```

### CPU Load

```
CPU %
  │
  │   Quality          Quality
  │   encoding         selection
  │      ▼                ▼
  │     ┌┐              ┌┐
  │     ││              ││
  │ ────┘└──────────────┘└─────  (Low baseline)
  │
  └──────────────────────────────►  Time
    Stability checking = negligible CPU
    (just face_distance calculations)
```

## Comparison: Before vs After

### Before (No Stability Check)
```
Frame 1: Detect → Start quality collection
Frame 2-6: Collect quality frames
Frame 6: Save face

Risk: False positive on Frame 1 → saves bad face
```

### After (With Stability Check)
```
Frame 1-5: Detect → Check stability (count 1→5)
Frame 5: Stability reached → Start quality collection
Frame 6-10: Collect quality frames
Frame 10: Save face

Benefit: 5 consecutive detections required → filters false positives
```

## Configuration Impact

| Setting | Total Frames | Total Time @ 30fps | Use Case |
|---------|--------------|-------------------|----------|
| `DETECTION_STABILITY_FRAMES = 1` | 6 frames | ~200ms | Fast detection, accept some false positives |
| `DETECTION_STABILITY_FRAMES = 3` | 8 frames | ~267ms | Balanced approach |
| `DETECTION_STABILITY_FRAMES = 5` (default) | 10 frames | ~333ms | Good reliability |
| `DETECTION_STABILITY_FRAMES = 10` | 15 frames | ~500ms | Maximum reliability |

*Assumes `QUALITY_FRAMES_TO_COLLECT = 5`*

