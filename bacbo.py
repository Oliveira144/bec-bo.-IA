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

    CORREÇÃO: Adicionado tratamento para histórico vazio/poucos elementos
    e correção da chave 'Vencedor'.
    """
    # Se o histórico estiver vazio, não há padrões para detectar
    if not historico_completo:
        return "Nenhum Padrão Detectado", None, 0 # Nome do padrão, Sugestão (Player/Banker), Confiança

    # Sempre podemos pegar o último resultado se o histórico não estiver vazio
    ultimo_resultado = historico_completo[-1]['Vencedor'] # USANDO 'Vencedor' com 'V' maiúsculo

    # Padrão 1: Alternância Simples (Player/Banker intercalado)
    if len(historico_completo) >= 2:
        segundo_ultimo_resultado = historico_completo[-2]['Vencedor'] # USANDO 'Vencedor'
        if ultimo_resultado != 'Empate' and segundo_ultimo_resultado != 'Empate' and \
           ultimo_resultado != segundo_ultimo_resultado:
            sugestao = 'Banker' if ultimo_resultado == 'Player' else 'Player'
            return "1. Alternância Simples", sugestao, 70 # 70% de confiança para este exemplo

    # Padrão 2: Sequência de 2
    if len(historico_completo) >= 2 and ultimo_resultado != 'Empate':
        if historico_completo[-1]['Vencedor'] == historico_completo[-2]['Vencedor']: # USANDO 'Vencedor'
            sugestao = ultimo_resultado
            return "2. Sequência de 2", sugestao, 75 # 75% de confiança
    
    # Padrão 3: Sequência de 3
    if len(historico_completo) >= 3 and ultimo_resultado != 'Empate':
        if (historico_completo[-1]['Vencedor'] == historico_completo[-2]['Vencedor'] and
            historico_completo[-2]['Vencedor'] == historico_completo[-3]['Vencedor']):
            sugestao = 'Banker' if ultimo_resultado == 'Player' else 'Player' # Reversão
            return "3. Sequência de 3", sugestao, 80 # 80% de confiança

    # Padrão Ouro (placeholder - você implementaria a lógica complexa aqui)
    # Por exemplo, se uma sequência específica de 5 rodadas se repetisse
    # if detectar_padrao_ouro_real(historico_completo): # Esta função seria sua lógica avançada
    #    return "🔒 Padrão Ouro", "Player", 95 # Altíssima confiança

    # Se nenhum padrão forte for detectado com alta confiança
    return "Nenhum Padrão Forte", None, 0

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
    nome_padrao, sugestao, confiança_base = detectar_padroes(historico)
    
    # Apenas sugere se a confiança for alta o suficiente (definido no return de detectar_padroes)
    if sugestao and confiança_base >= 70: # Ajuste o limite de confiança conforme seus padrões
        return nome_padrao, sugestao, confiança_base, False
    
    return "Aguardando Padrão Forte", None, 0, False # Não há sugestão com alta confiança

def atualizar_contadores_horarios(player_dado1, player_dado2, banker_dado1, banker_dado2, winner):
    """Atualiza contadores para detecção de horários críticos."""
    # Contar rodadas desde o último empate
    if winner == 'Empate':
        st.session_state.rodadas_desde_ultimo_empate = 0
        st.session_state.empates_recentes += 1 # Incrementa para controle de empates próximos
    else:
        st.session_state.rodadas_desde_ultimo_empate += 1
        # Se não é empate, reseta o contador de empates recentes, a menos que haja uma lógica para "3 empates em 10 rodadas"
        # que precise de um histórico mais longo
        st.session_state.empates_recentes = 0 # Reinicia se a sequência de empates foi quebrada

    # Contar dado '1' consecutivo (em qualquer dado)
    if 1 in [player_dado1, player_dado2, banker_dado1, banker_dado2]:
        st.session_state.count_dado_1_consecutivo += 1
    else:
        st.session_state.count_dado_1_consecutivo = 0


# --- Título do App ---
st.title("🎲 Bac Bo Predictor - Guia de Padrões")
st.markdown("---")

# --- Painel de Entrada de Dados ---
st.header("Adicionar Nova Rodada ao Histórico")

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.subheader("🔵 Player")
    player_dado1 = st.number_input("Dado 1 do Player", min_value=1, max_value=6, value=1, key="pd1")
    player_dado2 = st.number_input("Dado 2 do Player", min_value=1, max_value=6, value=1, key="pd2")

with col_input2:
    st.subheader("🔴 Banker")
    banker_dado1 = st.number_input("Dado 1 do Banker", min_value=1, max_value=6, value=1, key="bd1")
    banker_dado2 = st.number_input("Dado 2 do Banker", min_value=1, max_value=6, value=1, key="bd2")

add_round_button = st.button("➕ Adicionar Rodada e Analisar", use_container_width=True)

if add_round_button:
    player_sum = player_dado1 + player_dado2
    banker_sum = banker_dado1 + banker_dado2
    winner = get_winner(player_sum, banker_sum)

    # Armazena os dados da rodada no histórico
    # Certifique-se de que o nome da chave para o vencedor é 'Vencedor' (com V maiúsculo)
    st.session_state.historico.append({
        "Rodada": len(st.session_state.historico) + 1,
        "Player Dados": f"[{player_dado1},{player_dado2}]",
        "Player Soma": player_sum,
        "Banker Dados": f"[{banker_dado1},{banker_dado2}]",
        "Banker Soma": banker_sum,
        "Vencedor": winner, # Esta é a chave correta!
        "Timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    
    # Atualiza contadores de horários críticos
    atualizar_contadores_horarios(player_dado1, player_dado2, banker_dado1, banker_dado2, winner)

    # Exibe uma mensagem de sucesso
    st.success(f"Rodada {len(st.session_state.historico)} adicionada! Vencedor: {winner}")
    # Força uma re-execução para atualizar a sugestão imediatamente
    st.experimental_rerun()

st.markdown("---")

# --- Análise de Horários Críticos ---
st.header("⏰ Análise de Horários Críticos")

# Lógica para "Horários Ruins"
horario_ruim = False
# Critério 1: 3 empates em menos de 10 rodadas (necessita de um controle mais sofisticado, este é um placeholder)
if st.session_state.empates_recentes >= 3 and len(st.session_state.historico) <= 10 and len(st.session_state.historico) > 0:
    st.warning("⚠️ **Cuidado:** Novo baralho com muitos empates iniciais. Sugerimos cautela.")
    horario_ruim = True
# Critério 2: Dado '1' em 5 rodadas seguidas
if st.session_state.count_dado_1_consecutivo >= 5:
    st.warning("⚠️ **Atenção:** Dado '1' apareceu em 5 rodadas seguidas. Potencial de manipulação ou momento ruim.")
    horario_ruim = True
# Critério 3: Mesa travando ou delay (depende de feedback manual do usuário ou detecção avançada)
# Você pode adicionar um botão para o usuário reportar isso:
# if st.button("Mesa com Lag/Problemas"):
#    st.error("🚨 Problemas na mesa detectados. Sugestões desativadas.")
#    horario_ruim = True

if not horario_ruim and len(st.session_state.historico) > 0:
    st.info("No momento, não há indicação de horários ruins baseados em padrões simples. Continue monitorando.")

# Lógica para "Horários Bons"
horario_bom = False
# Critério 1: Vitórias seguidas do mesmo lado com margens 1 ou 2 (requer lógica de margem)
# Placeholder para este padrão
# if st.session_state.sequencia_vitorias_margem_1_ou_2 >= 3:
#    st.success("✅ Bom momento: Sequência de vitórias com margem 1 ou 2. Mantenha o foco!")
#    horario_bom = True
# Critério 2: Empates sumindo por mais de 15 rodadas
if st.session_state.rodadas_desde_ultimo_empate > 15 and len(st.session_state.historico) > 0:
    st.success("✅ **Excelente:** Ausência prolongada de empates. Oportunidade de padrões claros.")
    horario_bom = True
# Critério 3: Padrão Ouro se formando (detectado pela função analisar_sugestao)

if not horario_bom and len(st.session_state.historico) > 0:
    if not horario_ruim: # Não mostrar mensagem redundante se já for ruim
        st.info("No momento, não há indicação de horários especialmente bons.")


st.markdown("---")

# --- Sugestão de Entrada Inteligente ---
st.header("🎯 Sugestão de Entrada")

# Analisa e obtém a sugestão
nome_padrao_sugerido, entrada_sugerida, confianca, is_g1_active = analisar_sugestao(st.session_state.historico)

# Verifica se o app deve sugerir ou bloquear devido a horários ruins
if horario_ruim:
    st.warning("🚫 **Sugestões Bloqueadas:** O aplicativo está em um horário crítico (ruim). Não é recomendado fazer entradas.")
elif entrada_sugerida:
    st.session_state.last_suggested_entry = entrada_sugerida # Salva a última sugestão para o G1
    with st.expander("Ver Sugestão Detalhada", expanded=True): # Começa expandido para visibilidade
        st.subheader(f"🎉 Entrada Sugerida!")
        st.write(f"**Padrão Detectado:** {nome_padrao_sugerido}")
        st.markdown(f"**Entrada Sugerida:** {'<span style="color:blue; font-size: 20px;">🔵 PLAYER</span>' if entrada_sugerida == 'Player' else '<span style="color:red; font-size: 20px;">🔴 BANKER</span>'}", unsafe_allow_html=True)
        st.write(f"**Confiança:** **{confianca:.0f}%**")
        
        if is_g1_active:
            st.warning("🚨 **Status:** Modo G1 Ativo! Mantenha a entrada anterior.")
        else:
            st.info("✅ **Status:** Normal")

        # Botões de Feedback
        col_feedback1, col_feedback2, col_feedback3 = st.columns(3)
        with col_feedback1:
            if st.button("✅ GREEN (Acertou)", use_container_width=True):
                st.session_state.green_count += 1
                st.session_state.g1_active = False # Desativa G1 se acertou
                st.session_state.last_suggested_entry = None # Reseta a sugestão G1
                st.success("🎉 Parabéns! GREEN!")
                st.experimental_rerun() # Re-executa para atualizar os contadores
        with col_feedback2:
            if st.button("❌ RED (Errou)", use_container_width=True):
                st.session_state.red_count += 1
                st.session_state.g1_active = True # Ativa G1 se errou
                st.error("😥 Que pena! RED. G1 ativado para a próxima entrada.")
                st.experimental_rerun() # Re-executa para atualizar os contadores
        with col_feedback3:
            if st.button("🟡 EMPATE", use_container_width=True):
                st.info("Rodada foi um empate. Contadores de GREEN/RED e G1 não alterados.")
                st.experimental_rerun() # Re-executa para atualizar a interface
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
    # Cria um DataFrame para exibir o histórico de forma mais organizada
    # Garante que o histórico seja exibido em ordem reversa (mais recente primeiro)
    df_historico = pd.DataFrame(st.session_state.historico[::-1])
    st.dataframe(df_historico.set_index('Rodada'), use_container_width=True)
else:
    st.info("Nenhuma rodada adicionada ainda. Use o painel acima para começar.")

# Botão para limpar o histórico (útil para testes ou recomeçar)
st.markdown("---")
if st.button("🔄 Limpar Histórico e Resetar Contadores"):
    st.session_state.historico = []
    st.session_state.green_count = 0
    st.session_state.red_count = 0
    st.session_state.g1_active = False
    st.session_state.last_suggested_entry = None
    st.session_state.rodadas_desde_ultimo_empate = 0
    st.session_state.empates_recentes = 0
    st.session_state.count_dado_1_consecutivo = 0
    st.experimental_rerun() # Re-executa para limpar a tela
