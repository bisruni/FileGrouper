Testing Guidelines
==================

Test Katmanlari
---------------

- Unit: `tests/unit/`
- Integration: `tests/integration/`
- CLI: `tests/cli/`
- E2E: `tests/e2e/`
- Performance: `tests/performance/`

Calistirma Komutlari
--------------------

Tum testler:

.. code-block:: bash

   pytest -q

Katman bazli:

.. code-block:: bash

   pytest -q tests/unit
   pytest -q tests/integration
   pytest -q tests/cli
   pytest -q tests/e2e
   pytest -q tests/performance

Kalite Kapisi
-------------

.. code-block:: bash

   tox -e format,lint,type,py313

Coverage Notlari
----------------

- Coverage XML: `coverage.xml`
- HTML raporu: `htmlcov/index.html`
- Coverage artefakti CI'da codecov ile yayinlanir.

Test Yazma Prensipleri
----------------------

1. Deterministik veri kullan (sabit seed, sabit timestamp gerektiginde fixture).
2. Geçici dizinleri `tmp_path` ile izole et.
3. Guvenlik-kritik akislar (delete/quarantine/undo) icin pozitif + negatif test yaz.
4. Cancel/pause gibi kontrol akislarini testlerde mutlaka dogrula.

Regression Yaklasimi
--------------------

- Bug fix geldiyse once reproducer test, sonra fix.
- Performans tarafinda baseline ile regresyon kontrolu:

.. code-block:: bash

   python tests/performance/run_benchmark.py \
     --source /tmp/archiflow_perf \
     --iterations 3 \
     --baseline tests/performance/baseline_example.json
