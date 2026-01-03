# beam/shift

*Transmission electron microscopy notes, methods, and thinking.*

---

## Imaging Conditions

*Instrument:* 200 kV TEM  
*Source:* LaB₆  
*Mode:* Bright-field TEM  
*Detector:* CCD

> Minor astigmatism observed during initial alignment. Contrast optimized after condenser aperture adjustment.

---

## Links and Navigation

This site is organized as a small, linked knowledge base. For example:

- See the [[guides/intro.md]] for orientation
- Jump directly to the [API reference](reference/api.md)
- Inline links like [Material MkDocs](https://squidfunk.github.io/mkdocs-material/) should read clearly

---

## Code / Readouts

Inline values like `200 kV` or `1.2 Å` should feel like instrument annotations.

```text
Accelerating voltage: 200 kV
Magnification:        120,000×
Camera length:        800 mm
Spot size:            3
```

```python
# Example analysis stub
import numpy as np

fft = np.fft.fft2(image)
power = np.abs(fft)**2
```

---

## Figures

![Placeholder micrograph](https://via.placeholder.com/800x400.png?text=Micrograph+Placeholder)
*Figure 1 — Bright-field image showing lattice fringes at high magnification.*

---

## Tables (Acquisition Parameters)

| Parameter            | Value        | Notes              |
|----------------------|--------------|--------------------|
| Accelerating Voltage | 200 kV       | Standard operation |
| Objective Aperture   | 40 µm        | Inserted           |
| Defocus              | −1.5 µm      | Slight underfocus  |
| Exposure Time        | 0.5 s        | CCD limited        |

---

## Callouts

!!! note
    This is a general observation recorded during routine operation.

!!! warning
    Misalignment at high magnification can lead to misleading contrast.

---

## Horizontal Rule and Sectioning

Text above and below horizontal rules should feel like clearly separated panels or sections in an instrument interface.

---

## Emphasis and Annotation

Regular paragraph text should be easy to read over long stretches.

*Italic text* can be used for conditions, metadata, or interpretive notes.

Small annotations may appear as <small>secondary analytical comments</small>.

---

## Closing

This page exists purely to preview typography, color, spacing, and layout.  
Replace it with real content once the visual language feels right.