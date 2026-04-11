#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
import shutil
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"
REPORTS_DIR = ROOT / "reports"
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
EN_DIR = ROOT / "en"
ES_DIR = ROOT / "es"
SITE_URL = "https://mahsumaktas.github.io/oracle_arastirma"
SITE_NAME = "Oracle Night Research"
CACHE_PATH = DATA_DIR / "translation-cache.json"

LANGS = {
    "tr": {
        "code": "tr",
        "label": "Türkçe",
        "native": "Türkçe",
        "site_title": "Oracle Gece Araştırma",
        "site_tagline": "Her gece derlenen AI ve teknoloji araştırma arşivi",
        "archive_title": "Tüm raporlar",
        "archive_subtitle": "Gece üretilen araştırma raporlarının çok dilli arşivi.",
        "latest_report": "Son rapor",
        "total_reports": "Toplam rapor",
        "date_range": "Tarih aralığı",
        "languages": "Dil seçeneği",
        "search_label": "Arşivde ara",
        "search_placeholder": "Tarih, başlık veya özet ara",
        "search_empty": "Aramanızla eşleşen rapor bulunamadı.",
        "view_report": "Raporu aç",
        "view_raw": "Ham markdown",
        "view_rendered": "Rendered görünüm",
        "browse_raw": "Ham arşiv",
        "report_badge": "Araştırma raporu",
        "back_to_archive": "Arşive dön",
        "report_actions": "Hızlı erişim",
        "section_nav": "Bölümler",
        "report_overview": "Rapor özeti",
        "open_original": "Türkçe orijinal",
        "open_language": "Bu dilde aç",
        "raw_archive_title": "Ham markdown arşivi",
        "raw_archive_subtitle": "İstersen markdown kaynağını da indirebilirsin.",
        "raw_source": "Kaynak markdown",
        "generated_with": "Şablon tabanlı çok dilli yayın akışı",
        "footer_note": "Oracle gece araştırma arşivi, Türkçe asıl içerik korunarak üretilir.",
        "report_intro": "Türkçe kaynak korunur, alternatif diller otomatik olarak üretilir.",
        "summary_label": "Öne çıkan not",
        "toc_label": "İçindekiler",
        "prev_report": "Önceki rapor",
        "next_report": "Sonraki rapor",
        "latest_api_title": "Oracle Gece Araştırma",
        "feed_description": "Günlük AI ve teknoloji araştırma raporu",
        "lang_switch": "Dil",
        "meta_description": "Oracle Gece Araştırma arşivi, tüm raporlar ve çok dilli erişim.",
        "report_meta_description": "Oracle Gece Araştırma raporu",
        "raw_meta_description": "Ham markdown arşivi",
        "sections_count": "bölüm",
        "word_count_label": "kelime",
    },
    "en": {
        "code": "en",
        "label": "English",
        "native": "English",
        "site_title": "Oracle Night Research",
        "site_tagline": "A multilingual archive of nightly AI and technology research.",
        "archive_title": "All reports",
        "archive_subtitle": "Browse the published nightly research archive in Turkish, English, and Spanish.",
        "latest_report": "Latest report",
        "total_reports": "Total reports",
        "date_range": "Date range",
        "languages": "Languages",
        "search_label": "Search archive",
        "search_placeholder": "Search by date, title, or summary",
        "search_empty": "No reports matched your search.",
        "view_report": "Open report",
        "view_raw": "Raw markdown",
        "view_rendered": "Rendered view",
        "browse_raw": "Raw archive",
        "report_badge": "Research report",
        "back_to_archive": "Back to archive",
        "report_actions": "Quick links",
        "section_nav": "Sections",
        "report_overview": "Report overview",
        "open_original": "Turkish original",
        "open_language": "Open in this language",
        "raw_archive_title": "Raw markdown archive",
        "raw_archive_subtitle": "Download the original markdown when needed.",
        "raw_source": "Source markdown",
        "generated_with": "Template-driven multilingual publishing flow",
        "footer_note": "Oracle Night Research keeps Turkish as the source of truth and ships translated mirrors.",
        "report_intro": "The Turkish source stays intact, with generated language variants alongside it.",
        "summary_label": "Highlight",
        "toc_label": "Contents",
        "prev_report": "Previous report",
        "next_report": "Next report",
        "latest_api_title": "Oracle Night Research",
        "feed_description": "Daily AI and technology research report",
        "lang_switch": "Language",
        "meta_description": "Oracle Night Research archive with multilingual report access.",
        "report_meta_description": "Oracle Night Research report",
        "raw_meta_description": "Raw markdown archive",
        "sections_count": "sections",
        "word_count_label": "words",
    },
    "es": {
        "code": "es",
        "label": "Español",
        "native": "Español",
        "site_title": "Investigación Nocturna de Oracle",
        "site_tagline": "Archivo multilingüe de investigación nocturna sobre IA y tecnología.",
        "archive_title": "Todos los informes",
        "archive_subtitle": "Explora el archivo publicado en turco, inglés y español.",
        "latest_report": "Informe más reciente",
        "total_reports": "Informes totales",
        "date_range": "Rango de fechas",
        "languages": "Idiomas",
        "search_label": "Buscar en el archivo",
        "search_placeholder": "Buscar por fecha, título o resumen",
        "search_empty": "No se encontraron informes para tu búsqueda.",
        "view_report": "Abrir informe",
        "view_raw": "Markdown original",
        "view_rendered": "Vista renderizada",
        "browse_raw": "Archivo raw",
        "report_badge": "Informe de investigación",
        "back_to_archive": "Volver al archivo",
        "report_actions": "Accesos rápidos",
        "section_nav": "Secciones",
        "report_overview": "Resumen del informe",
        "open_original": "Original en turco",
        "open_language": "Abrir en este idioma",
        "raw_archive_title": "Archivo de markdown original",
        "raw_archive_subtitle": "También puedes descargar el markdown fuente.",
        "raw_source": "Markdown fuente",
        "generated_with": "Flujo de publicación multilingüe basado en plantillas",
        "footer_note": "Oracle Night Research mantiene el turco como fuente original y publica espejos traducidos.",
        "report_intro": "La fuente turca se conserva y las variantes de idioma se generan a su lado.",
        "summary_label": "Destacado",
        "toc_label": "Contenido",
        "prev_report": "Informe anterior",
        "next_report": "Siguiente informe",
        "latest_api_title": "Investigación Nocturna de Oracle",
        "feed_description": "Informe diario de investigación sobre IA y tecnología",
        "lang_switch": "Idioma",
        "meta_description": "Archivo de Oracle Night Research con acceso multilingüe a los informes.",
        "report_meta_description": "Informe de Oracle Night Research",
        "raw_meta_description": "Archivo de markdown original",
        "sections_count": "secciones",
        "word_count_label": "palabras",
    },
}

TURKISH_MAP = str.maketrans({
    "ç": "c",
    "ğ": "g",
    "ı": "i",
    "İ": "i",
    "ö": "o",
    "ş": "s",
    "ü": "u",
})

