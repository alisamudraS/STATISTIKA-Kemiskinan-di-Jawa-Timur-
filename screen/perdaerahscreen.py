import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client
import config
from io import BytesIO
import numpy as np

# Koneksi ke Supabase
def connect_supabase() -> Client:
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# Ambil semua data
def fetch_all_data():
    supabase = connect_supabase()
    response = supabase.table("jumlah_penduduk_miskin").select("*").neq("id", "jawa timur").execute()
    return pd.DataFrame(response.data)

# Ambil data berdasarkan daerah
def fetch_by_region(region_name):
    supabase = connect_supabase()
    response = supabase.table("jumlah_penduduk_miskin").select("*").eq("id", region_name).execute()
    return pd.DataFrame(response.data)

# Simpan grafik atau tabel sebagai file gambar berkualitas tinggi
def save_figure_as_image(fig, dpi=600):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    buf.seek(0)
    return buf

# Fungsi untuk melakukan peramalan menggunakan metode Kuadrat Terkecil
def forecast_least_squares(years, values, forecast_years):
    x = np.arange(len(years))
    y = values.values.astype(float)

    # Hitung koefisien regresi linier
    A = np.vstack([x, np.ones(len(x))]).T
    a, b = np.linalg.lstsq(A, y, rcond=None)[0]

    # Prediksi untuk tahun-tahun mendatang
    x_forecast = np.arange(len(years), len(years) + len(forecast_years))
    forecast_values = a * x_forecast + b

    return forecast_years, forecast_values

# Fungsi utama untuk layar Grafik Per Daerah
def perdaerahscreen():
    st.title("Grafik dan Tabel Per Daerah")
    data = fetch_all_data()
    
    # Pilih daerah
    region = st.selectbox("Pilih Daerah", data["id"].unique())
    
    # Tombol untuk generate grafik
    if st.button("Generate Grafik"):
        region_data = fetch_by_region(region)
        if not region_data.empty:
            # Data asli
            years = [col for col in region_data.columns if col.isnumeric()]
            values = region_data.iloc[0][years]

            # Peramalan untuk tahun 2025-2027
            forecast_years = ["2025", "2026", "2027"]
            forecast_years, forecast_values = forecast_least_squares(years, values, forecast_years)

            # Gabungkan data asli dengan data ramalan
            all_years = years + forecast_years
            all_values = list(values) + list(forecast_values)

            # Buat grafik batang
            fig, ax = plt.subplots(figsize=(10, 6))
            # Data asli
            ax.bar(years, values, label="Data Asli", color="blue")
            ax.plot(years, values, color="red", marker="o", label="Tren Data Asli")
            # Data peramalan
            ax.bar(forecast_years, forecast_values, label="Data Ramalan", color="orange")
            ax.plot(forecast_years, forecast_values, color="green", marker="x", linestyle="--", label="Tren Ramalan")
            
            # Atur tampilan grafik
            ax.set_title(f"Grafik Jumlah Penduduk Miskin - {region.capitalize()}")
            ax.set_xlabel("Tahun")
            ax.set_ylabel("Jumlah Penduduk Miskin (Ribu)")
            ax.legend()
            plt.tight_layout()
            
            # Tampilkan grafik di Streamlit
            st.pyplot(fig)

            # Tambahkan tombol download
            buf = save_figure_as_image(fig)
            st.download_button(
                label="Download Grafik Batang",
                data=buf,
                file_name=f"grafik_batang_{region}.png",
                mime="image/png"
            )
        else:
            st.write("Data tidak ditemukan.")
    
    # Tombol untuk generate tabel
    if st.button("Generate Tabel"):
        region_data = fetch_by_region(region)
        if not region_data.empty:
            # Data asli
            years = [col for col in region_data.columns if col.isnumeric()]
            values = region_data.iloc[0][years]

            # Peramalan untuk tahun 2025-2027
            forecast_years = ["2025", "2026", "2027"]
            _, forecast_values = forecast_least_squares(years, values, forecast_years)

            # Gabungkan data asli dengan ramalan
            all_years = years + forecast_years
            all_values = list(values) + list(forecast_values)

            # Buat DataFrame untuk tabel
            table_data = pd.DataFrame({
                "Tahun": all_years,
                "Jumlah Penduduk Miskin (Ribu)": all_values
            })

            # Tampilkan tabel di Streamlit
            st.dataframe(table_data)

            # Buat tabel sebagai gambar
            fig, ax = plt.subplots(figsize=(12, len(all_years) // 2))
            ax.axis("off")
            ax.axis("tight")
            ax.table(cellText=table_data.values, colLabels=table_data.columns, loc="center", cellLoc="center")
            plt.tight_layout()

            # Tambahkan tombol download
            buf = save_figure_as_image(fig)
            st.download_button(
                label="Download Tabel",
                data=buf,
                file_name=f"tabel_{region}.png",
                mime="image/png"
            )
        else:
            st.write("Data tidak ditemukan.")
    
    # Tombol kembali
    if st.button("Kembali"):
        st.session_state.screen = "menu"
