# BRIEF ANTIGRAVITY — Pembetulan Keselamatan Login (Susulan Audit)
## Projek: InfinityAI-Solutions
Repo: https://github.com/ferlin070/InfinityAI-Solutions

---

## 0. KONTEKS

Audit terhadap commit Fasa 2 (login) jumpa 4 isu keselamatan pada `backend/src/api/routes.py`. Ini brief kecil, fokus **hanya** pada pembetulan isu-isu ni — bukan fitur baharu. Ingat: setiap push ke `main` auto-deploy ke Hugging Face Spaces, jadi versi sekarang kemungkinan **sudah live** dengan isu-isu ni.

---

## 1. GUARDRAILS

- Jangan ubah struktur endpoint sedia ada (`/api/login`, `/api/me`, `/api/logout`, `/api/history`, `/api/execute`) — hanya ubah logic dalaman.
- Jangan tambah dependency baharu (contoh: `bcrypt`, `argon2-cffi`) tanpa cadangkan dulu — untuk Fasa 1 di bawah, guna `hmac` (built-in Python) sahaja, tiada install diperlukan.
- Jangan buang test sedia ada (`test_api_me_route`, `test_pwa_manifest`, `test_pwa_sw`, dll) — tambah test baharu untuk setiap fix.
- Jangan merge/deploy tanpa pengesahan saya.
- Edit bersasar sahaja — jangan refactor `routes.py` secara menyeluruh.

---

## 2. FASA KERJA — IKUT SEVERITY, BERURUTAN

### FASA 1 — CRITICAL: `secure=True` pada cookie session
**Fail:** `backend/src/api/routes.py` (baris ~42-48, `response.set_cookie(...)`)

- Tukar `secure=False` → `secure=True`.
- **Sebab:** Hugging Face Spaces sudah serve melalui HTTPS. `secure=False` bermakna cookie boleh terdedah kepada downgrade/interception walaupun laman guna HTTPS.
- Jika ini akan pecahkan testing tempatan (`http://localhost` bukan HTTPS), guna env var untuk toggle:
  ```python
  import os
  IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"
  # ...
  response.set_cookie(
      key="session_token",
      value=token,
      httponly=True,
      samesite="lax",
      secure=IS_PRODUCTION
  )
  ```
- Pastikan `.env.example` ada `ENVIRONMENT=production` sebagai contoh, dan `.env` production sebenar diset betul di Hugging Face Space Settings.
- **Checkpoint:** tunjuk perubahan kod + confirm `ENVIRONMENT` diset betul di HF Spaces secrets sebelum push.

### FASA 2 — CRITICAL: Fail-fast jika `ADMIN_PASSWORD` tiada
**Fail:** `backend/src/core/config.py` (atau mana-mana startup config sedia ada)

- Sistem MESTI refuse untuk start (raise exception / `sys.exit(1)`) jika `ADMIN_PASSWORD` atau `ADMIN_EMAIL` tidak diset di environment — jangan biar fallback senyap ke `password123`.
- Contoh:
  ```python
  ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
  ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

  if not ADMIN_EMAIL or not ADMIN_PASSWORD:
      raise RuntimeError(
          "ADMIN_EMAIL dan ADMIN_PASSWORD wajib diset di .env — "
          "sistem tidak akan start tanpa kelayakan admin yang sah."
      )
  ```
- Fallback `password123` **hanya** dibenarkan bila `ENVIRONMENT != "production"` (untuk local dev sahaja), dan mesti papar amaran jelas di console log bila fallback digunakan.
- **Checkpoint:** demo — jalankan backend tanpa `.env` diisi, sahkan ia crash dengan mesej jelas (bukan senyap fallback).

### FASA 3 — HIGH: Elak timing attack pada perbandingan password
**Fail:** `backend/src/api/routes.py` (baris ~40, `data.password == ADMIN_PASSWORD`)

- Tukar kepada `hmac.compare_digest()` — built-in Python, tiada dependency baharu:
  ```python
  import hmac

  if not hmac.compare_digest(data.password, ADMIN_PASSWORD):
      raise HTTPException(status_code=401, detail="E-mel atau kata laluan salah. Sila cuba lagi.")
  ```
- Ini fix minimum untuk sekarang. **Cadangan jangka panjang** (bincang dengan saya dahulu sebelum implement): tukar kepada hash `bcrypt`/`argon2` disimpan sebagai `ADMIN_PASSWORD_HASH` di `.env`, banding guna `checkpw()`. Ini lebih selamat kalau `.env` bocor. Jangan implement bahagian hash ni sekarang — cadangkan dulu, saya nak tengok kesan pada proses deployment (perlu generate hash dan update `.env` di HF Spaces).
- **Checkpoint:** tunjuk diff + jalankan test sedia ada untuk pastikan tiada regresi pada login flow.

### FASA 4 — MEDIUM: Rate-limiting pada `/api/login`
**Fail:** `backend/src/api/routes.py`, mungkin perlu `backend/src/core/middleware.py`

- Cadangkan pendekatan dahulu kepada saya sebelum implement — pilihan:
  - In-memory counter mudah (simpan percubaan gagal + timestamp, block IP selepas N percubaan dalam tempoh masa tertentu) — tiada dependency baharu, tapi reset bila server restart.
  - Library `slowapi` (FastAPI rate limiter) — perlu install dependency, minta kelulusan saya dulu.
- Nyatakan: had percubaan (cadangan: 5 percubaan / 15 minit), tempoh lockout, dan mesej ralat untuk pengguna (Bahasa Melayu, tanpa dedah sebab teknikal — cth: "Terlalu banyak percubaan. Sila cuba lagi selepas beberapa minit.").
- **Checkpoint:** bentangkan cadangan dahulu — jangan implement sebelum saya luluskan pendekatan.

---

## 3. KRITERIA PENERIMAAN

- Semua test sedia ada (`test_api_me_route`, `test_api_logout`, `test_pwa_manifest`, `test_pwa_sw`, dll) masih PASS.
- Test baharu ditambah untuk setiap fasa (contoh: `test_login_fails_without_env_credentials`, `test_secure_cookie_in_production`).
- Login flow sedia ada (login → dashboard → logout) masih berfungsi tanpa regresi selepas setiap fasa.
- Tiada credential/secret baharu terdedah dalam kod atau log.

---

**Nota untuk Antigravity:** Fasa 1 dan 2 (CRITICAL) kena buat dan push **secepat mungkin** memandangkan auto-deploy sedia ada — tapi tetap ikut checkpoint, jangan gabung dengan Fasa 3/4 dalam commit yang sama. Fasa 4 tunggu cadangan diluluskan dulu sebelum kod ditulis.