CSS = """
:root {
  --bg: #08111f;
  --bg-elevated: rgba(11, 19, 33, 0.82);
  --surface: rgba(15, 23, 42, 0.82);
  --surface-strong: rgba(15, 23, 42, 0.96);
  --surface-soft: rgba(30, 41, 59, 0.68);
  --text: #e5eefb;
  --text-muted: #9db0cf;
  --text-soft: #c7d5eb;
  --border: rgba(148, 163, 184, 0.18);
  --border-strong: rgba(96, 165, 250, 0.35);
  --accent: #7c9cff;
  --accent-2: #55d6ff;
  --accent-soft: rgba(124, 156, 255, 0.16);
  --success: #4ade80;
  --warning: #fbbf24;
  --danger: #fb7185;
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.34);
  --shadow-soft: 0 12px 32px rgba(2, 6, 23, 0.24);
  --radius-xl: 28px;
  --radius-lg: 22px;
  --radius-md: 16px;
  --radius-sm: 12px;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SFMono-Regular', monospace;
  color-scheme: dark;
}

:root[data-theme='light'] {
  --bg: #f4f8ff;
  --bg-elevated: rgba(255, 255, 255, 0.86);
  --surface: rgba(255, 255, 255, 0.86);
  --surface-strong: rgba(255, 255, 255, 0.98);
  --surface-soft: rgba(241, 245, 249, 0.92);
  --text: #122033;
  --text-muted: #5d6f8b;
  --text-soft: #2b3f5f;
  --border: rgba(99, 115, 129, 0.16);
  --border-strong: rgba(59, 130, 246, 0.22);
  --accent: #315efb;
  --accent-2: #0284c7;
  --accent-soft: rgba(49, 94, 251, 0.1);
  --shadow: 0 20px 60px rgba(36, 54, 80, 0.12);
  --shadow-soft: 0 10px 28px rgba(36, 54, 80, 0.08);
  color-scheme: light;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: var(--font-sans);
  background:
    radial-gradient(circle at top left, rgba(124, 156, 255, 0.24), transparent 30%),
    radial-gradient(circle at top right, rgba(85, 214, 255, 0.18), transparent 28%),
    linear-gradient(180deg, #050b14 0%, var(--bg) 18%, var(--bg) 100%);
  color: var(--text);
  line-height: 1.7;
  -webkit-text-size-adjust: 100%;
}
:root[data-theme='light'] body {
  background:
    radial-gradient(circle at top left, rgba(99, 102, 241, 0.11), transparent 32%),
    radial-gradient(circle at top right, rgba(56, 189, 248, 0.12), transparent 30%),
    linear-gradient(180deg, #eff5ff 0%, var(--bg) 20%, var(--bg) 100%);
}

a { color: var(--accent-2); text-decoration: none; }
a:hover { text-decoration: underline; }
button, input, select { font: inherit; }
img { max-width: 100%; }

.shell {
  width: min(1200px, calc(100vw - 32px));
  margin: 0 auto;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  padding: 16px 0;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  background: linear-gradient(180deg, rgba(5, 11, 20, 0.9), rgba(5, 11, 20, 0.45));
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}
:root[data-theme='light'] .site-header {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.55));
}

.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}
.brand-mark {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(124, 156, 255, 0.28), rgba(85, 214, 255, 0.28));
  border: 1px solid rgba(124, 156, 255, 0.3);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.18);
  font-size: 24px;
}
.brand-text {
  min-width: 0;
}
.brand-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  color: var(--text-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}
.brand-title {
  margin: 0;
  font-size: clamp(1.05rem, 2vw, 1.2rem);
}
.brand-subtitle {
  margin: 2px 0 0;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.lang-switch {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}
.lang-switch-label {
  padding-left: 10px;
  color: var(--text-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.lang-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  padding: 10px 14px;
  border-radius: 999px;
  color: var(--text-soft);
  font-weight: 600;
  font-size: 0.92rem;
  border: 1px solid transparent;
}
.lang-chip:hover { text-decoration: none; color: var(--text); }
.lang-chip.is-active {
  background: linear-gradient(135deg, rgba(124, 156, 255, 0.22), rgba(85, 214, 255, 0.24));
  border-color: rgba(124, 156, 255, 0.3);
  color: var(--text);
}

.theme-toggle {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  width: 44px;
  height: 44px;
  border-radius: 14px;
  box-shadow: var(--shadow-soft);
  cursor: pointer;
}

.hero {
  padding: 42px 0 28px;
}
.hero-card {
  position: relative;
  overflow: hidden;
  padding: clamp(28px, 5vw, 40px);
  border-radius: var(--radius-xl);
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.78)),
    linear-gradient(135deg, rgba(124, 156, 255, 0.32), transparent 42%),
    linear-gradient(315deg, rgba(85, 214, 255, 0.18), transparent 36%);
  border: 1px solid rgba(124, 156, 255, 0.18);
  box-shadow: var(--shadow);
}
:root[data-theme='light'] .hero-card {
  background:
    linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248, 251, 255, 0.96)),
    linear-gradient(135deg, rgba(124, 156, 255, 0.12), transparent 42%),
    linear-gradient(315deg, rgba(85, 214, 255, 0.12), transparent 36%);
}
.hero-card::after {
  content: '';
  position: absolute;
  inset: auto -60px -90px auto;
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, rgba(85, 214, 255, 0.28), transparent 66%);
  pointer-events: none;
}
.hero-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.9fr);
  gap: 28px;
  align-items: start;
}
.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  border-radius: 999px;
  color: var(--text-soft);
  background: rgba(124, 156, 255, 0.12);
  border: 1px solid rgba(124, 156, 255, 0.14);
  margin-bottom: 18px;
  font-size: 0.84rem;
}
.hero h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.5rem);
  line-height: 1.06;
  letter-spacing: -0.04em;
}
.hero p {
  margin: 18px 0 0;
  font-size: clamp(1rem, 1.6vw, 1.12rem);
  color: var(--text-soft);
  max-width: 62ch;
}
.hero-actions {
  margin-top: 26px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.hero-pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.12);
  color: var(--text-soft);
}
.hero-pill strong { color: var(--text); }

.stats-grid {
  display: grid;
  gap: 14px;
}
.stat-card {
  padding: 18px 18px 16px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: rgba(5, 11, 20, 0.36);
  backdrop-filter: blur(10px);
}
:root[data-theme='light'] .stat-card { background: rgba(255, 255, 255, 0.72); }
.stat-label {
  font-size: 0.76rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.stat-value {
  display: block;
  margin-top: 8px;
  font-size: clamp(1.4rem, 3vw, 2.4rem);
  font-weight: 700;
  letter-spacing: -0.04em;
}
.stat-detail {
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.78fr);
  gap: 24px;
  padding-bottom: 72px;
}

.stack { display: grid; gap: 18px; }
.panel {
  padding: 22px;
  border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}
.panel-title h2,
.panel-title h3 {
  margin: 0;
  font-size: 1.05rem;
}
.panel-title p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.search-box {
  position: relative;
}
.search-box input {
  width: 100%;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: rgba(15, 23, 42, 0.68);
  color: var(--text);
  padding: 14px 16px 14px 46px;
  outline: none;
}
:root[data-theme='light'] .search-box input { background: rgba(255, 255, 255, 0.8); }
.search-box svg {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.report-list {
  display: grid;
  gap: 14px;
}
.report-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.7));
  box-shadow: var(--shadow-soft);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}
:root[data-theme='light'] .report-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92));
}
.report-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-strong);
  box-shadow: var(--shadow);
}
.report-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.report-date {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.report-date strong {
  font-size: 1.1rem;
  color: var(--text);
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--accent-soft);
  border: 1px solid rgba(124, 156, 255, 0.14);
  color: var(--text-soft);
  font-size: 0.82rem;
  font-weight: 600;
}
.report-card h3 {
  margin: 0;
  font-size: 1.1rem;
}
.report-summary {
  color: var(--text-soft);
  margin: 0;
}
.report-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--text-muted);
  font-size: 0.88rem;
}
.report-actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.button, .ghost-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 14px;
  font-weight: 600;
  border: 1px solid transparent;
  cursor: pointer;
}
.button {
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: white;
  box-shadow: 0 12px 24px rgba(49, 94, 251, 0.24);
}
.button:hover, .ghost-button:hover { text-decoration: none; }
.ghost-button {
  color: var(--text);
  background: rgba(148, 163, 184, 0.08);
  border-color: var(--border);
}
.empty-state {
  display: none;
  padding: 22px;
  border: 1px dashed var(--border);
  border-radius: 20px;
  color: var(--text-muted);
  text-align: center;
}
.empty-state.is-visible { display: block; }

.side-list {
  display: grid;
  gap: 12px;
}
.side-link {
  display: grid;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: rgba(148, 163, 184, 0.05);
  color: var(--text);
}
.side-link:hover {
  border-color: var(--border-strong);
  text-decoration: none;
}
.side-link small { color: var(--text-muted); }

.footer {
  padding: 18px 0 40px;
  color: var(--text-muted);
}
.footer-card {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 20px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: rgba(148, 163, 184, 0.06);
}
.footer-card p { margin: 0; }

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  color: var(--text-muted);
  font-size: 0.92rem;
}
.breadcrumbs a { color: var(--text-soft); }

.report-layout {
  display: grid;
  grid-template-columns: minmax(0, 280px) minmax(0, 1fr);
  gap: 24px;
  padding-bottom: 80px;
}
.sticky-column {
  position: sticky;
  top: 94px;
  align-self: start;
}
.report-nav,
.report-tools {
  display: grid;
  gap: 10px;
}
.section-link {
  display: block;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(148, 163, 184, 0.05);
  color: var(--text-soft);
  font-size: 0.94rem;
}
.section-link:hover,
.section-link.is-active {
  color: var(--text);
  border-color: var(--border-strong);
  background: var(--accent-soft);
  text-decoration: none;
}

.report-main {
  display: grid;
  gap: 18px;
}
.report-summary-card,
.report-section,
.markdown-card {
  padding: 24px;
  border-radius: 24px;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--shadow-soft);
}
.report-summary-card p:last-child,
.report-section p:last-child,
.markdown-card p:last-child { margin-bottom: 0; }
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}
.section-kicker {
  color: var(--text-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.report-section h2 {
  margin: 4px 0 0;
  font-size: clamp(1.25rem, 2.5vw, 1.6rem);
}
.rendered-markdown :is(h1,h2,h3,h4) {
  line-height: 1.2;
  letter-spacing: -0.03em;
  margin: 1.1em 0 0.55em;
}
.rendered-markdown h1:first-child,
.rendered-markdown h2:first-child,
.rendered-markdown h3:first-child,
.rendered-markdown h4:first-child { margin-top: 0; }
.rendered-markdown p { margin: 0 0 1em; color: var(--text-soft); }
.rendered-markdown ul,
.rendered-markdown ol { margin: 0 0 1em 1.4em; color: var(--text-soft); }
.rendered-markdown li { margin: 0.45em 0; }
.rendered-markdown blockquote {
  margin: 1.2em 0;
  padding: 16px 18px;
  border-left: 4px solid var(--accent);
  border-radius: 0 18px 18px 0;
  background: rgba(124, 156, 255, 0.08);
  color: var(--text-soft);
}
.rendered-markdown code {
  font-family: var(--font-mono);
  font-size: 0.92em;
  padding: 2px 7px;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.92);
  color: #d6e4ff;
}
.rendered-markdown pre {
  overflow: auto;
  padding: 18px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(124, 156, 255, 0.12);
}
.rendered-markdown pre code { padding: 0; background: transparent; }
.rendered-markdown table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2em 0;
  min-width: 420px;
}
.rendered-markdown .table-wrap {
  overflow-x: auto;
  border-radius: 18px;
  border: 1px solid var(--border);
}
.rendered-markdown th,
.rendered-markdown td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
}
.rendered-markdown th { background: rgba(148, 163, 184, 0.08); }
.rendered-markdown hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.5em 0;
}

.raw-grid {
  display: grid;
  gap: 12px;
}
.raw-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--surface);
}
.raw-card-title { font-weight: 700; }
.raw-card small { color: var(--text-muted); }

.back-to-top {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 30;
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: white;
  box-shadow: var(--shadow-soft);
  display: none;
  cursor: pointer;
}
.back-to-top.is-visible { display: inline-flex; align-items: center; justify-content: center; }

@media (max-width: 980px) {
  .hero-layout,
  .content-grid,
  .report-layout { grid-template-columns: 1fr; }
  .sticky-column { position: static; }
}

@media (max-width: 720px) {
  .shell { width: min(100vw - 20px, 1200px); }
  .site-header { padding: 12px 0; }
  .header-bar,
  .footer-card,
  .report-card-top,
  .raw-card { flex-direction: column; align-items: stretch; }
  .header-actions { justify-content: flex-start; }
  .lang-switch { width: 100%; justify-content: flex-start; overflow-x: auto; }
  .lang-chip { min-width: 64px; }
  .hero-card,
  .panel,
  .report-summary-card,
  .report-section,
  .markdown-card { padding: 18px; border-radius: 22px; }
  .hero h1 { font-size: clamp(1.8rem, 10vw, 2.45rem); }
  .report-actions-row { flex-direction: column; }
  .button, .ghost-button { width: 100%; justify-content: center; }
}
""".strip()

