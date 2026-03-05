# ArchiFlow (Python)

ArchiFlow, harici disk veya klasorleri tarayip dosyalari tur + tarihe gore duzenleyen,
kopya dosyalari bulup temizleyebilen bir Python uygulamasidir.

- GUI: PySide6 masaustu arayuzu
- CLI: `scan`, `preview`, `apply`
- Scope ayrimi: sadece gruplama / sadece kopya temizleme / ikisi birden

## Gereksinimler

- Python 3.10+
- `pip` (sanal ortam icinde kullanilmasi onerilir)

Kurulum:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Calistirma

```bash
python3 main.py gui
```

Kisa yol:

```bash
python3 main.py
```

## CLI

Yardim:

```bash
python3 main.py -h
```

### 1) Scan

Sadece tarama ve ozet:

```bash
python3 main.py scan --source /Volumes/USB
```

### 2) Preview

Tarama + kopya analizi (degisiklik yapmaz):

```bash
python3 main.py preview --source /Volumes/USB
```

### 3) Apply

Secilen islemi uygular:

```bash
python3 main.py apply \
  --source /Volumes/USB \
  --target /Volumes/USB_Organized \
  --mode copy \
  --dedupe quarantine \
  --scope group_and_dedupe \
  --dry-run
```

`--dry-run` kaldirildiginda gercek degisiklik yapar.

## Temel Parametreler

- `--mode copy|move`
- `--dedupe off|quarantine|delete`
- `--scope group_and_dedupe|group_only|dedupe_only`
- `--similar-images` dHash tabanli benzer gorselleri bulur (Pillow gerekir)
- `--report <path.json>` sonuc raporu yazar

## Algoritma Notu

- Kopya bulma: boyut gruplama -> hizli imza -> SHA-256 (2 asamali)
- Benzer gorsel: dHash + band bucket adaylama (dogrudan N^2 tarama degil)

## GUI Ozeti

1. Kaynak klasoru sec
2. Hedef klasoru sec (gruplama varsa zorunlu)
3. Ustteki sekmeden is akisini sec: `Hepsi` / `Kopya Analizi` / `Gruplandirma`
4. `Onizleme` ile kontrol et
5. `Kopyalar` sekmesinde satira cift tiklayip dosya konumunu ac
6. Gerekirse `Grup Detayi` ile koru/sil secimini duzenle
7. `Uygula` onayi ekranini kontrol et
8. `Test modu`nu kapatip `Secili Islemi Uygula`

## Guvenlik Kurallari

- Kaynak ve hedef ayni olamaz.
- Hedef, kaynak klasorun icinde olamaz.
- `quarantine` modunda kopyalar su klasore tasinir:
  `TARGET/.filegrouper_quarantine/<timestamp>/...`
- `Benzer gorseller` analizi sadece rapor/inceleme icindir; otomatik silme yapmaz.
- Yapilan islem kayitlari `.filegrouper/transactions` altina yazilir.
- Her islemde JSON+CSV raporu otomatik yazilir: `.filegrouper/reports/`
- `Son Islemi Geri Al` transaction kaydina gore calisir.

## Dokumantasyon

Sphinx dokumantasyonunu derlemek icin:

```bash
python3 -m pip install -e .[dev]
make -C docs html
```

HTML cikti klasoru: `docs/_build/html/`

## Test ve CI

Yerel test:

```bash
pytest
```

`tox` ile coklu Python surumu:

```bash
tox
```

Pre-commit hook kurulumu:

```bash
pre-commit install
pre-commit run --all-files
```

CI pipeline dosyasi: `.github/workflows/ci.yml`

## QA Kontrolleri

Tek tek calistirma:

```bash
black --check filegrouper tests main.py
isort --check-only filegrouper tests main.py
flake8 filegrouper tests main.py
mypy filegrouper
```

Tek komut akisi (`tox`):

```bash
tox -e format
tox -e lint
tox -e type
tox -e py313
```

## Performans Benchmark (Faz 3.5)

Performans araclari `tests/performance/` altindadir.

Dataset uret + benchmark calistir:

```bash
python tests/performance/run_benchmark.py \
  --source /tmp/archiflow_perf \
  --generate \
  --files 5000 \
  --duplicate-ratio 0.2 \
  --same-size-ratio 0.1 \
  --iterations 2
```

Baseline regression kontrolu:

```bash
python tests/performance/run_benchmark.py \
  --source /tmp/archiflow_perf \
  --iterations 3 \
  --baseline tests/performance/baseline_example.json \
  --max-time-regression 1.2 \
  --max-memory-regression 1.2
```

## Logging

- Logger: `filegrouper/logger.py`
- Varsayilan log dosyasi: `./.filegrouper/logs/archiflow.log`
- Rotating file handler: 5 MB x 5 backup
- Format: key=value structured log (`ts`, `level`, `logger`, `module`, `line`, `msg`)

Ortam degiskenleri:

- `ARCHIFLOW_LOG_LEVEL` (ornek: `DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `ARCHIFLOW_CONSOLE_LOG_LEVEL` (varsayilan: `WARNING`)
- `ARCHIFLOW_LOG_DIR` (ozel log klasoru)

## Not

Bu repo artik Python ana uygulamasini icerir. Eski .NET dosyalari kaynakta duruyor olabilir,
ancak aktif calisma akisi `python3 main.py` uzerindendir.
