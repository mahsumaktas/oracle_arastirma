# 🔭 Oracle Gece Araştırma

Çok dilli GitHub Pages arşivi. Gece raporları ve gündüz briefing'leri aynı v3 yayın mimarisini kullanır. Türkçe kaynak kabul edilir. İngilizce ve İspanyolca authored markdown varsa doğrudan kullanılır, yoksa sadece fallback olarak çeviri üretilir.

## Yapı

```
oracle_arastirma/
├── assets/               # Ortak CSS ve JS
├── data/                 # Sadece fallback çeviri cache'i
├── reports/              # Türkçe rapor URL'leri korunur
├── briefings/            # Türkçe briefing arşivi
├── en/reports/           # İngilizce alternatif URL'ler
├── en/briefings/         # İngilizce briefing URL'leri
├── es/reports/           # İspanyolca alternatif URL'ler
├── es/briefings/         # İspanyolca briefing URL'leri
├── raw/                  # Türkçe kaynak markdown
├── raw/briefings/        # Türkçe briefing markdown
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
- `raw/briefings/*.md` dosyalarını okuyup briefing arşivini üretir
- `raw/en/*.md` ve `raw/es/*.md` varsa authored alternatifleri kullanır
- `raw/briefings/en/*.md` ve `raw/briefings/es/*.md` varsa authored briefing varyantlarını kullanır
- eksik dil artifact'lerinde yalnızca fallback çeviri üretir
- ana indeks, raw arşiv indeksleri, RSS, sitemap ve latest API çıktısını günceller
- fallback çevirileri `data/translation-cache.json` içinde cache'ler

## Notlar

- Mevcut Türkçe URL'ler korunur: `/index.html` ve `/reports/YYYY-MM-DD.html`
- Alternatif diller temiz URL'lerle yayınlanır: `/en/...` ve `/es/...`
- Briefing arşivi ayrı tutulur: `/briefings/...`
- `raw/` dizini korunur, authored EN/ES markdown varsa `raw/en/` ve `raw/es/` altında tutulur
