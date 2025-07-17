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
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'green_count' not in st.session_state:
    st.session_state.green_count = 0
if 'red_count' not in st.session_state:
    st.session_state.red_count = 0
if 'g1_active' not in st.session_state:
    st.session_state.g1_active = False
if 'last_suggested_entry' not in st.session_state:
    st.session_state.last_suggested_entry = None
if 'rodadas_desde_ultimo_empate' not in st.session_state:
    st.session_state.rodadas_desde_ultimo_empate = 0
if 'empates_recentes' not in st.session_state:
    st.session_state.empates_recentes = 0
if 'count_dado_1_consecutivo' not in st.session_state:
    st.session_state.count_dado_1_consecutivo = 0

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
            return "1. Alternância Simples (P-B-P)", sugestao, 70

    # Padrão 2: Sequência de 2 (Ex: Player -> Player)
    if len(historico_completo) >= 2 and ultimo_resultado != 'Empate':
        if historico_completo[-1]['Vencedor'] == historico_completo[-2]['Vencedor']:
            sugestao = ultimo_resultado
            return "2. Sequência de 2 (P-P)", sugestao, 75

    # Padrão 3: Sequência de 3 (Ex: Player -> Player -> Player) e sugestão de reversão
    if len(historico_completo) >= 3 and ultimo_resultado != 'Empate':
        if (historico_completo[-1]['Vencedor'] == historico_completo[-2]['Vencedor'] and
            historico_completo[-2]['Vencedor'] == historico_completo[-3]['Vencedor']):
            sugestao = 'Banker' if ultimo_resultado == 'Player' else 'Player'
            return "3. Sequência de 3 (P-P-P) - Reversão", sugestao, 80

    # --- Se nenhum padrão forte for detectado ---
    return "Aguardando Padrão Forte", None, 0

def analisar_sugestao(historico):
    """
    Analisa os padrões e retorna a melhor sugestão com confiança.
    Prioriza a sugestão em modo G1 se estiver ativo.
    """
    if st.session_state.g1_active and st.session_state.last_suggested_entry:
        return "Modo G1 Ativo", st.session_state.last_suggested_entry, 100, True

    nome_padrao, sugestao, confianca_base = detectar_padroes(historico)
    
    if sugestao and confianca_base >= 70:
        return nome_padrao, sugestao, confianca_base, False
    
    return "Aguardando Padrão Forte", None, 0, False

def atualizar_contadores_horarios(player_dado1, player_dado2, banker_dado1, banker_dado2, winner):
    """Atualiza contadores para detecção de horários críticos/bons."""
    
    if winner == 'Empate':
        st.session_state.rodadas_desde_ultimo_empate = 0
        st.session_state.empates_recentes += 1 
    else:
        st.session_state.rodadas_desde_ultimo_empate += 1
        st.session_state.empates_recentes = max(0, st.session_state.empates_recentes - 1)

    if 1 in [player_dado1, player_dado2, banker_dado1, banker_dado2]:
        st.session_state.count_dado_1_consecutivo += 1
    else:
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
        # Para a entrada direta, os dados e somas serão placeholders ou None
        # Você pode ajustar isso se precisar de valores fictícios ou específicos para cálculos futuros
        st.session_state.historico.append({
            "Rodada": len(st.session_state.historico) + 1,
            "Player Dados": "[N/A,N/A]",
            "Player Soma": "N/A",
            "Banker Dados": "[N/A,N/A]",
            "Banker Soma": "N/A",
            "Vencedor": winner_option,
            "Timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        # Note: 'atualizar_contadores_horarios' precisa dos dados, então não será chamada aqui
        # ou precisaria de uma versão adaptada que lide com 'N/A'
        
        st.success(f"Rodada {len(st.session_state.historico)} adicionada! Vencedor: **{winner_option}**")


st.markdown("---")

# --- Análise de Momentos da Mesa ---
st.header("⏰ Análise de Momentos da Mesa")

horario_ruim = False
horario_bom = False

if len(st.session_state.historico) > 0:
    if st.session_state.empates_recentes >= 3 and len(st.session_state.historico) <= 15:
        st.warning("⚠️ **Cuidado:** Mesa com muitos empates no início. Sugerimos cautela.")
        horario_ruim = True
    
    # A contagem de dado '1' consecutivo só funcionará se a entrada for via dados individuais
    if st.session_state.count_dado_1_consecutivo >= 5:
        st.warning(f"⚠️ **Atenção:** O dado '1' apareceu em **{st.session_state.count_dado_1_consecutivo}** rodadas seguidas. Potencial de manipulação ou momento ruim.")
        horario_ruim = True

if not horario_ruim and len(st.session_state.historico) > 0:
    st.info("No momento, não há indicação de horários ruins baseados em padrões simples.")

if len(st.session_state.historico) > 0:
    if st.session_state.rodadas_desde_ultimo_empate > 15:
        st.success(f"✅ **Excelente:** Ausência de empates por **{st.session_state.rodadas_desde_ultimo_empate}** rodadas. Oportunidade de padrões claros.")
        horario_bom = True
    
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
        else:
            st.write(f"**Entrada Sugerida:** {entrada_sugerida}")

        st.write(f"**Padrão Detectado:** {nome_padrao_sugerido}")
        st.write(f"**Confiança:** **{confianca:.0f}%**")
        
        if is_g1_active:
            st.warning("🚨 **Status:** Modo G1 Ativo! Mantenha a entrada anterior.")
        else:
            st.info("✅ **Status:** Normal. Sugestão baseada em novo padrão.")

        st.write("---")
        st.write("Registre o resultado real da rodada para contabilizar GREEN/RED:")
        
        # Botões de registro de resultado final da rodada
        col_result_buttons = st.columns(3)
        with col_result_buttons[0]:
            if st.button("🔵 Player Venceu", use_container_width=True, key="player_won_result"):
                if is_g1_active:
                    if st.session_state.last_suggested_entry == 'Player':
                        st.session_state.green_count += 1
                        st.success("🎉 G1 Bateu! GREEN!")
                    else:
                        st.session_state.red_count += 1
                        st.error("😥 G1 não bateu! RED.")
                    st.session_state.g1_active = False # Desativa G1 após o resultado
                    st.session_state.last_suggested_entry = None
                else: # Modo normal
                    if entrada_sugerida == 'Player':
                        st.session_state.green_count += 1
                        st.success("🎉 GREEN!")
                    else:
                        st.session_state.red_count += 1
                        st.error("😥 RED.")
                # st.experimental_rerun() # Não necessário, Streamlit lida com isso

        with col_result_buttons[1]:
            if st.button("🔴 Banker Venceu", use_container_width=True, key="banker_won_result"):
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
                # st.experimental_rerun() # Não necessário

        with col_result_buttons[2]:
            if st.button("🟡 Empate", use_container_width=True, key="tie_result"):
                # Empate não afeta contadores de GREEN/RED ou G1 se a aposta não foi em empate
                # Se a sugestão foi Player/Banker, e deu empate, não é RED nem GREEN
                # Se você quiser considerar RED em caso de empate para apostas em Player/Banker, altere aqui.
                st.info("Rodada foi um empate. Contadores de GREEN/RED e G1 não alterados para esta aposta.")
                # st.experimental_rerun() # Não necessário

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
