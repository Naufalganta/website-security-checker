# Website Security Checker

Website Security Checker adalah aplikasi Python berbasis Streamlit untuk memeriksa konfigurasi keamanan dasar pada sebuah website.

Project ini dibuat sebagai portofolio cyber security dasar dengan pendekatan pemeriksaan pasif, seperti HTTPS, SSL certificate, dan security headers.

## Fitur

- Cek penggunaan HTTPS
- Cek SSL certificate
- Cek masa berlaku SSL
- Cek HTTP status code
- Cek security headers:
  - Content-Security-Policy
  - Strict-Transport-Security
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
  - Permissions-Policy
- Security score sederhana
- Rekomendasi perbaikan

## Tech Stack

- Python
- Streamlit
- Requests
- SSL
- Socket

## Cara Menjalankan

1. Clone repository

```bash
git clone https://github.com/username/website-security-checker.git
```

2. Masuk ke folder project

```bash
cd website-security-checker
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Jalankan aplikasi

```bash
streamlit run app.py
```

## Contoh Penggunaan

Masukkan domain atau URL:

```text
example.com
```

Aplikasi akan menampilkan hasil pemeriksaan HTTPS, SSL, security headers, score, dan rekomendasi.

## Catatan Etika

Tool ini hanya melakukan pemeriksaan pasif terhadap konfigurasi website. Gunakan hanya pada website milik sendiri, website lab, atau website yang memang diizinkan untuk diuji.

## Pengembang

Naufal Ganta  
Python Developer | Web Developer | Cyber Security Enthusiast