import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Maria - Especialista Pingo Doce", page_icon="🍷")

# Estilo Pingo Doce
st.markdown("<style>.stApp {background-color: #f9fdf9;} h1 {color: #2e7d32;}</style>", unsafe_allow_html=True)

st.title("🌿 Maria - Especialista em Vinhos")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Tentamos o modelo Flash. Se falhar, o código no 'except' pode ser ajustado,
        # mas aqui vamos garantir a chamada correta:
        model = genai.GenerativeModel('gemini-1.5-flash')

        vinho = st.text_input("Qual é o vinho?", placeholder="Ex: Papa Figos...")

        if vinho:
            with st.spinner('A Maria está a escolher a melhor combinação...'):
                prompt = f"És a Maria, uma especialista em vinhos portuguesa. O utilizador tem este vinho: {vinho}. Sugere uma receita portuguesa e explica a harmonização. Responde em PT-PT."
                
                # Forçamos a geração de conteúdo
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
                
    except Exception as e:
        # Se der erro 404 com o flash, tentamos o pro automaticamente
        if "404" in str(e):
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e2:
                st.error(f"Erro técnico persistente: {e2}")
        else:
            st.error(f"Erro técnico: {e}")
else:
    st.error("Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
