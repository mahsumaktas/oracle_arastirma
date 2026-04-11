# 🔭 Oracle Gece Araştırma

Çok dilli GitHub Pages arşivi. Türkçe raporlar kaynak kabul edilir. İngilizce ve İspanyolca authored markdown varsa doğrudan kullanılır, yoksa sadece fallback olarak çeviri üretilir.

## Yapı

```
oracle_arastirma/
├── assets/               # Ortak CSS ve JS
├── data/                 # Sadece fallback çeviri cache'i
├── reports/              # Türkçe rapor URL'leri korunur
├── en/reports/           # İngilizce alternatif URL'ler
├── es/reports/           # İspanyolca alternatif URL'ler
├── raw/                  # Türkçe kaynak markdown
├── raw/en/               # Authored English markdown (varsa)
├── raw/es/               # Authored Spanish markdown (varsa)
├── scripts/build_site.py # Tüm statik site üretimi
└── api/latest.json       # Son rapor bilgisi
```

## Build

```bash
python3 scripts/build_site.py
```

Script şunları yapar:
- `raw/*.md` dosyalarını okuyup Türkçe rapor sayfalarını yeniden üretir
- `raw/en/*.md` ve `raw/es/*.md` varsa authored alternatifleri kullanır
- eksik dil artifact'lerinde yalnızca fallback çeviri üretir
- ana indeks, raw arşiv indeksleri, RSS, sitemap ve latest API çıktısını günceller
- fallback çevirileri `data/translation-cache.json` içinde cache'ler

## Notlar

- Mevcut Türkçe URL'ler korunur: `/index.html` ve `/reports/YYYY-MM-DD.html`
- Alternatif diller temiz URL'lerle yayınlanır: `/en/...` ve `/es/...`
- `raw/` dizini korunur, authored EN/ES markdown varsa `raw/en/` ve `raw/es/` altında tutulur
