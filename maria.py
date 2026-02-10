import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Maria - Especialista Pingo Doce", page_icon="🍷")

# Estilo Pingo Doce
st.markdown("""
    <style>
    .stApp {background-color: #f9fdf9;}
    h1 {color: #2e7d32;}
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Maria - Especialista em Vinhos")

# Validação da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

# Configuração do modelo
genai.configure(api_key=api_key)

# Usa o modelo mais recente e rápido: Gemini 2.5 Flash
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Input do utilizador
vinho = st.text_input(
    "Qual é o vinho?", 
    placeholder="Ex: Papa Figos, Esporão Reserva, Periquita...",
    max_chars=100
)

if vinho and vinho.strip():
    vinho
