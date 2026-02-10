import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Maria - Receitas & Vinhos", page_icon="🍷")

# Estilo Visual Pingo Doce
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
        width: 100%;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Maria - Especialista Pingo Doce")

# 2. Configuração da API (Usando a versão que confirmou funcionar)
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)
    # Note: Usamos a versão 2.0-flash que confirmou ter estabilidade
    model = genai.GenerativeModel('models/gemini-2.0-flash')

# 3. Carregamento da Tabela
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tabela Vinho.xlsx - Sheet1.csv")
        df.columns = df.columns.str.strip() # Limpa nomes de colunas
        return df
    except:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input("Que vinho escolheu para hoje?", placeholder="Ex: Bosque Premium, Alvarinho...")

if vinho_input and vinho_input.strip():
    resultado = None
    if df_vinhos is not None:
        busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
        if not busca.empty:
            resultado = busca.iloc[0]

    # --- MOMENTO 1: INFORMAÇÃO IMEDIATA DO VINHO ---
    st.markdown("### 🍷 Momento 1: A Garrafeira")
    
    if resultado is not None:
        # Extraímos os dados da tabela
        nome_vinho = resultado['Nome do Vinho']
        produtor = resultado['Região / Produtor']
        prato_sugerido = resultado['Receita Pingo Doce Sugerida']
        
        st.markdown(f"""
        <div class="vinho-box">
            <strong>Produtor / Região:</strong> {produtor}<br>
            <strong>Sugestão de Harmonização:</strong> Este vinho é o par ideal para <strong>{prato_sugerido}</strong>.
        </div>
        """, unsafe_allow_html=True)
        
        info_para_ia = f"Vinho: {nome_vinho} ({produtor}). Prato: {prato_sugerido}."
        
        # --- MOMENTO 2: A RECEITA DETALHADA (Só após clique) ---
        st.write("Deseja ver como preparar este prato?")
        if st.button("Sim, Maria! Ver Receita Detalhada"):
            with st.spinner('A Maria está a abrir o livro de receitas...'):
                prompt = f"""
                És a Maria, uma cozinheira portuguesa. O utilizador já viu o produtor e a harmonização.
                A tua tarefa é apresentar APENAS a receita detalhada para: {prato_sugerido}.
                
                Estrutura:
                # **{prato_sugerido}**
                ### 🛒 **Ingredientes** (para 2-4 pessoas)
                ### 👨‍🍳 **Modo de Preparação** (passo-a-passo claro)
                ### 💡 **Dica da Maria**
                
                Responde em Português de Portugal. Foca 100% na receita.
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro ao criar receita: {e}")

    else:
        # Se o vinho não estiver na tabela, a Maria propõe uma análise
        st.info(f"O vinho '{vinho_input}' não está na minha tabela, mas posso analisá-lo para si.")
        if st.button("Analisar Vinho e Gerar Receita"):
            with st.spinner('A Maria está a estudar este vinho...'):
                prompt_ia = f"És a Maria. Analisa o vinho {vinho_input}. Primeiro diz o produtor/região provável e a harmonização. Depois dá a receita detalhada."
                try:
                    response = model.generate_content(prompt_ia)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erro: {e}")

st.markdown("---")
st.caption("Maria - Sommelier & Chef | 2026")
