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
        line-height: 1.8;
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
model = genai.GenerativeModel('models/gemini-2.0-flash') # Atualizado para a versão mais estável

# 3. Interface de Utilizador
vinho_input = st.text_input(
    "Que vinho escolheu para hoje?", 
    placeholder="Ex: Papa Figos, Muralhas, Esporão...",
    max_chars=100
)

if vinho_input and vinho_input.strip():
    
    with st.spinner('A Maria está a preparar a garrafeira e a cozinha...'):
        
        # PROMPT REFORÇADO: Instruções diretas para evitar falhas na receita
        prompt_unico = f"""
        És a Maria, especialista em vinhos e cozinheira portuguesa.
        O utilizador tem o vinho: {vinho_input}.
        
        Gera uma resposta com duas secções claras separadas por "SEPARADOR_MARIA".
        
        Na primeira secção (Vinho):
        🍷 **Vinho:** [Nome]
        🏷️ **Produtor/Região:** [Nome]
        📝 **Perfil:** [Breve descrição]
        🌡️ **Servir a:** [Temperatura ideal]
        🤝 **Harmonização Ideal:** [Nome do Prato]

        Na segunda secção (Receita):
        # **[Nome do Prato]**
        ### 🛒 **Ingredientes** (2-4 pessoas)
        ### 👨‍🍳 **Modo de Preparação**
        ### 💡 **Dica da Maria**
        
        Regras: 
        - O prato da harmonização tem de ser o mesmo da receita.
        - Usa Português de Portugal.
        - Escreve "SEPARADOR_MARIA" entre as duas secções.
        """
        
        try:
            response = model.generate_content(prompt_unico)
            conteudo = response.text
            
            if "SEPARADOR_MARIA" in conteudo:
                partes = conteudo.split("SEPARADOR_MARIA")
                
                # --- MOMENTO 1 ---
                st.markdown("### 🍷 Momento 1: A Garrafeira")
                st.markdown(f'<div class="vinho-box">{partes[0].strip()}</div>', unsafe_allow_html=True)
                
                # --- MOMENTO 2 ---
                st.markdown("---")
                st.markdown("### 👨‍🍳 Momento 2: A Cozinha")
                st.markdown(partes[1].strip())
            else:
                # Se a IA falhar o separador, mostra tudo para não deixar o utilizador sem nada
                st.markdown(conteudo)
                
        except Exception as e:
            st.error(f"Erro ao contactar a Maria: {e}")

st.markdown("---")
st.caption("Maria - Sommelier & Chef | Versão 2026")
