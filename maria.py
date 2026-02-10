import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página e Meta-Tags para Adaptação de Cor
st.set_page_config(
    page_title="A Maria do Pingo Doce", 
    page_icon="🍳",
    layout="centered"
)

# CSS Adaptativo: Respeita o Dark/Light mode do telemóvel e estiliza o Momento 1
st.markdown("""
    <meta name="color-scheme" content="light dark">
    <style>
    :root {
        --pingo-green: #2e7d32;
    }
    h1 {
        color: var(--pingo-green) !important;
    }
    /* Caixa do Vinho (Momento 1) - Fundo translúcido para adaptar ao tema */
    .vinho-info-box {
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid var(--pingo-green);
        background-color: rgba(128, 128, 128, 0.1);
        margin-bottom: 25px;
    }
    /* Melhora legibilidade em telemóveis */
    input {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 A Maria do Pingo Doce")
st.markdown("##### O seu guia de vinhos e receitas.")

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
        df.columns = df.columns.str.strip() # Remove espaços invisíveis nos nomes das colunas
        return df
    except:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input(
    "Que vinho tem para hoje?", 
    placeholder="Ex: Papa Figos, Bosque Premium...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    resultado_interno = None
    
    # Pesquisa flexível (ignora maiúsculas/minúsculas)
    if df_vinhos is not None:
        busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
        if not busca.empty:
            resultado_interno = busca.iloc[0]

    # --- MOMENTO 1: INFORMAÇÃO IMEDIATA (PRODUTOR E HARMONIZAÇÃO) ---
    st.markdown("### 🍷 Momento 1: A Garrafeira")
    
    with st.container():
        if resultado_interno is not None:
            # Dados da Tabela
            nome_v = resultado_interno['Nome do Vinho']
            produtor_v = resultado_interno['Região / Produtor']
            prato_v = resultado_interno['Receita Pingo Doce Sugerida']
            
            st.markdown(f"""
            <div class="vinho-info-box">
                <strong>🍷 Vinho:</strong> {nome_v}<br>
                <strong>🏷️ Produtor / Região:</strong> {produtor_v}<br>
                <strong>🤝 Harmonização:</strong> Este vinho é o par ideal para <strong>{prato_v}</strong>.
            </div>
            """, unsafe_allow_html=True)
            
            contexto_ia = f"Vinho: {nome_v} ({produtor_v}). Receita: {prato_v}."
            nome_receita = prato_v
        else:
            # Se não estiver na tabela, a IA assume o Momento 1 rapidamente
            with st.spinner('A Maria está a consultar a cave...'):
                prompt_m1 = f"Diz apenas o produtor/região e uma harmonização curta (prato) para o vinho: {vinho_input}. Responde em PT-PT."
                try:
                    res_m1 = model.generate_content(prompt_m1)
                    st.markdown(f'<div class="vinho-info-box">{res_m1.text}</div>', unsafe_allow_html=True)
                    contexto_ia = vinho_input
                    nome_receita = "uma receita ideal"
                except:
                    st.error("Não consegui analisar este vinho.")
                    st.stop()

    # --- MOMENTO 2: GERAÇÃO DA RECEITA (STREAMING) ---
    st.markdown("---")
    with st.spinner('A Maria está a escrever a receita detalhada...'):
        prompt_receita = f"""
        És a Maria, cozinheira portuguesa. O utilizador já viu o produtor e a harmonização.
        Apresenta APENAS a receita detalhada para: {nome_receita}.
        Vinho de referência: {contexto_ia}.

        Estrutura:
        1. # **Título da Receita**
        2. ### 🛒 **Ingredientes** (2-4 pessoas)
        3. ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
        4. ### 💡 **Dica da Maria**

        Usa PT-PT. Não repitas o produtor ou a harmonização no texto da receita.
        """

        try:
            # st.write_stream faz com que o texto apareça enquanto é gerado (ótimo para mobile)
            response = model.generate_content(prompt_receita, stream=True)
            st.write_stream(response)
        except Exception as e:
            st.error(f"Erro ao gerar a receita: {e}")

st.markdown("---")
st.caption("Maria - Receitas Detalhadas | Versão 2.5 Flash | Modo Adaptativo Ativo")
