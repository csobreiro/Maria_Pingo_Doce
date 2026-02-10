import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# 1. Configuração da Página
st.set_page_config(page_title="Maria - Especialista Pingo Doce", page_icon="🍷")

st.markdown("""
    <style>
    .stApp {background-color: #f9fdf9;}
    h1 {color: #2e7d32;}
    .stTextInput > div > div > input {border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Maria - Especialista em Vinhos")

# 2. Validação da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
# Usando a versão estável mais recente
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Carregar a Base de Dados (Tabela Vinho)
@st.cache_data
def load_data():
    # Carrega o CSV que enviaste (garante que o nome do ficheiro está correto no GitHub)
    try:
        df = pd.read_csv("Tabela Vinho.xlsx - Sheet1.csv")
        return df
    except:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input(
    "Qual é o vinho que vai abrir?", 
    placeholder="Ex: Papa Figos, Pingo Doce Alvarinho, Monsaraz...",
    max_chars=100
)

if vinho_input:
    with st.spinner('A Maria está a analisar...'):
        resultado_interno = None
        
        # Tenta procurar na tabela local primeiro
        if df_vinhos is not None:
            # Procura por correspondência parcial no nome do vinho (ignorando maiúsculas)
            busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
            if not busca.empty:
                resultado_interno = busca.iloc[0]

        # Se encontrou na tabela, mostra os dados exatos
        if resultado_interno is not None:
            st.success(f"Encontrei este vinho na nossa seleção Pingo Doce!")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Preço aprox.", resultado_interno['Preço (aprox.)'])
                st.write(f"**Região:** {resultado_interno['Região / Produtor']}")
            with col2:
                st.write(f"**Descrição:** {resultado_interno['Descrição']}")
            
            st.markdown(f"### 🍴 Sugestão de Receita:")
            st.info(f"**{resultado_interno['Receita Pingo Doce Sugerida']}**")
            
        # Se NÃO encontrou na tabela, a IA assume o comando
        else:
            prompt = f"""
            És a Maria, especialista em vinhos do Pingo Doce. 
            O utilizador perguntou por um vinho que não está na minha lista imediata: {vinho_input}.
            1. Descreve brevemente o perfil deste vinho.
            2. Sugere uma receita típica portuguesa que combine bem.
            3. Explica a razão da combinação.
            Responde em Português de Portugal com um tom simpático e profissional.
            """
            try:
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {e}")

st.markdown("---")
st.caption("Maria - Assistente Pingo Doce | 2026")
