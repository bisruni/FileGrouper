Algorithm Explanations
======================

Kesin Kopya Tespiti
-------------------

Duplicate detection, asamali ve guvenli bir akis izler:

1. Boyuta gore gruplama (`size -> group`)
2. Hizli imza (quick signature) ile aday daraltma
3. SHA-256 ile kesin hashleme
4. Byte-by-byte dogrulama

Neden 4 asama?
~~~~~~~~~~~~~~

- Boyut gruplama: cok ucuz ilk filtre
- Quick signature: buyuk datasetlerde tam hash maliyetini ciddi azaltir
- SHA-256: yuksek dogruluk
- Byte compare: nadir edge-case'lerde ekstra guvence

Benzer Goruntu Tespiti
----------------------

Opsiyonel benzer goruntu modu:

- dHash (64-bit perceptual hash)
- Band bucket adaylama
- Hamming distance ile yakinlik kontrolu
- Pair limit ile buyuk datasetlerde donma korumasi

Bu mod neden varsayilan kapali?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Ek CPU ve I/O maliyeti getirir.
- Pillow kurulu degilse devre disi kalir.
- Benzerlik sonucu "kesin kopya" degildir; raporlama icindir.

Dosya Gruplama Algoritmasi
--------------------------

Organizer hedef yolu su sekilde kurar:

.. code-block:: text

   target/
     Images/YYYY/MM/
     Videos/YYYY/MM/
     Documents/YYYY/MM/
     Audio/YYYY/MM/
     Other/YYYY/MM/

Dosya adi cakismasi durumunda:

.. code-block:: text

   report.txt
   report (1).txt
   report (2).txt

Transaction ve Undo
-------------------

Her operasyon entry lifecycle:

.. code-block:: text

   PENDING -> DONE
   PENDING -> FAILED

Undo davranisi:

- Ters sirada ilerler.
- DONE disindakileri atlar.
- Hata olsa bile kalan entry'leri denemeye devam eder.
