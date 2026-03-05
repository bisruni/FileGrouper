API Genel Bakis
===============

Bu bolum modullerin sorumluluklarini ve birbiriyle iliskilerini ozetler.

Temel Servisler
---------------

- ``filegrouper.scanner``: Dosya sistemi taramasi ve ``FileRecord`` uretimi.
- ``filegrouper.duplicate_detector``: Kopya tespiti (boyut -> hizli imza -> SHA-256 -> byte karsilastirma).
- ``filegrouper.organizer``: Gruplama/duzenleme ve kopya islemleri (karantina/silme) uygulamasi.
- ``filegrouper.transaction_service``: Islem gunlugu kaydi ve geri alma (undo).
- ``filegrouper.pipeline``: Servisleri orkestre eden ana motor.

Arayuz Katmanlari
-----------------

- ``filegrouper.cli``: Komut satiri giris noktasi.
- ``filegrouper.gui``: Ana pencere.
- ``filegrouper.gui_components``: Dialoglar ve worker sinifi.
- ``filegrouper.gui_theme``: Tema uygulama yardimcilari.
- ``filegrouper.gui_texts``: GUI metinleri ve secim listeleri.

Ortak Moduller
--------------

- ``filegrouper.models``: Paylasilan dataclass ve enum tipleri.
- ``filegrouper.constants``: Sabitler ve ortak path yardimcilari.
- ``filegrouper.hash_cache``: Hash cache katmani.
- ``filegrouper.errors``: Ozel exception ve hata metni standartlari.
- ``filegrouper.logger``: Yapilandirilmis logger ayarlari.
- ``filegrouper.utils`` ve ``filegrouper.validators``: Yardimci fonksiyonlar.

Type Hints Dokumantasyonu
-------------------------

Bu API sayfalari type hint bilgisini parametre/aciklama bloklarinda gosterir:

- ``autodoc_typehints = "description"``
- ``always_document_param_types = True``
- ``autodoc_typehints_format = "short"``

Boylece fonksiyon imzalarindaki tipler hem okunabilir hem de Sphinx ciktilarinda acikca gorunur.
