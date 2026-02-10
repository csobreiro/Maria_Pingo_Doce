import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="A Maria do Pingo Doce", 
    page_icon="🍷",
    layout="centered"
)

# Estilo Adaptativo (Light/Dark Mode Automático)
st.markdown("""
    <style>
    /* O Streamlit já gere o fundo, vamos apenas estilizar os componentes */
    .vinho-box {
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2e7d32;
        margin-bottom: 25px;
        /* Esta cor adapta-se ligeiramente por ser semi-transparente */
        background-color: rgba(46, 125, 50, 0.1);
    }
    h1 {
        color: #2e7d32;
    }
    /* Ajuste para inputs no telemóvel */
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 A Maria do Pingo Doce")
st.markdown("##### O seu guia de vinhos e receitas adaptativo.")

# 2. Configuração da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

# 3. Carregamento da Tabela
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tabela Vinho.xlsx - Sheet1.csv")
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input(
    "Que vinho escolheu?", 
    placeholder="Escreva o nome do vinho...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    resultado_interno = None
    
    # Busca na tabela (Case Insensitive)
    if df_vinhos is not None:
        busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
        if not busca.empty:
            resultado_interno = busca.iloc[0]

    # --- MOMENTO 1: INFORMAÇÃO IMEDIATA ---
    st.markdown("### 🍷 Momento 1: O Sommelier")
    
    if resultado_interno is not None:
        nome_vinho = resultado_interno['Nome do Vinho']
        produtor = resultado_interno['Região / Produtor']
        prato_sugerido = resultado_interno['Receita Pingo Doce Sugerida']
        
        st.markdown(f"""
        <div class="vinho-box">
            <strong>🍷 Vinho:</strong> {nome_vinho}<br>
            <strong>🏷️ Produtor / Região:</strong> {produtor}<br>
            <strong>🤝 Harmonização:</strong> Este vinho pede um excelente <strong>{prato_sugerido}</strong>.
        </div>
        """, unsafe_allow_html=True)
        
        info_ia = f"Vinho: {nome_vinho} ({produtor}). Prato: {prato_sugerido}."
        nome_final_prato = prato_sugerido
    else:
        st.info("A analisar o perfil do seu vinho...")
        info_ia = vinho_input
        nome_final_prato = f"uma receita para acompanhar {vinho_input}"

    # --- MOMENTO 2: GERAÇÃO DA RECEITA ---
    st.markdown("---")
    with st.spinner('A Maria está a escrever a receita...'):
        prompt = f"""
        És a Maria, cozinheira portuguesa. O utilizador já viu o produtor e a harmonização.
        Apresenta APENAS a receita detalhada para: {nome_final_prato}.
        Vinho: {info_ia}.

        Estrutura:
        # **Título da Receita**
        ### 🛒 **Ingredientes**
        ### 👨‍🍳 **Modo de Preparação**
        ### 💡 **Dica da Maria**

        Usa PT-PT. Responde com clareza.
        """

        try:
            # Usar streaming para uma sensação de rapidez no telemóvel
            response = model.generate_content(prompt, stream=True)
            st.write_stream(response)
        except Exception as e:
            st.error(f"Erro na receita: {e}")

st.markdown("---")
st.caption("Maria - Inteligência Adaptativa | 2026")
