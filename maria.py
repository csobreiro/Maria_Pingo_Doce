import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="Maria - Livro de Receitas", 
    page_icon="🍳",
    layout="centered"
)

# Estilo Visual focado na clareza e no Pingo Doce
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
        line-height: 1.6;
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

    # --- PASSO 1: Informação Imediata (Vinho, Produtor e Harmonização) ---
    st.markdown("### 🍷 Informações da Cave")
    
    if resultado_interno is not None:
        nome_prato = resultado_interno['Receita Pingo Doce Sugerida']
        vinho_nome = resultado_interno['Nome do Vinho']
        produtor = resultado_interno['Região / Produtor']
        descricao = resultado_interno['Descrição']
        
        # O quadro verde aparece AGORA com tudo o que não é a receita
        st.markdown(f"""
        <div class="vinho-info">
            <strong>🍷 Vinho:</strong> {vinho_nome}<br>
            <strong>🏷️ Produtor/Região:</strong> {produtor}<br>
            <strong>📝 Perfil:</strong> {descricao}<br>
            <strong>🤝 Harmonização:</strong> Este vinho combina perfeitamente com <strong>{nome_prato}</strong> devido à sua estrutura e perfil aromático.
        </div>
        """, unsafe_allow_html=True)
        
        info_para_ia = f"Vinho: {vinho_nome} ({produtor}). Prato: {nome_prato}."
    else:
        st.info(f"Vou analisar o perfil do **{vinho_input}** e criar uma receita personalizada...")
        nome_prato = f"um prato ideal para acompanhar {vinho_input}"
        info_para_ia = vinho_input

    # --- PASSO 2: Spinner e Geração da Receita Detalhada ---
    with st.spinner('A Maria está a organizar os ingredientes e o fogão...'):
        prompt_receita = f"""
        És a Maria, uma cozinheira portuguesa experiente. 
        O utilizador já sabe os detalhes do vinho: {info_para_ia}.
        
        A tua tarefa agora é APENAS apresentar a receita detalhada para: {nome_prato}.

        Estrutura:
        1. # **Título da Receita**
        2. ### 🛒 **Ingredientes** (Quantidades para 2-4 pessoas)
        3. ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo detalhado)
        4. ### 💡 **Dica da Maria** (O segredo para o prato brilhar)

        Usa Português de Portugal. Sê muito detalhada na parte culinária. 
        Não repitas as informações do produtor ou da harmonização que já foram ditas.
        """

        try:
            response = model.generate_content(prompt_receita)
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Erro ao gerar a receita: {e}")

st.markdown("---")
st.caption("Maria - Receitas Detalhadas | Versão 2.5 Flash")
