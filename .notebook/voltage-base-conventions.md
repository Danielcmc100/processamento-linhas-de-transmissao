# ATP voltage-base conventions

- Phase-to-ground node maxima use 112677 V; see
  `src/services/preprocessing.py:extract_maxima_dataframe()`.
- Phase-to-phase branch statistics use 195161 V and are not extracted by the
  current analysis pipeline.
- `src/services/dataset_manifest.py:build_dataset_manifest()` validates both
  declarations before final evidence generation.
