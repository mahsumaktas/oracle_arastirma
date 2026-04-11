# 🔭 Oracle Gece Araştırma

Çok dilli GitHub Pages arşivi. Türkçe raporlar kaynak kabul edilir, İngilizce ve İspanyolca sürümler build sırasında üretilir.

## Yapı

```
oracle_arastirma/
├── assets/               # Ortak CSS ve JS
├── data/                 # Çeviri cache'i
├── reports/              # Türkçe rapor URL'leri korunur
├── en/reports/           # İngilizce alternatif URL'ler
├── es/reports/           # İspanyolca alternatif URL'ler
├── raw/                  # Türkçe kaynak markdown
├── scripts/build_site.py # Tüm statik site üretimi
└── api/latest.json       # Son rapor bilgisi
```

## Build

```bash
python3 scripts/build_site.py
```

Script şunları yapar:
- `raw/*.md` dosyalarını okuyup Türkçe rapor sayfalarını yeniden üretir
- İngilizce ve İspanyolca alternatif sayfaları oluşturur
- ana indeks, raw arşiv indeksleri, RSS, sitemap ve latest API çıktısını günceller
- Google Translate web endpoint üzerinden eksik çevirileri alır ve `data/translation-cache.json` içinde cache'ler

## Notlar

- Mevcut Türkçe URL'ler korunur: `/index.html` ve `/reports/YYYY-MM-DD.html`
- Alternatif diller temiz URL'lerle yayınlanır: `/en/...` ve `/es/...`
- `raw/` dizini korunur, ayrıca daha okunabilir arşiv sayfaları eklenir