JS = """
(function () {
  var root = document.documentElement;
  var storageKey = 'oracle-research-theme';
  function applyTheme(theme) {
    if (theme === 'light') root.setAttribute('data-theme', 'light');
    else if (theme === 'dark') root.setAttribute('data-theme', 'dark');
    else root.removeAttribute('data-theme');
    var icon = document.querySelector('[data-theme-icon]');
    if (icon) {
      icon.textContent = theme === 'light' ? '☀' : theme === 'dark' ? '☾' : '◐';
    }
  }
  applyTheme(localStorage.getItem(storageKey) || 'auto');
  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-theme-toggle]');
    if (!target) return;
    var current = localStorage.getItem(storageKey) || 'auto';
    var next = current === 'auto' ? 'dark' : current === 'dark' ? 'light' : 'auto';
    localStorage.setItem(storageKey, next);
    applyTheme(next);
  });

  var search = document.querySelector('[data-report-search]');
  if (search) {
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-report-card]'));
    var empty = document.querySelector('[data-search-empty]');
    var runSearch = function () {
      var query = search.value.trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (card) {
        var haystack = (card.getAttribute('data-search') || '').toLowerCase();
        var show = !query || haystack.indexOf(query) !== -1;
        card.style.display = show ? '' : 'none';
        if (show) visible += 1;
      });
      if (empty) empty.classList.toggle('is-visible', visible === 0);
    };
    search.addEventListener('input', runSearch);
    runSearch();
  }

  var topBtn = document.querySelector('[data-back-top]');
  if (topBtn) {
    var onScroll = function () {
      topBtn.classList.toggle('is-visible', window.scrollY > 420);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    topBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  var reportPayload = document.getElementById('report-data');
  if (reportPayload && window.marked) {
    var data = JSON.parse(reportPayload.textContent);
    var container = document.querySelector('[data-report-sections]');
    if (container) {
      marked.setOptions({ gfm: true, breaks: false, mangle: false, headerIds: false });
      var renderer = new marked.Renderer();
      renderer.table = function (header, body) {
        return '<div class="table-wrap"><table><thead>' + header + '</thead><tbody>' + body + '</tbody></table></div>';
      };
      container.innerHTML = data.sections.map(function (section, index) {
        return [
          '<section class="report-section" id="' + section.id + '">',
          '<div class="section-head">',
          '<div>',
          '<div class="section-kicker">' + data.sectionLabel + ' ' + String(index + 1).padStart(2, '0') + '</div>',
          '<h2>' + escapeHtml(section.title) + '</h2>',
          '</div>',
          '<a class="ghost-button" href="#' + section.id + '">#</a>',
          '</div>',
          '<div class="rendered-markdown">' + marked.parse(section.content, { renderer: renderer }) + '</div>',
          '</section>'
        ].join('');
      }).join('');
    }

    var sectionLinks = Array.prototype.slice.call(document.querySelectorAll('[data-section-link]'));
    if (sectionLinks.length) {
      var ids = sectionLinks.map(function (link) { return link.getAttribute('href').replace('#', ''); });
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.getAttribute('id');
          sectionLinks.forEach(function (link) {
            link.classList.toggle('is-active', link.getAttribute('href') === '#' + id);
          });
        });
      }, { rootMargin: '-30% 0px -55% 0px', threshold: 0 });
      ids.forEach(function (id) {
        var node = document.getElementById(id);
        if (node) observer.observe(node);
      });
    }
  }

  function escapeHtml(input) {
    return String(input)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
})();
""".strip()


