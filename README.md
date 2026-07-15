---
title: Sistem AI Ghazwah
emoji: 🤖
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# AI Command Center — Sistem Orkestrasi 8-Agent

Platform orkestrasi multi-agent AI: pengguna beri arahan kepada **Claudia (Manager)**, dan dia mengagihkan tugasan kepada 7 agent pakar (marketing, sales, finance, content, teknikal, latihan, operasi). Dibina dengan **FastAPI** + **NVIDIA NIM (Llama 3.1 / Kimi)**, storan hasil kerja ke **Google Drive**.

## Mula Pantas

| Cara | Arahan |
|---|---|
| Windows (mudah) | Klik dua kali `setup_dan_run.bat` |
| Manual | `pip install -r requirements.txt` kemudian `python main.py` |
| Docker | `docker build -t ai-command-center . && docker run -d -p 7860:7860 ai-command-center` |

Dashboard: `http://localhost:7860`. Konfigurasi `.env` diperlukan — rujuk [panduan pemasangan](docs/architecture/sistem-semasa.md#4-panduan-instalasi).

## Struktur Repo

```
├── main.py                 # Backend FastAPI + orkestrasi agent (aplikasi penuh)
├── index.html              # Dashboard web (single page)
├── tests/                  # Ujian pytest
├── docs/
│   ├── architecture/       # sistem-semasa.md (senibina semasa) · proposal-v2.md (DRAF v2)
│   ├── business/           # Dokumentasi produk untuk client/pemasaran
│   ├── frontend/           # Design system dashboard
│   ├── development/        # Rekod audit & nota pembangunan
│   └── archive/            # Dokumen lama yang dikekalkan untuk rujukan
├── Dockerfile              # Deployment (port 7860)
└── .github/workflows/      # Auto-sync ke Hugging Face Spaces
```

## Dokumentasi

- [Senibina & panduan teknikal sistem semasa](docs/architecture/sistem-semasa.md)
- [Cadangan senibina v2 — multi-tenant SaaS](docs/architecture/proposal-v2.md) — **status: DRAF, menunggu approval**
- [Design system dashboard ("dokumen pejabat")](docs/frontend/dashboard-design.md)
- [Dokumentasi perniagaan (untuk client)](docs/business/dokumentasi-perniagaan.md)
- [Laporan audit keselamatan (Julai 2026)](docs/development/audit-report-2026-07.md)

## Deployment

⚠️ **Setiap push ke `main` auto-deploy (force push) ke Hugging Face Spaces** melalui [sync_to_hf.yml](.github/workflows/sync_to_hf.yml). Pastikan perubahan telah diuji sebelum push. Secrets diisi di Settings Hugging Face Space.
