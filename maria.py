import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página e Meta-Tags para Mobile
st.set_page_config(
    page_title="A Maria do Pingo Doce", 
    page_icon="🍷",
    layout="centered"
)

# Força o navegador a aceitar modos claro/escuro e adapta o visual
st.markdown("""
    <meta name="color-scheme" content="light dark">
    <style>
    /* Variáveis que respeitam o tema do Streamlit */
    :root {
        --pingo-green: #2e7d32;
    }
    
    /* Título Adaptativo */
    h1 {
        color: var(--pingo-green) !important;
        font-weight: 700;
    }

    /* Quadro do Vinho (Momento 1) com transparência para se adaptar ao fundo */
    .vinho-box {
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid var(--pingo-green);
        background-color: rgba(128, 128, 128, 0.1);
        margin-bottom: 25px;
        line-height: 1.6;
    }

    /* Ajuste para inputs no telemóvel para não dar zoom indesejado */
    input {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 A Maria do Pingo Doce")
st.markdown("##### O seu guia de vinhos e receitas que se adapta ao seu olhar.")

# 2. Configuração da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)
    # Modelo Gemini 2.5 Flash conforme solicitado
    model = genai.GenerativeModel('models/gemini-2.5-flash')

# 3. Carregamento da Tabela CSV
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

    # --- MOMENTO 1: INFORMAÇÃO IMEDIATA (PRODUTOR E HARMONIZAÇÃO) ---
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
        # Caso o vinho não esteja na tabela, a IA gera o Momento 1 rapidamente
        with st.spinner('A Maria está a analisar o vinho...'):
            try:
                prompt_m1 = f"Diz apenas o produtor/região e uma harmonização curta (prato) para o vinho: {vinho_input}. Responde em PT-PT."
                res_m1 = model.generate_content(prompt_m1)
                st.markdown(f'<div class="vinho-box">{res_m1.text}</div>', unsafe_allow_html=True)
                info_ia = vinho_input
                nome_final_prato = "uma receita ideal"
            except:
                st.error("Não consegui analisar este vinho.")
                st.stop()

    # --- MOMENTO 2: GERAÇÃO DA RECEITA (STREAMING) ---
    st.markdown("---")
    # O streaming permite que o telemóvel comece a mostrar texto logo, sem esperas longas
    with st.spinner('A Maria está a escrever a receita detalhada...'):
        prompt_receita = f"""
        És a Maria, cozinheira portuguesa. O utilizador já viu o produtor e a harmonização.
        A tua tarefa é apresentar APENAS a receita completa e detalhada para: {nome_final_prato}.
        Vinho de referência: {info_ia}.

        Estrutura a resposta assim:
        # **Título da Receita**
        ### 🛒 **Ingredientes** (Quantidades para 2-4 pessoas)
        ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo numerado)
        ### 💡 **Dica da Maria** (O segredo do Chef)

        Usa Português de Portugal. Foca-te 100% na culinária e na clareza.
        """

        try:
            response = model.generate_content(prompt_receita, stream=True)
            st.write_stream(response)
        except Exception as e:
            st.error(f"Erro ao gerar a receita: {e}")

st.markdown("---")
st.caption("Maria - Sommelier & Chef | Versão 2.5 Flash | Modo Adaptativo Ativo")
