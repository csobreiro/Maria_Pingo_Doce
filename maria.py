import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="Maria - Livro de Receitas", 
    page_icon="🍳",
    layout="centered"
)

# Estilo Visual
st.markdown("""
    <style>
    .stApp {background-color: #fdfdfd;}
    h1 {color: #2e7d32;}
    .stTextInput > div > div > input {border-radius: 10px; border: 2px solid #2e7d32;}
    .vinho-info {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 Maria - O seu Livro de Receitas")
st.markdown("##### Escolha o seu vinho e eu preparo a receita detalhada.")

# 2. Configuração da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 3. Carregamento da Tabela
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tabela Vinho.xlsx - Sheet1.csv")
        return df
    except Exception:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input(
    "Que vinho tem para hoje?", 
    placeholder="Ex: Bosque Premium, Alvarinho, Dona Ermelinda...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    resultado_interno = None
    
    # Busca imediata na tabela
    if df_vinhos is not None:
        busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
        if not busca.empty:
            resultado_interno = busca.iloc[0]

    # --- PASSO 1: Apresentar info do vinho IMEDIATAMENTE ---
    st.markdown("### 🍷 Nota da Maria sobre o Vinho")
    with st.container():
        if resultado_interno is not None:
            st.markdown(f"""
            <div class="vinho-info">
                <strong>Vinho:</strong> {resultado_interno['Nome do Vinho']}<br>
                <strong>Perfil:</strong> {resultado_interno['Descrição']}<br>
                <strong>Região/Produtor:</strong> {resultado_interno['Região / Produtor']}<br>
                <strong>Preço aprox.:</strong> {resultado_interno['Preço (aprox.)']}
            </div>
            """, unsafe_allow_html=True)
            nome_prato = resultado_interno['Receita Pingo Doce Sugerida']
            info_vinho_prompt = f"{resultado_interno['Nome do Vinho']} ({resultado_interno['Região / Produtor']})"
        else:
            st.info(f"Vou procurar a melhor harmonização para o seu **{vinho_input}**...")
            nome_prato = f"um prato típico que combine com {vinho_input}"
            info_vinho_prompt = vinho_input

    # --- PASSO 2: Pensar e apresentar a Receita ---
    with st.spinner('A escrever a receita detalhada para si...'):
        prompt_receita = f"""
        És a Maria, cozinheira portuguesa. O utilizador tem este vinho: {info_vinho_prompt}.
        Apresenta a receita detalhada para: {nome_prato}.

        Estrutura:
        1. # **Título da Receita**
        2. ### 🛒 **Ingredientes** (Para 2-4 pessoas)
        3. ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
        4. ### 💡 **Dica da Maria** (Segredo de chef)
        5. ### 🍷 **Harmonização** (Curta explicação técnica)
        6. ### 🏷️ **Sobre o Produtor** (Curiosidade curta)

        Usa Português de Portugal. Foca na receita.
        """

        try:
            response = model.generate_content(prompt_receita)
            st.markdown("---")
            st.markdown(response.text)
            # Sem balões aqui
            
        except Exception as e:
            st.error(f"Erro ao gerar a receita: {e}")

st.markdown("---")
st.caption("Maria - Receitas Detalhadas | Versão 2.5 Flash")
