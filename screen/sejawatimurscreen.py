import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client
import config
from io import BytesIO

# Koneksi ke Supabase
def connect_supabase() -> Client:
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# Ambil data berdasarkan tahun
def fetch_by_year(year):
    supabase = connect_supabase()
    response = supabase.table("jumlah_penduduk_miskin").select(f"id, {year}").neq("id", "jawa timur").execute()
    return pd.DataFrame(response.data)

# Ambil semua data untuk total
def fetch_total_data():
    supabase = connect_supabase()
    response = supabase.table("jumlah_penduduk_miskin").select("*").execute()
    return pd.DataFrame(response.data)

# Fungsi untuk menyimpan grafik sebagai file gambar berkualitas tinggi
def save_figure_as_image(fig, dpi=600):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)  # Simpan grafik dengan DPI tinggi
    buf.seek(0)
    return buf

# Fungsi utama untuk layar Grafik Se-Jawa Timur
def sejawatimurscreen():
    st.title("Grafik Se-Jawa Timur")
    
    # Pilihan Tahun untuk Grafik Lingkaran
    year = st.selectbox("Pilih Tahun", [str(y) for y in range(2007, 2025)])
    
    # Tombol: Generate Grafik Lingkaran Berdasarkan Tahun
    if st.button("Generate Grafik Lingkaran"):
        year_data = fetch_by_year(year)
        if not year_data.empty:
            labels = year_data["id"]
            sizes = year_data[year]
            
            # Gabungkan segmen kecil
            threshold = 1  # Segmen dengan nilai <1% akan digabung
            filtered_labels = []
            filtered_sizes = []
            other_size = 0

            for label, size in zip(labels, sizes):
                percentage = (size / sum(sizes)) * 100
                if percentage < threshold:
                    other_size += size
                else:
                    filtered_labels.append(label)
                    filtered_sizes.append(size)

            # Tambahkan kategori "Lainnya"
            if other_size > 0:
                filtered_labels.append("Lainnya")
                filtered_sizes.append(other_size)

            # Buat Grafik Lingkaran
            fig, ax = plt.subplots(figsize=(20, 20))
            explode = [0.05 if size > (sum(filtered_sizes) * 0.05) else 0 for size in filtered_sizes]  # Pisahkan segmen besar
            wedges, texts, autotexts = ax.pie(
                filtered_sizes,
                labels=filtered_labels,
                autopct='%1.1f%%',
                startangle=140,
                explode=explode,
                labeldistance=1.4,  # Jarak label
                pctdistance=0.85,   # Jarak persentase
                wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'}  # Tambah ruang antar segmen
            )
            ax.set_title(f"Distribusi Penduduk Miskin - Tahun {year}")
            plt.tight_layout()  # Hindari elemen terpotong
            
            # Tampilkan Grafik di Streamlit
            st.pyplot(fig)

            # Tombol Download
            buf = save_figure_as_image(fig)
            st.download_button(
                label="Download Grafik Lingkaran",
                data=buf,
                file_name=f"grafik_lingkaran_{year}.png",
                mime="image/png"
            )
        else:
            st.write("Data tidak ditemukan.")
    
    # Tombol: Generate Grafik Batang Total Jawa Timur
    if st.button("Generate Grafik Batang Total Jawa Timur"):
        total_data = fetch_total_data()
        if not total_data.empty:
            total_data = total_data[total_data["id"] == "jawa timur"]
            years = [col for col in total_data.columns if col.isnumeric()]
            values = total_data.iloc[0][years]
            
            # Buat Grafik Batang
            fig, ax = plt.subplots(figsize=(20, 10))
            ax.bar(years, values, color="skyblue", label="Data")
            ax.plot(years, values, color="red", marker="o", label="Tren")
            ax.set_title("Grafik Total Jumlah Penduduk Miskin - Jawa Timur (2007–2024)")
            ax.set_xlabel("Tahun")
            ax.set_ylabel("Jumlah Penduduk Miskin (Ribu)")
            ax.legend()
            plt.tight_layout()

            # Tampilkan Grafik di Streamlit
            st.pyplot(fig)

            # Tombol Download
            buf = save_figure_as_image(fig)
            st.download_button(
                label="Download Grafik Batang",
                data=buf,
                file_name="grafik_batang_jawa_timur.png",
                mime="image/png"
            )
        else:
            st.write("Data tidak ditemukan.")
    
    # Tombol: Generate Grafik Lingkaran Total Semua Tahun
    if st.button("Generate Grafik Lingkaran Total Semua Tahun"):
        total_data = fetch_total_data()
        if not total_data.empty:
            total_data = total_data[total_data["id"] != "jawa timur"]
            total_data["total"] = total_data[[str(y) for y in range(2007, 2025)]].sum(axis=1)
            labels = total_data["id"]
            sizes = total_data["total"]
            
            # Atur Grafik Lingkaran Total
            fig, ax = plt.subplots(figsize=(20, 20))
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                startangle=140,
                labeldistance=1.4,
                pctdistance=0.85,
                wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'}
            )
            ax.set_title("Distribusi Total Penduduk Miskin - Semua Tahun (2007–2024)")
            plt.tight_layout()
            st.pyplot(fig)

            # Tombol Download
            buf = save_figure_as_image(fig)
            st.download_button(
                label="Download Grafik Lingkaran Total",
                data=buf,
                file_name="grafik_lingkaran_total_semua_tahun.png",
                mime="image/png"
            )
        else:
            st.write("Data tidak ditemukan.")
    
    # Tombol Kembali ke Menu Utama
    if st.button("Kembali"):
        st.session_state.screen = "menu"
