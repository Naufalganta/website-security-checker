import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse

import requests
import streamlit as st


SECURITY_HEADERS = {
    "Content-Security-Policy": "Membantu mencegah XSS dan injection attack.",
    "Strict-Transport-Security": "Memaksa browser menggunakan HTTPS.",
    "X-Frame-Options": "Mencegah clickjacking.",
    "X-Content-Type-Options": "Mencegah MIME sniffing.",
    "Referrer-Policy": "Mengontrol informasi referrer yang dikirim browser.",
    "Permissions-Policy": "Membatasi akses fitur browser seperti camera/location.",
}


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def get_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.split(":")[0]


def check_http_headers(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        return {
            "ok": True,
            "status_code": response.status_code,
            "final_url": response.url,
            "headers": dict(response.headers),
            "error": None,
        }
    except requests.RequestException as e:
        return {
            "ok": False,
            "status_code": None,
            "final_url": None,
            "headers": {},
            "error": str(e),
        }


def check_ssl_certificate(domain: str) -> dict:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                cert = secure_sock.getpeercert()

        expiry_text = cert.get("notAfter")
        expiry_date = datetime.strptime(expiry_text, "%b %d %H:%M:%S %Y %Z")
        days_left = (expiry_date - datetime.utcnow()).days

        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))

        return {
            "ok": True,
            "issuer": issuer.get("organizationName", "Unknown"),
            "subject": subject.get("commonName", "Unknown"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "days_left": days_left,
            "error": None,
        }
    except Exception as e:
        return {
            "ok": False,
            "issuer": None,
            "subject": None,
            "expiry_date": None,
            "days_left": None,
            "error": str(e),
        }


def calculate_score(headers: dict, ssl_result: dict, is_https: bool) -> tuple[int, list[str]]:
    score = 0
    recommendations = []

    if is_https:
        score += 20
    else:
        recommendations.append("Gunakan HTTPS untuk melindungi koneksi pengguna.")

    if ssl_result["ok"] and ssl_result["days_left"] is not None:
        if ssl_result["days_left"] > 30:
            score += 20
        else:
            recommendations.append("Perbarui SSL certificate karena masa berlaku hampir habis.")
    else:
        recommendations.append("Pastikan SSL certificate valid dan dapat diverifikasi.")

    for header in SECURITY_HEADERS:
        if header in headers:
            score += 10
        else:
            recommendations.append(f"Tambahkan header keamanan: {header}")

    return min(score, 100), recommendations


st.set_page_config(
    page_title="Website Security Checker",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ Website Security Checker")
st.write(
    "Tool sederhana untuk memeriksa HTTPS, SSL certificate, dan security headers pada sebuah website."
)

target = st.text_input("Masukkan URL website", placeholder="contoh: example.com")

if st.button("Scan Website"):
    url = normalize_url(target)

    if not url:
        st.warning("Masukkan URL terlebih dahulu.")
        st.stop()

    domain = get_domain(url)
    is_https = url.startswith("https://")

    st.subheader("Target")
    st.write(f"URL: `{url}`")
    st.write(f"Domain: `{domain}`")

    with st.spinner("Memeriksa website..."):
        http_result = check_http_headers(url)
        ssl_result = check_ssl_certificate(domain) if is_https else {
            "ok": False,
            "issuer": None,
            "subject": None,
            "expiry_date": None,
            "days_left": None,
            "error": "Website tidak menggunakan HTTPS.",
        }

    if not http_result["ok"]:
        st.error(f"Gagal mengakses website: {http_result['error']}")
        st.stop()

    headers = http_result["headers"]
    score, recommendations = calculate_score(headers, ssl_result, is_https)

    st.subheader("Security Score")
    st.progress(score / 100)
    st.metric("Score", f"{score}/100")

    st.subheader("HTTP Status")
    st.write(f"Status Code: `{http_result['status_code']}`")
    st.write(f"Final URL: `{http_result['final_url']}`")

    st.subheader("HTTPS & SSL")
    if is_https:
        st.success("Website menggunakan HTTPS.")
    else:
        st.error("Website tidak menggunakan HTTPS.")

    if ssl_result["ok"]:
        st.write(f"Issuer: `{ssl_result['issuer']}`")
        st.write(f"Subject: `{ssl_result['subject']}`")
        st.write(f"Expired Date: `{ssl_result['expiry_date']}`")
        st.write(f"Days Left: `{ssl_result['days_left']} hari`")
    else:
        st.warning(f"SSL tidak dapat diverifikasi: {ssl_result['error']}")

    st.subheader("Security Headers")
    for header, description in SECURITY_HEADERS.items():
        if header in headers:
            st.success(f"{header} ditemukan")
            st.caption(description)
        else:
            st.error(f"{header} tidak ditemukan")
            st.caption(description)

    st.subheader("Rekomendasi")
    if recommendations:
        for item in recommendations:
            st.write(f"- {item}")
    else:
        st.success("Konfigurasi dasar keamanan website sudah cukup baik.")

    st.info(
        "Catatan: Tool ini hanya melakukan pemeriksaan pasif terhadap header dan SSL. "
        "Gunakan hanya pada website milik sendiri atau website yang memang diizinkan untuk diuji."
    )