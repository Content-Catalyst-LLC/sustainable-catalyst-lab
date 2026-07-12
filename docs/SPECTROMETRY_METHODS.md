# Spectrometry Studio Methods and Boundaries

Spectrometry Studio operates on generic numeric x–y records and supplies transparent transformations. It does not claim vendor-file compatibility or instrument qualification.

## Processing operations

- Endpoint linear baseline subtraction.
- Rolling-minimum baseline estimate followed by smoothing.
- Moving-mean and moving-median smoothing.
- Maximum, area, and min–max normalization.
- Finite-difference derivatives.
- Transmittance/absorbance conversion.
- Trapezoidal integration.
- Local-maxima peak detection with threshold, minimum distance, and prominence controls.
- Linear-interpolation FWHM estimates.
- Signal centroid and first-difference noise estimate.
- Ordinary least-squares calibration, R², residual standard deviation, LOD, LOQ, and unknown estimation.

## Review requirements

Users must document instrument, detector, optical path, acquisition settings, blank, reference material, calibration range, replicate design, matrix, preprocessing parameters, rejected data, and uncertainty. Peak identity is not inferred automatically. Generated values require review against the relevant analytical method and instrument software.
