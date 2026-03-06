Phase 8.4 Performance Baselines
================================

Bu dokuman 8.4 kapsaminda performans baseline'larini, hedef beklentileri
ve operasyonel optimizasyon onerilerini toplar.

Benchmark Documentation
-----------------------

Kullanilan arac:

- ``tests/performance/run_benchmark.py``

Olcum cikti dosyalari:

- ``tests/performance/baseline_5k_group_only.json``
- ``tests/performance/baseline_5k_group_and_dedupe.json``
- ``tests/performance/baseline_10k_cold_group_and_dedupe.json``
- ``tests/performance/baseline_10k_group_and_dedupe.json``

Calistirilan komutlar:

.. code-block:: bash

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_baseline_5k \
     --generate \
     --files 5000 \
     --duplicate-ratio 0.2 \
     --same-size-ratio 0.1 \
     --iterations 2 \
     --scope group_and_dedupe \
     --output tests/performance/baseline_5k_group_and_dedupe.json

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_baseline_5k \
     --iterations 2 \
     --scope group_only \
     --output tests/performance/baseline_5k_group_only.json

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_realworld_10k \
     --generate \
     --files 10000 \
     --duplicate-ratio 0.2 \
     --same-size-ratio 0.1 \
     --iterations 1 \
     --output tests/performance/baseline_10k_cold_group_and_dedupe.json

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_realworld_10k \
     --iterations 2 \
     --scope group_and_dedupe \
     --output tests/performance/baseline_10k_group_and_dedupe.json

Performance Expectations
------------------------

Asagidaki degerler, su anki kod tabani icin referans beklentidir.
Makine/disk tipine gore degisebilir.

.. list-table:: Baseline Summary
   :header-rows: 1

   * - Senaryo
     - Elapsed (avg)
     - Peak Mem (avg, tracemalloc)
     - Throughput
     - Not
   * - 5K / group_only
     - 0.430s
     - 0.94 MB
     - 11,634 files/s
     - Streaming scan, hash yok
   * - 5K / group_and_dedupe
     - 8.119s
     - 14.09 MB
     - 964 files/s
     - 2-step hash + duplicate pipeline
   * - 10K / group_and_dedupe (cold)
     - 43.474s
     - 21.27 MB
     - 230 files/s
     - Ilk kosu, cache soguk
   * - 10K / group_and_dedupe (warm)
     - 6.975s
     - 22.59 MB
     - 1,435 files/s
     - Cache sicak, tekrar kosu

Recommended Release Gates
-------------------------

Release oncesi asagidaki minimum kapilar onerilir:

- ``group_only`` 5K: elapsed <= ``1.0s``
- ``group_and_dedupe`` 5K: elapsed <= ``15s``
- ``group_and_dedupe`` 10K cold: elapsed <= ``60s``
- ``group_and_dedupe`` 10K warm: elapsed <= ``15s``
- ``peak_memory_bytes.avg`` 10K: <= ``30 MB`` (tracemalloc)
- ``peak_rss_bytes.avg`` 10K: <= ``120 MB`` (platform-dependent)
- ``summary.errors``: ``[]`` olmalı

Optimization Recommendations
----------------------------

1. Hash cache'i koru:
   - Kaynak dosyalarin ``(path, size, mtime)`` anahtar stabilitesi sicak kosu hizini belirler.
2. Ilk gecis daima preview:
   - Buyuk diskte once ``preview`` ve rapor cikar, sonra ``apply`` yap.
3. Similar image modunu secici kullan:
   - Varsayilan kapalidir; buyuk kutuphanelerde sadece gerektiğinde ac.
4. Dedupe modunda quarantine tercih et:
   - Performans + geri alinabilirlik dengesi icin ``quarantine`` en guvenli yoldur.
5. Disk I/O etkisini azalt:
   - Harici yavas diskte benchmark sonuclari duser; baseline'i ayni disk sinifinda olc.
6. Regression check'i CI'a koy:
   - ``--baseline`` ile zaman/bellek regresyonunu erken yakala.

Operational Guideline
---------------------

Regression kontrolu komutu:

.. code-block:: bash

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_realworld_10k \
     --iterations 2 \
     --scope group_and_dedupe \
     --baseline tests/performance/baseline_10k_group_and_dedupe.json \
     --max-time-regression 1.2 \
     --max-memory-regression 1.2

Bu kontrol gecerse, performans kalite cizgisi korunuyor kabul edilir.
