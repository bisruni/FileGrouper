Common Use Cases
================

1) Harici diskte kopya temizligi
--------------------------------

Amac:
- Alan kazanmak
- Yanlislikla silme riskini azaltmak

Onerilen ayar:
- Scope: `dedupe_only`
- Dedupe: `quarantine`
- Dry-run: acik (ilk calistirma)

CLI:

.. code-block:: bash

   python3 main.py apply \
     --source /Volumes/USB \
     --scope dedupe_only \
     --dedupe quarantine \
     --dry-run

2) Medya arsivi duzenleme
-------------------------

Amac:
- Resim/video/ses dosyalarini tarihsel klasor yapisina oturtmak

Onerilen ayar:
- Scope: `group_only`
- Mode: `copy` (guvenli)

CLI:

.. code-block:: bash

   python3 main.py apply \
     --source /Volumes/Media \
     --target /Volumes/Media_Organized \
     --scope group_only \
     --mode copy \
     --dry-run

3) Tam akista guvenli temizlik
------------------------------

Amac:
- Gruplama + kopya temizleme

Onerilen ayar:
- Scope: `group_and_dedupe`
- Mode: `copy`
- Dedupe: `quarantine`

Not:
- Once `preview` ve `apply --dry-run` ile kontrol edin.
- Sonra gercek uygula adimina gecin.

4) Buyuk diskte performans odakli analiz
----------------------------------------

Amac:
- 1TB+ diskte once genel fotografin cikmasi

Onerilen adim:
1. Sadece `scan` ile tarama
2. `preview` ile duplicate analizi
3. Gerekirse benchmark araciyla performans olcumu

.. code-block:: bash

   python3 main.py scan --source /Volumes/BigDisk
   python3 main.py preview --source /Volumes/BigDisk
   python tests/performance/run_benchmark.py --source /Volumes/BigDisk --iterations 2
