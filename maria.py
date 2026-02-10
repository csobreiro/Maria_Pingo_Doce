import streamlit as st
import google.generativeai as genai

# 1. Configuração da Página e Adaptação de Cor para Mobile
st.set_page_config(
    page_title="A Maria do Pingo Doce", 
    page_icon="🍳",
    layout="centered"
)

# Estilo Adaptativo (Light/Dark Mode)
st.markdown("""
    <meta name="color-scheme" content="light dark">
    <style>
    :root { --pingo-green: #2e7d32; }
    h1 { color: var(--pingo-green) !important; }
    .vinho-box {
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid var(--pingo-green);
        background-color: rgba(128, 128, 128, 0.1);
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 A Maria do Pingo Doce")
st.markdown("##### O seu guia de vinhos e receitas inteligente.")

# 2. Configuração da API Key (Streamlit Secrets)
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 3. Interface de Utilizador
vinho_input = st.text_input(
    "Que vinho escolheu para hoje?", 
    placeholder="Ex: Papa Figos, Muralhas de Monção, Esporão...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    
    # --- MOMENTO 1: O SOMMELIER (Informação Online Imediata) ---
    st.markdown("### 🍷 Momento 1: A Garrafeira")
    
    with st.spinner('A Maria está a consultar a cave...'):
        prompt_vinho = f"""
        És a Maria, sommelier portuguesa. O utilizador tem o vinho: {vinho_input}.
        Diz-me de forma muito curta:
        1. Quem é o Produtor e qual a Região.
        2. Qual o perfil do vinho (breve).
        3. Qual a harmonização ideal (apenas o nome do prato).
        
        Responde em Português de Portugal com este formato exato:
        **Produtor/Região:** [Resposta]
        **Perfil:** [Resposta]
        **Harmonização Ideal:** [Nome do Prato]
        """
        
        try:
            res_vinho = model.generate_content(prompt_vinho)
            texto_vinho = res_vinho.text
            
            # Exibe o quadro informativo
            st.markdown(f'<div class="vinho-box">{texto_vinho}</div>', unsafe_allow_html=True)
            
            # --- MOMENTO 2: A RECEITA DETALHADA ---
            st.markdown("---")
            with st.spinner('A preparar o livro de receitas para esse prato...'):
                # Extraímos o prato da resposta anterior para a receita ser coerente
                prompt_receita = f"""
                Com base na harmonização que sugeriste para o vinho {vinho_input}, 
                apresenta agora a receita detalhada.
                
                Estrutura:
                # **Título da Receita**
                ### 🛒 **Ingredientes** (2-4 pessoas)
                ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
                ### 💡 **Dica da Maria**
                
                Usa PT-PT. Responde apenas com a receita.
                """
                response = model.generate_content(prompt_receita)
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"A Maria teve um pequeno problema: {e}")

st.markdown("---")
st.caption("Maria - Inteligência Artificial em Tempo Real | 2026")
