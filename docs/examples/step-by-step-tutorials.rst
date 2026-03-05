Step-by-Step Tutorials
======================

Tutorial 1: Guvenli Kopya Temizligi
-----------------------------------

1. Kaynak klasoru secin.
2. `preview` calistirin.
3. Kopya gruplarini inceleyin.
4. `apply --dry-run` ile simule edin.
5. Son olarak `apply` ile gercek islem yapin.

CLI ornegi:

.. code-block:: bash

   python3 main.py preview --source /Volumes/USB
   python3 main.py apply --source /Volumes/USB --scope dedupe_only --dedupe quarantine --dry-run
   python3 main.py apply --source /Volumes/USB --scope dedupe_only --dedupe quarantine

Tutorial 2: Belgeleri Tarihe Gore Gruplama
------------------------------------------

1. Kaynak ve hedef klasor belirleyin.
2. Scope'u `group_only` secin.
3. Mode'u `copy` secin.
4. Dry-run onizleme alin.
5. Sonra dry-run kapali olarak uygulayin.

CLI ornegi:

.. code-block:: bash

   python3 main.py apply \
     --source /Volumes/Documents \
     --target /Volumes/Documents_Organized \
     --scope group_only \
     --mode copy \
     --dry-run

Tutorial 3: Grup Detayi ile Koru/Sil Karari (GUI)
--------------------------------------------------

1. GUI acin (`python3 main.py gui`).
2. Onizleme calistirin.
3. Kopya tablosunda bir gruba cift tiklayin.
4. `Grup Detayi` ekraninda korunacak dosyalari isaretleyin.
5. Uygulamaya gecmeden once ozet kartini tekrar kontrol edin.

Checklist
---------

- [ ] Hedef kaynak altinda degil
- [ ] Dedupe modu `quarantine`
- [ ] Dry-run ile en az bir deneme yapildi
- [ ] Rapor dosyasi olustu
