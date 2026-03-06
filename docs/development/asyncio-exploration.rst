AsyncIO Exploration
===================

Bu not, Faz 6.4 kapsaminda ``asyncio`` kullaniminin teknik degerlendirmesini ozetler.

Neden arastirildi?
------------------

- Disk tarama ve hash islemlerinde daha iyi paralellik kazanimi aramak.
- GUI thread'i disinda daha olceklenebilir bir yurutme modeli ihtimali.

Mevcut durum
------------

- Dosya I/O ve hash hesaplamalari agirlikli olarak senkron ve bloklayici.
- PIL/HEIF acma ve byte-level hash adimlari ``async`` API sunmuyor.
- Mevcut tasarimda ``ThreadPoolExecutor`` ile I/O-bound adimlar icin kontrollu paralellik kullaniliyor.

Arastirma sonucu
----------------

- Salt ``asyncio``'ya gecmek tek basina hiz kazanci getirmiyor; cogu is yine thread'e offload ediliyor.
- Uygulama icinde full async mimariye gecis, mevcut moduler yapida buyuk yeniden tasarim gerektiriyor.
- Bu fazda pragmatic tercih:
  ``ThreadPoolExecutor`` tuning + lock contention gorunurlugu + benchmark metrikleri.

Probe script
------------

``asyncio.to_thread`` tabanli deneysel karsilastirma scripti:

.. code-block:: bash

   python tests/performance/asyncio_probe.py \
     --source /tmp/archiflow_perf \
     --limit 1000 \
     --workers 8

Bu script urun akisini degistirmez; sadece olasi async yaklasimlari karsilastirmak icin kullanilir.
