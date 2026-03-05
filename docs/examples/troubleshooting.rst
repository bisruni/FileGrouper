Troubleshooting Guide
=====================

1) `externally-managed-environment` hatasi
------------------------------------------

Neden:
- Homebrew Python sistem ortamina dogrudan `pip install` izin vermiyor.

Cozum:

.. code-block:: bash

   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install -r requirements.txt

2) `Hedef klasor kaynak klasorun icinde olamaz`
-----------------------------------------------

Neden:
- Hedef klasor kaynak agacinin altinda secilmis.

Cozum:
- Hedefi kaynak disinda baska bir klasor olarak secin.

Ornek:
- Yanlis: `/disk/source/organized`
- Dogru: `/disk/source_organized`

3) GUI acilmiyor
----------------

Neden:
- PySide6 eksik olabilir.

Cozum:

.. code-block:: bash

   source .venv/bin/activate
   python3 -m pip install PySide6
   python3 main.py gui

4) Undo beklenen dosyalari geri getirmedi
-----------------------------------------

Kontrol:
- Islem `delete` modunda mi yapildi?
- Transaction dosyasinda entry status `DONE` mu?

Not:
- `delete` ile silinen dosyalar geri alinamaz.

5) Sphinx dokumantasyonunda requests warning
--------------------------------------------

Mesaj:
- `RequestsDependencyWarning` gorulebilir.

Cozum:

.. code-block:: bash

   source .venv/bin/activate
   python3 -m pip install "chardet>=5.2,<6"
   make -C docs html

6) Taramada bazi dosyalar gorunmuyor
------------------------------------

Neden:
- Filtreler (uzanti/boyut/tarih)
- Gizli dosya dislama
- Erisilemeyen dosya/klasor

Cozum:
- Filtreleri temizleyin
- Hata/log listesini inceleyin
