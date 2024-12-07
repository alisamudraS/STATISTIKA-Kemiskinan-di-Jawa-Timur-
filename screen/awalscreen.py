import streamlit as st

def awalscreen():
    st.title("Aplikasi Analisis Penduduk Miskin")
    st.write("Selamat datang di aplikasi analisis jumlah penduduk miskin di Jawa Timur.")
    
    if st.button("Mulai"):
        st.session_state.screen = "menu"
