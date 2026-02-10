import streamlit as st
import google.generativeai as genai
import os

# Configuração da Página
st.set_page_config(page_title="Maria - Especialista Pingo Doce", page_icon="🍷")

st.title("🌿 Maria - Especialista em Vinhos")

# Tenta ler a chave de dois sítios (Secrets do Streamlit ou Variáveis de Ambiente)
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        vinho = st.text_input("Qual é o vinho ou região?", placeholder="Ex: Papa Figos, Muralhas, Cartuxa...")

        if vinho:
            with st.spinner('A Maria está a escolher a melhor combinação...'):
                prompt = f"""
                És a Maria, uma assistente pessoal portuguesa. 
                O utilizador tem este vinho: {vinho}.
                1. Identifica o vinho e sugere uma receita com ingredientes frescos.
                2. Explica a harmonização (acidez, corpo).
                3. Dá uma dica de mestre.
                Responde em Português de Portugal com negritos.
                """
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
                st.balloons()
    except Exception as e:
        # Isto vai mostrar o erro real para sabermos o que falhou
        st.error(f"Erro técnico: {e}")
else:
    st.error("A chave API não foi encontrada nos Secrets do Streamlit.")