@dataclass
class Section:
    id: str
    title: str
    content: str


@dataclass
class Report:
    date: str
    raw_markdown: str
    raw_path: str
    title: str
    intro: str
    summary: str
    sections: List[Section]
    word_count: int


def slugify(value: str) -> str:
    cleaned = value.translate(TURKISH_MAP).lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or "section"


def load_cache() -> Dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: Dict[str, str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def translate_google(text: str, target_lang: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": "tr",
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }
    )
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=40) as response:
        data = json.loads(response.read().decode("utf-8"))
    return "".join(part[0] for part in data[0])


def chunk_text(text: str, limit: int = 3200) -> List[str]:
    paragraphs = re.split(r"(\n\n+)", text)
    chunks: List[str] = []
    buffer = ""
    for part in paragraphs:
        if not part:
            continue
        if len(buffer) + len(part) <= limit:
            buffer += part
            continue
        if buffer:
            chunks.append(buffer)
            buffer = ""
        if len(part) <= limit:
            buffer = part
            continue
        lines = re.split(r"(\n)", part)
        for piece in lines:
            if not piece:
                continue
            if len(buffer) + len(piece) <= limit:
                buffer += piece
            else:
                if buffer:
                    chunks.append(buffer)
                buffer = piece
        
    if buffer:
        chunks.append(buffer)
    return chunks


def protect_tokens(text: str) -> Tuple[str, Dict[str, str]]:
    mapping: Dict[str, str] = {}

    def replace(pattern: str, value: str) -> None:
        nonlocal text
        regex = re.compile(pattern, re.MULTILINE)

        def repl(match: re.Match[str]) -> str:
            token = f"[[[{value}_{len(mapping)}]]]"
            mapping[token] = match.group(0)
            return token

        text = regex.sub(repl, text)

    replace(r"https?://[^\s)]+", "URL")
    replace(r"`[^`]+`", "CODE")
    return text, mapping


def restore_tokens(text: str, mapping: Dict[str, str]) -> str:
    for token, original in mapping.items():
        text = text.replace(token, original)
    return text


POST_TRANSLATION_FIXES = {
    "en": {
        "welding streams": "source streams",
        "Automatic compilation": "Automated build",
        "Oracle Night Research": "Oracle Night Research",
    },
    "es": {
        "corrientes de soldadura": "fuentes de origen",
        "Compilación automática": "Generación automática",
    },
}


def apply_post_fixes(text: str, target_lang: str) -> str:
    for old, new in POST_TRANSLATION_FIXES.get(target_lang, {}).items():
        text = text.replace(old, new)
    return text


FENCED_BLOCK_RE = re.compile(r"(```[\s\S]*?```)")


def translate_markdown(markdown: str, target_lang: str, cache: Dict[str, str]) -> str:
    if target_lang == "tr":
        return markdown
    digest = hashlib.sha256((target_lang + "\n" + markdown).encode("utf-8")).hexdigest()
    if digest in cache:
        return cache[digest]

    parts = FENCED_BLOCK_RE.split(markdown)
    translated_parts: List[str] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("```"):
            translated_parts.append(part)
            continue
        protected, mapping = protect_tokens(part)
        translated_chunks = []
        for chunk in chunk_text(protected):
            translated_chunks.append(translate_google(chunk, target_lang))
        translated = "".join(translated_chunks)
        translated = restore_tokens(translated, mapping)
        translated_parts.append(apply_post_fixes(translated, target_lang))

    output = "".join(translated_parts)
    cache[digest] = output
    return output


TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def parse_report(date: str, markdown: str, raw_path: str) -> Report:
    lines = markdown.strip().splitlines()
    title_index = next((idx for idx, line in enumerate(lines) if re.match(r"^#\s*", line)), None)
    if title_index is None:
        fallback_title = f"Oracle Gece Araştırma — {date}"
        fallback_body = markdown.strip()
        fallback_summary = re.sub(r"\s+", " ", fallback_body)
        if len(fallback_summary) > 220:
            fallback_summary = fallback_summary[:217].rstrip() + "..."
        return Report(
            date=date,
            raw_markdown=markdown,
            raw_path=raw_path,
            title=fallback_title,
            intro="",
            summary=fallback_summary,
            sections=[Section(id="sec-1-ozet", title="Özet", content=fallback_body)],
            word_count=len(re.findall(r"\w+", markdown, re.UNICODE)),
        )

    title = re.sub(r"^#\s*", "", lines[title_index]).strip()
    sections: List[Section] = []
    intro_lines: List[str] = []
    current_title: str | None = None
    current_lines: List[str] = []

    def flush_section() -> None:
        nonlocal current_title, current_lines
        if current_title is None:
            return
        body = "\n".join(current_lines).strip()
        sections.append(Section(id=f"sec-{len(sections)+1}-{slugify(current_title)[:48]}", title=current_title, content=body))
        current_title = None
        current_lines = []

    for line in lines[title_index + 1:]:
        if re.match(r"^##\s*", line):
            flush_section()
            current_title = re.sub(r"^##\s*", "", line).strip()
        elif current_title is None:
            intro_lines.append(line)
        else:
            current_lines.append(line)
    flush_section()

    intro = "\n".join(intro_lines).strip()
    summary = ""
    for candidate in intro.splitlines() + [section.content for section in sections]:
        cleaned = candidate.strip().lstrip("> ").strip()
        if cleaned:
            summary = cleaned
            break
    summary = re.sub(r"\s+", " ", summary)
    if len(summary) > 220:
        summary = summary[:217].rstrip() + "..."

    word_count = len(re.findall(r"\w+", markdown, re.UNICODE))
    return Report(
        date=date,
        raw_markdown=markdown,
        raw_path=raw_path,
        title=title,
        intro=intro,
        summary=summary,
        sections=sections,
        word_count=word_count,
    )


def clean_intro(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip() != "---"]
    return "\n".join(lines).strip()


def build_summary(intro: str, sections: List[Section]) -> str:
    candidates = intro.splitlines() + [section.content for section in sections]
    for candidate in candidates:
        cleaned = candidate.strip().lstrip("> ").strip()
        if cleaned and not cleaned.startswith("#"):
            cleaned = re.sub(r"\s+", " ", cleaned)
            if len(cleaned) > 220:
                return cleaned[:217].rstrip() + "..."
            return cleaned
    return ""


def suspicious_section_title(title: str) -> bool:
    return (
        len(title) > 80
        or "http" in title
        or "**" in title
        or re.search(r"\d\.\s", title) is not None
        or title.count(" ") > 10
    )


def translate_heading_text(text: str, level: int, target_lang: str, cache: Dict[str, str]) -> str:
    if re.fullmatch(r"KAT-\d+", text) or text.isupper():
        return text
    translated = translate_markdown(f"{'#' * level} {text}", target_lang, cache)
    return re.sub(rf"^#{{{level}}}\s*", "", translated).strip()


def translate_report(report: Report, target_lang: str, cache: Dict[str, str]) -> Report:
    if target_lang == "tr":
        return report
    translated_markdown = translate_markdown(report.raw_markdown, target_lang, cache)
    translated = parse_report(report.date, translated_markdown, report.raw_path)

    translated_title = translate_heading_text(report.title, 1, target_lang, cache)
    translated_intro = clean_intro(translate_markdown(report.intro, target_lang, cache)) if report.intro else ""

    translated_sections: List[Section] = []
    force_section_retranslate = (
        len(translated.sections) != len(report.sections)
        or any(suspicious_section_title(section.title) for section in translated.sections)
    )
    for index, original in enumerate(report.sections):
        parsed_section = translated.sections[index] if index < len(translated.sections) else None
        section_title = translate_heading_text(original.title, 2, target_lang, cache)
        if force_section_retranslate or parsed_section is None:
            section_content = translate_markdown(original.content, target_lang, cache)
        else:
            section_content = parsed_section.content.strip() or translate_markdown(original.content, target_lang, cache)
        translated_sections.append(Section(id=original.id, title=section_title, content=section_content))

    return Report(
        date=report.date,
        raw_markdown=translated_markdown,
        raw_path=report.raw_path,
        title=translated_title,
        intro=translated_intro,
        summary=build_summary(translated_intro, translated_sections),
        sections=translated_sections,
        word_count=len(re.findall(r"\w+", translated_markdown, re.UNICODE)),
    )


def relative_root(lang: str) -> Path:
    if lang == "tr":
        return ROOT
    return ROOT / lang


def lang_path(lang: str, suffix: str = "") -> str:
    if lang == "tr":
        return suffix or "index.html"
    return f"{lang}/{suffix or 'index.html'}"


def report_rel_path(lang: str, date: str) -> str:
    return f"reports/{date}.html" if lang == "tr" else f"{lang}/reports/{date}.html"


def raw_index_rel_path(lang: str) -> str:
    return "raw/index.html" if lang == "tr" else f"{lang}/raw/index.html"


def absolute_url(relative: str) -> str:
    return f"{SITE_URL}/{relative}"


def relative_href(from_rel: str, to_rel: str) -> str:
    from_dir = posixpath.dirname(from_rel) or "."
    return posixpath.relpath(to_rel, from_dir)


def page_title(lang: str, title: str) -> str:
    return f"{title} · {LANGS[lang]['site_title']}"


def render_lang_switch(current_lang: str, paths: Dict[str, str], label: str) -> str:
    chips = []
    for code, meta in LANGS.items():
        active = " is-active" if code == current_lang else ""
        chips.append(f'<a class="lang-chip{active}" href="{html.escape(paths[code])}" lang="{code}">{html.escape(meta["label"][:2].upper())}</a>')
    return (
        f'<div class="lang-switch">'
        f'<span class="lang-switch-label">{html.escape(label)}</span>'
        + "".join(chips)
        + "</div>"
    )


def render_header(lang: str, subtitle: str, lang_paths: Dict[str, str], home_href: str) -> str:
    return f"""
<header class=\"site-header\">
  <div class=\"shell header-bar\">
    <a class=\"brand\" href=\"{home_href}\">
      <span class=\"brand-mark\">🦉</span>
      <span class=\"brand-text\">
        <span class=\"brand-kicker\">Oracle archive</span>
        <h1 class=\"brand-title\">{html.escape(LANGS[lang]['site_title'])}</h1>
        <p class=\"brand-subtitle\">{html.escape(subtitle)}</p>
      </span>
    </a>
    <div class=\"header-actions\">
      {render_lang_switch(lang, lang_paths, LANGS[lang]['lang_switch'])}
      <button class=\"theme-toggle\" type=\"button\" data-theme-toggle aria-label=\"Toggle theme\"><span data-theme-icon>◐</span></button>
    </div>
  </div>
</header>
""".strip()


def base_head(lang: str, title: str, description: str, canonical_rel: str, alternate_paths: Dict[str, str], asset_prefix: str) -> str:
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{absolute_url(path)}">' for code, path in alternate_paths.items()
    )
    return f"""
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<meta name=\"description\" content=\"{html.escape(description)}\">
<title>{html.escape(page_title(lang, title))}</title>
<link rel=\"canonical\" href=\"{absolute_url(canonical_rel)}\">
{alternates}
<link rel=\"alternate\" hreflang=\"x-default\" href=\"{absolute_url(canonical_rel if lang == 'tr' else alternate_paths['tr'])}\">
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap\" rel=\"stylesheet\">
<link rel=\"stylesheet\" href=\"{asset_prefix}assets/site.css\">
<script defer src=\"{asset_prefix}assets/site.js\"></script>
""".strip()


