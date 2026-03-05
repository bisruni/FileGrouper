"""GUI text resources and selection item definitions."""

from __future__ import annotations

from .models import DedupeMode, ExecutionScope, OrganizationMode

TR = {
    "title": "ArchiFlow",
    "subtitle": "Disk düzenleme ve kopya temizleme merkezi",
    "source": "Kaynak klasör",
    "target": "Hedef klasör (organize/karantina)",
    "browse": "Gözat…",
    "scope": "Kapsam",
    "workflow": "İş akışı",
    "flow_all": "Hepsi",
    "flow_all_desc": "Gruplandırma ve kopya temizleme birlikte çalışır.",
    "flow_dedupe": "Kopya Analizi",
    "flow_dedupe_desc": "Sadece kopya analiz/temizleme çalışır.",
    "flow_group": "Gruplandırma",
    "flow_group_desc": "Sadece klasörleme ve düzenleme çalışır.",
    "target_not_needed": "Bu akışta hedef klasör gerekmez.",
    "mode": "Taşıma modu",
    "dedupe": "Kopya modu",
    "dry_run": "Test modu (önerilir)",
    "similar": "Benzer görselleri analiz et (silinmez)",
    "similar_unavailable": "Benzer goruntu analizi icin Pillow gerekli.",
    "filters": "Filtreler…",
    "preview": "Önizleme",
    "apply": "Uygula",
    "pause": "Duraklat",
    "resume": "Devam",
    "cancel": "İptal",
    "undo": "Geri al",
    "export": "Rapor",
    "tab_dupes": "Kopyalar",
    "tab_logs": "Log",
    "ready": "Hazır",
    "running": "Çalışıyor…",
    "paused": "Duraklatıldı",
    "cancelled": "İptal edildi",
    "done": "Tamamlandı",
    "err": "Hata",
    "need_source": "Kaynak klasör seçmeden başlayamazsın.",
    "need_target_undo": "Geri alma için hedef klasör gerekli.",
    "need_preview": "Önce bir önizleme/uygulama çalıştır.",
    "preview_summary": "Önizleme Özeti",
    "sum_total": "Toplam dosya",
    "sum_dupes": "Kopya bulundu",
    "sum_dupe_groups": "Kopya grup",
    "sum_reclaim": "Kazanılabilir alan",
    "sum_quarantine": "Karantinaya gidecek",
    "sum_organize": "Gruplanacak dosya",
    "sum_errors": "Hata sayısı",
    "sum_skipped": "Atlanan dosya",
    "confirm_apply_title": "Uygulama Onayı",
    "confirm_apply_text": "İşlem uygulanacak. Devam etmek istiyor musun?",
    "summary_dialog_title": "Çalışma Özeti",
    "summary_preview_done": "Önizleme tamamlandı.",
    "open_quarantine": "Karantina Klasörünü Aç",
    "quarantine_missing": "Karantina klasörü henüz oluşmadı.",
    "open_file_location_failed": "Dosya konumu açılamadı.",
    "dupe_detail": "Grup Detayı",
}

SCOPE_ITEMS = [
    ("Grupla + Kopya Temizle", ExecutionScope.GROUP_AND_DEDUPE),
    ("Sadece Grupla", ExecutionScope.GROUP_ONLY),
    ("Sadece Kopya Temizle", ExecutionScope.DEDUPE_ONLY),
]
MODE_ITEMS = [
    ("Kopyala", OrganizationMode.COPY),
    ("Taşı", OrganizationMode.MOVE),
]
DEDUPE_ITEMS = [
    ("Karantina", DedupeMode.QUARANTINE),
    ("Kapalı", DedupeMode.OFF),
    ("Sil (tehlikeli)", DedupeMode.DELETE),
]
WORKFLOW_ITEMS = [
    (TR["flow_all"], ExecutionScope.GROUP_AND_DEDUPE, TR["flow_all_desc"]),
    (TR["flow_dedupe"], ExecutionScope.DEDUPE_ONLY, TR["flow_dedupe_desc"]),
    (TR["flow_group"], ExecutionScope.GROUP_ONLY, TR["flow_group_desc"]),
]
