Phase 8.2 Real-World Testing
============================

Bu dokuman, 8.2 maddesindeki uretim benzeri dogrulamalari kaydeder:

- 10K+ dosya ile buyuk dataset testi
- Edge-case testleri (broken symlink, permission error, duplicate varyasyonlari)
- Coklu OS smoke matrisi (Linux, macOS, Windows)

Large Dataset Test (10K+)
-------------------------

Calistirilan komut:

.. code-block:: bash

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_realworld_10k \
     --generate \
     --files 10000 \
     --duplicate-ratio 0.2 \
     --same-size-ratio 0.1 \
     --iterations 1 \
     --output tests/performance/real_world_10k_benchmark.json

Olusan rapor:

- ``tests/performance/real_world_10k_benchmark.json``

Ornek sonuc (2026-03-06):

- ``total_files_scanned``: 10000
- ``duplicate_group_count``: 1000
- ``duplicate_files_found``: 1000
- ``duplicate_bytes_reclaimable``: 148,458,496 bytes
- ``elapsed_seconds.avg``: 43.47s
- ``files_per_second.avg``: 230.02 files/s
- ``peak_memory_bytes.avg``: 22,305,436 bytes (~21.27 MB)
- ``peak_rss_bytes.avg``: 85,753,856 bytes (~81.78 MB)

Edge Cases
----------

Eklenen / dogrulanan testler:

- ``tests/unit/test_scanner_edge_cases.py``
  - broken symlink scan skip
  - permission error durumunda scan'in devam etmesi + error kaydi
- ``tests/e2e/test_end_to_end.py::test_e2e_edge_case_preview_duplicate_counts``
  - duplicate count varyasyonlarinda preview dogrulugu

Yerel smoke komutu:

.. code-block:: bash

   pytest -q --no-cov \
     tests/unit/test_scanner.py \
     tests/unit/test_scanner_edge_cases.py \
     tests/integration/test_pipeline.py::test_pipeline_preview_and_apply_quarantine_with_undo \
     tests/e2e/test_end_to_end.py::test_e2e_edge_case_preview_duplicate_counts

Coklu OS (macOS, Linux, Windows)
--------------------------------

GitHub Actions smoke matrisi eklendi:

- ``.github/workflows/os-smoke.yml``
- Matrix:
  - ``ubuntu-latest``
  - ``macos-latest``
  - ``windows-latest``
- Python: ``3.11``
- Scope: scanner + pipeline + edge-case smoke testleri

Acceptance
----------

8.2 kapsaminda hedeflenen dogrulamalar mevcut:

- 10K+ dataset benchmark: tamam
- edge-case test coverage: tamam
- cross-platform smoke matrix: tamam