def render_index_page(lang: str, reports_by_lang: Dict[str, List[Report]], generated_at: str) -> str:
    labels = LANGS[lang]
    reports = reports_by_lang[lang]
    latest = reports[0]
    current_rel = lang_path(lang)
    report_cards = []
    for report in reports:
        raw_href = relative_href(current_rel, f"raw/{report.date}.md")
        report_href = relative_href(current_rel, report_rel_path(lang, report.date))
        search_text = f"{report.date} {report.title} {report.summary}"
        report_cards.append(
            f"""
<article class=\"report-card\" data-report-card data-search=\"{html.escape(search_text)}\">
  <div class=\"report-card-top\">
    <div>
      <div class=\"report-date\"><strong>{html.escape(report.date)}</strong><span>· {len(report.sections)} {html.escape(labels['sections_count'])}</span></div>
      <h3>{html.escape(report.title)}</h3>
    </div>
    <span class=\"badge\">{html.escape(labels['report_badge'])}</span>
  </div>
  <p class=\"report-summary\">{html.escape(report.summary)}</p>
  <div class=\"report-meta\">
    <span>{report.word_count} {html.escape(labels['word_count_label'])}</span>
    <span>{len(report.sections)} {html.escape(labels['sections_count'])}</span>
  </div>
  <div class=\"report-actions-row\">
    <a class=\"button\" href=\"{html.escape(report_href)}\">{html.escape(labels['view_report'])}</a>
    <a class=\"ghost-button\" href=\"{html.escape(raw_href)}\">{html.escape(labels['view_raw'])}</a>
  </div>
</article>
""".strip()
        )

    raw_archive_href = relative_href(current_rel, raw_index_rel_path(lang))
    lang_paths = {code: relative_href(current_rel, lang_path(code)) for code in LANGS}
    asset_prefix = "" if lang == "tr" else "../"
    alternate_paths = {code: lang_path(code) for code in LANGS}
    page = f"""
<!doctype html>
<html lang=\"{lang}\">
<head>
  {base_head(lang, labels['site_title'], labels['meta_description'], lang_path(lang), alternate_paths, asset_prefix)}
</head>
<body>
  {render_header(lang, labels['site_tagline'], lang_paths, relative_href(current_rel, lang_path(lang)))}
  <main class=\"shell\">
    <section class=\"hero\">
      <div class=\"hero-card\">
        <div class=\"hero-layout\">
          <div>
            <span class=\"hero-kicker\">{html.escape(labels['generated_with'])}</span>
            <h1>{html.escape(labels['archive_title'])}</h1>
            <p>{html.escape(labels['archive_subtitle'])}</p>
            <div class=\"hero-actions\">
              <span class=\"hero-pill\"><strong>{html.escape(labels['latest_report'])}</strong> {html.escape(latest.date)}</span>
              <span class=\"hero-pill\"><strong>{len(LANGS)}</strong> {html.escape(labels['languages']).lower()}</span>
            </div>
          </div>
          <div class=\"stats-grid\">
            <div class=\"stat-card\">
              <span class=\"stat-label\">{html.escape(labels['total_reports'])}</span>
              <span class=\"stat-value\">{len(reports)}</span>
              <div class=\"stat-detail\">{html.escape(labels['report_intro'])}</div>
            </div>
            <div class=\"stat-card\">
              <span class=\"stat-label\">{html.escape(labels['date_range'])}</span>
              <span class=\"stat-value\">{html.escape(reports[-1].date)} → {html.escape(reports[0].date)}</span>
              <div class=\"stat-detail\">{html.escape(generated_at)}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class=\"content-grid\">
      <div class=\"stack\">
        <div class=\"panel\">
          <div class=\"panel-title\">
            <div>
              <h2>{html.escape(labels['archive_title'])}</h2>
              <p>{html.escape(labels['search_label'])}</p>
            </div>
          </div>
          <label class=\"search-box\">
            <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"11\" cy=\"11\" r=\"7\"></circle><path d=\"M20 20l-3.5-3.5\"></path></svg>
            <input type=\"search\" placeholder=\"{html.escape(labels['search_placeholder'])}\" data-report-search>
          </label>
        </div>
        <div class=\"report-list\">{' '.join(report_cards)}</div>
        <div class=\"empty-state\" data-search-empty>{html.escape(labels['search_empty'])}</div>
      </div>
      <aside class=\"stack\">
        <div class=\"panel\">
          <div class=\"panel-title\"><div><h3>{html.escape(labels['latest_report'])}</h3><p>{html.escape(latest.summary)}</p></div></div>
          <div class=\"side-list\">
            <a class=\"side-link\" href=\"{relative_href(current_rel, report_rel_path(lang, latest.date))}\">
              <strong>{html.escape(latest.title)}</strong>
              <small>{html.escape(latest.date)} · {len(latest.sections)} sections</small>
            </a>
          </div>
        </div>
        <div class=\"panel\">
          <div class=\"panel-title\"><div><h3>{html.escape(labels['raw_archive_title'])}</h3><p>{html.escape(labels['raw_archive_subtitle'])}</p></div></div>
          <a class=\"side-link\" href=\"{html.escape(raw_archive_href)}\">
            <strong>{html.escape(labels['browse_raw'])}</strong>
            <small>{html.escape(labels['open_original'])}</small>
          </a>
        </div>
      </aside>
    </section>
  </main>
  <footer class=\"shell footer\">
    <div class=\"footer-card\">
      <p>{html.escape(labels['footer_note'])}</p>
      <p>{html.escape(generated_at)}</p>
    </div>
  </footer>
  <button class=\"back-to-top\" type=\"button\" data-back-top aria-label=\"Back to top\">↑</button>
</body>
</html>
""".strip()
    return page + "\n"


