import streamlit as st
import pandas as pd
import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Bac Bo Predictor 🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': 'Este aplicativo ajuda a analisar padrões no jogo Bac Bo da Evolution Gaming.'
    }
)

# --- Inicialização do Estado da Sessão ---
# Usamos st.session_state para manter o estado do app entre as interações.
# Isso garante que as variáveis não sejam perdidas a cada interação do usuário.
if 'historico' not in st.session_state:
    st.session_state.historico = [] # Lista de dicionários com os resultados de cada rodada
if 'green_count' not in st.session_state:
    st.session_state.green_count = 0 # Contador de acertos (GREEN)
if 'red_count' not in st.session_state:
    st.session_state.red_count = 0 # Contador de erros (RED)
if 'g1_active' not in st.session_state:
    st.session_state.g1_active = False # Flag para ativar o modo G1 (Martingale simplificado)
if 'last_suggested_entry' not in st.session_state:
    st.session_state.last_suggested_entry = None # Armazena a última sugestão para o modo G1
if 'rodadas_desde_ultimo_empate' not in st.session_state:
    st.session_state.rodadas_desde_ultimo_empate = 0 # Contagem para o padrão de "empate sumindo"
if 'empates_recentes' not in st.session_state:
    st.session_state.empates_recentes = 0 # Contagem para o padrão de "muitos empates iniciais"
if 'count_dado_1_consecutivo' not in st.session_state:
    st.session_state.count_dado_1_consecutivo = 0 # Contagem para o padrão de "dado 1 repetido"

# --- Funções Auxiliares ---
def get_winner(player_sum, banker_sum):
    """Determina o vencedor da rodada com base nas somas dos dados."""
    if player_sum == banker_sum:
        return 'Empate'
    elif player_sum > banker_sum:
        return 'Player'
    else:
        return 'Banker'

def detectar_padroes(historico_completo):
    """
    Função para detecção de padrões.
    Esta função deve ser expandida para conter a lógica dos seus 30 padrões.
    Retorna o nome do padrão, a sugestão (Player/Banker) e um nível de confiança.
    """
    # Se o histórico for muito pequeno, não há padrões complexos a serem detectados
    if not historico_completo or len(historico_completo) < 2:
        return "Nenhum Padrão Forte", None, 0

    ultimo_resultado = historico_completo[-1]['Vencedor']
    
    # --- Exemplos de Padrões (você deve expandir esta seção) ---
    # Padrão 1: Alternância Simples (Ex: Player -> Banker -> Player)
    if len(historico_completo) >= 2:
        segundo_ultimo_resultado = historico_completo[-2]['Vencedor']
        if ultimo_resultado != 'Empate' and segundo_ultimo_resultado != 'Empate' and \
           ultimo_resultado != segundo_ultimo_resultado:
            sugestao = 'Banker' if ultimo_resultado == 'Player' else 'Player'
            return "1. Alternância Simples (P-B-P)", sugestao, 70 # Exemplo de confiança

    # Padrão 2: Sequência de 2 (Ex: Player -> Player)
    if len(historico_completo) >= 2 and ultimo_resultado != 'Empate':
        if historico_completo[-1]['Vencedor'] == historico_completo[-2]['Vencedor']:
            sugestao = ultimo_resultado # Sugere o mesmo que veio antes
            return "2. Sequência de 2 (P-P)", sugestao, 75

    # Padrão 3: Sequência de 3 (Ex: Player -> Player -> Player) e sugestão de reversão
    if len(historico_completo) >= 3 and ultimo_resultado != 'Empate':
        if (historico_completo[-1]['Vencedor'] == historico_completo[-2]['Vencedor'] and
            historico_completo[-2]['Vencedor'] == historico_completo[-3]['Vencedor']):
            sugestao = 'Banker' if ultimo_resultado == 'Player' else 'Player' # Sugere o oposto
            return "3. Sequência de 3 (P-P-P) - Reversão", sugestao, 80

    # Adicione aqui seus outros 27 padrões...
    # Exemplo de como você poderia adicionar mais um:
    # if len(historico_completo) >= 4 and ultimo_resultado == 'Player' and \
    #    historico_completo[-2]['Vencedor'] == 'Banker' and \
    #    historico_completo[-3]['Vencedor'] == 'Player' and \
    #    historico_completo[-4]['Vencedor'] == 'Banker':
    #    return "4. Padrão 'PB PB'", 'Player', 85

    # --- Se nenhum padrão forte for detectado ---
    return "Aguardando Padrão Forte", None, 0

