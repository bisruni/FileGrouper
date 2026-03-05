# ArchiFlow Marketing Kit

Bu dokuman, ArchiFlow'un pazarlama ve satis gorusmelerinde kullanilacak cekirdek mesajlarini toplar.

## 1) Product Overview

ArchiFlow; buyuk disklerde dosya gruplama, duplicate tespiti ve guvenli temizlik yapan masaustu uygulamasidir.

Temel vaadi:
- Guvenli varsayilanlar (`quarantine`, `dry-run`)
- Islem gunlugu + undo ile izlenebilirlik
- Buyuk veri setlerinde performans odakli duplicate pipeline

Kime uygun:
- Fotograf/video arsivi tutan bireysel kullanicilar
- Ajanslar, medya ekipleri, IT operasyon ekipleri
- Harici disk / NAS duzenleyen kucuk isletmeler

## 2) Feature Highlights

- Guvenli duplicate temizligi:
  `size -> quick signature -> sha256 -> byte verification`
- Varsayilan guvenlik:
  Silme default degil, quarantine default
- Transaction journaling:
  Her mutasyon adimi kayitli, undo destekli
- GUI + CLI:
  Teknik ve teknik olmayan kullaniciya uygun
- Raporlama:
  JSON ve CSV ciktilar
- Buyuk olcek hazirligi:
  50k+ dosya senaryolari icin benchmark ve self-test scriptleri

## 3) Use Cases

1. Harici disk duplicate temizligi
2. Medya arsivini tarih bazli klasorleme
3. Sirket paylasim klasorlerinde tekrar eden dosyalari azaltma
4. Tasinma/backup oncei veri hijyeni
5. Adli/operasyonel inceleme oncesi dosya envanteri cikarma

## 4) ROI Calculator Example

Ornek ROI hesabi:

- Gunluk kayip sure (arama/kopya yonetimi): `1.5 saat`
- Ekip buyuklugu: `6 kisi`
- Saatlik maliyet: `20 USD`
- Yilda calisma gunu: `220`
- ArchiFlow ile verim kazanci: `%30`
- Yillik lisans maliyeti: `600 USD`

Formul:

`Yillik Tasarruf = Gunluk Kayip Sure * Ekip * Saatlik Maliyet * Gun * Verim Orani`

`Net Kazanc = Yillik Tasarruf - Lisans Maliyeti`

Bu ornek icin:
- Yillik tasarruf: `11,880 USD`
- Net kazanc: `11,280 USD`
- ROI: `%1880`

Detayli tablo:
- `assets/marketing/roi-calculator-example.csv`

## 5) Comparison Chart

ArchiFlow; manuel temizlik ve genel amacli dosya yoneticilerine gore su alanlarda fark yaratir:
- Varsayilan guvenlik
- Islem geri alinabilirligi
- Buyuk disk icin optimize duplicate pipeline
- Kurumsal rapor ciktilari

Detayli karsilastirma:
- `assets/marketing/comparison-chart.md`

## 6) Positioning Message

Tek cumlelik konumlandirma:

`ArchiFlow, buyuk disklerde guvenli duplicate temizligi ve tutarli dosya organizasyonu sunan, undo destekli profesyonel masaustu cozumudur.`