def render_report_page(lang: str, report: Report, reports_by_lang: Dict[str, List[Report]], generated_at: str) -> str:
    labels = LANGS[lang]
    report_list = reports_by_lang[lang]
    index_lookup = {item.date: idx for idx, item in enumerate(report_list)}
    idx = index_lookup[report.date]
    prev_report = report_list[idx + 1] if idx + 1 < len(report_list) else None
    next_report = report_list[idx - 1] if idx - 1 >= 0 else None

    current_rel = report_rel_path(lang, report.date)
    asset_prefix = "../" if lang == "tr" else "../../"
    home_href = relative_href(current_rel, lang_path(lang))
    raw_href = relative_href(current_rel, f"raw/{report.date}.md")
    lang_paths = {code: relative_href(current_rel, report_rel_path(code, report.date)) for code in LANGS}
    summary_html = html.escape(report.summary)
    section_links = "".join(
        f'<a class="section-link" href="#{section.id}" data-section-link>{html.escape(section.title)}</a>'
        for section in report.sections
    )
    payload = {
        "sectionLabel": labels["section_nav"],
        "sections": [{"id": s.id, "title": s.title, "content": s.content} for s in report.sections],
    }
    alternate_paths = {code: report_rel_path(code, report.date) for code in LANGS}
    page = f"""
<!doctype html>
<html lang=\"{lang}\">
<head>
  {base_head(lang, report.title, f"{labels['report_meta_description']} {report.date}", report_rel_path(lang, report.date), alternate_paths, asset_prefix)}
</head>
<body>
  {render_header(lang, report.date, lang_paths, home_href)}
  <main class=\"shell\">
    <section class=\"hero\">
      <div class=\"hero-card\">
        <div class=\"hero-layout\">
          <div>
            <div class=\"breadcrumbs\"><a href=\"{home_href}\">{html.escape(labels['back_to_archive'])}</a><span>•</span><span>{html.escape(report.date)}</span></div>
            <span class=\"hero-kicker\">{html.escape(labels['report_badge'])}</span>
            <h1>{html.escape(report.title)}</h1>
            <p>{summary_html}</p>
            <div class=\"hero-actions\">
              <span class=\"hero-pill\"><strong>{len(report.sections)}</strong> {html.escape(labels['sections_count'])}</span>
              <span class=\"hero-pill\"><strong>{report.word_count}</strong> {html.escape(labels['word_count_label'])}</span>
            </div>
          </div>
          <div class=\"stats-grid\">
            <div class=\"stat-card\">
              <span class=\"stat-label\">{html.escape(labels['summary_label'])}</span>
              <div class=\"stat-detail\">{summary_html}</div>
            </div>
            <div class=\"stat-card\">
              <span class=\"stat-label\">{html.escape(labels['report_actions'])}</span>
              <div class=\"report-actions-row\" style=\"margin-top:12px\">
                <a class=\"button\" href=\"{raw_href}\">{html.escape(labels['view_raw'])}</a>
                <a class=\"ghost-button\" href=\"{home_href}\">{html.escape(labels['archive_title'])}</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class=\"report-layout\">
      <aside class=\"sticky-column stack\">
        <div class=\"panel\">
          <div class=\"panel-title\"><div><h3>{html.escape(labels['toc_label'])}</h3><p>{html.escape(labels['report_intro'])}</p></div></div>
          <nav class=\"report-nav\">{section_links}</nav>
        </div>
        <div class=\"panel\">
          <div class=\"panel-title\"><div><h3>{html.escape(labels['report_actions'])}</h3></div></div>
          <div class=\"report-tools\">
            <a class=\"ghost-button\" href=\"{raw_href}\">{html.escape(labels['raw_source'])}</a>
            <a class=\"ghost-button\" href=\"{lang_paths['tr']}\">{html.escape(labels['open_original'])}</a>
            {f'<a class="ghost-button" href="{relative_href(current_rel, report_rel_path(lang, prev_report.date))}">{html.escape(labels["prev_report"])}' + '</a>' if prev_report else ''}
            {f'<a class="ghost-button" href="{relative_href(current_rel, report_rel_path(lang, next_report.date))}">{html.escape(labels["next_report"])}' + '</a>' if next_report else ''}
          </div>
        </div>
      </aside>
      <div class=\"report-main\">
        <section class=\"report-summary-card rendered-markdown\">
          <div class=\"section-head\">
            <div>
              <div class=\"section-kicker\">{html.escape(labels['report_overview'])}</div>
              <h2>{html.escape(labels['report_overview'])}</h2>
            </div>
          </div>
          {markdown_to_html(clean_intro(report.intro))}
        </section>
        <div data-report-sections></div>
      </div>
    </section>
  </main>
  <footer class=\"shell footer\">
    <div class=\"footer-card\">
      <p>{html.escape(labels['footer_note'])}</p>
      <p>{html.escape(generated_at)}</p>
    </div>
  </footer>
  <script id=\"report-data\" type=\"application/json\">{html.escape(json.dumps(payload, ensure_ascii=False))}</script>
  <script src=\"https://cdn.jsdelivr.net/npm/marked@9.1.6/marked.min.js\"></script>
  <button class=\"back-to-top\" type=\"button\" data-back-top aria-label=\"Back to top\">↑</button>
</body>
</html>
""".strip()
    return page + "\n"


INLINE_STRONG_RE = re.compile(r"\*\*(.+?)\*\*")
INLINE_EM_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
URL_ONLY_RE = re.compile(r"(https?://[^\s<]+)")