def analisar_sugestao(historico):
    """
    Analisa os padrões e retorna a melhor sugestão com confiança.
    Prioriza a sugestão em modo G1 se estiver ativo.
    """
    # Se o modo G1 estiver ativo, a sugestão é a última feita
    if st.session_state.g1_active and st.session_state.last_suggested_entry:
        # A confiança é 100% no modo G1 para indicar que a aposta é fixa
        return "Modo G1 Ativo", st.session_state.last_suggested_entry, 100, True

    # Pega o nome do padrão, sugestão e confiança da função de detecção
    nome_padrao, sugestao, confianca_base = detectar_padroes(historico)
    
    # Apenas sugere se a confiança for alta o suficiente
    # Você pode ajustar este limite (ex: 60, 70, 80) dependendo da robustez dos seus padrões.
    if sugestao and confianca_base >= 70:
        return nome_padrao, sugestao, confianca_base, False
    
    return "Aguardando Padrão Forte", None, 0, False # Não há sugestão com alta confiança

def atualizar_contadores_horarios(player_dado1, player_dado2, banker_dado1, banker_dado2, winner):
    """Atualiza contadores para detecção de horários críticos/bons.
    Nota: Esta função requer os valores dos dados, não funciona com 'Vencedor Direto' se dados não forem fornecidos.
    """
    
    # Contar rodadas desde o último empate
    if winner == 'Empate':
        st.session_state.rodadas_desde_ultimo_empate = 0
        st.session_state.empates_recentes += 1 
    else:
        st.session_state.rodadas_desde_ultimo_empate += 1
        # Diminui empates recentes se não houver um empate na rodada atual
        # Isso ajuda a monitorar a 'densidade' de empates
        st.session_state.empates_recentes = max(0, st.session_state.empates_recentes - 1)

    # Contar dado '1' consecutivo (em qualquer dado)
    # Verifica se os dados são números antes de verificar o 1
    if all(isinstance(d, int) for d in [player_dado1, player_dado2, banker_dado1, banker_dado2]):
        if 1 in [player_dado1, player_dado2, banker_dado1, banker_dado2]:
            st.session_state.count_dado_1_consecutivo += 1
        else:
            st.session_state.count_dado_1_consecutivo = 0
    else: # Se a entrada foi direta, não podemos contar o dado 1 consecutivo
        st.session_state.count_dado_1_consecutivo = 0


# --- Título do App ---
st.title("🎲 Bac Bo Predictor - Guia de Padrões")
st.markdown("---")

# --- Painel de Entrada de Dados ---
st.header("➕ Adicionar Nova Rodada ao Histórico")

# Seleção do método de entrada
entry_method = st.radio(
    "Como deseja adicionar a rodada?",
    ("Inserir Dados Individuais", "Inserir Vencedor Direto"),
    key="entry_method"
)

