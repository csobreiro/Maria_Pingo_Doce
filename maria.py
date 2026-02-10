import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Maria - Especialista de Vinhos", page_icon="🍷")

st.markdown("""
    <style>
    .stApp {background-color: #fdfdfd;}
    h1 {color: #2e7d32;}
    .vinho-box {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2e7d32;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Maria - Especialista Pingo Doce")

# 2. Configuração da API
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.0-flash')

# 3. Carregar Tabela
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tabela Vinho.xlsx - Sheet1.csv")
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

df_vinhos = load_data()

# 4. Interface
vinho_input = st.text_input("Que vinho escolheu hoje?", placeholder="Ex: Papa Figos, Bosque Premium...")

if vinho_input and vinho_input.strip():
    resultado = None
    if df_vinhos is not None:
        # Pesquisa mais flexível
        busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
        if not busca.empty:
            resultado = busca.iloc[0]

    # --- MOMENTO 1: PRODUTOR E HARMONIZAÇÃO (IMEDIATO) ---
    st.markdown("### 🍷 Momento 1: A Garrafeira")
    
    with st.container():
        if resultado is not None:
            # Dados da Tabela
            produtor = resultado['Região / Produtor']
            harmonizacao = f"Este vinho é o par ideal para **{resultado['Receita Pingo Doce Sugerida']}**."
            st.markdown(f"""
            <div class="vinho-box">
                <strong>Vinho:</strong> {resultado['Nome do Vinho']}<br>
                <strong>🏷️ Produtor / Região:</strong> {produtor}<br>
                <strong>🤝 Harmonização:</strong> {harmonizacao}
            </div>
            """, unsafe_allow_html=True)
            prato_para_ia = resultado['Receita Pingo Doce Sugerida']
            vinho_para_ia = resultado['Nome do Vinho']
        else:
            # Se não estiver na tabela, a IA dá o Momento 1 rapidamente
            with st.spinner('A Maria está a consultar a cave...'):
                prompt_m1 = f"Diz apenas o produtor/região e uma harmonização curta para o vinho: {vinho_input}. Responde em PT-PT."
                try:
                    res_m1 = model.generate_content(prompt_m1)
                    st.markdown(f'<div class="vinho-box">{res_m1.text}</div>', unsafe_allow_html=True)
                    prato_para_ia = "uma receita adequada"
                    vinho_para_ia = vinho_input
                except:
                    st.error("Erro ao analisar vinho.")
                    st.stop()

    # --- MOMENTO 2: RECEITA DETALHADA (SOB DEMANDA) ---
    st.write("---")
    if st.button(f"Chef Maria, pode dar-me a receita detalhada?"):
        with st.spinner('A preparar o fogão e os ingredientes...'):
            prompt_receita = f"""
            És a Maria, cozinheira portuguesa.
            O utilizador vai beber: {vinho_para_ia}.
            Apresenta a receita detalhada para acompanhar este vinho.
            
            Estrutura:
            # **Título da Receita**
            ### 🛒 **Ingredientes** (2-4 pessoas)
            ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
            ### 💡 **Dica da Maria**
            
            Usa Português de Portugal. Foca na receita.
            """
            try:
                response = model.generate_content(prompt_receita)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro: {e}")

st.markdown("---")
st.caption("Maria - Sommelier & Chef | Versão 2.5 Flash")
