# ArchiFlow Tutorials

Bu dokuman, en sik kullanim senaryolarini hizlica uygulamak icin kisa adimlar sunar.

## 1) Guvenli duplicate temizligi (onerilen)

1. `preview` ile sonucu gor:
   ```bash
   python3 main.py preview --source /Volumes/USB
   ```
2. `dry-run` ile simulasyon yap:
   ```bash
   python3 main.py apply --source /Volumes/USB --scope dedupe_only --dedupe quarantine --dry-run
   ```
3. Gercek uygula:
   ```bash
   python3 main.py apply --source /Volumes/USB --scope dedupe_only --dedupe quarantine
   ```

## 2) Sadece dosya gruplandirma

```bash
python3 main.py apply \
  --source /Volumes/Documents \
  --target /Volumes/Documents_Organized \
  --scope group_only \
  --mode copy \
  --dry-run
```

## 3) Gruplandirma + dedupe birlikte

```bash
python3 main.py apply \
  --source /Volumes/Media \
  --target /Volumes/Media_Organized \
  --scope group_and_dedupe \
  --mode copy \
  --dedupe quarantine
```

## 4) Undo son islemi geri al

```bash
python3 main.py undo --transaction-id <ID>
```

## 5) Hizli kontrol listesi

- Hedef klasor kaynak altinda degil
- Ilk kosu `dry-run`
- Dedupe modu `quarantine`
- Islem sonrasi JSON/CSV rapor kaydi alinmis