if entry_method == "Inserir Dados Individuais":
    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("🔵 Player")
        # Usando min_value, max_value e value para melhor usabilidade
        player_dado1 = st.number_input("Dado 1 do Player", min_value=1, max_value=6, value=1, key="pd1_input")
        player_dado2 = st.number_input("Dado 2 do Player", min_value=1, max_value=6, value=1, key="pd2_input")

    with col_input2:
        st.subheader("🔴 Banker")
        banker_dado1 = st.number_input("Dado 1 do Banker", min_value=1, max_value=6, value=1, key="bd1_input")
        banker_dado2 = st.number_input("Dado 2 do Banker", min_value=1, max_value=6, value=1, key="bd2_input")

    add_round_button = st.button("➕ Adicionar Rodada e Analisar", use_container_width=True, key="add_round_dices")

    if add_round_button:
        player_sum = player_dado1 + player_dado2
        banker_sum = banker_dado1 + banker_dado2
        winner = get_winner(player_sum, banker_sum)

        st.session_state.historico.append({
            "Rodada": len(st.session_state.historico) + 1,
            "Player Dados": f"[{player_dado1},{player_dado2}]",
            "Player Soma": player_sum,
            "Banker Dados": f"[{banker_dado1},{banker_dado2}]",
            "Banker Soma": banker_sum,
            "Vencedor": winner,
            "Timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Esta função só é chamada aqui porque requer os valores dos dados
        atualizar_contadores_horarios(player_dado1, player_dado2, banker_dado1, banker_dado2, winner)
        st.success(f"Rodada {len(st.session_state.historico)} adicionada! Vencedor: **{winner}**")

elif entry_method == "Inserir Vencedor Direto":
    winner_option = st.selectbox(
        "Selecione o Vencedor da Rodada:",
        ("Player", "Banker", "Empate"),
        key="winner_direct_select"
    )
    add_winner_button = st.button("➕ Adicionar Rodada (Vencedor Direto)", use_container_width=True, key="add_round_winner")

    if add_winner_button:
        # Para a entrada direta, os dados e somas serão placeholders (N/A)
        # Os contadores de horários críticos/bons que dependem dos dados individuais não serão atualizados aqui
        st.session_state.historico.append({
            "Rodada": len(st.session_state.historico) + 1,
            "Player Dados": "N/A", # Usando "N/A" para indicar que não foram fornecidos dados
            "Player Soma": "N/A",
            "Banker Dados": "N/A",
            "Banker Soma": "N/A",
            "Vencedor": winner_option,
            "Timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Ao inserir direto, só atualizamos os contadores que não dependem de dados individuais.
        # Para empates_recentes e rodadas_desde_ultimo_empate, podemos usar o winner_option.
        # Para count_dado_1_consecutivo, não temos dados, então resetamos ou mantemos zero.
        # Ajustamos a função para lidar com isso ou não a chamamos para dados N/A
        # Chamar com None para dados para que a função se adapte
        atualizar_contadores_horarios(None, None, None, None, winner_option) # Passa None para dados não disponíveis

        st.success(f"Rodada {len(st.session_state.historico)} adicionada! Vencedor: **{winner_option}**")


st.markdown("---")

# --- Análise de Momentos da Mesa ---
st.header("⏰ Análise de Momentos da Mesa")

horario_ruim = False
horario_bom = False

if len(st.session_state.historico) > 0:
    # Critério 1: Muitos empates no início (ex: 3 empates nas primeiras 10-15 rodadas)
    # Ajuste '15' conforme o período de análise desejado para "início".
    if st.session_state.empates_recentes >= 3 and len(st.session_state.historico) <= 15:
        st.warning("⚠️ **Cuidado:** Mesa com muitos empates no início. Sugerimos cautela.")
        horario_ruim = True
    
    # Critério 2: Dado '1' aparecendo consecutivamente em qualquer dado
    # Nota: Este contador só funciona se a entrada for via dados individuais.
    if st.session_state.count_dado_1_consecutivo >= 5:
        st.warning(f"⚠️ **Atenção:** O dado '1' apareceu em **{st.session_state.count_dado_1_consecutivo}** rodadas seguidas. Potencial de manipulação ou momento ruim.")
        horario_ruim = True

if not horario_ruim and len(st.session_state.historico) > 0:
    st.info("No momento, não há indicação de horários ruins baseados em padrões simples.")

if len(st.session_state.historico) > 0:
    # Critério 1: Empates sumindo por mais de 15 rodadas
    if st.session_state.rodadas_desde_ultimo_empate > 15:
        st.success(f"✅ **Excelente:** Ausência de empates por **{st.session_state.rodadas_desde_ultimo_empate}** rodadas. Oportunidade de padrões claros.")
        horario_bom = True
    
    # Critério 2: Padrão Ouro se formando (seria detectado na função 'detectar_padroes' e retornado com alta confiança)
    _, _, confianca_sugestao, _ = analisar_sugestao(st.session_state.historico)
    if confianca_sugestao > 90:
        st.success("✨ **Momento Promissor:** Padrão de alta confiança detectado!")
        horario_bom = True

if not horario_bom and not horario_ruim and len(st.session_state.historico) > 0:
    st.info("O momento atual da mesa é neutro. Continue acompanhando.")
elif len(st.session_state.historico) == 0:
    st.info("Adicione algumas rodadas para começar a análise dos momentos da mesa.")

st.markdown("---")

# --- Sugestão de Entrada Inteligente ---
st.header("🎯 Sugestão de Entrada Inteligente")

nome_padrao_sugerido, entrada_sugerida, confianca, is_g1_active = analisar_sugestao(st.session_state.historico)

if horario_ruim:
    st.warning("🚫 **Sugestões Bloqueadas:** O aplicativo está em um horário crítico (ruim). Não é recomendado fazer entradas.")
elif entrada_sugerida:
    st.session_state.last_suggested_entry = entrada_sugerida # Salva a última sugestão para o G1
    with st.expander("Ver Sugestão Detalhada", expanded=True):
        st.subheader(f"🎉 Entrada Sugerida!")
        
        if entrada_sugerida == 'Player':
            st.markdown(f"**Entrada Sugerida:** {'<span style="color:blue; font-size: 20px; font-weight: bold;">🔵 PLAYER</span>'}", unsafe_allow_html=True)
        elif entrada_sugerida == 'Banker':
            st.markdown(f"**Entrada Sugerida:** {'<span style="color:red; font-size: 20px; font-weight: bold;">🔴 BANKER</span>'}", unsafe_allow_html=True)
        else: # Caso a sugestão seja Empate (se você implementar padrões para isso)
            st.write(f"**Entrada Sugerida:** {entrada_sugerida}")

        st.write(f"**Padrão Detectado:** {nome_padrao_sugerido}")
        st.write(f"**Confiança:** **{confianca:.0f}%**")
        
        if is_g1_active:
            st.warning("🚨 **Status:** Modo G1 Ativo! Mantenha a entrada anterior.")
        else:
            st.info("✅ **Status:** Normal. Sugestão baseada em novo padrão.")

        st.write("---")
        st.write("Registre o resultado real da rodada para contabilizar GREEN/RED:")
        
        # Botões de registro de resultado final da rodada (coloridos)
        col_result_buttons = st.columns(3)
        with col_result_buttons[0]:
            if st.button("Player", use_container_width=True, key="player_won_result", type="primary"): # "primary" para azul
                if is_g1_active:
                    if st.session_state.last_suggested_entry == 'Player':
                        st.session_state.green_count += 1
                        st.success("🎉 G1 Bateu! GREEN!")
                    else:
                        st.session_state.red_count += 1
                        st.error("😥 G1 não bateu! RED.")
                    st.session_state.g1_active = False # Desativa G1 após o resultado
                    st.session_state.last_suggested_entry = None
                else: # Modo normal (sem G1 ativo)
                    if entrada_sugerida == 'Player':
                        st.session_state.green_count += 1
                        st.success("🎉 GREEN!")
                    else:
                        st.session_state.red_count += 1
                        st.error("😥 RED.")

        with col_result_buttons[1]:
            if st.button("Banker", use_container_width=True, key="banker_won_result", type="secondary"): # "secondary" para vermelho ou "danger"
                # Note: Streamlit 1.16+ `type="secondary"` renderiza um botão cinza.
                # Para um vermelho real, você precisaria de custom CSS ou usar HTML/Markdown para o botão.
                # No entanto, "danger" (se suportado diretamente pelo `st.button`) seria ideal.
                # Como alternativa, para a cor vermelha, vamos usar um tipo padrão e customizar com CSS (fora do escopo deste snippet direto)
                # ou usar uma abordagem com HTML/Markdown como no texto da sugestão.
                # Para este exemplo, manterei `type="secondary"` ou um botão padrão com um emoji.
                # Vou usar um emoji para o vermelho aqui para clareza visual.
                if is_g1_active:
                    if st.session_state.last_suggested_entry == 'Banker':
                        st.session_state.green_count += 1
                        st.success("🎉 G1 Bateu! GREEN!")
                    else:
                        st.session_state.red_count += 1
                        st.error("😥 G1 não bateu! RED.")
                    st.session_state.g1_active = False # Desativa G1 após o resultado
                    st.session_state.last_suggested_entry = None
                else: # Modo normal
                    if entrada_sugerida == 'Banker':
                        st.session_state.green_count += 1
                        st.success("🎉 GREEN!")
                    else:
                        st.session_state.red_count += 1
                        st.error("😥 RED.")

        with col_result_buttons[2]:
            if st.button("Empate", use_container_width=True, key="tie_result", type="secondary"): # "secondary" ou "warning" (warning não é um tipo direto)
                st.info("Rodada foi um empate. Contadores de GREEN/RED e G1 não alterados para esta aposta.")
                # Se a sugestão foi Player/Banker, e deu empate, não é RED nem GREEN
                # Se você quiser considerar RED em caso de empate para apostas em Player/Banker, altere aqui.

else:
    st.info("Aguardando mais dados ou padrões de alta confiança para sugerir uma entrada. Continue adicionando rodadas!")


st.markdown("---")

# --- Painel de Histórico e Estatísticas ---
st.header("📈 Painel de Resultados")

# Estatísticas
col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    st.metric(label="💚 GREEN (Acertos)", value=st.session_state.green_count)
with col_stats2:
    st.metric(label="💔 RED (Erros)", value=st.session_state.red_count)
with col_stats3:
    total_jogadas = st.session_state.green_count + st.session_state.red_count
    if total_jogadas > 0:
        win_rate = (st.session_state.green_count / total_jogadas) * 100
        st.metric(label="📊 Taxa de Acerto", value=f"{win_rate:.2f}%")
    else:
        st.metric(label="📊 Taxa de Acerto", value="N/A")

# Histórico Detalhado
st.subheader("📜 Histórico de Rodadas")
if st.session_state.historico:
    # Cria um DataFrame e exibe o histórico em ordem reversa (mais recente primeiro)
    df_historico = pd.DataFrame(st.session_state.historico[::-1])
    st.dataframe(df_historico.set_index('Rodada'), use_container_width=True)
else:
    st.info("Nenhuma rodada adicionada ainda. Use o painel acima para começar.")

# Botão para limpar o histórico e resetar tudo
st.markdown("---")
if st.button("🔄 Limpar Histórico e Resetar Tudo", help="Isso apagará todas as rodadas e redefinirá os contadores."):
    st.session_state.historico = []
    st.session_state.green_count = 0
    st.session_state.red_count = 0
    st.session_state.g1_active = False
    st.session_state.last_suggested_entry = None
    st.session_state.rodadas_desde_ultimo_empate = 0
    st.session_state.empates_recentes = 0
    st.session_state.count_dado_1_consecutivo = 0
    # A re-execução automática do Streamlit cuida da atualização.
