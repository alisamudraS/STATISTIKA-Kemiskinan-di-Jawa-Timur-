import streamlit as st

def menuscreen():
    st.title("Menu Utama")
    st.write("Pilih menu untuk melanjutkan:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Grafik Per Daerah"):
            st.session_state.screen = "perdaerah"
    with col2:
        if st.button("Grafik Se-Jawa Timur"):
            st.session_state.screen = "sejawatimur"
