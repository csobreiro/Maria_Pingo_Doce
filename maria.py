import streamlit as st
import google.generativeai as genai

# 1. Configuração da Página e Estilo Adaptativo
st.set_page_config(
    page_title="A Maria do Pingo Doce", 
    page_icon="🍷",
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
        line-height: 1.8; /* Aumenta o espaço entre linhas para ler melhor */
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 A Maria do Pingo Doce")

# 2. Configuração da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 3. Interface de Utilizador
vinho_input = st.text_input(
    "Que vinho escolheu para hoje?", 
    placeholder="Ex: Papa Figos, Muralhas, Esporão...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    
    with st.spinner('A Maria está a organizar a garrafeira e a cozinha...'):
        
        # PROMPT ÚNICO: Organiza o Momento 1 em linhas separadas e garante a coerência
        prompt_unico = f"""
        És a Maria, especialista em vinhos e cozinheira portuguesa.
        O utilizador tem o vinho: {vinho_input}.
        
        Responde seguindo rigorosamente esta estrutura dividida por "---":
        
        MOMENTO1
        🍷 **Vinho:** [Nome do Vinho]
        🏷️ **Produtor/Região:** [Nome do Produtor e Região]
        📝 **Perfil:** [Breve descrição do vinho]
        🤝 **Harmonização Ideal:** [Nome do Prato Específico]
        ---
        MOMENTO2
        # **[Nome do Prato Específico]**
        ### 🛒 **Ingredientes** (2-4 pessoas)
        ### 👨‍🍳 **Modo de Preparação** (Passo-a-passo)
        ### 💡 **Dica da Maria**
        
        Regras: 
        - No MOMENTO1, coloca cada item obrigatoriamente numa linha nova.
        - O prato no MOMENTO1 tem de ser rigorosamente o MESMO da receita no MOMENTO2.
        - Usa Português de Portugal.
        """
        
        try:
            response = model.generate_content(prompt_unico)
            partes = response.text.split("---")
            
            if len(partes) >= 2:
                # --- MOMENTO 1: O SOMMELIER (Organizado por linhas) ---
                st.markdown("### 🍷 Momento 1: A Garrafeira")
                info_vinho = partes[0].replace("MOMENTO1", "").strip()
                st.markdown(f'<div class="vinho-box">{info_vinho}</div>', unsafe_allow_html=True)
                
                # --- MOMENTO 2: A RECEITA ---
                st.markdown("---")
                st.markdown("### 👨‍🍳 Momento 2: A Cozinha")
                receita_detalhada = partes[1].replace("MOMENTO2", "").strip()
                st.markdown(receita_detalhada)
            else:
                # Fallback caso a IA não use o separador
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Erro na Maria: {e}")

st.markdown("---")
st.caption("Maria - Harmonização Garantida 2.5 Flash | 2026")
