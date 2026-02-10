import streamlit as st
import google.generativeai as genai
import os

# 1. Configuração Visual da Página
st.set_page_config(
    page_title="Maria - Especialista Pingo Doce", 
    page_icon="🍷",
    layout="centered"
)

# Estilo para cores inspiradas no Pingo Doce (Verde e Branco)
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
    h1 {
        color: #1b5e20;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título e Saudação
st.title("🌿 Maria - Especialista em Vinhos")
st.markdown("### Olá! Diga-me que vinho tem em casa e eu sugiro a receita ideal.")

# 3. Configuração da API (Lida a partir dos Secrets do Streamlit)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        # Configuração do Google Gemini
        genai.configure(api_key=api_key)
        
        # Uso do nome de modelo completo para evitar o erro 404
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

        # 4. Interface de Pesquisa
        vinho = st.text_input(
            "Qual é o vinho, região ou estilo?", 
            placeholder="Ex: Papa Figos, Muralhas de Monção, ou um Reserva do Alentejo..."
        )

        if vinho:
            with st.spinner('A Maria está a consultar a cave e o livro de receitas...'):
                # Prompt personalizado para a Maria
                prompt_da_maria = f"""
                És a Maria, uma assistente pessoal inspirada na frescura do Pingo Doce.
                O utilizador tem este vinho: {vinho}.

                1. Identifica o perfil do vinho de forma breve e charmosa.
                2. Sugere uma receita com ingredientes frescos (foca-te em pratos portugueses).
                3. Explica a harmonização técnica (ex: "este branco corta a gordura do peixe").
                4. Dá uma dica de mestre sobre a temperatura de serviço ou um ingrediente extra.

                Usa um tom prestável, como se estivesses a ajudar um cliente no corredor do vinho.
                Responde obrigatoriamente em Português de Portugal e usa negritos para destacar os pontos chave.
                """
                
                # Gerar resposta da IA
                response = model.generate_content(prompt_da_maria)
                
                # Exibir Resultado
                st.markdown("---")
                st.markdown(response.text)
                st.balloons() 
                
    except Exception as e:
        # Mostra o erro real se algo falhar na comunicação
        st.error(f"Erro técnico: {e}")
        st.info("Dica: Verifique se a sua API Key nos Secrets do Streamlit está correta e ativa.")
else:
    st.warning("⚠️ Atenção: A chave da API (GEMINI_API_KEY) não foi encontrada nos Secrets do Streamlit.")

# Rodapé
st.markdown("---")
st.caption("Maria - Assistente de Harmonização | Repositório: Maria_Pingo_Doce")
