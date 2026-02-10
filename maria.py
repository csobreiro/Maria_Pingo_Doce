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

# Validação da API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets do Streamlit.")
    st.info("👉 Obtenha em: https://aistudio.google.com/apikey")
    st.stop()

# Configuração
genai.configure(api_key=api_key)

# Botão para debug
if st.sidebar.button("🔍 Ver modelos disponíveis"):
    with st.sidebar:
        try:
            st.write("**Modelos com generateContent:**")
            modelos_encontrados = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_encontrados.append(m.name)
                    st.success(f"✅ {m.name}")
            
            if not modelos_encontrados:
                st.error("❌ Nenhum modelo encontrado!")
                st.warning("Possíveis causas:")
                st.markdown("""
                - API key inválida
                - Região bloqueada
                - Conta sem acesso ao Gemini
                """)
        except Exception as e:
            st.error(f"Erro: {e}")

# Input do utilizador
vinho = st.text_input(
    "Qual é o vinho?", 
    placeholder="Ex: Papa Figos, Esporão, Periquita...",
    max_chars=100
)

if vinho and vinho.strip():
    vinho_limpo = vinho.strip()
    
    with st.spinner('🍇 A Maria está a trabalhar...'):
        prompt = f"""És a Maria, sommelier portuguesa experiente.

Vinho do utilizador: {vinho_limpo}

Tarefa:
1. Identifica o tipo de vinho
2. Sugere UMA receita portuguesa que harmonize bem
3. Explica brevemente porquê (em 2-3 linhas)

Responde em português de Portugal, tom amigável."""

        try:
            # IMPORTANTE: Usar o nome COMPLETO do modelo
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            if response.text:
                st.markdown("---")
                st.markdown("### 🍽️ Sugestão da Maria")
                st.markdown(response.text)
                st.balloons()
            else:
                st.warning("A resposta veio vazia. Tente novamente.")
                
        except Exception as e:
            erro_texto = str(e)
            
            # Se for erro 404, tenta outros modelos
            if "404" in erro_texto:
                st.error("❌ Modelo não encontrado. A tentar alternativas...")
                
                modelos_fallback = [
                    'gemini-1.5-pro',
                    'gemini-1.5-flash-latest',
                    'gemini-pro',
                ]
                
                sucesso = False
                for modelo_alt in modelos_fallback:
                    try:
                        st.info(f"Tentando {modelo_alt}...")
                        model_alt = genai.GenerativeModel(modelo_alt)
                        response = model_alt.generate_content(prompt)
                        
                        if response.text:
                            st.markdown("---")
                            st.markdown("### 🍽️ Sugestão da Maria")
                            st.markdown(response.text)
                            st.caption(f"*Modelo usado: {modelo_alt}*")
                            sucesso = True
                            break
                    except Exception:
                        continue
                
                if not sucesso:
                    st.error("❌ Nenhum modelo funcionou.")
                    st.markdown("""
                    ### 🔧 Soluções:
                    1. Verifique se a API key está correta
                    2. Clique em **"Ver modelos disponíveis"** na barra lateral
                    3. Acesse: https://aistudio.google.com/apikey
                    4. Crie uma nova API key se necessário
                    """)
            else:
                st.error(f"❌ Erro: {erro_texto}")
