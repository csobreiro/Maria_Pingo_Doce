import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Maria - Receitas & Vinhos", page_icon="🍳")

# Estilo Visual
st.markdown("""
    <style>
    .stApp {background-color: #fdfdfd;}
    h1 {color: #2e7d32;}
    .vinho-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 20px;
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
        # Lê o CSV e garante que remove espaços extras nos nomes das colunas
        df = pd.read_csv("Tabela Vinho.xlsx - Sheet1.csv")
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input("Que vinho tem para hoje?", placeholder="Ex: Bosque Premium, Alvarinho...")

if vinho_input and vinho_input.strip():
    resultado_interno = None
    
    # Busca na tabela
    if df_vinhos is not None:
        mask = df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)
        if mask.any():
            resultado_interno = df_vinhos[mask].iloc[0]

    # --- PASSO 1: Exibir Informação da Tabela (Se existir) ---
    if resultado_interno is not None:
        st.markdown(f"""
        <div class="vinho-box">
            <strong>🍷 Vinho Identificado:</strong> {resultado_interno['Nome do Vinho']}<br>
            <strong>🏷️ Produtor/Região:</strong> {resultado_interno['Região / Produtor']}<br>
            <strong>📝 Perfil:</strong> {resultado_interno['Descrição']}<br>
            <strong>💰 Preço:</strong> {resultado_interno['Preço (aprox.)']}
        </div>
        """, unsafe_allow_html=True)
        
        prato_sugerido = resultado_interno['Receita Pingo Doce Sugerida']
        contexto = f"Vinho: {resultado_interno['Nome do Vinho']} | Produtor: {resultado_interno['Região / Produtor']} | Prato: {prato_sugerido}"
    else:
        st.info(f"Vou analisar o seu **{vinho_input}**...")
        prato_sugerido = f"um prato ideal para {vinho_input}"
        contexto = f"Vinho: {vinho_input}"

    # --- PASSO 2: Geração com Streaming (Aparece enquanto pensa) ---
    # O prompt obriga a IA a começar pelo Produtor e Harmonização
    prompt = f"""
    És a Maria, cozinheira e sommelier portuguesa.
    Contexto: {contexto}.

    ESTRUTURA OBRIGATÓRIA DA RESPOSTA:
    1. Começa por: "### 🏷️ O Produtor e a Região" (Dá uma explicação curta).
    2. Segue com: "### 🍷 Porquê esta Harmonização" (Explica a lógica técnica entre o vinho e o prato).
    3. Depois apresenta a receita: "# **Título da Receita**"
    4. "### 🛒 Ingredientes" (Lista para 2-4 pessoas)
    5. "### 👨‍🍳 Modo de Preparação" (Passo-a-passo)
    6. Termina com "### 💡 Dica da Maria".

    Responde em Português de Portugal. 
    MUITO IMPORTANTE: O Produtor e a Harmonização têm de vir no TOPO da resposta.
    """

    try:
        # A magia do streaming: o texto aparece enquanto é gerado
        response = model.generate_content(prompt, stream=True)
        st.write_stream(response)
    except Exception as e:
        st.error(f"Erro ao processar: {e}")

st.markdown("---")
st.caption("Maria - Receitas Detalhadas | Versão 2.5 Flash")
