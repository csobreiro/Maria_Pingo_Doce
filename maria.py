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
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2e7d32;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 Maria - O seu Livro de Receitas")

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
    
    # Busca na tabela
    if df_vinhos is not None:
        busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
        if not busca.empty:
            resultado_interno = busca.iloc[0]

    # --- EXIBIÇÃO IMEDIATA (Antes da Receita) ---
    st.markdown("### 🍷 Informações do Sommelier")
    
    if resultado_interno is not None:
        nome_prato = resultado_interno['Receita Pingo Doce Sugerida']
        
        # Mostramos logo o Produtor e a Harmonização
        st.markdown(f"""
        <div class="vinho-info">
            <strong>🍷 Vinho:</strong> {resultado_interno['Nome do Vinho']}<br>
            <strong>🏷️ Produtor/Região:</strong> {resultado_interno['Região / Produtor']}<br>
            <strong>📝 Perfil:</strong> {resultado_interno['Descrição']}<br>
            <strong>🤝 Harmonização:</strong> Este vinho é o par ideal para <strong>{nome_prato}</strong>.
        </div>
        """, unsafe_allow_html=True)
        
        info_ia = f"Vinho: {resultado_interno['Nome do Vinho']} ({resultado_interno['Região / Produtor']}). Receita: {nome_prato}."
    else:
        st.info(f"Vou analisar o perfil do seu **{vinho_input}**...")
        nome_prato = f"um prato ideal para acompanhar {vinho_input}"
        info_ia = vinho_input

    # --- GERAÇÃO DA RECEITA (Com Spinner) ---
    with st.spinner('A preparar a receita detalhada...'):
        prompt = f"""
        És a Maria, cozinheira portuguesa. O utilizador já tem as notas do vinho: {info_ia}.
        Apresenta a receita detalhada para: {nome_prato}.

        Estrutura:
        1. # **Título da Receita**
        2. ### 🛒 **Ingredientes** (2-4 pessoas)
        3. ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
        4. ### 💡 **Dica da Maria**

        Usa Português de Portugal. Não repitas o produtor ou a harmonização.
        """

        try:
            response = model.generate_content(prompt)
            st.markdown("---")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro na receita: {e}")

st.markdown("---")
st.caption("Maria - Receitas Detalhadas | 2026")
