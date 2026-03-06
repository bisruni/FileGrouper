Phase 8.3 Documentation Review
==============================

Bu sayfa 8.3 kapsaminda yapilan dokuman kalite kontrollerini kaydeder.

Kapsam
------

- Tum local markdown linklerinin kontrolu
- RST toctree hedeflerinin kontrolu
- Dokumanlarda gecen temel komut orneklerinin calistirilmasi
- Sphinx HTML build dogrulamasi

Calistirilan Komut
------------------

.. code-block:: bash

   python scripts/docs_self_check.py

Kontrol Sonucu
--------------

- Local markdown linkler: PASS
- RST toctree referanslari: PASS
- Komut ornekleri (`main.py -h`, `scan`, `preview`, `apply --dry-run`, `profiles --json`): PASS
- Sphinx build (`make -C docs html`): PASS

Raporun ciktisi:

- ``docs/_build/html/index.html``

Not
---

8.3 sonrasinda dokuman kalite kontrolu tek komutta tekrar edilebilir:

.. code-block:: bash

   python scripts/docs_self_check.py
