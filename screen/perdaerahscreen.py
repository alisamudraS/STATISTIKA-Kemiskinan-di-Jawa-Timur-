import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client
import config
from io import BytesIO

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

# Simpan grafik sebagai file gambar berkualitas tinggi
def save_figure_as_image(fig, dpi=600):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)  # Simpan grafik dengan DPI tinggi
    buf.seek(0)
    return buf

# Fungsi utama untuk layar Grafik Per Daerah
def perdaerahscreen():
    st.title("Grafik Per Daerah")
    data = fetch_all_data()
    
    # Pilih daerah
    region = st.selectbox("Pilih Daerah", data["id"].unique())
    
    if st.button("Generate"):
        region_data = fetch_by_region(region)
        if not region_data.empty:
            years = [col for col in region_data.columns if col.isnumeric()]
            values = region_data.iloc[0][years]
            
            # Buat grafik batang
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(years, values, label="Data")
            ax.plot(years, values, color="red", marker="o", label="Tren")
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
    
    # Tambahkan tombol "Kembali"
    if st.button("Kembali"):
        st.session_state.screen = "menu"
