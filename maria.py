import streamlit as st
import requests
import json

st.set_page_config(page_title="Maria - Especialista Pingo Doce", page_icon="🍷")

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
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets")
    st.stop()

# TESTE DA API KEY - MUITO IMPORTANTE
st.sidebar.title("🔧 Diagnóstico")

if st.sidebar.button("🧪 Testar API Key"):
    with st.sidebar:
        st.info("A testar ligação à API...")
        
        # Testa listar modelos
        url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        try:
            response = requests.get(url_list, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'models' in data:
                    modelos = [
                        m['name'] for m in data['models'] 
                        if 'generateContent' in m.get('supportedGenerationMethods', [])
                    ]
                    
                    if modelos:
                        st.success(f"✅ API Key válida!")
                        st.write(f"**{len(modelos)} modelos disponíveis:**")
                        for m in modelos:
                            st.code(m)
                    else:
                        st.error("❌ API Key válida MAS sem modelos disponíveis")
                        st.warning("Sua conta não tem acesso aos modelos Gemini")
                        st.markdown("""
                        **Causas possíveis:**
                        - Região bloqueada
