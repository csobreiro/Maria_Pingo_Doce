import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="A Maria do Pingo Doce - Livro de Receitas ", 
    page_icon="🍳",
    layout="centered"
)

# Estilo Visual focado em Culinária e no Pingo Doce
st.markdown("""
    <style>
    .stApp {background-color: #fdfdfd;}
    h1 {color: #2e7d32;}
    .stTextInput > div > div > input {border-radius: 10px; border: 2px solid #2e7d32;}
    </style>
""", unsafe_allow_html=True)

st.title("🍳 Maria - O seu Livro de Receitas")
st.markdown("##### Escolha o seu vinho e eu preparo a receita detalhada para o seu almoço ou jantar.")

# 2. Configuração da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
# Utilizando o modelo Gemini 2.5 Flash como solicitado
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 3. Carregamento da Tabela
@st.cache_data
def load_data():
    try:
        # Garante que o nome do ficheiro CSV coincide com o do teu repositório
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
        
        # Procura na tabela (Case Insensitive)
        if df_vinhos is not None:
            busca = df_vinhos[df_vinhos['Nome do Vinho'].str.contains(vinho_input, case=False, na=False)]
            if not busca.empty:
                resultado_interno = busca.iloc[0]

        # Definir as variáveis para o Prompt
        if resultado_interno is not None:
            nome_prato = resultado_interno['Receita Pingo Doce Sugerida']
            info_vinho = f"Vinho: {resultado_interno['Nome do Vinho']} | Produtor/Região: {resultado_interno['Região / Produtor']}"
        else:
            nome_prato = f"um prato típico português que combine com {vinho_input}"
            info_vinho = f"Vinho: {vinho_input}"

        # Prompt focado na Receita Detalhada e Produtor
        prompt_receita = f"""
        És a Maria, uma cozinheira portuguesa experiente e conhecedora do Pingo Doce. 
        O utilizador vai beber: {info_vinho}.
        A tua tarefa é apresentar a receita completa e detalhada para o prato: {nome_prato}.

        Estrutura a tua resposta exatamente assim:
        1. # **Título da Receita**
        2. ### 🛒 **Ingredientes**
           (Lista detalhada para 2 a 4 pessoas)
        3. ### 👨‍🍳 **Modo de Preparação**
           (Passo-a-passo numerado e claro)
        4. ### 💡 **Dica da Maria**
           (Um segredo de cozinha para o prato ficar perfeito)
        5. ### 🍷 **Harmonização**
           (Frase curta sobre o porquê de combinar com este vinho)
        6. ### 🏷️ **Sobre o Produtor**
           (Frase curta sobre o produtor ou região mencionada: {info_vinho})

        Usa Português de Portugal. Foca-te na culinária e na clareza das instruções.
        """

        try:
            response = model.generate_content(prompt_receita)
            
            # Apresentação do Resultado
            if resultado_interno is not None:
                st.success(f"🍷 Vinho identificado: {resultado_interno['Nome do Vinho']}")
            
            st.markdown("---")
            st.markdown(response.text)
            
            
        except Exception as e:
            st.error(f"Erro ao gerar a receita: {e}")

st.markdown("---")
st.caption("Maria - Receitas Detalhadas | Versão 2.5 Flash | 2026")
