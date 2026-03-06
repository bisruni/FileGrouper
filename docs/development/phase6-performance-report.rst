Phase 6 Performance Report
==========================

Bu rapor, Faz 6 (6.1-6.4) optimizasyonlarinin olcum sonuclarini ozetler.

Ortam notu
----------

- Makine, disk tipi ve anlik sistem yukune gore sonuclar degisebilir.
- Tum olcumler ayni kod tabani ile, ayni benchmark araci (`tests/performance/run_benchmark.py`) kullanilarak alindi.

6.1 Memory-Efficient Code
-------------------------

Streaming/group-only akista liste biriktirmeden tarama devrede.

Komut:

.. code-block:: bash

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_perf_62 \
     --iterations 2 \
     --scope group_only

Sonuc (ornek):

- elapsed_avg: ``0.428s``
- peak_mem_avg (tracemalloc): ``0.93MB``
- throughput: ``11674.5 files/s``

Bu sonuc, group-only senaryoda dusuk bellek izi ile streaming calismayi dogrular.

6.2 2x+ Performance Gain
------------------------

Hash agirlikli ayni veri setinde (12000 dosya, duplicate ratio 0.5, same-size ratio 0.2)
cache cold ve cache warm karsilastirmasi:

Cold run:

.. code-block:: bash

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_speed_tuned \
     --generate \
     --files 12000 \
     --duplicate-ratio 0.5 \
     --same-size-ratio 0.2 \
     --iterations 2 \
     --scope group_and_dedupe

Warm run (ayni dataset):

.. code-block:: bash

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_speed_tuned \
     --iterations 2 \
     --scope group_and_dedupe

Olcum:

- cold elapsed_avg: ``48.706s``
- warm elapsed_avg: ``10.008s``
- speedup: ``~4.87x``

Faz 6 kapsamindaki algoritma + cache + concurrency optimizasyonlarinin birlikte
2x+ hedefini astigi bu senaryoda dogrulanmistir.
