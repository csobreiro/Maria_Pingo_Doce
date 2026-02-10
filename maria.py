import streamlit as st
import google.generativeai as genai

# 1. Configuração Visual da Página
st.set_page_config(
    page_title="Maria - Especialista Pingo Doce", 
    page_icon="🍷",
    layout="centered"
)

# Estilo para as cores remeterem um pouco ao tema (opcional)
st.markdown("""
    <style>
    .stApp {
        background-color: #f9fdf9;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título e Saudação
st.title("🌿 Maria - Especialista em Vinhos")
st.markdown("### Olá! Diga-me que vinho tem em casa e eu sugiro a receita ideal.")

# 3. Configuração da API (Lida a partir dos Secrets do Streamlit)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 4. Interface de Pesquisa (Caixa de Texto)
    vinho = st.text_input(
        "Qual é o vinho ou região?", 
        placeholder="Ex: Grão Vasco, Herdade do Esporão, ou um Vinho Verde..."
    )

    if vinho:
        with st.spinner('A Maria está a pensar na melhor combinação...'):
            # O PROMPT que pediste está inserido aqui abaixo:
            prompt_da_maria = f"""
            És a Maria, uma assistente pessoal inspirada na frescura do Pingo Doce.
            O utilizador tem este vinho: {vinho}.

            1. Identifica o vinho e sugere uma receita com ingredientes que se encontram facilmente na zona dos frescos.
            2. Dá preferência a pratos de conforto portugueses.
            3. Explica por que razão o vinho combina com essa comida (fala de acidez, taninos ou corpo).
            4. Termina com um conselho prático sobre como escolher os melhores ingredientes para essa receita.

            Usa um tom prestável, como se estivesses a ajudar um cliente no corredor do vinho.
            Responde em Português de Portugal e usa negritos para destacar os nomes dos pratos.
            """
            
            try:
                # Gerar resposta da IA
                response = model.generate_content(prompt_da_maria)
                
                # Exibir Resultado
                st.markdown("---")
                st.markdown(response.text)
                st.balloons() # Um pequeno efeito visual de sucesso
                
            except Exception as e:
                st.error("A Maria teve um pequeno precalço a consultar o livro de receitas. Tente novamente!")
else:
    st.warning("⚠️ Atenção: A chave da API não foi configurada. Vá às definições do Streamlit e adicione GEMINI_API_KEY nos Secrets.")

# Rodapé
st.markdown("---")
st.caption("Maria - Assistente de Harmonização | Repositório: Maria_Pingo_Doce")
