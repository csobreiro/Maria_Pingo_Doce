import streamlit as st
import google.generativeai as genai

# 1. Configuração da Página e Estilo Adaptativo
st.set_page_config(
    page_title="A Maria do Pingo Doce", 
    page_icon="🍳",
    layout="centered"
)

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
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 A Maria do Pingo Doce")

# 2. Configuração da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-flash-latest')
except Exception as e:
    st.error(f"Erro ao configurar modelo: {e}")
    st.info("Tente: pip install --upgrade google-generativeai")
    st.stop()

# 3. Interface
vinho_input = st.text_input(
    "Que vinho escolheu para hoje?", 
    placeholder="Ex: Papa Figos, Muralhas, Esporão...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    
    # Evita repetir chamadas desnecessárias
    if 'ultimo_vinho' not in st.session_state or st.session_state.ultimo_vinho != vinho_input:
        st.session_state.ultimo_vinho = vinho_input
        
        with st.spinner('A Maria está a preparar tudo para si...o vinho e a cozinha'):
            
            # PROMPT ÚNICO: Garante que a harmonização e a receita são a mesma coisa
            prompt_unico = f"""
            És a Maria, especialista em vinhos e cozinheira portuguesa.
            O utilizador tem o vinho: {vinho_input}.
            
            Responde seguindo rigorosamente esta estrutura dividida por "---":
            
            Sobre o Vinho
            🍷 **Vinho:** [Nome] <br>
            🏷️ **Produtor/Região:** [Nome] <br>
            📝 **Perfil:** [Breve descrição] <br>
            🌡️ **Servir a:** [Temperatura] <br>
            🤝 **Harmonização Ideal:** [Nome do Prato] <br>
            ---
            A melhor receita para este vinho
            # **[Nome do Prato Específico]**
            ### 🛒 **Ingredientes** (2-4 pessoas)
            ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
            ### 💡 **Dica da Maria**
            
            Regras: 
            - O prato no MOMENTO1 tem de ser o MESMO da receita no MOMENTO2.
            - Usa Português de Portugal.
            """
            
            try:
                response = model.generate_content(prompt_unico)
                partes = response.text.split("---")
                
                # Guarda a resposta no session_state
                st.session_state.resposta_partes = partes
                
            except Exception as e:
                st.error(f"Erro na Maria: {e}")
                st.session_state.resposta_partes = None
    
    # Mostra a resposta guardada
    if 'resposta_partes' in st.session_state and st.session_state.resposta_partes:
        partes = st.session_state.resposta_partes
        
        if len(partes) >= 2:
            # --- MOMENTO 1: O SOMMELIER ---
            st.markdown("### 🍷 Momento 1: A Garrafeira")
            info_vinho = partes[0].replace("MOMENTO1", "").strip()
            st.markdown(f'<div class="vinho-box">{info_vinho}</div>', unsafe_allow_html=True)
            
            # --- MOMENTO 2: A RECEITA ---
            st.markdown("---")
            st.markdown("### 👨‍🍳 Momento 2: A Cozinha")
            receita_detalhada = partes[1].replace("MOMENTO2", "").strip()
            st.markdown(receita_detalhada)
        else:
            st.markdown(partes[0] if partes else "Resposta inválida")

st.markdown("---")
st.caption("Maria - Harmonização Garantida 1.5 Flash | 2026")
