import streamlit as st
import requests
import json

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
    st.error("⚠️ Configure a GEMINI_API_KEY nos Secrets")
    st.stop()

# TESTE DA API KEY - MUITO IMPORTANTE
st.sidebar.title("🔧 Diagnóstico")

if st.sidebar.button("🧪 Testar API Key"):
    with st.sidebar:
        st.info("A testar ligação à API...")
        
        # Testa listar modelos
        url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        try:
            response = requests.get(url_list, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'models' in data:
                    modelos = [
                        m['name'] for m in data['models'] 
                        if 'generateContent' in m.get('supportedGenerationMethods', [])
                    ]
                    
                    if modelos:
                        st.success(f"✅ API Key válida!")
                        st.write(f"**{len(modelos)} modelos disponíveis:**")
                        for m in modelos:
                            st.code(m)
                    else:
                        st.error("❌ API Key válida MAS sem modelos disponíveis")
                        st.warning("Sua conta não tem acesso aos modelos Gemini")
                        st.markdown("""
                        **Causas possíveis:**
                        - Região bloqueada
                        - Conta sem permissões
                        - API Gemini não ativada
                        
                        **Solução:**
                        1. Acesse: https://aistudio.google.com/
                        2. Faça login
                        3. Crie uma nova API key
                        4. Teste gerando texto manualmente no site
                        """)
                else:
                    st.error("❌ Resposta inesperada da API")
                    st.json(data)
                    
            elif response.status_code == 400:
                st.error("❌ API Key inválida ou malformada")
                st.code(response.text)
                
            elif response.status_code == 403:
                st.error("❌ API Key sem permissões ou região bloqueada")
                st.markdown("""
                **Regiões suportadas:**
                - Europa (exceto alguns países)
                - EUA
                - Ásia (maioria)
                
                **Portugal está suportado!**
                
                Verifique em: https://ai.google.dev/gemini-api/docs/available-regions
                """)
                
            else:
                st.error(f"❌ Erro {response.status_code}")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"❌ Erro de conexão: {e}")

# Interface principal
vinho = st.text_input(
    "Qual é o vinho?", 
    placeholder="Ex: Papa Figos, Esporão, Periquita...",
    max_chars=100
)

if vinho and vinho.strip():
    vinho_limpo = vinho.strip()
    
    with st.spinner('🍇 A Maria está a trabalhar...'):
        
        prompt = f"""És a Maria, uma sommelier portuguesa com 20 anos de experiência.

O cliente tem este vinho: {vinho_limpo}

Por favor:
1. Identifica o tipo de vinho (se conheceres)
2. Sugere UMA receita portuguesa tradicional que harmonize bem
3. Explica brevemente porquê (acidez, corpo, taninos, etc.)

Responde em português de Portugal, tom amigável e profissional."""

        # Lista de endpoints para tentar
        modelos_tentar = [
            'gemini-1.5-flash-002',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
        ]
        
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 600,
            }
        }
        
        sucesso = False
        
        for modelo in modelos_tentar:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Verifica se tem resposta
                    if 'candidates' in result and len(result['candidates']) > 0:
                        texto = result['candidates'][0]['content']['parts'][0]['text']
                        
                        st.markdown("---")
                        st.markdown("### 🍽️ Sugestão da Maria")
                        st.markdown(texto)
                        st.balloons()
                        st.caption(f"*Modelo: {modelo}*")
                        sucesso = True
                        break
                    else:
                        st.warning(f"⚠️ {modelo}: Resposta vazia")
                        
                elif response.status_code == 404:
                    continue  # Tenta próximo modelo
                    
                else:
                    st.warning(f"⚠️ {modelo}: Erro {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.warning(f"⏱️ {modelo}: Timeout")
                continue
                
            except Exception as e:
                st.warning(f"⚠️ {modelo}: {str(e)[:100]}")
                continue
        
        if not sucesso:
            st.error("❌ Nenhum modelo funcionou")
            st.markdown("""
            ### 🔧 O que fazer:
            
            1. **Clique em "🧪 Testar API Key"** na barra lateral
            2. Veja qual é o problema específico
            3. Siga as instruções apresentadas
            
            ### 🔑 Criar nova API Key:
            1. Acesse: https://aistudio.google.com/apikey
            2. Clique em **"Create API Key"**
            3. Copie a key
            4. Cole nos Secrets do Streamlit
            
            ### 🌍 Verificar região:
            Portugal está suportado, mas verifique em:
            https://ai.google.dev/gemini-api/docs/available-regions
            """)
