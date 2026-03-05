Quick Start
===========

En guvenli hizli baslangic akisi:

1. Kaynak klasoru sec.
2. Onizleme al.
3. Ozeti ve kopya gruplarini kontrol et.
4. Once test modu acik sekilde `apply` dene.
5. Sonra test modunu kapatip gercek islemi uygula.

GUI ile Hizli Baslangic
-----------------------

.. code-block:: bash

   python3 main.py gui

CLI ile Hizli Baslangic
-----------------------

Scan:

.. code-block:: bash

   python3 main.py scan --source /Volumes/USB

Preview:

.. code-block:: bash

   python3 main.py preview --source /Volumes/USB

Dry-run apply:

.. code-block:: bash

   python3 main.py apply \
     --source /Volumes/USB \
     --target /Volumes/USB_Organized \
     --scope group_and_dedupe \
     --mode copy \
     --dedupe quarantine \
     --dry-run

Ornek Guvenli Uygulama Akisi
----------------------------

.. code-block:: text

   1) preview
   2) duplicate group secimlerini kontrol et
   3) apply --dry-run
   4) apply (dry-run olmadan)
   5) gerekirse undo

Undo:

GUI icinde "Geri al" islemi son transaction kaydina gore calisir.
