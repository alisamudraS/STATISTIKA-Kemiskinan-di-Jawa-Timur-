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

# Simpan grafik atau tabel sebagai file gambar berkualitas tinggi
def save_figure_as_image(fig, dpi=600):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    buf.seek(0)
    return buf

# Peramalan menggunakan metode Kuadrat Terkecil
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

# Fungsi untuk menyesuaikan lebar segmen lingkaran
def adjust_pie_sizes(sizes, min_percent=1, max_percent=5):
    total = sum(sizes)
    adjusted_sizes = []

    for size in sizes:
        percent = (size / total) * 100
        if percent < min_percent:
            adjusted_sizes.append(min_percent)  # Berikan nilai minimum untuk segmen kecil
        elif percent > max_percent:
            adjusted_sizes.append(max_percent)  # Batasi ukuran maksimum segmen besar
        else:
            adjusted_sizes.append(percent)  # Gunakan ukuran asli jika sesuai

    # Skalakan kembali ke total ukuran asli
    scaling_factor = total / sum(adjusted_sizes)
    adjusted_sizes = [size * scaling_factor for size in adjusted_sizes]
    return adjusted_sizes

# Fungsi utama untuk layar Grafik Se-Jawa Timur
def sejawatimurscreen():
    st.title("Grafik dan Tabel Se-Jawa Timur")

    # Pilihan Tahun untuk Grafik Lingkaran
    year = st.selectbox("Pilih Tahun", [str(y) for y in range(2007, 2028)])  # Tambahkan tahun 2025–2027

    # Grafik Lingkaran Berdasarkan Tahun
    if st.button("Generate Grafik Lingkaran"):
        if year in ["2025", "2026", "2027"]:
            # Data ramalan
            all_data = fetch_total_data()
            if not all_data.empty:
                all_data = all_data[all_data["id"] != "jawa timur"]
                forecast_years = ["2025", "2026", "2027"]

                # Hitung total peramalan
                forecast_totals = []
                for _, row in all_data.iterrows():
                    years = [col for col in row.index if col.isnumeric()]
                    values = row[years].values.astype(float)
                    _, forecast_values = forecast_least_squares(years, pd.Series(values), forecast_years)
                    forecast_totals.append(sum(forecast_values))

                labels = all_data["id"].tolist()
                sizes = adjust_pie_sizes(forecast_totals, min_percent=1, max_percent=5)

                # Grafik Lingkaran
                fig, ax = plt.subplots(figsize=(20, 20))
                explode = [0.05 if size > (sum(sizes) * 0.05) else 0 for size in sizes]
                wedges, texts, autotexts = ax.pie(
                    sizes,
                    labels=labels,
                    autopct='%1.1f%%',
                    startangle=140,
                    explode=explode,
                    labeldistance=1.4,
                    pctdistance=0.85,
                    wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'}
                )
                ax.set_title(f"Distribusi Penduduk Miskin - Tahun {year} (Ramalan)")
                plt.tight_layout()
                st.pyplot(fig)

                # Tombol Download Grafik Lingkaran
                buf = save_figure_as_image(fig)
                st.download_button(
                    label=f"Download Grafik Lingkaran {year}",
                    data=buf,
                    file_name=f"grafik_lingkaran_{year}.png",
                    mime="image/png"
                )
        else:
            # Data asli
            year_data = fetch_by_year(year)
            if not year_data.empty:
                labels = year_data["id"]
                sizes = adjust_pie_sizes(year_data[year].values, min_percent=1, max_percent=5)

                # Grafik Lingkaran
                fig, ax = plt.subplots(figsize=(20, 20))
                explode = [0.05 if size > (sum(sizes) * 0.05) else 0 for size in sizes]
                wedges, texts, autotexts = ax.pie(
                    sizes,
                    labels=labels,
                    autopct='%1.1f%%',
                    startangle=140,
                    explode=explode,
                    labeldistance=1.4,
                    pctdistance=0.85,
                    wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'}
                )
                ax.set_title(f"Distribusi Penduduk Miskin - Tahun {year}")
                plt.tight_layout()
                st.pyplot(fig)

                # Tombol Download Grafik Lingkaran
                buf = save_figure_as_image(fig)
                st.download_button(
                    label=f"Download Grafik Lingkaran {year}",
                    data=buf,
                    file_name=f"grafik_lingkaran_{year}.png",
                    mime="image/png"
                )

    # Grafik Batang Jawa Timur
    if st.button("Generate Grafik Batang Total Jawa Timur"):
        total_data = fetch_total_data()
        if not total_data.empty:
            total_data = total_data[total_data["id"] == "jawa timur"]
            years = [col for col in total_data.columns if col.isnumeric()]
            values = total_data.iloc[0][years]

            # Peramalan untuk 2025-2027
            forecast_years = ["2025", "2026", "2027"]
            forecast_years, forecast_values = forecast_least_squares(years, values, forecast_years)

            # Gabungkan data asli dan ramalan
            all_years = years + forecast_years
            all_values = list(values) + list(forecast_values)

            # Grafik Batang
            fig, ax = plt.subplots(figsize=(20, 10))
            ax.bar(years, values, color="skyblue", label="Data Asli")
            ax.bar(forecast_years, forecast_values, color="orange", label="Data Ramalan")
            ax.plot(all_years, all_values, color="red", marker="o", label="Tren Data dan Ramalan")
            ax.set_title("Grafik Total Jumlah Penduduk Miskin - Jawa Timur (2007–2027)")
            ax.set_xlabel("Tahun")
            ax.set_ylabel("Jumlah Penduduk Miskin (Ribu)")
            ax.legend()
            plt.tight_layout()
            st.pyplot(fig)

            # Tombol Download Grafik Batang
            buf = save_figure_as_image(fig)
            st.download_button(
                label="Download Grafik Batang Jawa Timur",
                data=buf,
                file_name="grafik_batang_jawa_timur.png",
                mime="image/png"
            )

            # Tabel Data Jawa Timur (2007–2027)
            table_data = pd.DataFrame({
                "Tahun": all_years,
                "Jumlah Penduduk Miskin (Ribu)": all_values
            })
            st.dataframe(table_data)
            buf = BytesIO()
            table_data.to_csv(buf, index=False)
            st.download_button(
                label="Download Tabel Jawa Timur",
                data=buf.getvalue(),
                file_name="tabel_jawa_timur.csv",
                mime="text/csv"
            )

    # Tabel Semua Daerah dengan Ramalan
    if st.button("Tampilkan Tabel Lengkap Semua Daerah"):
        all_data = fetch_total_data()
        if not all_data.empty:
            all_data = all_data[all_data["id"] != "jawa timur"]
            forecast_years = ["2025", "2026", "2027"]

            # Tambahkan data ramalan untuk setiap daerah
            full_table = []
            for _, row in all_data.iterrows():
                years = [col for col in row.index if col.isnumeric()]
                values = row[years].values.astype(float)
                _, forecast_values = forecast_least_squares(years, pd.Series(values), forecast_years)
                row_data = list(values) + list(forecast_values)
                full_table.append([row["id"]] + row_data)

            # Buat tabel lengkap
            columns = ["Daerah"] + years + forecast_years
            full_table_df = pd.DataFrame(full_table, columns=columns)
            st.dataframe(full_table_df)

            # Tombol Download Tabel Lengkap
            buf = BytesIO()
            full_table_df.to_csv(buf, index=False)
            st.download_button(
                label="Download Tabel Lengkap Semua Daerah",
                data=buf.getvalue(),
                file_name="tabel_lengkap_semua_daerah.csv",
                mime="text/csv"
            )

    # Tombol Kembali ke Menu Utama
    if st.button("Kembali"):
        st.session_state.screen = "menu"
