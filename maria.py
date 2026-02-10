import streamlit as st
import google.generativeai as genai
import os

# Configuração da Página
st.set_page_config(page_title="Maria - Sommelier Pessoal", page_icon="🍷")

# Estilo Personalizado (Opcional - para ficar mais elegante)
st.markdown("""
    <style>
    .main {
        background-color: #fdfaf7;
    }
    stTextInput > div > div > input {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Título e Introdução
st.title("Olá, eu sou a Maria! 👋")
st.subheader("Diga-me que vinho vai abrir e eu trato da receita.")

# --- Configuração da API Key ---
# No Streamlit Cloud, adicione em Settings -> Secrets: GEMINI_API_KEY = "sua_chave"
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # --- Interface de Pesquisa ---
    with st.container():
        vinho = st.text_input(
            "Pesquise pelo nome do vinho, região ou tipo:",
            placeholder="Ex: Papa Figos Tinto, Alvarinho de Monção, ou um Rosé fresco..."
        )

    if vinho:
        with st.spinner('A Maria está a consultar a cave e o livro de receitas...'):
            # Prompt otimizado para a Maria
            prompt = f"""
            És a Maria, uma assistente pessoal portuguesa, expert em vinhos e gastronomia.
            O utilizador tem este vinho: {vinho}.
            
            1. Descreve o vinho de forma curta e charmosa (ex: "Esse Douro é encorpado e elegante").
            2. Sugere uma receita ideal (foca-te em pratos portugueses ou mediterrânicos).
            3. Dá uma dica de mestre (ex: temperatura de serviço ou um ingrediente secreto na receita).
            
            Usa um tom simpático, prestável e português de Portugal. 
            Formata com negritos e bullet points.
            """
            
            try:
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
                
                # Botão extra de cortesia
                st.balloons()
            except Exception as e:
                st.error("Ops! Tive um problema ao aceder à minha base de dados. Verifique a API Key.")
else:
    st.error("Erro: Não encontrei a chave da API (GEMINI_API_KEY) nos Secrets do Streamlit.")

# Rodapé
st.markdown("---")
st.caption("A Maria recomenda sempre consumo moderado. Saúde! 🍷")
