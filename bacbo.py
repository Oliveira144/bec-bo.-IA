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
# Usamos st.session_state para manter o estado do app entre as interações
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
    st.session_state.empates_recentes = 0 # Para controle de horários ruins (ex: 3 empates em 10 rodadas)
if 'count_dado_1_consecutivo' not in st.session_state:
    st.session_state.count_dado_1_consecutivo = 0


# --- Funções Auxiliares ---
def get_winner(player_sum, banker_sum):
    """Determina o vencedor da rodada."""
    if player_sum == banker_sum:
        return 'Empate'
    elif player_sum > banker_sum:
        return 'Player'
    else:
        return 'Banker'

def detectar_padroes(historico_completo):
    """
    Função placeholder para detecção de padrões.
    Esta função seria expandida para conter a lógica dos 30 padrões.
    Por enquanto, retorna um padrão genérico e uma sugestão.
    """
    if not historico_completo:
        return "Nenhum Padrão Detectado", None, 0 # Nome do padrão, Sugestão (Player/Banker), Confiança

    ultimo_resultado = historico_completo[-1]['winner']
    
    # Exemplo simples de padrão: Alternância Simples (P-B-P-B)
    if len(historico_completo) >= 2:
        segundo_ultimo_resultado = historico_completo[-2]['winner']
        if ultimo_resultado != 'Empate' and segundo_ultimo_resultado != 'Empate' and \
           ultimo_resultado != segundo_ultimo_resultado:
            sugestao = 'Banker' if ultimo_resultado == 'Player' else 'Player'
            return "Alternância Simples", sugestao, 70 # 70% de confiança para este exemplo

    # Exemplo simples de padrão: Sequência de 2
    if len(historico_completo) >= 2 and ultimo_resultado != 'Empate':
        if historico_completo[-1]['winner'] == historico_completo[-2]['winner']:
            sugestao = ultimo_resultado
            return "Sequência de 2", sugestao, 75 # 75% de confiança
            
    # Placeholder para o Padrão Ouro
    # Na implementação real, você teria um algoritmo complexo aqui.
    # Por exemplo, se uma sequência P-P-B se repetiu duas vezes recentemente:
    # if detectar_padrao_ouro_real(historico_completo):
    #     return "Padrão Ouro", "Player", 95 # Altíssima confiança
            
    return "Nenhum Padrão Forte", None, 0 # Se nenhum padrão significativo for encontrado


def analisar_sugestao(historico):
    """
    Analisa os padrões e retorna a melhor sugestão com confiança.
    Prioriza a sugestão em modo G1 se estiver ativo.
    """
    if st.session_state.g1_active and st.session_state.last_suggested_entry:
        return "Modo G1 Ativo", st.session_state.last_suggested_entry, 100, True

    # Pega o nome do padrão, sugestão e confiança da função de detecção
    nome_padrao, sugestao, confiança_base = detectar_padroes(historico)
    
    if confiança_base >= 90: # Apenas sugere se a confiança for alta
        return nome_padrao, sugestao, confiança_base, False
    
    return "Nenhum Padrão Forte", None, 0, False # Não há sugestão com alta confiança

def atualizar_contadores_horarios(player_dado1, player_dado2, banker_dado1, banker_dado2, winner):
    """Atualiza contadores para detecção de horários críticos."""
    # Contar rodadas desde o último empate
    if winner == 'Empate':
        st.session_state.rodadas_desde_ultimo_empate = 0
        st.session_state.empates_recentes += 1
    else:
        st.session_state.rodadas_desde_ultimo_empate += 1
        st.session_state.empates_recentes = 0 # Reseta se houver uma sequência sem empate

    # Contar dado '1' consecutivo
    if 1 in [player_dado1, player_dado2, banker_dado1, banker_dado2]:
        st.session_state.count_dado_1_consecutivo += 1
    else:
        st.session_state.count_dado_1_consecutivo = 0


# --- Título do App ---
st.title("🎲 Bac Bo Predictor")
st.markdown("---")

# --- Painel de Entrada de Dados ---
st.header("Adicionar Nova Rodada")

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.subheader("🔵 Player")
    player_dado1 = st.number_input("Dado 1 do Player", min_value=1, max_value=6, value=1, key="pd1")
    player_dado2 = st.number_input("Dado 2 do Player", min_value=1, max_value=6, value=1, key="pd2")

with col_input2:
    st.subheader("🔴 Banker")
    banker_dado1 = st.number_input("Dado 1 do Banker", min_value=1, max_value=6, value=1, key="bd1")
    banker_dado2 = st.number_input("Dado 2 do Banker", min_value=1, max_value=6, value=1, key="bd2")

add_round_button = st.button("➕ Adicionar Rodada e Analisar")

