import streamlit as st

def awalscreen():
    st.title("Aplikasi Analisis Dan Peramalan Penduduk Miskin")
    st.write("Selamat datang di aplikasi analisis dan peramalan jumlah penduduk miskin di Jawa Timur.")
    
    if st.button("Mulai"):
        st.session_state.screen = "menu"
