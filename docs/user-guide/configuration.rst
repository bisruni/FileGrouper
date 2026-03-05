Configuration Guide
===================

Bu bolum uygulamanin mevcut ayar noktalarini ozetler.

Runtime Secimleri
-----------------

Uygulama davranisi asagidaki seceneklerle degisir:

- Is akisi (`scope`): gruplama/kopya temizleme kapsamı
- Tasima modu (`mode`): copy veya move
- Kopya modu (`dedupe`): off, quarantine veya delete
- Dry-run: dosya degisikligi olmadan simule calisma
- Benzer goruntu analizi: Pillow varsa aktiflestirilebilir

CLI Parametre Tabanli Konfigurasyon
------------------------------------

Kalici bir `config.yaml` yapisi yoktur; konfigurasyon su anda komut satiri argumanlari
ve GUI secimleriyle yonetilir.

Ortam Degiskenleri
------------------

Logging tarafinda desteklenen ortam degiskenleri:

- `ARCHIFLOW_LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `ARCHIFLOW_CONSOLE_LOG_LEVEL`: konsol cikis seviye filtresi
- `ARCHIFLOW_LOG_DIR`: log dosyalarinin yazilacagi klasor

Log Dosyasi Varsayilani:

.. code-block:: text

   ./.filegrouper/logs/archiflow.log

Profil Konfigurasyonu
---------------------

Profil kayitlari `ProfileService` ile JSON dosyasinda tutulur.

Platforma gore varsayilan profil yolu:

- macOS: `~/Library/Application Support/ArchiFlow/profiles.json`
- Linux: `${XDG_CONFIG_HOME:-~/.config}/ArchiFlow/profiles.json`
- Windows: `%APPDATA%\\ArchiFlow\\profiles.json`

Not:
Eski `FileGrouper/profiles.json` yolu varsa geriye donuk uyumluluk icin kullanilir.

Islem Kayitlari ve Rapor Klasorleri
-----------------------------------

Transaction kayitlari:

.. code-block:: text

   <target>/.filegrouper/transactions/

Otomatik raporlar:

.. code-block:: text

   <target>/.filegrouper/reports/

Karantina:

.. code-block:: text

   <target>/.filegrouper_quarantine/<timestamp>/
