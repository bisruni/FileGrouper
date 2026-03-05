# Contributing

Bu proje guvenlik ve dogruluk odaklidir. Katki verirken asagidaki adimlari izleyin.

## Gelistirme Ortami

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -e .[dev]
```

## Kod Standartlari

```bash
black filegrouper main.py
isort filegrouper main.py
flake8 filegrouper main.py
mypy filegrouper
```

## Test

```bash
pytest
```

## Pull Request Kurallari

1. Degisiklikleri tek bir konuya odakli tutun.
2. Commit mesajlarini acik yazin.
3. Davranis degisikligi varsa README veya docs guncelleyin.
4. Veri kaybi riski olusturan degisikliklerde ek test ekleyin.
