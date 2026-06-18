import streamlit as st
import pandas as pd
import numpy as np
import random
import os
import json
import pickle
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ==========================================
# CONFIGURAÇÕES GLOBAIS E CONSTANTES (PARTE 1)
# ==========================================
CHAVE_ADMINISTRADOR = "ctg123"  # Defina sua senha master aqui
ARQUIVO_BACKUP = "estado_torneio.pkl"
ARQUIVO_GALERIA = "galeria_campeoes.json"

st.set_page_config(page_title="Gestor de Truco Premium", layout="wide", initial_sidebar_state="expanded")

# Injeção de CSS Customizado para Identidade Visual de Ultra Contraste
st.markdown("""
<style>
    /* Configuração Geral do App e Textos Básicos */
    .stApp { background-color: #04120a; color: #ffffff; }
    h1, h2, h3, h4, h5, h6 { color: #ffb703 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 900; }
    
    /* ------------------------------------------------------------- */
    /* CORREÇÃO DO PAINEL DO DIRETOR (SIDEBAR) E SEUS BOTÕES         */
    /* ------------------------------------------------------------- */
    /* Transforma a barra lateral cinza no visual escuro do torneio */
    section[data-testid="stSidebar"] {
        background-color: #030d07 !important;
        border-right: 2px solid #ffb703 !important;
    }
    
    /* Garante contraste para todos os textos e labels da barra lateral */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Destaca títulos dentro da barra lateral em Amarelo */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffb703 !important;
    }

    /* CORREÇÃO DO BOTÃO "AUTENTICAR" (E outros da Sidebar): Texto Preto com Fundo Amarelo */
    section[data-testid="stSidebar"] button {
        background-color: #ffb703 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 1px solid #ffb703 !important;
        transition: background-color 0.3s ease;
    }

    /* Efeito ao passar o mouse por cima do botão na sidebar */
    section[data-testid="stSidebar"] button:hover {
        background-color: #dda15e !important;
        color: #000000 !important;
        border-color: #dda15e !important;
    }
    
    /* ------------------------------------------------------------- */
    /* ELEMENTOS DE ULTRA CONTRASTE DA ARENA CORRIGIDOS              */
    /* ------------------------------------------------------------- */
    
    /* Força os títulos "Nome do Evento" e "Nome do Competidor" a ficarem em Branco Puro */
    div[data-testid="stWidgetLabel"] p, 
    label[data-testid="stWidgetLabel"] p,
    .st-emotion-cache-q8s8vi p,
    .st-emotion-cache-q8s8vi {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }

    /* Força o texto das abas (Tabs) desativadas/secundárias a ficarem visíveis em Branco */
    button[data-testid="stMarkdownContainer"] p,
    .stTabs button p,
    .st-emotion-cache-6t18gh p {
        color: #ffffff !important;
    }
    
    /* Mantém e destaca a Aba Ativa (Selecionada) em Amarelo Ouro */
    button[aria-selected="true"] p,
    button[aria-selected="true"] div[data-testid="stMarkdownContainer"] p,
    .stTabs button[aria-selected="true"] p {
        color: #ffb703 !important;
        font-weight: bold !important;
    }

    /* Garante que as opções do botão de rádio (Modos de Tela) fiquem em Branco */
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Caixa do Cronômetro Gigante */
    .cronometro-box-gigante {
        background: linear-gradient(135deg, #ff3232, #7a0000);
        border: 4px solid #ffb703;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
    }
    .cronometro-tempo { font-size: 4.5rem !important; font-weight: 900 !important; color: #ffffff !important; font-family: monospace; }
    
    /* Componentes de Mesas e Métricas */
    .titulo-mesa-destaque { background-color: #0d301b; color: #ffb703; padding: 10px; border-radius: 8px; font-weight: bold; text-align: center; margin-top: 15px; border: 1px solid #ffb703; }
    .metric-panel { background: #0b2b18; border: 2px solid #69db7c; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
    .metric-val { font-size: 2.2rem; font-weight: 900; color: #ffb703; }
    .metric-lbl { font-size: 0.9rem; color: #69db7c; font-weight: bold; text-transform: uppercase; }
    .chapeu-container-novo { background: linear-gradient(135deg, #1b1b1b, #0a0a0a); border: 3px dashed #ffb703; border-radius: 15px; padding: 20px; text-align: center; margin: 15px 0; }
    .titulo-passo-admin { color: #ffb703 !important; font-size: 1rem !important; font-weight: bold; margin-top: 10px; margin-bottom: 5px; }
    
    /* Caixa de Formulários de Cadastro e Lançamento */
    div[data-testid="stForm"] { background-color: #0b2b18 !important; border: 2px solid #ffb703 !important; border-radius: 12px !important; }
    
   /* Estilização dos Botões da Tabela de Inscritos */
    .botao-editar button { background-color: #228be6 !important; color: white !important; border-radius: 6px !important; width: 100%; }
    .botao-excluir button { background-color: #fa5252 !important; color: white !important; border-radius: 6px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# Inicialização do Estado Interno (Session State) - ESTRUTURA ATUALIZADA
if "jogadores" not in st.session_state: st.session_state["jogadores"] = []  # Agora guardará {"id": X, "nome": "X", "entidade": "X"}
if "torneio_iniciado" not in st.session_state: st.session_state["torneio_iniciado"] = False
if "rodada_atual" not in st.session_state: st.session_state["rodada_atual"] = 1
if "confrontos" not in st.session_state: st.session_state["confrontos"] = []
if "placares_rodada_atual" not in st.session_state: st.session_state["placares_rodada_atual"] = {}
if "historico_rodadas" not in st.session_state: st.session_state["historico_rodadas"] = {}
if "classificacao" not in st.session_state: st.session_state["classificacao"] = None
if "jogadores_no_chapeu" not in st.session_state: st.session_state["jogadores_no_chapeu"] = set()
if "admin_logado" not in st.session_state: st.session_state["admin_logado"] = False
if "cronometro_ativo" not in st.session_state: st.session_state["cronometro_ativo"] = False
if "hora_inicio_rodada" not in st.session_state: st.session_state["hora_inicio_rodada"] = None
if "em_matamata" not in st.session_state: st.session_state["em_matamata"] = False
if "fase_matamata" not in st.session_state: st.session_state["fase_matamata"] = ""
if "confrontos_mm" not in st.session_state: st.session_state["confrontos_mm"] = []
if "campeao" not in st.session_state: st.session_state["campeao"] = None
if "vice_campeao" not in st.session_state: st.session_state["vice_campeao"] = None
if "terceiro_lugar" not in st.session_state: st.session_state["terceiro_lugar"] = None
if "quarto_lugar" not in st.session_state: st.session_state["quarto_lugar"] = None
if "jogador_sendo_editado" not in st.session_state: st.session_state["jogador_sendo_editado"] = None

def salvar_estado_no_disco():
    try:
        dados = {k: v for k, v in st.session_state.items() if k != "jogador_sendo_editado"}
        with open(ARQUIVO_BACKUP, "wb") as f: pickle.dump(dados, f)
    except Exception: pass

def carregar_estado_do_disco():
    if os.path.exists(ARQUIVO_BACKUP):
        try:
            with open(ARQUIVO_BACKUP, "rb") as f:
                dados = pickle.load(f)
                for k, v in dados.items(): 
                    st.session_state[k] = v
                
                # CONVERSOR DE SEGURANÇA: Se houver dados antigos em formato de texto, converte para dicionário
                if "jogadores" in st.session_state and st.session_state["jogadores"]:
                    lista_atualizada = []
                    for i, jog in enumerate(st.session_state["jogadores"]):
                        if isinstance(jog, str):
                            lista_atualizada.append({"id": i + 1, "nome": jog.upper(), "entidade": "AVULSO"})
                        else:
                            lista_atualizada.append(jog)
                    st.session_state["jogadores"] = lista_atualizada
        except Exception: pass

def limpar_placares_memoria():
    st.session_state["placares_rodada_atual"] = {}
    st.session_state["semente_reset"] = st.session_state.get("semente_reset", 1) + 1

carregar_estado_do_disco()

# ==========================================
# BOTÃO TEMPORÁRIO PARA LIMPAR BACKUP ANTIGO
# ==========================================
with st.sidebar:
    st.write("---")
    if st.button("🚨 ATUALIZAR BANCO DE DADOS (RESET)", use_container_width=True):
        # Limpa o estado atual da memória
        st.session_state["jogadores"] = []
        st.session_state["torneio_iniciado"] = False
        st.session_state["classificacao"] = None
        st.session_state["historico_rodadas"] = {}
        st.session_state["placares_rodada_atual"] = {}
        
        # Apaga fisicamente o arquivo antigo se ele existir no servidor
        if os.path.exists(ARQUIVO_BACKUP):
            try:
                os.remove(ARQUIVO_BACKUP)
            except Exception:
                pass
                
        st.success("Banco de dados limpo com sucesso! Agora a nova estrutura está ativa.")
        st.rerun()

# ==========================================
# RECALCULADOR MATRIZ E CHAVES (PARTE 2)
# ==========================================
def reconstruir_classificacao_global():
    # Extrai a lista de nomes únicos para montar a tabela de classificação
    nomes_jogadores = [j["nome"] for j in st.session_state["jogadores"]]
    
    st.session_state["classificacao"] = pd.DataFrame({
        'Jogador': nomes_jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 
        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
    }).set_index('Jogador')
    
    for r_num, mesas in st.session_state["historico_rodadas"].items():
        for m_id, dados in mesas.items():
            if dados.get("is_chapeu", False):
                j1_nome = dados["j1"]["nome"] if isinstance(dados["j1"], dict) else dados["j1"]
                if j1_nome in st.session_state["classificacao"].index:
                    st.session_state["classificacao"].loc[j1_nome, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
            else:
                j1, j2 = dados["j1"], dados["j2"]
                j1_nome = j1["nome"] if isinstance(j1, dict) else j1
                j2_nome = j2["nome"] if isinstance(j2, dict) else j2
                
                s1, s2, t1, t2, f1, f2 = dados["s1"], dados["s2"], dados["t1"], dados["t2"], dados["f1"], dados["f2"]
                s1_c = 3 if (s1 == 2 and s2 == 0) else s1
                s2_c = 3 if (s2 == 2 and s1 == 0) else s2
                v1, v2 = (1, 0) if s1 > s2 else (0, 1)
                
                if j1_nome in st.session_state["classificacao"].index:
                    st.session_state["classificacao"].loc[j1_nome, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v1, s1_c, t1, t2, f1]
                if j2_nome in st.session_state["classificacao"].index:
                    st.session_state["classificacao"].loc[j2_nome, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v2, s2_c, t2, t1, f2]
                
    st.session_state["classificacao"]['Saldo_Tentos'] = st.session_state["classificacao"]['Tentos_Pro'] - st.session_state["classificacao"]['Tentos_Contra']
    salvar_estado_no_disco()

def gerar_rodada_web():
    limpar_placares_memoria()
    if st.session_state["rodada_atual"] == 1:
        lista_rodada = list(st.session_state["jogadores"])
        random.shuffle(lista_rodada)
    else:
        df_ord = st.session_state["classificacao"].sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
        # Reassocia os nomes ordenados aos dicionários completos correspondentes
        mapa_jogadores = {j["nome"]: j for j in st.session_state["jogadores"]}
        lista_rodada = [mapa_jogadores[nome] for nome in df_ord.index if nome in mapa_jogadores]

    st.session_state["confrontos"] = []
    
    # Tratamento do Chapéu com a nova estrutura de dicionários
    if len(lista_rodada) % 2 != 0:
        nomes_no_chapeu = {j["nome"] if isinstance(j, dict) else j for j in st.session_state["jogadores_no_chapeu"]}
        cand = [j for j in lista_rodada if (j["nome"] if isinstance(j, dict) else j) not in nomes_no_chapeu]
        chapeu = random.choice(cand if cand else lista_rodada)
        lista_rodada.remove(chapeu)
        st.session_state["jogadores_no_chapeu"].add(chapeu["nome"] if isinstance(chapeu, dict) else chapeu)
        st.session_state["confrontos"].append((chapeu, "CHAPÉU (Folga)"))

    contador_mesa = 1
    for i in range(0, len(lista_rodada), 2):
        st.session_state["confrontos"].append((lista_rodada[i], lista_rodada[i+1]))
        st.session_state["placares_rodada_atual"][str(contador_mesa)] = [0, 0, 0, 0, 0, 0, False]
        contador_mesa += 1
    
    st.session_state["hora_inicio_rodada"] = None
    st.session_state["cronometro_ativo"] = False
    salvar_estado_no_disco()

def iniciar_fase_matamata(lista_jogadores, nome_fase):
    limpar_placares_memoria()
    st.session_state["em_matamata"] = True
    st.session_state["fase_matamata"] = nome_fase
    st.session_state["confrontos_mm"] = []
    
    if nome_fase == "FINAL E TERCEIRO": return 

    n = len(lista_jogadores)
    for i in range(n // 2):
        id_m = str(i+1)
        st.session_state["confrontos_mm"].append({"id_original": id_m, "tipo": "normal", "j1": lista_jogadores[i], "j2": lista_jogadores[n-1-i]})
        st.session_state["placares_rodada_atual"][id_m] = [0, 0, 0, 0, 0, 0, False]
    
    st.session_state["hora_inicio_rodada"] = None
    st.session_state["cronometro_ativo"] = False
    salvar_estado_no_disco()

def disparar_atualizacao_placar(m_str, j1, j2):
    sem = st.session_state.get("semente_reset", 1)
    s1 = st.session_state.get(f"dir_s1_{m_str}_r{sem}", 0)
    s2 = st.session_state.get(f"dir_s2_{m_str}_r{sem}", 0)
    p_antigo = st.session_state["placares_rodada_atual"].get(m_str, [0, 0, 0, 0, 0, 0, False])
    
    if (s1 == 2 and s2 == 0):
        t1, t2 = 72, min(st.session_state.get(f"dir_t2_{m_str}_r{sem}_2x0j1", p_antigo[3]), 46)
    elif (s2 == 2 and s1 == 0):
        t2, t1 = 72, min(st.session_state.get(f"dir_t1_{m_str}_r{sem}_2x0j2", p_antigo[2]), 46)
    else:
        t1_raw = st.session_state.get(f"dir_t1_{m_str}_r{sem}_2x1", "")
        t2_raw = st.session_state.get(f"dir_t2_{m_str}_r{sem}_2x1", "")
        try: t1 = int(t1_raw) if str(t1_raw).strip() != "" else 0
        except ValueError: t1 = 0
        try: t2 = int(t2_raw) if str(t2_raw).strip() != "" else 0
        except ValueError: t2 = 0

    f1 = st.session_state.get(f"dir_f1_{m_str}_r{sem}", p_antigo[4])
    f2 = st.session_state.get(f"dir_f2_{m_str}_r{sem}", p_antigo[5])
    
    st.session_state["placares_rodada_atual"][m_str] = [s1, s2, t1, t2, f1, f2, True]
    salvar_estado_no_disco()

def salvar_mudanca_retroativa(r_alvo, m_id, j1, j2):
    st.session_state["historico_rodadas"][r_alvo][m_id]["s1"] = st.session_state.get(f"ret_s1_{r_alvo}_{m_id}", 0)
    st.session_state["historico_rodadas"][r_alvo][m_id]["t1"] = st.session_state.get(f"ret_t1_{r_alvo}_{m_id}", 0)
    st.session_state["historico_rodadas"][r_alvo][m_id]["f1"] = st.session_state.get(f"ret_f1_{r_alvo}_{m_id}", 0)
    st.session_state["historico_rodadas"][r_alvo][m_id]["s2"] = st.session_state.get(f"ret_s2_{r_alvo}_{m_id}", 0)
    st.session_state["historico_rodadas"][r_alvo][m_id]["t2"] = st.session_state.get(f"ret_t2_{r_alvo}_{m_id}", 0)
    st.session_state["historico_rodadas"][r_alvo][m_id]["f2"] = st.session_state.get(f"ret_f2_{r_alvo}_{m_id}", 0)
    reconstruir_classificacao_global()

def desenhar_mesa_planta_baixa(j1, j2, mesa_num, s1, t1, f1, s2, t2, f2, tipo_jogo="normal"):
    # Extrai o nome e entidade de forma segura se forem dicionários
    j1_nome = j1["nome"] if isinstance(j1, dict) else str(j1)
    j1_entidade = j1["entidade"] if isinstance(j1, dict) else ""
    
    j2_nome = j2["nome"] if isinstance(j2, dict) else str(j2)
    j2_entidade = j2["entidade"] if isinstance(j2, dict) else ""

    animacao_css = ""
    if tipo_jogo == "final":
        borda_cor = "#ffb703" 
        bg_topo = "linear-gradient(135deg, #ffb703, #b8860b)"
        texto_topo = "#000000"
        tag_titulo = "👑 GRANDE FINAL ABSOLUTA 👑"
        card_height = "440px"
        fonte_jogadores = "1.5rem"
        animacao_css = "animation: pulsarFinal 2s infinite ease-in-out;"
    elif tipo_jogo == "3place":
        borda_cor = "#cd7f32" 
        bg_topo = "linear-gradient(135deg, #cd7f32, #8b5a2b)"
        texto_topo = "#ffffff"
        tag_titulo = "🥉 DISPUTA DE 3º LUGAR 🥉"
        card_height = "420px"
        fonte_jogadores = "1.3rem"
    elif (s1 == 2 or s2 == 2):
        borda_cor = "#2b8a3e" 
        bg_topo = "#124027"
        texto_topo = "#ffffff"
        tag_titulo = f"🎰 MESA {mesa_num} (CONCLUÍDO)"
        card_height = "370px"
        fonte_jogadores = "1.1rem"
    else:
        borda_cor = "#e67e22" 
        bg_topo = "#2c1e11"
        texto_topo = "#ffffff"
        tag_titulo = f"🎰 MESA {mesa_num}"
        card_height = "370px"
        fonte_jogadores = "1.1rem"

    # Monta as strings de entidade estilizadas se elas existirem
    ent1_html = f'<div style="font-size: 0.8rem; color: #ffb703; font-weight: bold; margin-top: 2px;">🔰 {j1_entidade}</div>' if j1_entidade else ""
    ent2_html = f'<div style="font-size: 0.8rem; color: #ffb703; font-weight: bold; margin-top: 2px;">🔰 {j2_entidade}</div>' if j2_entidade else ""

    html_mesa = f"""
    <style>
    @keyframes pulsarFinal {{
        0% {{ box-shadow: 0px 0px 15px rgba(255,183,3,0.5); border-color: #ffb703; }}
        50% {{ box-shadow: 0px 0px 35px rgba(255,183,3,1); border-color: #ffffff; }}
        100% {{ box-shadow: 0px 0px 15px rgba(255,183,3,0.5); border-color: #ffb703; }}
    }}
    </style>
    <div style="background: linear-gradient(135deg, #0f2d1b, #06170d); border: 4px solid {borda_cor}; border-radius: 20px; padding: 15px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; position: relative; box-shadow: 0px 8px 16px rgba(0,0,0,0.5); height: {card_height}; box-sizing: border-box; color: #ffffff; font-family: system-ui, -apple-system, sans-serif; margin-bottom: 5px; {animacao_css}">
        
        <div style="text-align: center; width: 100%;">
            <div style="font-size: 0.75rem; color: #69db7c; font-weight: bold; text-transform: uppercase;">🧔 Jogador 1</div>
            <div style="background: #04120a; color: #ffffff; padding: 6px 15px; border-radius: 8px; font-size: {fonte_jogadores}; font-weight: 900; display: inline-block; border: 1px solid #ffb703; max-width: 85%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{j1_nome}</div>
            {ent1_html}
        </div>
        
        <div style="background-color: #04120a; border: 2px solid {borda_cor}; border-radius: 12px; padding: 10px; width: 90%; text-align: center; box-shadow: inset 0 2px 5px rgba(0,0,0,0.6);">
            <div style="background: {bg_topo}; color: {texto_topo}; font-size: 0.9rem; font-weight: 900; padding: 5px 0; border-radius: 6px; letter-spacing: 1.5px; text-transform: uppercase;">{tag_titulo}</div>
            <div style="display: flex; justify-content: space-around; align-items: center; font-size: 2.2rem; font-weight: 900; margin-top: 8px;">
                <div style="color: #ffb703;">{int(s1)}<span style="font-size:1.2rem; color:#69db7c;">s</span> {int(t1)}<span style="font-size:1.2rem; color:#69db7c;">t</span></div>
                <div style="font-size: 1rem; color: #69db7c; font-weight: bold;">X</div>
                <div style="color: #ffffff;">{int(s2)}<span style="font-size:1.2rem; color:#69db7c;">s</span> {int(t2)}<span style="font-size:1.2rem; color:#69db7c;">t</span></div>
            </div>
            <div style="margin-top: 6px; font-size: 0.95rem; color: #ff69b4; font-weight: bold;">
                🌸 {int(f1)} fl. <span style="color:#ffb703; margin:0 5px;">|</span> 🌸 {int(f2)} fl.
            </div>
        </div>
        
        <div style="text-align: center; width: 100%;">
            <div style="background: #04120a; color: #ffffff; padding: 6px 15px; border-radius: 8px; font-size: {fonte_jogadores}; font-weight: 900; display: inline-block; border: 1px solid #ffb703; max-width: 85%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{j2_nome}</div>
            {ent2_html}
            <div style="font-size: 0.75rem; color: #69db7c; font-weight: bold; text-transform: uppercase; margin-top: 2px;">🧔 Jogador 2</div>
        </div>
    </div>
    """
    components.html(html_mesa, height=int(card_height.replace("px","")) + 15, scrolling=False)

def renderizar_formulario_mesa_admin(m, j1, j2, sem_id):
    p = st.session_state["placares_rodada_atual"].get(m, [0,0,0,0,0,0,False])
    s1, s2, t1, t2, f1, f2 = p[0], p[1], p[2], p[3], p[4], p[5]
    
    # Resolve nomes amigáveis para as labels do formulário
    j1_label = j1["nome"] if isinstance(j1, dict) else str(j1)
    j2_label = j2["nome"] if isinstance(j2, dict) else str(j2)
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown(f"<h4 class='titulo-passo-admin'>• SETS (Passo 1)</h4>", unsafe_allow_html=True)
        s1_in = st.number_input(f"Sets - {j1_label}", 0, 2, int(s1), key=f"dir_s1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
        s2_in = st.number_input(f"Sets - {j2_label}", 0, 2, int(s2), key=f"dir_s2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))

    jogo_encerrado = (s1_in == 2 or s2_in == 2)
    
    with c2:
        if not jogo_encerrado:
            st.warning("Aguardando Sets...")
        else:
            st.markdown(f"<h4 class='titulo-passo-admin'>• TENTOS (Passo 2)</h4>", unsafe_allow_html=True)
            if s1_in == 2 and s2_in == 0:
                st.number_input(f"Tentos - {j2_label} (Máx: 46)", 0, 46, min(int(t2), 46), key=f"dir_t2_{m}_r{sem_id}_2x0j1", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            elif s2_in == 2 and s1_in == 0:
                st.number_input(f"Tentos - {j1_label} (Máx: 46)", 0, 46, min(int(t1), 46), key=f"dir_t1_{m}_r{sem_id}_2x0j2", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            else:
                t1_val_str = "" if (t1 == 72 or t1 == 0) else str(t1)
                t2_val_str = "" if (t2 == 72 or t2 == 0) else str(t2)
                st.text_input(f"Tentos - {j1_label}", value=t1_val_str, key=f"dir_t1_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Tentos...")
                st.text_input(f"Tentos - {j2_label}", value=t2_val_str, key=f"dir_t2_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Tentos...")
            
            st.markdown(f"<h4 class='titulo-passo-admin'>• FLORES (Passo 3)</h4>", unsafe_allow_html=True)
            st.number_input(f"Flores - {j1_label}", 0, 20, int(f1), key=f"dir_f1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            st.number_input(f"Flores - {j2_label}", 0, 20, int(f2), key=f"dir_f2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))


# ==========================================
# SIDEBAR E CONTEXTO DE VISUALIZAÇÃO (PARTE 3)
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Painel do Diretor")
    if not st.session_state["admin_logado"]:
        senha = st.text_input("Chave Master:", type="password")
        if st.button("🔓 Autenticar"):
            if senha == CHAVE_ADMINISTRADOR:
                st.session_state["admin_logado"] = True
                st.rerun()
            else: st.sidebar.error("Incorreta!")
    else:
        st.success("⚡ Modo Diretor Ativo")
        if st.button("🔒 Sair do Modo Adm"):
            st.session_state["admin_logado"] = False
            st.rerun()
            
    is_admin = st.session_state["admin_logado"]
    st.markdown("---")
    
    if is_admin:
        if st.button("⏱️ Iniciar Cronômetro (45m)"):
            st.session_state["hora_inicio_rodada"] = datetime.now()
            st.session_state["cronometro_ativo"] = True
            salvar_estado_no_disco(); st.rerun()
        if st.button("⏹️ Pausar Cronômetro"):
            st.session_state["cronometro_ativo"] = False
            salvar_estado_no_disco(); st.rerun()
        st.markdown("---")
        if st.button("🚨 RESET TOTAL DO EVENTO"):
            if os.path.exists(ARQUIVO_BACKUP): os.remove(ARQUIVO_BACKUP)
            st.session_state.clear(); st.rerun()

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center; color:#ffb703; font-weight:900; margin-top:0;'>🃏 {st.session_state.get('nome_torneio', 'Torneio de Truco')}</h1>", unsafe_allow_html=True)

modo_exibicao = st.radio("Selecione o Modo de Visualização da Tela:", ["Arena de Gerenciamento", "🖥️ MODO TELÃO DE PROJETOR (Automático)"], horizontal=True)

if modo_exibicao == "🖥️ MODO TELÃO DE PROJETOR (Automático)":
    st.markdown("<h2 style='text-align:center; color:#ffb703; margin-bottom:20px;'>📺 QUADRO OFICIAL DE CONFRONTOS</h2>", unsafe_allow_html=True)
    
    # 1. Cronômetro Gigante Centralizado
    if st.session_state["cronometro_ativo"] and st.session_state["hora_inicio_rodada"]:
        tl = st.session_state["hora_inicio_rodada"] + timedelta(minutes=45)
        tr = tl - datetime.now()
        if tr.total_seconds() > 0:
            st.markdown(f'<div class="cronometro-box-gigante"><span style="color:#ffffff; font-size:1.1rem; font-weight:bold; text-transform:uppercase; letter-spacing:2px; display:block; margin-bottom:5px;">⏱️ Tempo Restante de Jogo</span><div class="cronometro-tempo">{int(tr.total_seconds()//60):02d}:{int(tr.total_seconds()%60):02d}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cronometro-box-gigante" style="border-color:#ff3232;"><div class="cronometro-tempo" style="color:#ff3232 !important;">⏰ TEMPO ESGOTADO</div></div>', unsafe_allow_html=True)
    
    # 2. Grid de Mesas em Tamanho Gigante
    if st.session_state["torneio_iniciado"]:
        if not st.session_state["em_matamata"]:
            grid_telao = st.columns(3)
            cont_m = 1
            for j1, j2 in st.session_state["confrontos"]:
                if j2 == "CHAPÉU (Folga)":
                    st.markdown(f'<div class="chapeu-container-novo"><h3 style="color:#ffb703; margin:0;">🎩 FOLGA REGULAMENTAR (CHAPÉU): {j1}</h3></div>', unsafe_allow_html=True)
                else:
                    col_alvo = grid_telao[(cont_m - 1) % 3]
                    p = st.session_state["placares_rodada_atual"].get(str(cont_m), [0,0,0,0,0,0,False])
                    with col_alvo:
                        desenhar_mesa_planta_baixa(j1, j2, str(cont_m), p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo="normal")
                    cont_m += 1
        else:
            if st.session_state["fase_matamata"] == "FINAL E TERCEIRO":
                col_f1, col_f2 = st.columns(2)
                for c in st.session_state["confrontos_mm"]:
                    p = st.session_state["placares_rodada_atual"].get(c["id_original"], [0,0,0,0,0,0,False])
                    if c["tipo"] == "final":
                        with col_f1:
                            desenhar_mesa_planta_baixa(c["j1"], c["j2"], c["id_original"], p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo="final")
                    elif c["tipo"] == "3place":
                        with col_f2:
                            desenhar_mesa_planta_baixa(c["j1"], c["j2"], c["id_original"], p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo="3place")
            else:
                grid_telao = st.columns(2)
                for c in st.session_state["confrontos_mm"]:
                    col_alvo = grid_telao[(int(c["id_original"]) - 1) % 2]
                    p = st.session_state["placares_rodada_atual"].get(c["id_original"], [0,0,0,0,0,0,False])
                    with col_alvo:
                        desenhar_mesa_planta_baixa(c["j1"], c["j2"], c["id_original"], p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo="normal")
    else:
        st.info("Aguardando o início do torneio pela arbitragem para projetar as chaves.")
        
    components.html("<script>setTimeout(function(){ window.parent.location.reload(); }, 10000);</script>", height=0)

else:
    aba_arena, aba_tabela, aba_historico = st.tabs(["⚔️ Arena de Confrontos", "📊 Classificação & Auditoria", "📜 Galeria de Campeões"])

    with aba_arena:
        if not st.session_state["torneio_iniciado"]:
            st.markdown("### 🎮 Inscrições de Competidores")
            nome_t = st.text_input("Nome do Evento:", value="Torneio de Truco do CTG")
            
            if is_admin:
                if st.session_state.get("jogador_sendo_editado") is not None:
                    idx_edit = st.session_state["jogador_sendo_editado"]
                    nome_antigo = st.session_state["jogadores"][idx_edit]
                    
                    # Tenta quebrar o nome antigo para preencher a edição se houver CTG
                    p_nome = nome_antigo.split(" | ")[0] if " | " in nome_antigo else nome_antigo
                    p_ctg = nome_antigo.split(" | ")[1] if " | " in nome_antigo else ""
                    
                    with st.form("form_edicao"):
                        novo_nome = st.text_input("Corrigir Nome:", value=p_nome)
                        novo_ctg = st.text_input("Corrigir Entidade / CTG:", value=p_ctg)
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.form_submit_button("💾 Salvar") and novo_nome.strip():
                                texto_salvar = f"{novo_nome.strip()} | {novo_ctg.strip()}" if novo_ctg.strip() else novo_nome.strip()
                                st.session_state["jogadores"][idx_edit] = texto_salvar
                                st.session_state["jogador_sendo_editado"] = None
                                salvar_estado_no_disco(); st.rerun()
                        with col_b2:
                            if st.form_submit_button("❌ Cancelar"): st.session_state["jogador_sendo_editado"] = None; st.rerun()
                else:
                    # layout de abas para inscrição individual vs em massa (Excel)
                    aba_cad_unico, aba_cad_massa = st.tabs(["👤 Cadastro Individual", "📋 Importar do Excel / Lista"])
                    
                    with aba_cad_unico:
                        col_nj, col_ctg = st.columns([60, 40])
                        with col_nj:
                            nj = st.text_input("Nome do Competidor:", key="txt_individual_nome")
                        with col_ctg:
                            nctg = st.text_input("Entidade / CTG (Opcional):", key="txt_individual_ctg")
                        
                        # Botão comum substitui o st.form_submit_button para liberar o session_state
                        if st.button("➕ Cadastrar Competidor", type="secondary", key="btn_cad_individual_direto"):
                            if nj.strip():
                                texto_completo = f"{nj.strip()} | {nctg.strip()}" if nctg.strip() else nj.strip()
                                if texto_completo not in st.session_state["jogadores"]:
                                    st.session_state["jogadores"].append(texto_completo)
                                    salvar_estado_no_disco()
                                    st.success(f"🔹 {texto_completo} cadastrado!")
                                    st.rerun()
                                else:
                                    st.warning("Este competidor já está cadastrado.")
                            else:
                                st.error("O nome do competidor não pode ficar vazio.")
                                
                    with aba_cad_massa:
                        # Estilização forçada para a caixa de texto não ficar branca com texto branco
                        st.markdown("""
                            <style>
                                div[data-baseweb="textarea"] textarea {
                                    color: #ffffff !important;
                                    background-color: #05180e !important;
                                    border: 1px solid #ffb703 !important;
                                    font-family: monospace;
                                }
                                div[data-baseweb="textarea"] {
                                    background-color: #05180e !important;
                                    border-radius: 6px;
                                }
                            </style>
                        """, unsafe_allow_html=True)

                        # Quadro Verde com Borda Amarela padrão do seu sistema
                        st.markdown("""
                            <div style="background-color:#0d301b; border: 2px solid #ffb703; padding:15px; border-radius:10px; margin-bottom:15px;">
                                <h4 style="color:#ffb703; margin-top:0; margin-bottom:10px;">📋 Importação Rápida de Planilha</h4>
                                <p style="color:#ffffff; font-size:0.9rem; margin:0;">
                                    💡 No seu Excel, selecione as colunas de <b>Nome</b> e <b>CTG</b>, copie (Ctrl+C) e cole no campo abaixo.<br>
                                    O sistema aceita o formato <b>Nome;CTG</b> ou apenas <b>Nome</b> (um por linha).
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        lista_colada = st.text_area("Dados Copiados do Excel:", height=150, placeholder="Exemplo:\nJoão Silva;CTG Sentinela\nPedro Souza;CTG Farroupilha", key="txt_excel_import_final")
                        
                        if st.button("📥 Processar e Inserir Lista", type="primary", key="btn_importar_massa_final"):
                            if lista_colada.strip():
                                linhas = lista_colada.split("\n")
                                novos_jogadores = []
                                
                                for linha in linhas:
                                    if linha.strip():
                                        if ";" in linha:
                                            partes = linha.split(";")
                                            c_nome = partes[0].strip()
                                            c_ctg = partes[1].strip() if len(partes) > 1 else ""
                                            registro = f"{c_nome} | {c_ctg}" if c_ctg else c_nome
                                        else:
                                            registro = linha.strip()
                                        
                                        if registro not in st.session_state["jogadores"] and registro not in novos_jogadores:
                                            novos_jogadores.append(registro)
                                
                                if novos_jogadores:
                                    st.session_state["jogadores"].extend(novos_jogadores)
                                    salvar_estado_no_disco()
                                    st.success(f"✔️ {len(novos_jogadores)} competidores importados com sucesso!")
                                    st.rerun()
                                else:
                                    st.warning("Nenhum competidor novo para adicionar.")
                            
            st.write(f"**Competidores Registrados ({len(st.session_state['jogadores'])}):**")
            if st.session_state["jogadores"]:
                if is_admin:
                    for idx, jogador in enumerate(st.session_state["jogadores"]):
                        c_nome, c_edit, c_excluir = st.columns([70, 15, 15])
                        with c_nome: st.markdown(f"<p style='padding:8px; background-color:#0d301b; border-radius:6px; font-weight:bold; border: 1px solid #ffb703;'>🔹 {jogador}</p>", unsafe_allow_html=True)
                        with c_edit:
                            st.markdown('<div class="botao-editar">', unsafe_allow_html=True)
                            if st.button("✏️", key=f"btn_edit_{idx}"): st.session_state["jogador_sendo_editado"] = idx; st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        with c_excluir:
                            st.markdown('<div class="botao-excluir">', unsafe_allow_html=True)
                            if st.button("🗑️", key=f"btn_del_{idx}"):
                                st.session_state["jogadores"].pop(idx)
                                salvar_estado_no_disco(); st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                else: st.info(", ".join(st.session_state["jogadores"]))
                
            if is_admin and len(st.session_state["jogadores"]) >= 4:
                st.markdown("---")
                if st.button("🃏 GERAR CHAVES E DISPARAR TORNEIO"):
                    st.session_state["nome_torneio"] = nome_t
                    st.session_state["classificacao"] = pd.DataFrame({'Jogador': st.session_state["jogadores"], 'Vitorias': 0, 'Sets_Ganhos': 0, 'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0}).set_index('Jogador')
                    st.session_state["torneio_iniciado"] = True
                    gerar_rodada_web(); st.rerun()
        else:
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1: st.markdown(f'<div class="metric-panel"><div class="metric-val">{len(st.session_state["jogadores"])}</div><div class="metric-lbl">Inscritos na Arena</div></div>', unsafe_allow_html=True)
            with c_m2:
                fase_txt = f"Rodada {st.session_state['rodada_atual']} / 5" if not st.session_state["em_matamata"] else str(st.session_state["fase_matamata"])
                st.markdown(f'<div class="metric-panel"><div class="metric-val">{fase_txt}</div><div class="metric-lbl">Estágio Atual</div></div>', unsafe_allow_html=True)
            with c_m3:
                rei_f = "Ninguém" if st.session_state["classificacao"] is None else str(st.session_state["classificacao"]['Flores'].idxmax())
                st.markdown(f'<div class="metric-panel"><div class="metric-val">🌸 {rei_f[:12]}</div><div class="metric-lbl">Líder das Flores</div></div>', unsafe_allow_html=True)

# ==========================================
# PLAYOFFS, AUDITORIA E HONRA (PARTE 4)
# ==========================================
            if st.session_state["campeao"]:
                st.markdown("<h1 style='text-align:center; color:#ffb703 !important; font-weight:900; letter-spacing:2px; margin-top:20px;'>🏆 CERIMÔNIA DE PREMIAÇÃO FINAL</h1>", unsafe_allow_html=True)
                
                efeito_confete_html = """
                <canvas id="canvas-confetti" style="position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:9999;"></canvas>
                <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
                <script>
                    var duration = 15 * 1000;
                    var animationEnd = Date.now() + duration;
                    var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };
                    function randomInRange(min, max) { return Math.random() * (max - min) + min; }
                    var interval = setInterval(function() {
                        var timeLeft = animationEnd - Date.now();
                        if (timeLeft <= 0) { return clearInterval(interval); }
                        var particleCount = 50 * (timeLeft / duration);
                        confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }));
                        confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }));
                    }, 250);
                </script>
                """
                components.html(efeito_confete_html, height=1)

                champ, vice = str(st.session_state["campeao"]), str(st.session_state["vice_campeao"])
                third = str(st.session_state["terceiro_lugar"]) if st.session_state["terceiro_lugar"] else "N/A"
                fourth = str(st.session_state["quarto_lugar"]) if st.session_state["quarto_lugar"] else "N/A"
                rei_flor_nome = str(st.session_state["classificacao"]['Flores'].idxmax())
                rei_flor_val = int(st.session_state["classificacao"]['Flores'].max())

                html_iframe_podio = f"""
                <div style="background-color: transparent; padding: 10px; font-family: sans-serif; display: flex; flex-direction: column; gap: 20px; align-items: center; width: 100%; box-sizing: border-box;">
                    <div style="display: flex; align-items: flex-end; justify-content: center; gap: 20px; width: 100%; max-width: 950px; margin: 20px auto;">
                        <div style="flex: 1; background: linear-gradient(135deg, #ffffff, #b0b0b0); height: 210px; border-radius: 12px; text-align: center; padding: 20px 10px; box-shadow: 0px 15px 35px rgba(0,0,0,0.5); border: 2px solid #e0e0e0;">
                            <p style="font-size: 3.2rem; font-weight: 900; margin: 0; color: #111111;">2º</p>
                            <div style="font-size: 1.4rem; font-weight: 900; text-transform: uppercase; color: #0b0f19;">👤 {vice}</div>
                            <div style="font-size: 0.8rem; font-weight: bold; text-transform: uppercase; color: #333333;">🥈 Vice-Campeão</div>
                        </div>
                        <div style="flex: 1; background: linear-gradient(135deg, #ffe066, #ffb703); height: 270px; border-radius: 12px; text-align: center; padding: 25px 10px; border: 3px solid #ffffff; box-shadow: 0px 0px 30px rgba(255, 183, 3, 0.6);">
                            <p style="font-size: 3.5rem; font-weight: 900; margin: 0; color: #000000;">1º</p>
                            <div style="font-size: 1.6rem; font-weight: 900; text-transform: uppercase; color: #0b0f19;">👑 {champ}</div>
                            <div style="font-size: 0.8rem; font-weight: bold; text-transform: uppercase; color: #403000;">Campeão Absoluto</div>
                        </div>
                        <div style="flex: 1; background: linear-gradient(135deg, #e69d5e, #cd7f32); height: 170px; border-radius: 12px; text-align: center; padding: 15px 10px; box-shadow: 0px 15px 35px rgba(0,0,0,0.5); border: 2px solid #cd7f32;">
                            <p style="font-size: 2.8rem; font-weight: 900; margin: 0; color: #ffffff;">3º</p>
                            <div style="font-size: 1.3rem; font-weight: 900; text-transform: uppercase; color: #ffffff;">👤 {third}</div>
                            <div style="font-size: 0.8rem; font-weight: bold; text-transform: uppercase; color: #f0f0f0;">🥉 3º Colocado</div>
                        </div>
                    </div>
                </div>
                """
                components.html(html_iframe_podio, height=350)
                
                if is_admin and st.button("💾 Imortalizar Resultados na Galeria Histórica"):
                    novo_registro = {"Data": datetime.now().strftime("%d/%m/%Y"), "Torneio": st.session_state.get("nome_torneio", "Torneio de Truco"), "Campeao": champ, "Vice": vice, "Terceiro": third, "Quarto": fourth, "ReiDaFlor": f"{rei_flor_nome} ({rei_flor_val} fl.)"}
                    lista_g = []
                    if os.path.exists(ARQUIVO_GALERIA):
                        try:
                            with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: lista_g = json.load(f)
                        except Exception: pass
                    lista_g.append(novo_registro)
                    with open(ARQUIVO_GALERIA, "w", encoding="utf-8") as f: json.dump(lista_g, f, ensure_ascii=False, indent=4)
                    st.success("Resultados imortalizados!")
            else:
                if st.session_state["cronometro_ativo"] and st.session_state["hora_inicio_rodada"]:
                    tl = st.session_state["hora_inicio_rodada"] + timedelta(minutes=45)
                    tr = tl - datetime.now()
                    if tr.total_seconds() > 0:
                        st.markdown(f'<div class="cronometro-box-gigante"><div class="cronometro-tempo">{int(tr.total_seconds()//60):02d}:{int(tr.total_seconds()%60):02d}</div></div>', unsafe_allow_html=True)
                    else: st.markdown('<div class="cronometro-box-gigante" style="border-color:#ff3232;"><div class="cronometro-tempo" style="color:#ff3232 !important;">⏰ TIMEOUT!</div></div>', unsafe_allow_html=True)

                sem_id = st.session_state.get("semente_reset", 1)

                if not st.session_state["em_matamata"]:
                    st.markdown(f"### 📅 Rodada Corrente: {st.session_state['rodada_atual']} de 5")
                    for j1, j2 in st.session_state["confrontos"]:
                        if j2 == "CHAPÉU (Folga)":
                            st.markdown(f'<div class="chapeu-container-novo"><div class="metric-lbl">🎩 Jogador no Chapéu (Folga)</div><div class="cronometro-tempo" style="font-size:2rem!important;">{j1}</div></div>', unsafe_allow_html=True)
                    
                    cont = 1
                    for j1, j2 in st.session_state["confrontos"]:
                        if j2 != "CHAPÉU (Folga)":
                            m = str(cont)
                            p = st.session_state["placares_rodada_atual"].get(m, [0,0,0,0,0,0,False])
                            st.markdown(f'<div class="titulo-mesa-destaque">🎰 MESA DE JOGO {m}</div>', unsafe_allow_html=True)
                            
                            if is_admin:
                                col_painel, col_entradas = st.columns([45, 55])
                                with col_painel: desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo="normal")
                                with col_entradas: renderizar_formulario_mesa_admin(m, j1, j2, sem_id)
                            else: desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo="normal")
                            cont += 1
                    
                    if is_admin:
                        st.markdown("### 🏁 Finalização")
                        if st.button("Validar e Encerrar Rodada Atual", type="primary"):
                            erro_v = False; m_c = 1
                            for j1, j2 in st.session_state["confrontos"]:
                                if j2 != "CHAPÉU (Folga)":
                                    p = st.session_state["placares_rodada_atual"].get(str(m_c), [0,0,0,0,0,0,False])
                                    if not (p[0] == 2 or p[1] == 2): st.error(f"❌ Mesa {m_c}: Partida incompleta!"); erro_v = True
                                    m_c += 1
                            if not erro_v:
                                id_r_str = str(st.session_state["rodada_atual"])
                                st.session_state["historico_rodadas"][id_r_str] = {}
                                m_c = 1
                                for j1, j2 in st.session_state["confrontos"]:
                                    if j2 == "CHAPÉU (Folga)": st.session_state["historico_rodadas"][id_r_str][f"chapeu_{j1}"] = {"is_chapeu": True, "j1": j1, "j2": "Folga", "s1": 3, "s2": 0, "t1": 72, "t2": 0, "f1": 0, "f2": 0}
                                    else:
                                        p = st.session_state["placares_rodada_atual"].get(str(m_c), [0,0,0,0,0,0,False])
                                        st.session_state["historico_rodadas"][id_r_str][str(m_c)] = {"is_chapeu": False, "j1": j1, "j2": j2, "s1": p[0], "s2": p[1], "t1": p[2], "t2": p[3], "f1": p[4], "f2": p[5]}
                                        m_c += 1
                                reconstruir_classificacao_global()
                                st.session_state["rodada_atual"] += 1
                                if st.session_state["rodada_atual"] <= 5: gerar_rodada_web()
                                else:
                                    n_in = len(st.session_state["jogadores"])
                                    f_n = "OITAVAS DE FINAL" if n_in > 16 else ("QUARTAS DE FINAL" if n_in >= 8 else "SEMIFINAL")
                                    dv = st.session_state["classificacao"].sort_values(by=['Vitorias','Sets_Ganhos','Saldo_Tentos'], ascending=False)
                                    iniciar_fase_matamata(list(dv.index[:16 if n_in>16 else (8 if n_in>=8 else 4)]), f_n)
                                st.rerun()
                else:
                    st.markdown(f"### ⚡ Eliminatórias: {st.session_state['fase_matamata']}")
                    for c in st.session_state["confrontos_mm"]:
                        m = c["id_original"]; j1, j2 = c["j1"], c["j2"]
                        p = st.session_state["placares_rodada_atual"].get(m, [0,0,0,0,0,0,False])
                        st.markdown(f'<div class="titulo-mesa-destaque">{st.session_state["fase_matamata"]} - MESA {m}</div>', unsafe_allow_html=True)
                        if is_admin:
                            col_p_mm, col_e_mm = st.columns([45, 55])
                            with col_p_mm: desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo=c["tipo"])
                            with col_e_mm: renderizar_formulario_mesa_admin(m, j1, j2, sem_id)
                        else: desenhar_mesa_planta_baixa(j1, j2, m, p[0], p[2], p[4], p[1], p[3], p[5], tipo_jogo=c["tipo"])

                    if is_admin:
                        if st.button("🏆 Validar e Avançar Playoffs", type="primary"):
                            erro_mm = False
                            for c in st.session_state["confrontos_mm"]:
                                p = st.session_state["placares_rodada_atual"].get(c["id_original"], [0,0,0,0,0,0,False])
                                if not (p[0] == 2 or p[1] == 2): st.error(f"❌ Partida pendente na mesa {c['id_original']}!"); erro_mm = True
                            if not erro_mm:
                                venc, perd = [], []
                                for c in st.session_state["confrontos_mm"]:
                                    p = st.session_state["placares_rodada_atual"].get(c["id_original"], [0,0,0,0,0,0,False])
                                    st.session_state["classificacao"].loc[c["j1"], 'Flores'] += p[4]
                                    st.session_state["classificacao"].loc[c["j2"], 'Flores'] += p[5]
                                    w, l = (c["j1"], c["j2"]) if p[0] >= p[1] else (c["j2"], c["j1"])
                                    if c["tipo"]=="normal": venc.append(w); perd.append(l)
                                    elif c["tipo"]=="final": st.session_state["campeao"]=w; st.session_state["vice_campeao"]=l
                                    elif c["tipo"]=="3place": st.session_state["terceiro_lugar"]=w; st.session_state["quarto_lugar"]=l
                                f_at = st.session_state["fase_matamata"]
                                if f_at == "OITAVAS DE FINAL": iniciar_fase_matamata(venc, "QUARTAS DE FINAL")
                                elif f_at == "QUARTAS DE FINAL": iniciar_fase_matamata(venc, "SEMIFINAL")
                                elif f_at == "SEMIFINAL":
                                    limpar_placares_memoria()
                                    st.session_state["fase_matamata"] = "FINAL E TERCEIRO"
                                    st.session_state["confrontos_mm"] = [{"id_original": "1", "tipo": "final", "j1": venc[0], "j2": venc[1]}, {"id_original": "2", "tipo": "3place", "j1": perd[0], "j2": perd[1]}]
                                    st.session_state["placares_rodada_atual"] = {"1": [0,0,0,0,0,0,False], "2": [0,0,0,0,0,0,False]}
                                salvar_estado_no_disco(); st.rerun()

    with aba_tabela:
        if st.session_state["classificacao"] is not None:
            st.markdown("### 📊 Tabela Oficial de Pontuação")
            df_r = st.session_state["classificacao"].sort_values(by=['Vitorias','Sets_Ganhos','Saldo_Tentos'], ascending=False)
            st.table(df_r)
            
            if st.session_state["historico_rodadas"]:
                st.markdown("---")
                st.markdown("### 🔍 Central de Correção Retroativa")
                r_sel = st.selectbox("Selecione a Rodada Fechada:", list(st.session_state["historico_rodadas"].keys()))
                if r_sel:
                    for m_id, dados in st.session_state["historico_rodadas"][r_sel].items():
                        if not dados.get("is_chapeu", False):
                            st.markdown(f"**Mesa {m_id}: {dados['j1']} VS {dados['j2']}**")
                            if is_admin:
                                c_e1, c_e2 = st.columns(2)
                                with c_e1:
                                    st.number_input(f"Sets ({dados['j1']})", 0, 2, int(dados["s1"]), key=f"ret_s1_{r_sel}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_sel, m_id, dados['j1'], dados['j2']))
                                    st.number_input(f"Tentos ({dados['j1']})", 0, 72, int(dados["t1"]), key=f"ret_t1_{r_sel}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_sel, m_id, dados['j1'], dados['j2']))
                                with c_e2:
                                    st.number_input(f"Sets ({dados['j2']})", 0, 2, int(dados["s2"]), key=f"ret_s2_{r_sel}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_sel, m_id, dados['j1'], dados['j2']))
                                    st.number_input(f"Tentos ({dados['j2']})", 0, 72, int(dados["t2"]), key=f"ret_t2_{r_sel}_{m_id}", on_change=salvar_mudanca_retroativa, args=(r_sel, m_id, dados['j1'], dados['j2']))
                            else: st.markdown(f"👉 **Placar Histórico:** {dados['s1']}s {dados['t1']}t VS {dados['s2']}s {dados['t2']}t")

    with aba_historico:
        st.markdown("### 📜 Galeria de Honra")
        if os.path.exists(ARQUIVO_GALERIA):
            try:
                with open(ARQUIVO_GALERIA, "r", encoding="utf-8") as f: dg = json.load(f)
                for reg in reversed(dg):
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #0d301b, #04120a); border: 2px solid #ffb703; border-radius: 12px; padding: 15px; margin-bottom: 15px;">
                            <b style="color:#ffb703;">🏆 {reg.get('Torneio')}</b> <span style="float:right; color:#69db7c;">📅 {reg.get('Data')}</span><br>
                            <span style="color:#ffffff;">🥇 Campeão: {reg.get('Campeao')} | 🥈 Vice: {reg.get('Vice')}</span><br>
                            <span style="color:#ff69b4; font-weight:bold;">🌸 Maior Cantador de Flor: {reg.get('ReiDaFlor')}</span>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception: st.info("Galeria vazia.")
        else: st.info("Nenhum torneio imortalizado ainda.")

# --- RODAPÉ INSTITUCIONAL PROFISSIONAL DE ULTRA CONTRASTE ---
st.markdown("""
    <hr style="border: 0; border-top: 1px solid rgba(255, 183, 3, 0.4); margin-top: 60px; margin-bottom: 15px;">
    <div style="
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        flex-wrap: wrap; 
        padding: 12px 20px; 
        background: linear-gradient(90deg, #04120a, #0b2b18); 
        border: 2px solid #ffb703; 
        border-radius: 10px; 
        font-family: system-ui, sans-serif;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.5);
    ">
        <div style="color: #ffffff; font-size: 0.9rem; font-weight: bold; text-shadow: 1px 1px 2px #000;">
            🚀 Desenvolvido por: <span style="color: #ffb703; font-weight: 900; letter-spacing: 0.5px;">Eduardo Luis Ferreira</span>
        </div>
        <div style="color: #ffffff; font-size: 0.85rem; font-weight: bold; display: flex; gap: 15px; align-items: center; text-shadow: 1px 1px 2px #000;">
            <span>📦 Versão: <span style="color: #ffb703; font-weight: 900;">2.6.0-Stable</span></span>
            <span style="color: #ffb703; font-weight: 900;">|</span>
            <span style="color: #69db7c; font-weight: 900; display: inline-flex; align-items: center; gap: 4px;">🟢 Sistema Online</span>
            <span style="color: #ffb703; font-weight: 900;">|</span>
            <span style="color: #ffffff; font-weight: bold;">© 2026 Todos os Direitos Reservados</span>
        </div>
    </div>
""", unsafe_allow_html=True)
