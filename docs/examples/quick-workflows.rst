Hizli Is Akislari
=================

Kopya analizi (onizleme)
------------------------

.. code-block:: bash

   python3 main.py preview --source /Volumes/USB

Sadece gruplandirma (test modu)
-------------------------------

.. code-block:: bash

   python3 main.py apply \
     --source /Volumes/USB \
     --target /Volumes/USB_Organized \
     --scope group_only \
     --mode copy \
     --dry-run

Gruplandirma + kopya temizleme
------------------------------

.. code-block:: bash

   python3 main.py apply \
     --source /Volumes/USB \
     --target /Volumes/USB_Organized \
     --scope group_and_dedupe \
     --dedupe quarantine