def apply_inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = LINK_RE.sub(lambda m: f'<a href="{html.escape(m.group(2))}">{html.escape(m.group(1))}</a>', escaped)
    escaped = URL_ONLY_RE.sub(lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>', escaped)
    escaped = INLINE_CODE_RE.sub(lambda m: f'<code>{html.escape(m.group(1))}</code>', escaped)
    escaped = INLINE_STRONG_RE.sub(lambda m: f'<strong>{m.group(1)}</strong>', escaped)
    escaped = INLINE_EM_RE.sub(lambda m: f'<em>{m.group(1)}</em>', escaped)
    return escaped


TABLE_SPLIT_RE = re.compile(r"^\|.*\|$")


def markdown_to_html(markdown: str) -> str:
    if not markdown.strip():
        return ""
    lines = markdown.strip().splitlines()
    chunks: List[str] = []
    paragraph: List[str] = []
    list_buffer: List[str] = []
    quote_buffer: List[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            chunks.append(f"<p>{apply_inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_buffer
        if list_buffer:
            items = "".join(f"<li>{apply_inline_markdown(item)}</li>" for item in list_buffer)
            chunks.append(f"<ul>{items}</ul>")
            list_buffer = []

    def flush_quote() -> None:
        nonlocal quote_buffer
        if quote_buffer:
            content = " ".join(quote_buffer)
            chunks.append(f"<blockquote><p>{apply_inline_markdown(content)}</p></blockquote>")
            quote_buffer = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph(); flush_list(); flush_quote()
            continue
        if stripped.startswith(">"):
            flush_paragraph(); flush_list()
            quote_buffer.append(stripped.lstrip("> "))
            continue
        if stripped.startswith("- "):
            flush_paragraph(); flush_quote()
            list_buffer.append(stripped[2:].strip())
            continue
        if stripped.startswith("### "):
            flush_paragraph(); flush_list(); flush_quote()
            chunks.append(f"<h3>{apply_inline_markdown(stripped[4:])}</h3>")
            continue
        if stripped.startswith("## "):
            flush_paragraph(); flush_list(); flush_quote()
            chunks.append(f"<h2>{apply_inline_markdown(stripped[3:])}</h2>")
            continue
        paragraph.append(stripped)
    flush_paragraph(); flush_list(); flush_quote()
    return "\n".join(chunks)


def render_raw_index(lang: str, reports_by_lang: Dict[str, List[Report]], generated_at: str) -> str:
    labels = LANGS[lang]
    reports = reports_by_lang[lang]
    current_rel = raw_index_rel_path(lang)
    asset_prefix = "../" if lang == "tr" else "../../"
    lang_paths = {code: relative_href(current_rel, raw_index_rel_path(code)) for code in LANGS}
    raw_cards = []
    for report in reports:
        raw_href = relative_href(current_rel, f"raw/{report.date}.md")
        rendered_href = relative_href(current_rel, report_rel_path(lang, report.date))
        raw_cards.append(
            f"""
<div class=\"raw-card\">
  <div>
    <div class=\"raw-card-title\">{html.escape(report.date)}</div>
    <small>{html.escape(report.title)}</small>
  </div>
  <div class=\"report-actions-row\">
    <a class=\"ghost-button\" href=\"{html.escape(raw_href)}\">{html.escape(labels['view_raw'])}</a>
    <a class=\"button\" href=\"{html.escape(rendered_href)}\">{html.escape(labels['view_rendered'])}</a>
  </div>
</div>
""".strip()
        )
    alternate_paths = {code: raw_index_rel_path(code) for code in LANGS}
    page = f"""
<!doctype html>
<html lang=\"{lang}\">
<head>
  {base_head(lang, labels['raw_archive_title'], labels['raw_meta_description'], raw_index_rel_path(lang), alternate_paths, asset_prefix)}
</head>
<body>
  {render_header(lang, labels['raw_archive_subtitle'], lang_paths, relative_href(current_rel, raw_index_rel_path(lang)))}
  <main class=\"shell\">
    <section class=\"hero\">
      <div class=\"hero-card\">
        <span class=\"hero-kicker\">{html.escape(labels['raw_source'])}</span>
        <h1>{html.escape(labels['raw_archive_title'])}</h1>
        <p>{html.escape(labels['raw_archive_subtitle'])}</p>
        <div class=\"hero-actions\">
          <a class=\"button\" href=\"{relative_href(current_rel, lang_path(lang))}\">{html.escape(labels['archive_title'])}</a>
        </div>
      </div>
    </section>
    <section class=\"raw-grid\">{' '.join(raw_cards)}</section>
  </main>
  <footer class=\"shell footer\">
    <div class=\"footer-card\">
      <p>{html.escape(labels['footer_note'])}</p>
      <p>{html.escape(generated_at)}</p>
    </div>
  </footer>
  <button class=\"back-to-top\" type=\"button\" data-back-top aria-label=\"Back to top\">↑</button>
</body>
</html>
""".strip()
    return page + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_feed(reports: List[Report], generated_dt: datetime) -> str:
    items = []
    for report in reports:
        pub_date = format_datetime(datetime.fromisoformat(report.date).replace(hour=1, tzinfo=timezone.utc))
        link = absolute_url(report_rel_path("tr", report.date))
        items.append(
            f"""
    <item>
      <title>{html.escape(report.title)}</title>
      <link>{link}</link>
      <guid isPermaLink=\"true\">{link}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{html.escape(report.summary)}</description>
    </item>
""".rstrip()
        )
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">
  <channel>
    <title>{LANGS['tr']['site_title']}</title>
    <link>{SITE_URL}/</link>
    <description>{LANGS['tr']['feed_description']}</description>
    <language>tr</language>
    <lastBuildDate>{format_datetime(generated_dt)}</lastBuildDate>
    <atom:link href=\"{SITE_URL}/feed.xml\" rel=\"self\" type=\"application/rss+xml\"/>
    <generator>oracle_arastirma/scripts/build_site.py</generator>
{''.join(items)}
  </channel>
</rss>
"""


def generate_latest_json(reports: List[Report], generated_dt: datetime) -> str:
    latest = reports[0]
    payload = {
        "status": "ok",
        "generated_at": generated_dt.isoformat(),
        "latest": {
            "title": latest.title,
            "date": latest.date,
            "url": absolute_url(report_rel_path("tr", latest.date)),
            "filename": f"{latest.date}.html",
            "alternates": {code: absolute_url(report_rel_path(code, latest.date)) for code in LANGS},
        },
        "total_reports": len(reports),
        "feed_url": f"{SITE_URL}/feed.xml",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def generate_sitemap(reports: List[Report]) -> str:
    urls = [
        absolute_url("index.html"),
        absolute_url("en/index.html"),
        absolute_url("es/index.html"),
        absolute_url("raw/index.html"),
        absolute_url("en/raw/index.html"),
        absolute_url("es/raw/index.html"),
    ]
    for report in reports:
        for code in LANGS:
            urls.append(absolute_url(report_rel_path(code, report.date)))
    body = "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls)
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
{body}
</urlset>
"""


def load_reports() -> List[Report]:
    reports = []
    for path in sorted(RAW_DIR.glob("*.md"), reverse=True):
        markdown = path.read_text(encoding="utf-8")
        reports.append(parse_report(path.stem, markdown, f"raw/{path.name}"))
    if not reports:
        raise SystemExit("No raw markdown files found.")
    return reports


def refresh_output_dirs() -> None:
    for path in [ASSETS_DIR, EN_DIR, ES_DIR, REPORTS_DIR, ROOT / "raw"]:
        path.mkdir(parents=True, exist_ok=True)
    for locale_dir in [EN_DIR / "reports", ES_DIR / "reports", EN_DIR / "raw", ES_DIR / "raw"]:
        locale_dir.mkdir(parents=True, exist_ok=True)


def update_readme() -> None:
    content = textwrap.dedent(
        """
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
        """
    ).strip() + "\n"
    write_text(ROOT / "README.md", content)


def main() -> None:
    refresh_output_dirs()
    cache = load_cache()
    source_reports = load_reports()

    reports_by_lang: Dict[str, List[Report]] = {"tr": source_reports}
    for lang in ["en", "es"]:
        translated_reports: List[Report] = []
        total = len(source_reports)
        for index, report in enumerate(source_reports, start=1):
            print(f"[{lang}] translating {index}/{total}: {report.date}", flush=True)
            translated_reports.append(translate_report(report, lang, cache))
            save_cache(cache)
        reports_by_lang[lang] = translated_reports

    generated_dt = datetime.now(timezone.utc)
    generated_at_label = generated_dt.strftime("%Y-%m-%d %H:%M UTC")

    write_text(ASSETS_DIR / "site.css", CSS + "\n")
    write_text(ASSETS_DIR / "site.js", JS + "\n")
    write_text(ROOT / "index.html", render_index_page("tr", reports_by_lang, generated_at_label))
    write_text(EN_DIR / "index.html", render_index_page("en", reports_by_lang, generated_at_label))
    write_text(ES_DIR / "index.html", render_index_page("es", reports_by_lang, generated_at_label))
    write_text(ROOT / "raw" / "index.html", render_raw_index("tr", reports_by_lang, generated_at_label))
    write_text(EN_DIR / "raw" / "index.html", render_raw_index("en", reports_by_lang, generated_at_label))
    write_text(ES_DIR / "raw" / "index.html", render_raw_index("es", reports_by_lang, generated_at_label))

    for lang, reports in reports_by_lang.items():
        base_dir = ROOT if lang == "tr" else ROOT / lang
        for report in reports:
            write_text(base_dir / "reports" / f"{report.date}.html", render_report_page(lang, report, reports_by_lang, generated_at_label))

    write_text(ROOT / "feed.xml", generate_feed(source_reports, generated_dt))
    write_text(ROOT / "api" / "latest.json", generate_latest_json(source_reports, generated_dt))
    write_text(ROOT / "sitemap.xml", generate_sitemap(source_reports))
    update_readme()


if __name__ == "__main__":
    main()