if add_round_button:
    player_sum = player_dado1 + player_dado2
    banker_sum = banker_dado1 + banker_dado2
    winner = get_winner(player_sum, banker_sum)

    # Armazena os dados da rodada no histórico
    st.session_state.historico.append({
        "Rodada": len(st.session_state.historico) + 1,
        "Player Dados": f"[{player_dado1},{player_dado2}]",
        "Player Soma": player_sum,
        "Banker Dados": f"[{banker_dado1},{banker_dado2}]",
        "Banker Soma": banker_sum,
        "Vencedor": winner,
        "Timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    
    # Atualiza contadores de horários críticos
    atualizar_contadores_horarios(player_dado1, player_dado2, banker_dado1, banker_dado2, winner)

    # Exibe uma mensagem de sucesso
    st.success(f"Rodada {len(st.session_state.historico)} adicionada! Vencedor: {winner}")

st.markdown("---")

# --- Análise de Horários Críticos ---
st.header("⏰ Análise de Horários Críticos")

if st.session_state.empates_recentes >= 3 and len(st.session_state.historico) <= 10 and len(st.session_state.historico) > 0:
    st.warning("⚠️ **Cuidado:** Novo baralho com muitos empates iniciais. Sugerimos cautela.")
elif st.session_state.count_dado_1_consecutivo >= 5:
    st.warning("⚠️ **Atenção:** Dado '1' apareceu em 5 rodadas seguidas. Potencial de manipulação ou momento ruim.")
else:
    st.info("No momento, não há indicação de horários ruins baseados em padrões simples. Continue monitorando.")

if st.session_state.rodadas_desde_ultimo_empate > 15 and len(st.session_state.historico) > 0:
    st.success("✅ **Excelente:** Ausência prolongada de empates. Oportunidade de padrões claros.")


st.markdown("---")

# --- Sugestão de Entrada Inteligente ---
st.header("🎯 Sugestão de Entrada")

# Analisa e obtém a sugestão
nome_padrao_sugerido, entrada_sugerida, confianca, is_g1_active = analisar_sugestao(st.session_state.historico)

if entrada_sugerida:
    st.session_state.last_suggested_entry = entrada_sugerida # Salva a última sugestão para o G1
    with st.expander("Ver Sugestão Detalhada"):
        st.subheader(f"🎉 Entrada Sugerida!")
        st.write(f"**Padrão Detectado:** {nome_padrao_sugerido}")
        st.write(f"**Entrada Sugerida:** {'🔵 PLAYER' if entrada_sugerida == 'Player' else '🔴 BANKER'}")
        st.write(f"**Confiança:** {confianca:.0f}%")
        if is_g1_active:
            st.warning("**Status:** 🚨 Modo G1 Ativo! Mantenha a entrada anterior.")
        else:
            st.info("**Status:** Normal")

        # Botões de Feedback
        col_feedback1, col_feedback2, col_feedback3 = st.columns(3)
        with col_feedback1:
            if st.button("✅ GREEN (Acertou)"):
                st.session_state.green_count += 1
                st.session_state.g1_active = False # Desativa G1 se acertou
                st.session_state.last_suggested_entry = None # Reseta a sugestão G1
                st.success("🎉 Parabéns! GREEN!")
        with col_feedback2:
            if st.button("❌ RED (Errou)"):
                st.session_state.red_count += 1
                st.session_state.g1_active = True # Ativa G1 se errou
                st.error("😥 Que pena! RED. G1 ativado para a próxima entrada.")
        with col_feedback3:
            if st.button("🟡 EMPATE"):
                st.info("Rodada foi um empate. Contadores e G1 não alterados.")
else:
    st.info("Aguardando mais dados ou padrões de alta confiança para sugerir uma entrada. Continue adicionando rodadas!")


st.markdown("---")

# --- Painel de Histórico e Estatísticas ---
st.header("📈 Painel de Resultados")

# Estatísticas
col_stats1, col_stats2 = st.columns(2)
with col_stats1:
    st.metric(label="💚 GREEN (Acertos)", value=st.session_state.green_count)
with col_stats2:
    st.metric(label="💔 RED (Erros)", value=st.session_state.red_count)

if st.session_state.green_count + st.session_state.red_count > 0:
    win_rate = (st.session_state.green_count / (st.session_state.green_count + st.session_state.red_count)) * 100
    st.metric(label="📊 Taxa de Acerto", value=f"{win_rate:.2f}%")

# Histórico Detalhado
st.subheader("📜 Histórico de Rodadas")
if st.session_state.historico:
    # Cria um DataFrame para exibir o histórico de forma mais organizada
    df_historico = pd.DataFrame(st.session_state.historico)
    st.dataframe(df_historico.set_index('Rodada'), use_container_width=True)
else:
    st.info("Nenhuma rodada adicionada ainda. Use o painel acima para começar.")

