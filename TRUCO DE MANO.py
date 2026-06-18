import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import json
import os
import socket
import requests 
from PIL import Image 
from io import BytesIO
from datetime import datetime, timedelta

# 🃏 CONFIGURAÇÃO DA PÁGINA PREMIUM ULTRA WIDE
st.set_page_config(
    page_title="Central de Torneios de Truco - Planta Baixa",
    page_icon="🃏",
    layout="wide"
)

NOME_CRIADOR = "Eduardo Luis Ferreira"
ARQUIVO_BACKUP = "torneio_atual_pb.json"
ARQUIVO_GALERIA = "galeria_campeoes.json"
CHAVE_ADMINISTRADOR = "truco123"

# 🛠️ ESTILIZAÇÃO CSS PREMIUM AMBIENTE DE TRUCO (VERDE IMPERIAL + DOURADO PREMIUM)
st.markdown("""
    <style>
    /* Fundo Temático de Feltro de Mesa de Jogo */
    .stApp { 
        background: radial-gradient(circle, #0e3b23 0%, #061c10 100%) !important; 
    } 
    
    section[data-testid="stSidebar"] {
        background-color: #04120a !important;
        border-right: 3px solid #ffb703;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 { color: #ffb703; }
    
    h1, h2, h3, h4, h5, p, label, .stText, [data-testid="stMarkdownContainer"] p { 
        color: #ffffff !important; 
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }
    
    .titulo-passo-admin {
        color: #ffb703 !important;
        font-weight: bold !important;
        margin-top: 12px !important;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .titulo-mesa-destaque {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        background: linear-gradient(90deg, #124027, transparent);
        padding: 6px 12px;
        border-left: 5px solid #ffb703;
        margin-top: 25px;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-radius: 0 8px 8px 0;
    }
    
    /* Inputs Estilizados */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #071c11 !important;
        border: 2px solid #ffb703 !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label {
        color: #69db7c !important; /* Verde Menta Fluorescente para total leitura */
        font-size: 0.85rem !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    
    /* Abas Customizadas */
    button[data-baseweb="tab"] { color: #69db7c !important; font-size: 1.1rem !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #ffb703 !important; font-weight: 900 !important; border-bottom-color: #ffb703 !important; }
    
    /* Botões */
    .stButton>button, div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #124027, #071c11) !important;
        color: #ffffff !important; border: 2px solid #ffb703 !important;
        font-weight: bold !important; border-radius: 8px !important; padding: 10px 16px !important; transition: all 0.3s ease !important;
        width: 100%; font-size: 1rem !important; text-transform: uppercase; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button:hover, div[data-testid="stForm"] button:hover {
        background: #ffb703 !important; color: #061c10 !important; border-color: #ffffff !important; transform: scale(1.02);
    }
    
    /* Modificadores de Ação Rápida */
    div.botao-excluir > button { background: #4a121a !important; color: #ff8787 !important; border: 1px solid #ff4848 !important; }
    div.botao-excluir > button:hover { background: #e03131 !important; color: #ffffff !important; }
    div.botao-editar > button { background: #0b2b18 !important; color: #69db7c !important; border: 1px solid #2b8a3e !important; }
    div.botao-editar > button:hover { background: #37b24d !important; color: #ffffff !important; }
    
    /* MÓDULO DO CRONÔMETRO PULSANTE GIGANTE */
    @keyframes pulsarAviso {
        0% { transform: scale(1); box-shadow: 0 0 15px rgba(255, 183, 3, 0.4); }
        50% { transform: scale(1.02); box-shadow: 0 0 30px rgba(255, 50, 50, 0.8); border-color: #ff3232; }
        100% { transform: scale(1); box-shadow: 0 0 15px rgba(255, 183, 3, 0.4); }
    }
    .cronometro-box-gigante { 
        background: linear-gradient(135deg, #092415, #04120a); 
        border: 4px solid #ffb703; 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 25px;
        text-align: center;
        animation: pulsarAviso 3s infinite ease-in-out;
    }
    .cronometro-tempo {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        color: #ffb703 !important;
        letter-spacing: 3px;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* CHAPÉU CONTAINER */
    .chapeu-container-novo {
        background: linear-gradient(135deg, #195434, #071c11);
        border: 3px dashed #ffb703;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.5);
    }
    
    /* PANÉIS DE MÉTRICAS MODERNOS */
    .metric-panel { 
        background: linear-gradient(135deg, #0d301b, #06170d); 
        border: 2px solid #ffb703; 
        border-radius: 12px; 
        padding: 15px; 
        text-align: center; 
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .metric-val { font-size: 2rem; font-weight: 900; color: #ffb703; }
    .metric-lbl { font-size: 0.8rem; text-transform: uppercase; color: #69db7c; font-weight: bold; letter-spacing: 1px; }

    /* TABELAS */
    div[data-testid="stTable"] { background-color: #071c11 !important; border-radius: 10px; overflow: hidden; border: 2px solid #ffb703 !important; }
    div[data-testid="stTable"] th { background-color: #04120a !important; color: #ffb703 !important; font-size: 1rem !important; text-align: center !important; padding: 12px !important; }
    div[data-testid="stTable"] td { background-color: #0d301b !important; color: #ffffff !important; font-weight: bold !important; text-align: center !important; padding: 12px !important; border: 1px solid #04120a !important;}
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO INICIAL RIGOROSA DOS ATRIBUTOS DE SESSÃO ---
if "jogadores" not in st.session_state: st.session_state["jogadores"] = []
if "torneio_iniciado" not in st.session_state: st.session_state["torneio_iniciado"] = False
if "rodada_atual" not in st.session_state: st.session_state["rodada_atual"] = 1
if "classificacao" not in st.session_state: st.session_state["classificacao"] = None
if "confrontos" not in st.session_state: st.session_state["confrontos"] = []
if "jogadores_no_chapeu" not in st.session_state: st.session_state["jogadores_no_chapeu"] = set()
if "hora_inicio_rodada" not in st.session_state: st.session_state["hora_inicio_rodada"] = None
if "cronometro_ativo" not in st.session_state: st.session_state["cronometro_ativo"] = False
if "em_matamata" not in st.session_state: st.session_state["em_matamata"] = False
if "fase_matamata" not in st.session_state: st.session_state["fase_matamata"] = ""
if "confrontos_mm" not in st.session_state: st.session_state["confrontos_mm"] = []
if "campeao" not in st.session_state: st.session_state["campeao"] = None
if "vice_campeao" not in st.session_state: st.session_state["vice_campeao"] = None
if "terceiro_lugar" not in st.session_state: st.session_state["terceiro_lugar"] = None
if "quarto_lugar" not in st.session_state: st.session_state["quarto_lugar"] = None
if "historico_rodadas" not in st.session_state: st.session_state["historico_rodadas"] = {}
if "placares_rodada_atual" not in st.session_state: st.session_state["placares_rodada_atual"] = {}
if "semente_reset" not in st.session_state: st.session_state["semente_reset"] = 1
if "nome_torneio" not in st.session_state: st.session_state["nome_torneio"] = "Torneio de Truco"
if "jogador_sendo_editado" not in st.session_state: st.session_state["jogador_sendo_editado"] = None
if "admin_logado" not in st.session_state: st.session_state["admin_logado"] = False

# --- FUNÇÃO DE LIMPEZA DE MEMÓRIA ---
def limpar_placares_memoria():
    st.session_state["placares_rodada_atual"] = {}
    st.session_state["semente_reset"] = st.session_state.get("semente_reset", 1) + 1
    chaves_para_remover = [k for k in st.session_state.keys() if k.startswith("dir_s") or k.startswith("dir_t") or k.startswith("dir_f")]
    for k in chaves_para_remover:
        del st.session_state[k]

# --- PERSISTÊNCIA EM DISCO ---
def salvar_estado_no_disco():
    estado = {
        "jogadores": st.session_state["jogadores"],
        "torneio_iniciado": st.session_state["torneio_iniciado"],
        "rodada_atual": st.session_state["rodada_atual"],
        "confrontos": st.session_state["confrontos"],
        "jogadores_no_chapeu": list(st.session_state["jogadores_no_chapeu"]),
        "hora_inicio_rodada": st.session_state["hora_inicio_rodada"].isoformat() if st.session_state["hora_inicio_rodada"] else None,
        "cronometro_ativo": st.session_state["cronometro_ativo"],
        "historico_rodadas": st.session_state["historico_rodadas"],
        "nome_torneio": st.session_state.get("nome_torneio", "Torneio de Truco"),
        "em_matamata": st.session_state["em_matamata"],
        "fase_matamata": st.session_state["fase_matamata"],
        "confrontos_mm": st.session_state["confrontos_mm"],
        "campeao": st.session_state["campeao"],
        "vice_campeao": st.session_state["vice_campeao"],
        "terceiro_lugar": st.session_state["terceiro_lugar"],
        "quarto_lugar": st.session_state["quarto_lugar"],
        "placares_rodada_atual": st.session_state["placares_rodada_atual"],
        "semente_reset": st.session_state.get("semente_reset", 1)
    }
    if st.session_state["classificacao"] is not None:
        estado["classificacao"] = st.session_state["classificacao"].to_dict(orient="index")
    with open(ARQUIVO_BACKUP, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=4)

def carregar_estado_do_disco():
    if os.path.exists(ARQUIVO_BACKUP):
        try:
            with open(ARQUIVO_BACKUP, "r", encoding="utf-8") as f:
                estado = json.load(f)
            st.session_state["jogadores"] = estado.get("jogadores", [])
            st.session_state["torneio_iniciado"] = estado.get("torneio_iniciado", False)
            st.session_state["rodada_atual"] = estado.get("rodada_atual", 1)
            st.session_state["confrontos"] = estado.get("confrontos", [])
            st.session_state["jogadores_no_chapeu"] = set(estado.get("jogadores_no_chapeu", []))
            st.session_state["em_matamata"] = estado.get("em_matamata", False)
            st.session_state["fase_matamata"] = estado.get("fase_matamata", "")
            st.session_state["confrontos_mm"] = estado.get("confrontos_mm", [])
            st.session_state["campeao"] = estado.get("campeao", None)
            st.session_state["vice_campeao"] = estado.get("vice_campeao", None)
            st.session_state["terceiro_lugar"] = estado.get("terceiro_lugar", None)
            st.session_state["quarto_lugar"] = estado.get("quarto_lugar", None)
            st.session_state["historico_rodadas"] = estado.get("historico_rodadas", {})
            st.session_state["placares_rodada_atual"] = estado.get("placares_rodada_atual", {})
            st.session_state["semente_reset"] = estado.get("semente_reset", 1)
            if estado.get("nome_torneio"): st.session_state["nome_torneio"] = estado.get("nome_torneio")
            if estado.get("classificacao") is not None: st.session_state["classificacao"] = pd.DataFrame.from_dict(estado["classificacao"], orient="index")
            if estado.get("hora_inicio_rodada"): st.session_state["hora_inicio_rodada"] = datetime.fromisoformat(estado["hora_inicio_rodada"])
        except Exception: pass

carregar_estado_do_disco()

# --- RECALCULADOR MATRIZ ---
def reconstruir_classificacao_global():
    st.session_state["classificacao"] = pd.DataFrame({
        'Jogador': st.session_state["jogadores"], 'Vitorias': 0, 'Sets_Ganhos': 0, 
        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
    }).set_index('Jogador')
    
    for r_num, mesas in st.session_state["historico_rodadas"].items():
        for m_id, dados in mesas.items():
            if dados.get("is_chapeu", False):
                st.session_state["classificacao"].loc[dados["j1"], ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
            else:
                j1, j2 = dados["j1"], dados["j2"]
                s1, s2, t1, t2, f1, f2 = dados["s1"], dados["s2"], dados["t1"], dados["t2"], dados["f1"], dados["f2"]
                s1_c = 3 if (s1 == 2 and s2 == 0) else s1
                s2_c = 3 if (s2 == 2 and s1 == 0) else s2
                v1, v2 = (1, 0) if s1 > s2 else (0, 1)
                
                st.session_state["classificacao"].loc[j1, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v1, s1_c, t1, t2, f1]
                st.session_state["classificacao"].loc[j2, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v2, s2_c, t2, t1, f2]
                
    st.session_state["classificacao"]['Saldo_Tentos'] = st.session_state["classificacao"]['Tentos_Pro'] - st.session_state["classificacao"]['Tentos_Contra']
    salvar_estado_no_disco()

# --- LÓGICA DE GERAÇÃO DE CHAVES ---
def gerar_rodada_web():
    limpar_placares_memoria()
    if st.session_state["rodada_atual"] == 1:
        lista_rodada = list(st.session_state["jogadores"])
        random.shuffle(lista_rodada)
    else:
        df_ord = st.session_state["classificacao"].sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
        lista_rodada = list(df_ord.index)

    st.session_state["confrontos"] = []
    if len(lista_rodada) % 2 != 0:
        cand = [j for j in lista_rodada if j not in st.session_state["jogadores_no_chapeu"]]
        chapeu = random.choice(cand if cand else lista_rodada)
        lista_rodada.remove(chapeu)
        st.session_state["jogadores_no_chapeu"].add(chapeu)
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

# --- DISPARADOR DE ATUALIZAÇÃO ---
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

# --- CARDS DINÂMICOS DE MESA COM STATUS COLORIDO (PLANTA BAIXA PREMIUM) ---
def desenhar_mesa_planta_baixa(j1, j2, mesa_num, s1, t1, f1, s2, t2, f2, tipo_jogo="normal"):
    animacao_css = ""
    if tipo_jogo == "final":
        borda_cor = "#ffb703" 
        bg_topo = "linear-gradient(135deg, #ffb703, #b8860b)"
        texto_topo = "#000000"
        tag_titulo = "👑 GRANDE FINAL ABSOLUTA 👑"
        card_height = "420px"
        fonte_jogadores = "1.5rem"
        animacao_css = "animation: pulsarFinal 2s infinite ease-in-out;"
    elif tipo_jogo == "3place":
        borda_cor = "#cd7f32" 
        bg_topo = "linear-gradient(135deg, #cd7f32, #8b5a2b)"
        texto_topo = "#ffffff"
        tag_titulo = "🥉 DISPUTA DE 3º LUGAR 🥉"
        card_height = "400px"
        fonte_jogadores = "1.3rem"
    elif (s1 == 2 or s2 == 2):
        borda_cor = "#2b8a3e" 
        bg_topo = "#124027"
        texto_topo = "#ffffff"
        tag_titulo = f"🎰 MESA {mesa_num} (CONCLUÍDO)"
        card_height = "350px"
        fonte_jogadores = "1.1rem"
    else:
        borda_cor = "#e67e22" 
        bg_topo = "#2c1e11"
        texto_topo = "#ffffff"
        tag_titulo = f"🎰 MESA {mesa_num}"
        card_height = "350px"
        fonte_jogadores = "1.1rem"

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
            <div style="background: #04120a; color: #ffffff; padding: 6px 15px; border-radius: 8px; font-size: {fonte_jogadores}; font-weight: 900; display: inline-block; border: 1px solid #ffb703; max-width: 85%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{j1}</div>
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
            <div style="background: #04120a; color: #ffffff; padding: 6px 15px; border-radius: 8px; font-size: {fonte_jogadores}; font-weight: 900; display: inline-block; border: 1px solid #ffb703; max-width: 85%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{j2}</div>
            <div style="font-size: 0.75rem; color: #69db7c; font-weight: bold; text-transform: uppercase; margin-top: 2px;">🧔 Jogador 2</div>
        </div>
    </div>
    """
    components.html(html_mesa, height=int(card_height.replace("px","")) + 15, scrolling=False)

# --- CONFIGURAÇÃO DO FORMULÁRIO DO PAINEL DE CONTROLE DE ENTRADAS ---
def renderizar_formulario_mesa_admin(m, j1, j2, sem_id):
    p = st.session_state["placares_rodada_atual"].get(m, [0,0,0,0,0,0,False])
    s1, s2, t1, t2, f1, f2 = p[0], p[1], p[2], p[3], p[4], p[5]
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown(f"<h4 class='titulo-passo-admin'>• SETS (Passo 1)</h4>", unsafe_allow_html=True)
        s1_in = st.number_input(f"Sets - {j1}", 0, 2, int(s1), key=f"dir_s1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
        s2_in = st.number_input(f"Sets - {j2}", 0, 2, int(s2), key=f"dir_s2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))

    jogo_encerrado = (s1_in == 2 or s2_in == 2)
    
    with c2:
        if not jogo_encerrado:
            st.warning("Aguardando Sets...")
        else:
            st.markdown(f"<h4 class='titulo-passo-admin'>• TENTOS (Passo 2)</h4>", unsafe_allow_html=True)
            if s1_in == 2 and s2_in == 0:
                st.number_input(f"Tentos - {j2} (Máx: 46)", 0, 46, min(int(t2), 46), key=f"dir_t2_{m}_r{sem_id}_2x0j1", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            elif s2_in == 2 and s1_in == 0:
                st.number_input(f"Tentos - {j1} (Máx: 46)", 0, 46, min(int(t1), 46), key=f"dir_t1_{m}_r{sem_id}_2x0j2", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            else:
                t1_val_str = "" if (t1 == 72 or t1 == 0) else str(t1)
                t2_val_str = "" if (t2 == 72 or t2 == 0) else str(t2)
                st.text_input(f"Tentos - {j1}", value=t1_val_str, key=f"dir_t1_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Tentos...")
                st.text_input(f"Tentos - {j2}", value=t2_val_str, key=f"dir_t2_{m}_r{sem_id}_2x1", on_change=disparar_atualizacao_placar, args=(m, j1, j2), placeholder="Tentos...")
            
            st.markdown(f"<h4 class='titulo-passo-admin'>• FLORES (Passo 3)</h4>", unsafe_allow_html=True)
            st.number_input(f"Flores - {j1}", 0, 20, int(f1), key=f"dir_f1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
            st.number_input(f"Flores - {j2}", 0, 20, int(f2), key=f"dir_f2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))

# --- BARRA LATERAL PERSISTENTE ---
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

# SELETOR DE MODO DE EXIBIÇÃO (ARENA VS TELÃO AUTOMÁTICO DE PROJETOR)
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
                    with st.form("form_edicao"):
                        novo_nome = st.text_input("Corrigir Nome:", value=nome_antigo)
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.form_submit_button("💾 Salvar") and novo_nome.strip():
                                st.session_state["jogadores"][idx_edit] = novo_nome.strip()
                                st.session_state["jogador_sendo_editado"] = None
                                salvar_estado_no_disco(); st.rerun()
                        with col_b2:
                            if st.form_submit_button("❌ Cancelar"): st.session_state["jogador_sendo_editado"] = None; st.rerun()
                else:
                    with st.form("cad", clear_on_submit=True):
                        nj = st.text_input("Nome do Competidor:")
                        if st.form_submit_button("➕ Cadastrar Competidor") and nj:
                            st.session_state["jogadores"].append(nj.strip())
                            salvar_estado_no_disco(); st.rerun()
                            
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

# --- RODAPÉ INSTITUCIONAL PROFISSIONAL DE ULTRA CONTRASTE (SEM CINZA) ---
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
