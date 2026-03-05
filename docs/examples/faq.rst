SSS (FAQ)
=========

1) Kopya dosya neye gore tespit ediliyor?
-----------------------------------------

Varsayilan duplicate akisi:
1. Boyuta gore aday gruplama
2. Quick signature karsilastirma
3. SHA-256 hash
4. Gerekirse byte-by-byte dogrulama

Bu nedenle ayni isimli ama farkli icerikli dosyalar kopya sayilmaz.

2) `abc.pdf` ve `abc (1).pdf` neden bazen kopya cikmiyor?
---------------------------------------------------------

Dosya adi degil, icerik kontrol edilir.
Iki dosyanin icerigi farkliysa kopya olarak isaretlenmez.

3) Guvenli varsayilan mod nedir?
--------------------------------

Onerilen varsayilan:
- Dedupe mode: `quarantine`
- Ilk calistirma: `dry-run`

4) Undo hangi islemleri geri alir?
----------------------------------

`DONE` durumundaki transaction girisleri ters sirada geri alinmaya calisilir.
`FAILED` ve `PENDING` girisleri atlanir ve rapora yazilir.

5) Buyuk diskte (1TB) neden uzun suruyor?
-----------------------------------------

Sure; dosya sayisi, dosya boyutu, disk hizi ve baglanti tipine baglidir.
Ilk calistirma daha uzun surer, hash cache sonraki calistirmalari hizlandirir.

6) Similar image modu neden default kapali?
-------------------------------------------

Bu mod daha maliyetlidir ve yanlis pozitif riski duplicate moduna gore yuksektir.
Uretim kullaniminda once duplicate temizligi onerilir.

7) Hedef klasor neden kaynak icinde olamaz?
-------------------------------------------

Bu durum recursive buyume ve tekrar tarama riskine yol acar.
Hedefi kaynak disinda secmek gerekir.
