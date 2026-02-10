import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página e Adaptação de Cor (Mobile Friendly)
st.set_page_config(
    page_title="A Maria do Pingo Doce", 
    page_icon="🍳",
    layout="centered"
)

# Estilo Adaptativo: Evita o clarão branco à noite e organiza os blocos
st.markdown("""
    <meta name="color-scheme" content="light dark">
    <style>
    :root { --pingo-green: #2e7d32; }
    h1 { color: var(--pingo-green) !important; }
    .vinho-box {
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid var(--pingo-green);
        background-color: rgba(128, 128, 128, 0.1);
        margin-bottom: 25px;
    }
    /* Garante que o texto da receita não pareça código */
    .recipe-text {
        white-space: pre-wrap;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 A Maria do Pingo Doce")

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
    except:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input("Que vinho tem para hoje?", placeholder="Ex: Papa Figos, Bosque Premium...")

if vinho_input and vinho_input.strip():
    resultado_interno = None
    
    # Busca na tabela (mais flexível)
    if df_vinhos is not None:
        busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
        if not busca.empty:
            resultado_interno = busca.iloc[0]

    # --- MOMENTO 1: INFORMAÇÃO IMEDIATA ---
    st.markdown("### 🍷 Momento 1: A Garrafeira")
    
    if resultado_interno is not None:
        nome_v = resultado_interno['Nome do Vinho']
        produtor_v = resultado_interno['Região / Produtor']
        prato_v = resultado_interno['Receita Pingo Doce Sugerida']
        
        st.markdown(f"""
        <div class="vinho-box">
            <strong>🍷 Vinho:</strong> {nome_v}<br>
            <strong>🏷️ Produtor / Região:</strong> {produtor_v}<br>
            <strong>🤝 Harmonização:</strong> Perfeito para acompanhar <strong>{prato_v}</strong>.
        </div>
        """, unsafe_allow_html=True)
        
        contexto_ia = f"Vinho: {nome_v} ({produtor_v}). Receita: {prato_v}."
        nome_receita = prato_v
    else:
        st.info("A analisar o perfil deste vinho...")
        contexto_ia = vinho_input
        nome_receita = f"uma receita para {vinho_input}"

    # --- MOMENTO 2: GERAÇÃO DA RECEITA (SEM MOSTRAR CÓDIGO) ---
    st.markdown("---")
    
    # Criamos um container para a receita aparecer de forma organizada
    with st.spinner('A Maria está a escrever a receita detalhada...'):
        prompt = f"""
        És a Maria, cozinheira portuguesa. O utilizador já viu o produtor e a harmonização.
        Apresenta a receita completa e detalhada para: {nome_receita}.
        Vinho: {contexto_ia}.

        Estrutura a resposta em Markdown limpo:
        # **Título da Receita**
        ### 🛒 **Ingredientes** (2-4 pessoas)
        ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
        ### 💡 **Dica da Maria**

        Usa PT-PT. Não uses blocos de código (```).
        """

        try:
            # Substituímos o write_stream por markdown direto para evitar o aspeto de código
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro ao gerar a receita: {e}")

st.markdown("---")
st.caption("Maria - Sommelier & Chef | Versão 2.5 Flash | 2026")
