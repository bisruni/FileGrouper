CLI Reference
=============

Genel Kullanim
--------------

.. code-block:: bash

   python3 main.py <command> [options]

Komutlar
--------

`scan`
~~~~~~

Kaynak klasoru tarar ve ozet yazar.

.. code-block:: bash

   python3 main.py scan --source /path/source [--report /path/report.json]

`preview`
~~~~~~~~~

Tarama + kopya analizi yapar, dosya degistirmez.

.. code-block:: bash

   python3 main.py preview --source /path/source [--report /path/report.json]

`apply`
~~~~~~~

Gruplama/kopya islemlerini uygular.

.. code-block:: bash

   python3 main.py apply \
     --source /path/source \
     --target /path/target \
     --scope group_and_dedupe \
     --mode copy \
     --dedupe quarantine \
     [--dry-run] \
     [--similar-images] \
     [--report /path/report.json]

`gui`
~~~~~

Masaustu arayuzu acar.

.. code-block:: bash

   python3 main.py gui

Parametreler
------------

- `--mode`: `copy|move`
- `--dedupe`: `off|quarantine|delete`
- `--scope`: `group_and_dedupe|group_only|dedupe_only`
- `--dry-run`: Gercek dosya degisikligi yapmaz.
- `--similar-images`: dHash tabanli benzer goruntu analizi.
- `--report`: JSON rapor dosyasi cikisi.

Exit Code Referansi
-------------------

- `0`: Basarili calisma
- `1`: Validation/runtime hata
- `2`: Iptal edildi

CLI Guvenlik Notlari
--------------------

- `group_only` scope kullanirken `--target` zorunludur.
- Kaynak ve hedef ayni olamaz.
- Hedef klasor kaynak klasorun icinde olamaz.
- `delete` modu geri alinamaz kayiplara yol acabilir.
