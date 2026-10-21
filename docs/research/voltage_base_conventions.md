# ATP voltage-base conventions

The validated 138 kV ATP cases declare two peak-voltage bases:

- Phase-to-ground node voltage: 112,677 V.
- Phase-to-phase branch voltage: 195,161 V.

`src.services.preprocessing` extracts only phase-to-ground node maxima.
Consequently, every generated analysis package uses 112,677 V. The dataset
manifest separately validates the 195,161 V phase-to-phase declarations in the
ATP/LIS sources, preventing the two voltage conventions from being confused.

Phase-to-phase branch maxima require a separate extraction and analysis path;
they must not be combined with phase-to-ground observations in P.U. statistics.
