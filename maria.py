import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Maria - Especialista Pingo Doce", page_icon="🍷")

# Estilo Pingo Doce
st.markdown("""
    <style>
    .stApp {background-color: #f9fdf9;}
    h1 {color: #2e7d32;}
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Maria - Especialista em Vinhos")

# Validação da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

# Configuração do modelo
try:
    genai.configure(api_key=api_key)
    
    # Lista de modelos para tentar (do mais recente ao mais antigo)
    MODELOS_DISPONIVEIS = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-pro-latest',
        'gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-1.5-flash-latest',
        'models/gemini-1.5-flash',
    ]
    
    model = None
    modelo_usado = None
    
    # Tenta encontrar um modelo que funcione
    for modelo_nome in MODELOS_DISPONIVEIS:
        try:
            model = genai.GenerativeModel(modelo_nome)
            # Teste rápido para ver se o modelo funciona
            test_response = model.generate_content("Olá")
            modelo_usado = modelo_nome
            break
        except Exception:
            continue
    
    if not model or not modelo_usado:
        st.error("❌ Nenhum modelo Gemini disponível. Verifique sua API key ou tente mais tarde.")
        st.info("💡 Modelos testados: " + ", ".join(MODELOS_DISPONIVEIS))
        st.stop()
    
    # Mostra qual modelo está a usar (apenas em debug)
    # st.caption(f"🤖 A usar: {modelo_usado}")
    
except Exception as e:
    st.error(f"❌ Erro ao configurar a API: {e}")
    st.stop()

# Input do utilizador
vinho = st.text_input(
    "Qual é o vinho?", 
    placeholder="Ex: Papa Figos, Esporão Reserva, Mateus Rosé...",
    max_chars=100
)

if vinho and vinho.strip():
    vinho_limpo = vinho.strip()
    
    with st.spinner('🍇 A Maria está a escolher a melhor combinação...'):
        prompt = f"""És a Maria, uma sommelier portuguesa com 20 anos de experiência.

O utilizador tem este vinho: {vinho_limpo}

Por favor:
1. Identifica o tipo e características do vinho
2. Sugere uma receita portuguesa tradicional que harmonize perfeitamente
3. Explica brevemente a razão da harmonização

Responde em Português de Portugal, de forma calorosa e acessível."""

        try:
            response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                st.markdown("---")
                st.markdown("### 🍽️ Sugestão da Maria")
                st.markdown(response.text)
                st.balloons()
            else:
                st.warning("⚠️ A Maria não conseguiu gerar uma sugestão. Tente outro vinho.")
                
        except Exception as e:
            st.error(f"❌ Erro ao gerar harmonização: {str(e)}")
            st.info("💡 Tente novamente em alguns segundos.")
