# 🔭 Oracle Gece Araştırma

**Oracle Nightly Research v2** raporlarının herkese açık arşivi.

Her gece otomatik olarak üretilen AI/tech araştırma raporları bu sitede yayınlanmaktadır.

## 📋 Raporlar

Tüm raporları **[index sayfasından](https://mahsumaktas.github.io/oracle_arastirma/)** görebilirsiniz.

## Dizin Yapısı

```
oracle_arastirma/
├── index.html          ← Rapor listesi (GitHub Pages ana sayfası)
├── reports/
│   └── YYYY-MM-DD.html ← Her gecenin HTML raporu (mobile-friendly)
├── raw/
│   └── YYYY-MM-DD.md   ← Ham markdown kopyaları
└── .nojekyll           ← GitHub Pages Jekyll işlemeyi devre dışı bırakır
```

## GitHub Pages

Site adresi: **https://mahsumaktas.github.io/oracle_arastirma/**

Pages etkinleştirme (tek seferlik):
```bash
gh repo edit mahsumaktas/oracle_arastirma --enable-pages
# veya GitHub → Settings → Pages → Source: Deploy from branch → main / (root)
```

## Kaynak Pipeline

Raporlar `/Users/mahsum/clawd/research/nightly-v2/` pipeline'ından üretilir.
Yayıncı betik: `research/nightly-v2/scripts/publish-html.py`

---
*Oracle 🦉 · Gece Araştırma v2*
