import streamlit as st
from screen.awalscreen import awalscreen
from screen.menuscreen import menuscreen
from screen.perdaerahscreen import perdaerahscreen
from screen.sejawatimurscreen import sejawatimurscreen

# Inisialisasi session_state
if "screen" not in st.session_state:
    st.session_state.screen = "awal"

if st.session_state.screen == "awal":
    awalscreen()
elif st.session_state.screen == "menu":
    menuscreen()
elif st.session_state.screen == "perdaerah":
    perdaerahscreen()
elif st.session_state.screen == "sejawatimur":
    sejawatimurscreen()
else:
    st.write("Halaman tidak ditemukan.")
