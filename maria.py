import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="Maria - Receitas & Vinhos", 
    page_icon="🍳",
    layout="centered"
)

# Estilo Visual focado em Culinária
st.markdown("""
    <style>
    .stApp {background-color: #fdfdfd;}
    h1 {color: #2e7d32;}
    .recipe-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #2e7d32;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 Maria - O seu Livro de Receitas")
st.markdown("##### Escolha o seu vinho e eu preparo a receita detalhada para o seu jantar.")

# 2. Configuração da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
# Utilizando o modelo 2.5 conforme solicitado
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 3. Carregamento da Tabela
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tabela Vinho.xlsx - Sheet1.csv")
        return df
    except Exception as e:
        return None

df_vinhos = load_data()

# 4. Interface de Utilizador
vinho_input = st.text_input(
    "Que vinho tem para hoje?", 
    placeholder="Ex: Bosque Premium, Alvarinho, Dona Ermelinda...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    with st.spinner('A Maria está a escrever a receita...'):
        resultado_interno = None
        
        if df_vinhos is not None:
            busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
            if not busca.empty:
                resultado_interno = busca.iloc[0]

        # Definir o nome do prato para a IA detalhar
        if resultado_interno is not None:
            nome_prato = resultado_interno['Receita Pingo Doce Sugerida']
            detalhes_vinho = f"Vinho: {resultado_interno['Nome do Vinho']} ({resultado_interno['Região / Produtor']})"
        else:
            nome_prato = f"um prato ideal para acompanhar {vinho_input}"
            detalhes_vinho = f"Vinho: {vinho_input}"

        # Prompt focado 100% na Receita Detalhada
        prompt_receita = f"""
        És a Maria, uma cozinheira portuguesa experiente. 
        O utilizador vai beber: {detalhes_vinho}.
        A tua tarefa é apresentar a receita detalhada para o prato: {nome_prato}.

        Estrutura a tua resposta assim:
        1. **Título da Receita** (em destaque).
        2. **Ingredientes**: Lista detalhada com quantidades para 2-4 pessoas.
        3. **Modo de Preparação**: Passo-a-passo claro e numerado.
        4. **Dica da Maria**: Um segredo de cozinha para o prato ficar perfeito.
        5. **Harmonização**: Uma frase curta (máximo 15 palavras) sobre o porquê de combinar com o vinho.

        Usa Português de Portugal. Foca-te na culinária, não te alongues sobre o vinho.
        """

        try:
            response = model.generate_content(prompt_receita)
            
            # Apresentação do Resultado
            if resultado_interno is not None:
                st.success(f"🍷 Combinação encontrada: {resultado_interno['Nome do Vinho']}")
            
            st.markdown("---")
            st.markdown(response.text)
            st.balloons()
            
        except Exception as e:
            st.error(f"Erro ao gerar a receita: {e}")

st.markdown("---")
st.caption("Maria - Receitas Detalhadas | Versão 2.5 Flash")
