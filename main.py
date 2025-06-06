import streamlit as st
import google.generativeai as genai


# Configuração da API Key e Modelo (conforme solicitado)
api_key = "AIzaSyDoZbscReqYZKdyCns26MrvkFFXbtHwWMU" 
genai.configure(api_key=api_key)

try:
    # Utilizando o modelo especificado
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Erro ao carregar o modelo Gemini 'gemini-2.0-flash': {e}")
    st.info("Verifique se o nome do modelo está correto e se sua chave API tem acesso a ele.")
    st.stop()

def gerar_resposta_gemini(prompt_completo):
    try:
        response = model.generate_content(prompt_completo)

        if response.parts:
            return response.text
        else:
            if response.prompt_feedback:
                st.warning(f"O prompt foi bloqueado. Razão: {response.prompt_feedback.block_reason}")
                if response.prompt_feedback.safety_ratings:
                    for rating in response.prompt_feedback.safety_ratings:
                        st.caption(f"Categoria: {rating.category}, Probabilidade: {rating.probability}")
            return "A IA não pôde gerar uma resposta para este prompt. Verifique as mensagens acima ou tente reformular seu pedido."
    except Exception as e:
        st.error(f"Erro ao gerar resposta da IA: {str(e)}")
        if hasattr(e, 'message'): # Tenta obter mais detalhes do erro da API do Gemini
            st.error(f"Detalhe da API Gemini: {e.message}")
        return None

# Título do aplicativo
st.title("Gerador de Histórias Interativas com IA 📚✨")
st.markdown("Crie histórias únicas definindo protagonista, gênero e cenário!")

# Entradas do usuário
nome_protagonista = st.text_input("Nome do Protagonista:", placeholder="Ex: Ana, João, Zara...")

genero_literario = st.selectbox(
    "Escolha o Gênero Literário:",
    ["Fantasia", "Ficção Científica", "Mistério", "Aventura", "Terror", "Romance", "Drama"]
)

local_inicial = st.radio(
    "Selecione o Local Inicial da História:",
    [
        "Uma floresta antiga e misteriosa",
        "Uma cidade futurista com torres de cristal",
        "Um castelo assombrado em ruínas",
        "Uma nave espacial à deriva no cosmos",
        "Uma pequena vila à beira-mar",
        "Um laboratório subterrâneo abandonado"
    ]
)

frase_desafio = st.text_area(
    "Frase de Efeito ou Desafio Inicial:",
    placeholder="Ex: 'E de repente, tudo ficou escuro.' ou 'O mapa indicava um perigo iminente.' ou 'Uma voz ecoou pelo corredor vazio.'"
)

detalhes_adicionais = st.text_area(
    "Detalhes e Informações Adicionais (opcional):",
    placeholder="Ex: 'O protagonista tem medo de altura', 'A história se passa no século XVIII', 'Incluir elementos de magia', 'O protagonista possui uma habilidade especial'...",
    help="Campo opcional para adicionar características específicas do protagonista, época, elementos especiais ou qualquer detalhe que você gostaria de ver na história."
)

if st.button("Gerar Início da História"):
    if not nome_protagonista:
        st.warning("Por favor, informe o nome do protagonista.")
    elif not frase_desafio.strip():
        st.warning("Por favor, adicione uma frase de efeito ou desafio inicial.")
    else:
        # Construção do prompt para geração da história
        prompt_historia = (
            f"Crie o início de uma história de '{genero_literario}' com o protagonista chamado '{nome_protagonista}'. "
            f"A história começa em '{local_inicial}'. "
            f"Incorpore a seguinte frase ou desafio no início da narrativa: '{frase_desafio}'. "
        )
        
        # Adiciona detalhes adicionais ao prompt se fornecidos
        if detalhes_adicionais.strip():
            prompt_historia += f"Considere também os seguintes detalhes e informações adicionais: '{detalhes_adicionais}'. "
        
        prompt_historia += (
            f"Escreva 2-3 parágrafos que estabeleçam o cenário, apresentem o protagonista e criem uma atmosfera envolvente "
            f"adequada ao gênero '{genero_literario}'. "
            f"Use uma linguagem rica e descritiva que capture a imaginação do leitor. "
            f"Termine o início da história com um gancho que deixe o leitor curioso para saber o que acontece a seguir."
        )

        st.markdown("---")
        st.markdown("⚙️ **Prompt que será enviado para a IA (para fins de aprendizado):**")
        st.text_area("", prompt_historia, height=200)
        st.markdown("---")

        st.info("Aguarde, a IA está criando sua história...")
        resposta_ia = gerar_resposta_gemini(prompt_historia)

        if resposta_ia:
            # Armazena a história no session state
            st.session_state.historia_completa = resposta_ia
            st.session_state.historia_gerada = True
            st.session_state.genero_historia = genero_literario
        else:
            st.error("Não foi possível gerar a história. Verifique as mensagens acima ou tente novamente mais tarde.")

# Exibe a história e opções de continuação se já foi gerada
if 'historia_gerada' in st.session_state and st.session_state.historia_gerada:
    st.markdown("---")
    st.markdown("### 📖 Início da História Gerada:")
    st.markdown(st.session_state.historia_completa)
    
    st.markdown("---")
    st.markdown("### ✍️ Continue a História:")
    
    continuacao_usuario = st.text_area(
        "Escreva como você gostaria de continuar a história:",
        placeholder="Ex: 'Então, Maria decidiu abrir a porta misteriosa...' ou 'De repente, um ruído estranho ecoou pela floresta...'",
        help="Digite o que acontece a seguir na história. Seja criativo!",
        key="continuacao_texto"
    )
    
    if st.button("Gerar Continuação com IA", key="gerar_continuacao"):
        if continuacao_usuario.strip():
            # Prompt para continuação
            prompt_continuacao = (
                f"Aqui está o início da história que foi gerada anteriormente:\n\n"
                f"{st.session_state.historia_completa}\n\n"
                f"O usuário agora quer continuar a história com o seguinte desenvolvimento:\n"
                f"'{continuacao_usuario}'\n\n"
                f"Continue a narrativa de forma fluida e coerente, mantendo o estilo e tom da história original. "
                f"Escreva 2-3 parágrafos que desenvolvam a história a partir do ponto onde o usuário continuou. "
                f"Mantenha a atmosfera do gênero '{st.session_state.genero_historia}' e termine com outro gancho interessante."
            )
            
            st.info("Aguarde, a IA está continuando sua história...")
            continuacao_ia = gerar_resposta_gemini(prompt_continuacao)
            
            if continuacao_ia:
                # Atualiza a história completa
                historia_completa_atual = f"{st.session_state.historia_completa}\n\n**[Sua continuação:]** {continuacao_usuario}\n\n{continuacao_ia}"
                st.session_state.historia_completa = historia_completa_atual
                
                st.markdown("### 📖 Continuação da História:")
                st.markdown(continuacao_ia)
            else:
                st.error("Não foi possível gerar a continuação. Tente novamente.")
        else:
            st.warning("Por favor, escreva algo para continuar a história.")
    
    # Botão para mostrar história completa
    if st.button("📚 Mostrar História Completa", key="mostrar_completa"):
        st.markdown("### 📚 História Completa até Agora:")
        st.markdown(st.session_state.historia_completa)
    
    # Botão para reiniciar
    if st.button("🔄 Criar Nova História", key="reiniciar"):
        # Limpa o session state
        for key in ['historia_completa', 'historia_gerada', 'genero_historia']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Dicas:")
    st.info("💡 Você pode continuar adicionando mais partes à história quantas vezes quiser! Cada continuação será incorporada ao contexto para manter a coerência narrativa.")