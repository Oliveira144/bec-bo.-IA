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
    """Atualiza contadores para detecção de horários críticos/bons."""
    
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
    if 1 in [player_dado1, player_dado2, banker_dado1, banker_dado2]:
        st.session_state.count_dado_1_consecutivo += 1
    else:
        st.session_state.count_dado_1_consecutivo = 0


# --- Título do App ---
st.title("🎲 Bac Bo Predictor - Guia de Padrões")
st.markdown("---")

# --- Painel de Entrada de Dados ---
st.header("➕ Adicionar Nova Rodada ao Histórico")

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

add_round_button = st.button("➕ Adicionar Rodada e Analisar", use_container_width=True)

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

    st.success(f"Rodada {len(st.session_state.historico)} adicionada! Vencedor: **{winner}**")
    # A re-execução automática do Streamlit geralmente cuida da atualização da interface
    # após a modificação de st.session_state. Nenhuma chamada explícita a rerun é necessária aqui.

st.markdown("---")

# --- Análise de Momentos da Mesa ---
st.header("⏰ Análise de Momentos da Mesa")

horario_ruim = False
horario_bom = False

# Lógica para "Horários Ruins"
if len(st.session_state.historico) > 0: # Só analisa se houver histórico
    # Critério 1: Muitos empates no início (ex: 3 empates nas primeiras 10-15 rodadas)
    # Ajuste '15' conforme o período de análise desejado para "início".
    if st.session_state.empates_recentes >= 3 and len(st.session_state.historico) <= 15:
        st.warning("⚠️ **Cuidado:** Mesa com muitos empates no início. Sugerimos cautela.")
        horario_ruim = True
    
    # Critério 2: Dado '1' aparecendo consecutivamente em qualquer dado
    if st.session_state.count_dado_1_consecutivo >= 5: # 5 ou mais vezes
        st.warning(f"⚠️ **Atenção:** O dado '1' apareceu em **{st.session_state.count_dado_1_consecutivo}** rodadas seguidas. Potencial de manipulação ou momento ruim.")
        horario_ruim = True

    # Critério 3: Mesa travando ou delay (depende de feedback manual ou detecção mais avançada)
    # Você pode adicionar um botão para o usuário reportar isso manualmente:
    # if st.button("Mesa com Lag/Problemas", help="Clique se você notar atrasos ou travamentos no jogo."):
    #    st.error("🚨 Problemas na mesa detectados. Sugestões podem ser imprecisas.")
    #    horario_ruim = True

if not horario_ruim and len(st.session_state.historico) > 0:
    st.info("No momento, não há indicação de horários ruins baseados em padrões simples.")

# Lógica para "Horários Bons"
if len(st.session_state.historico) > 0: # Só analisa se houver histórico
    # Critério 1: Empates sumindo por mais de 15 rodadas
    if st.session_state.rodadas_desde_ultimo_empate > 15:
        st.success(f"✅ **Excelente:** Ausência de empates por **{st.session_state.rodadas_desde_ultimo_empate}** rodadas. Oportunidade de padrões claros.")
        horario_bom = True
    
    # Critério 2: Padrão Ouro se formando (seria detectado na função 'detectar_padroes' e retornado com alta confiança)
    _, _, confianca_sugestao, _ = analisar_sugestao(st.session_state.historico)
    if confianca_sugestao > 90: # Assumindo que padrões de alta confiança indicam "horário bom"
        st.success("✨ **Momento Promissor:** Padrão de alta confiança detectado!")
        horario_bom = True

if not horario_bom and not horario_ruim and len(st.session_state.historico) > 0:
    st.info("O momento atual da mesa é neutro. Continue acompanhando.")
elif len(st.session_state.historico) == 0:
    st.info("Adicione algumas rodadas para começar a análise dos momentos da mesa.")

st.markdown("---")

# --- Sugestão de Entrada Inteligente ---
st.header("🎯 Sugestão de Entrada Inteligente")

# Analisa e obtém a sugestão
nome_padrao_sugerido, entrada_sugerida, confianca, is_g1_active = analisar_sugestao(st.session_state.historico)

# Verifica se o app deve sugerir ou bloquear devido a horários ruins
if horario_ruim:
    st.warning("🚫 **Sugestões Bloqueadas:** O aplicativo está em um horário crítico (ruim). Não é recomendado fazer entradas.")
elif entrada_sugerida:
    st.session_state.last_suggested_entry = entrada_sugerida # Salva a última sugestão para o G1
    with st.expander("Ver Sugestão Detalhada", expanded=True):
        st.subheader(f"🎉 Entrada Sugerida!")
        
        # Usa Markdown com HTML para colorir o texto da sugestão
        if entrada_sugerida == 'Player':
            st.markdown(f"**Entrada Sugerida:** {'<span style="color:blue; font-size: 20px; font-weight: bold;">🔵 PLAYER</span>'}", unsafe_allow_html=True)
        elif entrada_sugerida == 'Banker':
            st.markdown(f"**Entrada Sugerida:** {'<span style="color:red; font-size: 20px; font-weight: bold;">🔴 BANKER</span>'}", unsafe_allow_html=True)
        else:
            st.write(f"**Entrada Sugerida:** {entrada_sugerida}") # Para Empate, caso você adicione sugestões de empate

        st.write(f"**Padrão Detectado:** {nome_padrao_sugerido}")
        st.write(f"**Confiança:** **{confianca:.0f}%**")
        
        if is_g1_active:
            st.warning("🚨 **Status:** Modo G1 Ativo! Mantenha a entrada anterior.")
        else:
            st.info("✅ **Status:** Normal. Sugestão baseada em novo padrão.")

        # Botões de Feedback da Sugestão
        st.write("---")
        st.write("Registre o resultado da sua aposta com base na sugestão:")
        col_feedback1, col_feedback2, col_feedback3 = st.columns(3)
        with col_feedback1:
            if st.button("✅ GREEN (Acertou)", use_container_width=True):
                st.session_state.green_count += 1
                st.session_state.g1_active = False # Desativa G1 se acertou
                st.session_state.last_suggested_entry = None # Reseta a sugestão G1
                st.success("🎉 Parabéns! GREEN!")
                # O Streamlit vai re-executar automaticamente após a mudança no session_state
        with col_feedback2:
            if st.button("❌ RED (Errou)", use_container_width=True):
                st.session_state.red_count += 1
                st.session_state.g1_active = True # Ativa G1 se errou
                st.error("😥 Que pena! RED. G1 ativado para a próxima entrada.")
                # O Streamlit vai re-executar automaticamente após a mudança no session_state
        with col_feedback3:
            if st.button("🟡 EMPATE (Na Aposta)", use_container_width=True): # O empate na aposta não é RED nem GREEN
                st.info("Rodada foi um empate. Contadores de GREEN/RED e G1 não alterados para esta aposta.")
                # O Streamlit vai re-executar automaticamente após a mudança no session_state
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
    # O Streamlit vai re-executar automaticamente após a mudança no session_state

