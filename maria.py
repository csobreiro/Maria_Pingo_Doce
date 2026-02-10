import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Maria - Especialista Pingo Doce", page_icon="🍷")

st.markdown("""
    <style>
    .stApp {background-color: #f9fdf9;}
    h1 {color: #2e7d32;}
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Maria - Especialista em Vinhos")

api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    
    # Botão debug para ver modelos disponíveis
    if st.sidebar.checkbox("🔍 Mostrar modelos disponíveis (debug)"):
        with st.sidebar:
            st.write("**Modelos disponíveis na sua conta:**")
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name)
            except Exception as e:
                st.error(f"Erro ao listar: {e}")
    
    # Tenta usar o modelo mais comum primeiro
    model = None
    
    # Ordem de preferência
    modelos_tentar = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro-latest', 
        'gemini-pro'
    ]
    
    for modelo_nome in modelos_tentar:
        try:
            model = genai.GenerativeModel(modelo_nome)
            # Teste simples
            _ = model.generate_content("teste")
            st.sidebar.success(f"✅ A usar: {modelo_nome}")
            break
        except Exception as e:
            st.sidebar.warning(f"❌ {modelo_nome}: {str(e)[:50]}")
            continue
    
    if not model:
        st.error("❌ Nenhum modelo disponível. Verifique:")
        st.markdown("""
        1. A sua **API key** está correta?
        2. A API Gemini está **ativa** no Google AI Studio?
        3. Tem **quota disponível**?
        
        👉 Aceda a: https://aistudio.google.com/apikey
        """)
        st.stop()

except Exception as e:
    st.error(f"❌ Erro de configuração: {e}")
    st.stop()

# Interface principal
vinho = st.text_input(
    "Qual é o vinho?", 
    placeholder="Ex: Papa Figos, Esporão, Mateus...",
    max_chars=100
)

if vinho and vinho.strip():
    with st.spinner('🍇 A Maria está a pensar...'):
        prompt = f"""És a Maria, sommelier portuguesa.

Vinho: {vinho.strip()}

Sugere:
- Uma receita portuguesa
- Porquê harmoniza bem

Responde em PT-PT, de forma breve e simpática."""

        try:
            response = model.generate_content(prompt)
            
            st.markdown("---")
            st.markdown("### 🍽️ Sugestão da Maria")
            st.markdown(response.text)
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Erro: {e}")
