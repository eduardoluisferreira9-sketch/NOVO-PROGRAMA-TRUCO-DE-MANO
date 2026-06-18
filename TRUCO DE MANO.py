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
CHAVE_ADMINISTRADOR = "ctg123"  # Senha master da arbitragem
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
    section[data-testid="stSidebar"] {
        background-color: #030d07 !important;
        border-right: 2px solid #ffb703 !important;
    }
    
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffb703 !important;
    }

    section[data-testid="stSidebar"] button {
        background-color: #ffb703 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 1px solid #ffb703 !important;
        transition: background-color 0.3s ease;
    }

    section[data-testid="stSidebar"] button:hover {
        background-color: #dda15e !important;
        color: #000000 !important;
        border-color: #dda15e !important;
    }
    
    /* ------------------------------------------------------------- */
    /* ELEMENTOS DE ULTRA CONTRASTE DA ARENA CORRIGIDOS              */
    /* ------------------------------------------------------------- */
    div[data-testid="stWidgetLabel"] p, 
    label[data-testid="stWidgetLabel"] p,
    .st-emotion-cache-q8s8vi p,
    .st-emotion-cache-q8s8vi {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }

    button[data-testid="stMarkdownContainer"] p,
    .stTabs button p,
    .st-emotion-cache-6t18gh p {
        color: #ffffff !important;
    }
    
    button[aria-selected="true"] p,
    button[aria-selected="true"] div[data-testid="stMarkdownContainer"] p,
    .stTabs button[aria-selected="true"] p {
        color: #ffb703 !important;
        font-weight: bold !important;
    }

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

    /* CSS DO BOTÃO GIGANTE COPIADO PARA A RAIZ GLOBAL */
    div.botao-grande-comando .stButton > button,
    div.botao-grande-comando .stButton > button p,
    div.botao-grande-comando .stButton > button span {
        color: #05180e !important;
        background-color: #ffffff !important;
        font-weight: 900 !important;
    }
    div.botao-grande-comando .stButton > button {
        border: 2px solid #ffb703 !important;
        width: 100% !important;
        padding: 10px !important;
    }
    div.botao-grande-comando .stButton > button:hover,
    div.botao-grande-comando .stButton > button:hover p,
    div.botao-grande-comando .stButton > button:hover span {
        color: #ffffff !important;
        background-color: #ffb703 !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização Blindada do Estado Interno (Session State)
ESTADOS_INICIAIS = {
    "jogadores": [],
    "torneio_iniciado": False,
    "rodada_atual": 1,
    "confrontos": [],
    "placares_rodada_atual": {},
    "historico_rodadas": {},
    "classificacao": None,
    "jogadores_no_chapeu": set(),
    "admin_logado": False,
    "cronometro_ativo": False,
    "hora_inicio_rodada": None,
    "em_matamata": False,
    "fase_matamata": "",
    "confrontos_mm": [],
    "campeao": None,
    "vice_campeao": None,
    "terceiro_lugar": None,
    "quarto_lugar": None,
    "jogador_sendo_editado": None
}

for chave, valor_padrao in ESTADOS_INICIAIS.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor_padrao

def salvar_estado_no_disco():
    """Gravação atômica segura para evitar corrupção em torneios oficiais"""
    try:
        dados = {k: v for k, v in st.session_state.items() if k != "jogador_sendo_editado"}
        arquivo_temp = ARQUIVO_BACKUP + ".tmp"
        with open(arquivo_temp, "wb") as f:
            pickle.dump(dados, f)
        os.replace(arquivo_temp, ARQUIVO_BACKUP)  # Substituição segura a nível de S.O.
    except Exception:
        pass

def carregar_estado_do_disco():
    if os.path.exists(ARQUIVO_BACKUP):
        try:
            with open(ARQUIVO_BACKUP, "rb") as f:
                dados = pickle.load(f)
                for k, v in dados.items(): 
                    st.session_state[k] = v
                
                # SANEAMENTO CRÍTICO DE DADOS DOS COMPETIDORES
                if "jogadores" in st.session_state and st.session_state["jogadores"]:
                    lista_atualizada = []
                    import ast
                    for i, jog in enumerate(st.session_state["jogadores"]):
                        if isinstance(jog, str):
                            if "{" in jog and "'nome':" in jog:
                                try:
                                    d = ast.literal_eval(jog)
                                    if isinstance(d, dict):
                                        lista_atualizada.append({
                                            "id": d.get("id", i + 1),
                                            "nome": str(d.get("nome", "SEM NOME")).upper().strip(),
                                            "entidade": str(d.get("entidade", "AVULSO")).upper().strip()
                                        })
                                    else:
                                        lista_atualizada.append({"id": i + 1, "nome": str(jog).upper().strip(), "entidade": "AVULSO"})
                                except:
                                    lista_atualizada.append({"id": i + 1, "nome": jog.upper().strip(), "entidade": "AVULSO"})
                            else:
                                lista_atualizada.append({"id": i + 1, "nome": jog.upper().strip(), "entidade": "AVULSO"})
                        elif isinstance(jog, dict):
                            lista_atualizada.append({
                                "id": jog.get("id", i + 1),
                                "nome": str(jog.get("nome", "SEM NOME")).upper().strip(),
                                "entidade": str(jog.get("entidade", "AVULSO")).upper().strip()
                            })
                    st.session_state["jogadores"] = lista_atualizada
        except Exception:
            pass

def limpar_placares_memoria():
    st.session_state["placares_rodada_atual"] = {}
    st.session_state["semente_reset"] = st.session_state.get("semente_reset", 1) + 1

# Executa carga inicial segura
carregar_estado_do_disco()

# ==========================================
# PAINEL LATERAL - LIMPEZA DO EVENTO
# ==========================================
with st.sidebar:
    st.write("---")
    if st.button("🚨 ATUALIZAR BANCO DE DADOS (RESET)", use_container_width=True):
        for chave, valor_padrao in ESTADOS_INICIAIS.items():
            st.session_state[chave] = valor_padrao
        
        if os.path.exists(ARQUIVO_BACKUP):
            try: os.remove(ARQUIVO_BACKUP)
            except Exception: pass
                
        st.success("Banco de dados resetado com sucesso! Sistema pronto e limpo.")
        st.rerun()

# ==========================================
# RECALCULADOR MATRIZ E CHAVES (PARTE 2)
# ==========================================

def reconstruir_classificacao_global():
    """Gera novamente a tabela de classificação oficial limpando qualquer inconsistência"""
    # Extrai estritamente a string do nome único para evitar problemas de chaves no DataFrame
    nomes_jogadores = [j["nome"].strip().upper() for j in st.session_state["jogadores"] if isinstance(j, dict) and "nome" in j]
    
    st.session_state["classificacao"] = pd.DataFrame({
        'Jogador': nomes_jogadores, 'Vitorias': 0, 'Sets_Ganhos': 0, 
        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
    }).set_index('Jogador')
    
    for r_num, mesas in st.session_state["historico_rodadas"].items():
        for m_id, dados in mesas.items():
            if dados.get("is_chapeu", False):
                j1_dados = dados["j1"]
                j1_nome = (j1_dados["nome"] if isinstance(j1_dados, dict) else j1_dados).strip().upper()
                
                if j1_nome in st.session_state["classificacao"].index:
                    # Regra Oficial: Vitória por folga (Chapéu) concede placar padrão de 3 sets e 72 tentos pro
                    st.session_state["classificacao"].loc[j1_nome, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
            else:
                j1, j2 = dados["j1"], dados["j2"]
                j1_nome = (j1["nome"] if isinstance(j1, dict) else j1).strip().upper()
                j2_nome = (j2["nome"] if isinstance(j2, dict) else j2).strip().upper()
                
                s1, s2 = dados.get("s1", 0), dados.get("s2", 0)
                t1, t2 = dados.get("t1", 0), dados.get("t2", 0)
                f1, f2 = dados.get("f1", 0), dados.get("f2", 0)
                
                # Bonificação Oficial de Sets: Vitória por 2x0 conta como 3 sets ganhos para critérios de ranking
                s1_c = 3 if (s1 == 2 and s2 == 0) else s1
                s2_c = 3 if (s2 == 2 and s1 == 0) else s2
                v1, v2 = (1, 0) if s1 > s2 else (0, 1)
                
                if j1_nome in st.session_state["classificacao"].index:
                    st.session_state["classificacao"].loc[j1_nome, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v1, s1_c, t1, t2, f1]
                if j2_nome in st.session_state["classificacao"].index:
                    st.session_state["classificacao"].loc[j2_nome, ['Vitorias','Sets_Ganhos','Tentos_Pro','Tentos_Contra','Flores']] += [v2, s2_c, t2, t1, f2]
                
    # Recalcula o saldo absoluto e limpa a tabela para exibição estável
    st.session_state["classificacao"]['Saldo_Tentos'] = st.session_state["classificacao"]['Tentos_Pro'] - st.session_state["classificacao"]['Tentos_Contra']
    salvar_estado_no_disco()

def gerar_rodada_web():
    """Executa o emparceiramento oficial baseado no modelo Suíço de alta performance"""
    limpar_placares_memoria()
    
    if st.session_state["rodada_atual"] == 1:
        lista_rodada = list(st.session_state["jogadores"])
        random.shuffle(lista_rodada)
    else:
        # Ordenação oficial por critérios sucessivos: Vitórias -> Sets -> Saldo Tentos -> Flores
        df_ord = st.session_state["classificacao"].sort_values(
            by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos', 'Flores'], 
            ascending=False
        )
        mapa_jogadores = {j["nome"].strip().upper(): j for j in st.session_state["jogadores"] if isinstance(j, dict)}
        lista_rodada = [mapa_jogadores[nome] for nome in df_ord.index if nome in mapa_jogadores]

    st.session_state["confrontos"] = []
    
    # Gerenciamento Inteligente do Chapéu (Garante que ninguém repita folga)
    if len(lista_rodada) % 2 != 0:
        nomes_no_chapeu = {str(nome).strip().upper() for nome in st.session_state["jogadores_no_chapeu"]}
        cand = [j for j in lista_rodada if j["nome"].strip().upper() not in nomes_no_chapeu]
        
        chapeu = random.choice(cand if cand else lista_rodada)
        lista_rodada.remove(chapeu)
        
        st.session_state["jogadores_no_chapeu"].add(chapeu["nome"].strip().upper())
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
    
    if nome_fase == "FINAL E TERCEIRO": 
        return 

    n = len(lista_jogadores)
    for i in range(n // 2):
        id_m = str(i+1)
        st.session_state["confrontos_mm"].append({
            "id_original": id_m, "tipo": "normal", 
            "j1": lista_jogadores[i], "j2": lista_jogadores[n-1-i]
        })
        st.session_state["placares_rodada_atual"][id_m] = [0, 0, 0, 0, 0, 0, False]
        
    st.session_state["hora_inicio_rodada"] = None
    st.session_state["cronometro_ativo"] = False
    salvar_estado_no_disco()

def disparar_atualizacao_placar(m_str, j1, j2):
    """Callback seguro ativado a cada alteração de placar no painel do Diretor"""
    sem = st.session_state.get("semente_reset", 1)
    s1 = st.session_state.get(f"dir_s1_{m_str}_r{sem}", 0)
    s2 = st.session_state.get(f"dir_s2_{m_str}_r{sem}", 0)
    p_antigo = st.session_state["placares_rodada_atual"].get(m_str, [0, 0, 0, 0, 0, 0, False])
    
    # Tratamento automático de scores perfeitos (2x0 garante 72 tentos diretos)
    if (s1 == 2 and s2 == 0):
        t1, t2 = 72, min(st.session_state.get(f"dir_t2_{m_str}_r{sem}_2x0j1", p_antigo[3]), 46)
    elif (s2 == 2 and s1 == 0):
        t2, t1 = 72, min(st.session_state.get(f"dir_t1_{m_str}_r{sem}_2x0j2", p_antigo[2]), 46)
    else:
        # Garante resiliência contra strings ou entradas nulas em jogos terminados em 2x1
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
    # Resolução robusta de tipos para injeção segura no componente HTML
    j1_nome = j1["nome"].strip().upper() if isinstance(j1, dict) else str(j1).strip().upper()
    j1_entidade = j1["entidade"].strip().upper() if isinstance(j1, dict) else ""
    
    j2_nome = j2["nome"].strip().upper() if isinstance(j2, dict) else str(j2).strip().upper()
    j2_entidade = j2["entidade"].strip().upper() if isinstance(j2, dict) else ""

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
    
    j1_label = j1["nome"].strip().upper() if isinstance(j1, dict) else str(j1).strip().upper()
    j2_label = j2["nome"].strip().upper() if isinstance(j2, dict) else str(j2).strip().upper()
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown(f"<h4 class='titulo-passo-admin'>• SETS (Passo 1)</h4>", unsafe_allow_html=True)
        s1_in = st.number_input(f"Sets - {j1_label}", 0, 2, int(s1), key=f"dir_s1_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))
        s2_in = st.number_input(f"Sets - {j2_label}", 0, 2, int(s2), key=f"dir_s2_{m}_r{sem_id}", on_change=disparar_atualizacao_placar, args=(m, j1, j2))

    jogo_encerrado = (s1_in == 2 or s2_in == 2)
    
    with c2:
        if not jogo_encerrado:
            st.warning("Aguardando definição dos Sets...")
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
            else: 
                st.sidebar.error("Incorreta!")
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
            salvar_estado_no_disco()
            st.rerun()
        if st.button("⏹️ Pausar Cronômetro"):
            st.session_state["cronometro_ativo"] = False
            salvar_estado_no_disco()
            st.rerun()

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
                    j1_nome = j1["nome"].strip().upper() if isinstance(j1, dict) else str(j1).strip().upper()
                    st.markdown(f'<div class="chapeu-container-novo"><h3 style="color:#ffb703; margin:0;">🎩 FOLGA REGULAMENTAR (CHAPÉU): {j1_nome}</h3></div>', unsafe_allow_html=True)
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
            
            # Sub-Abas de Cadastro
            aba_cad_unico, aba_cad_massa = st.tabs(["👤 Cadastro Individual", "📋 Importar do Excel / Lista"])

            with aba_cad_unico:
                col_nj, col_ctg = st.columns([60, 40])
                with col_nj:
                    nj = st.text_input("Nome do Competidor:")
                with col_ctg:
                    nctg = st.text_input("Entidade / CTG (Opcional):")
                
                if st.button("➕ Cadastrar Competidor", type="secondary"):
                    if nj.strip():
                        nome_limpo = str(nj).upper().strip()
                        ctg_limpo = str(nctg).upper().strip() if nctg.strip() else "AVULSO"
                        
                        nomes_existentes = [j["nome"] for j in st.session_state["jogadores"]]
                        if nome_limpo not in nomes_existentes:
                            novo_id = len(st.session_state["jogadores"]) + 1
                            st.session_state["jogadores"].append({
                                "id": novo_id,
                                "nome": nome_limpo,
                                "entidade": ctg_limpo
                            })
                            salvar_estado_no_disco()
                            st.success(f"🔹 {nome_limpo} [{ctg_limpo}] cadastrado!")
                            st.rerun()
                        else:
                            st.warning("Este competidor já está cadastrado.")
                    else:
                        st.error("O nome do competidor não pode ficar vazio.")
                        
            with aba_cad_massa:
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

                st.markdown("""
                    <div style="background-color:#0d301b; border: 2px solid #ffb703; padding:15px; border-radius:10px; margin-bottom:15px;">
                        <h4 style="color:#ffb703; margin-top:0; margin-bottom:10px;">📋 Importação Rápida de Planilha</h4>
                        <p style="color:#ffffff; font-size:0.9rem; margin:0;">
                            💡 No seu Excel, selecione as colunas de <b>Nome</b> e <b>CTG</b>, copie (Ctrl+C) e cole no campo abaixo.<br>
                            O sistema aceita o formato contendo ponto e vírgula <b>Nome;CTG</b> ou apenas o <b>Nome</b> por linha.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Form isolado para garantir retenção de memória e sanitização de carriage returns (\r)
                with st.form("form_importacao_excel", clear_on_submit=True):
                    lista_colada = st.text_area("Dados Copiados do Excel:", height=150, placeholder="Exemplo:\nJOÃO SILVA;CTG SENTINELA\nPEDRO SOUZA;CTG FARROUPILHA")
                    botao_processar = st.form_submit_button("📥 Processar e Inserir Lista", type="primary")
                
                if botao_processar:
                    if lista_colada.strip():
                        linhas = lista_colada.replace("\r", "").split("\n")
                        cont_importados = 0
                        nomes_existentes = [str(j["nome"]).upper().strip() for j in st.session_state["jogadores"]]
                        
                        for linha in linhas:
                            linha_limpa = linha.strip()
                            if linha_limpa:
                                if ";" in linha_limpa:
                                    partes = linha_limpa.split(";")
                                    c_nome = str(partes[0]).upper().strip()
                                    c_ctg = str(partes[1]).upper().strip() if len(partes) > 1 and partes[1].strip() else "AVULSO"
                                else:
                                    c_nome = str(linha_limpa).upper().strip()
                                    c_ctg = "AVULSO"
                                    
                                if c_nome and c_nome not in nomes_existentes:
                                    novo_id = len(st.session_state["jogadores"]) + 1
                                    st.session_state["jogadores"].append({
                                        "id": novo_id,
                                        "nome": c_nome,
                                        "entidade": c_ctg
                                    })
                                    nomes_existentes.append(c_nome)
                                    cont_importados += 1
                        
                        if cont_importados > 0:
                            salvar_estado_no_disco()
                            st.toast(f"✔️ {cont_importados} novos competidores adicionados!", icon="🚀")
                            st.rerun()
                        else:
                            st.warning("Nenhum competidor novo ou inédito identificado na lista.")
                                    
            st.write(f"**Competidores Registrados ({len(st.session_state['jogadores'])}):**")
            
            if st.session_state["jogadores"]:
                df_jogadores = pd.DataFrame(st.session_state["jogadores"])[["id", "nome", "entidade"]]
                
                if is_admin:
                    st.info("💡 **Gerenciador Ativo:** Dê dois cliques em uma célula para editar o Nome/CTG. Selecione a linha clicando na lateral esquerda e aperte 'Delete' no teclado para excluir um competidor.")
                    
                    df_editado = st.data_editor(
                        df_jogadores,
                        column_config={
                            "id": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                            "nome": st.column_config.TextColumn("Nome do Competidor", required=True),
                            "entidade": st.column_config.TextColumn("Entidade / CTG"),
                        },
                        hide_index=True,
                        num_rows="dynamic",
                        use_container_width=True,
                        key="editor_competidores_tabela"
                    )
                    
                    lista_sincronizada = []
                    for idx, row in df_editado.iterrows():
                        if str(row["nome"]).strip():
                            lista_sincronizada.append({
                                "id": int(row["id"]) if pd.notna(row["id"]) else len(lista_sincronizada) + 1,
                                "nome": str(row["nome"]).upper().strip(),
                                "entidade": str(row["entidade"]).upper().strip() if pd.notna(row["entidade"]) and str(row["entidade"]).strip() else "AVULSO"
                            })
                    
                    if lista_sincronizada != st.session_state["jogadores"]:
                        st.session_state["jogadores"] = lista_sincronizada
                        salvar_estado_no_disco()
                        st.rerun()
                else: 
                    st.dataframe(df_jogadores, hide_index=True, use_container_width=True)
                
            if is_admin and len(st.session_state["jogadores"]) >= 4:
                st.markdown("---")
                st.markdown('<div class="botao-grande-comando">', unsafe_allow_html=True)
                if st.button("🃏 GERAR CHAVES E DISPARAR TORNEIO"):
                    st.session_state["nome_torneio"] = nome_t
                    
                    jogadores_limpos = [str(j["nome"]).upper().strip() for j in st.session_state["jogadores"]]
                    
                    st.session_state["classificacao"] = pd.DataFrame({
                        'Jogador': jogadores_limpos, 'Vitorias': 0, 'Sets_Ganhos': 0, 
                        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
                    }).set_index('Jogador')
                    
                    st.session_state["torneio_iniciado"] = True
                    gerar_rodada_web()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
# ==========================================
# ARENA DE CONFRONTOS E MATAMATA (PARTE 4)
# ==========================================
        else:
            # --- FUNÇÃO AUXILIAR PARA EVITAR QUEBRA DE TIPOS ---
            def obter_nome_limpo(objeto_jogador):
                if isinstance(objeto_jogador, dict):
                    return str(objeto_jogador.get("nome", "")).strip().upper()
                return str(objeto_jogador).strip().upper()

            st.markdown(f"### ⚔️ Rodada Atual: **{st.session_state['rodada_atual']}**")
            
            # Controle de abas internas na Arena quando o torneio está rodando
            if not st.session_state["em_matamata"]:
                st.info("📢 Os mesários/arbitragem podem atualizar os tentos em tempo real abaixo.")
                
                cont_m = 1
                for j1, j2 in st.session_state["confrontos"]:
                    nome_j1 = obter_nome_limpo(j1)
                    nome_j2 = obter_nome_limpo(j2)
                    
                    if nome_j2 == "CHAPÉU (FOLGA)":
                        st.markdown(f"""
                            <div class="chapeu-container-novo">
                                <h4 style="color:#ffb703; margin:0;">🎩 FOLGA REGULAMENTAR (CHAPÉU)</h4>
                                <p style="color:#ffffff; margin:5px 0 0 0; font-size:1.1rem;">O competidor <b>{nome_j1}</b> garantiu vitória automática nesta rodada.</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"#### 🎰 MESA {cont_m}")
                        p = st.session_state["placares_rodada_atual"].get(str(cont_m), [0, 0, 0, 0, 0, 0, False])
                        
                        # Layout de inputs para lançamento de tentos por Set
                        c_set1, c_set2, c_set3, c_status = st.columns([25, 25, 25, 25])
                        
                        with c_set1:
                            s1_j1 = st.number_input(f"1º Set - Tentos de {nome_j1}:", min_value=0, max_value=12, value=int(p[0]), key=f"s1_j1_{cont_m}")
                            s1_j2 = st.number_input(f"1º Set - Tentos de {nome_j2}:", min_value=0, max_value=12, value=int(p[1]), key=f"s1_j2_{cont_m}")
                        with c_set2:
                            s2_j1 = st.number_input(f"2º Set - Tentos de {nome_j1}:", min_value=0, max_value=12, value=int(p[2]), key=f"s2_j1_{cont_m}")
                            s2_j2 = st.number_input(f"2º Set - Tentos de {nome_j2}:", min_value=0, max_value=12, value=int(p[3]), key=f"s2_j2_{cont_m}")
                        with c_set3:
                            s3_j1 = st.number_input(f"3º Set - Tentos de {nome_j1}:", min_value=0, max_value=12, value=int(p[4]), key=f"s3_j1_{cont_m}")
                            s3_j2 = st.number_input(f"3º Set - Tentos de {nome_j2}:", min_value=0, max_value=12, value=int(p[5]), key=f"s3_j2_{cont_m}")
                        
                        with c_status:
                            st.write("**Situação da Mesa**")
                            mesa_finalizada = st.checkbox("Mesa Encerrada", value=bool(p[6]), key=f"encerrada_{cont_m}")
                        
                        # Detecta se houve mudança para persistir dados imediatamente no disco
                        novo_placar = [s1_j1, s1_j2, s2_j1, s2_j2, s3_j1, s3_j2, mesa_finalizada]
                        if st.session_state["placares_rodada_atual"].get(str(cont_m)) != novo_placar:
                            st.session_state["placares_rodada_atual"][str(cont_m)] = novo_placar
                            salvar_estado_no_disco()
                        
                        # Renderização visual da mesa abaixo dos inputs para conferência
                        desenhar_mesa_planta_baixa(j1, j2, str(cont_m), s1_j1, s2_j1, s3_j1, s1_j2, s2_j2, s3_j2, tipo_jogo="normal")
                        st.markdown("---")
                        cont_m += 1
                
                # Botão de Ação do Diretor para Computar Rodada
                if is_admin:
                    st.markdown('<div class="botao-grande-comando">', unsafe_allow_html=True)
                    if st.button("🏁 COMPUTAR RESULTADOS E AVANÇAR"):
                        todas_fechadas = True
                        for m in range(1, cont_m):
                            if not st.session_state["placares_rodada_atual"].get(str(m), [0,0,0,0,0,0,False])[6]:
                                todas_fechadas = False
                        
                        if not todas_fechadas:
                            st.error("⚠️ Não é possível avançar: Existem mesas ativas que ainda não foram marcadas como 'Mesa Encerrada'.")
                        else:
                            fechar_rodada_web()
                            st.success("Rodada processada e salva com sucesso!")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            else:
                # --- INTERFACE DE EXIBIÇÃO E ENTRADA DO MATA-MATA ---
                st.warning(f"🏆 FASE DE MATA-MATA ATIVA: **{st.session_state['fase_matamata']}**")
                
                for idx, c in enumerate(st.session_state["confrontos_mm"]):
                    id_mesa = c["id_original"]
                    nome_j1 = obter_nome_limpo(c["j1"])
                    nome_j2 = obter_nome_limpo(c["j2"])
                    tipo_partida = c["tipo"]
                    
                    st.markdown(f"#### 🥊 CONFRONTO OFICIAL — MESA {id_mesa} ({tipo_partida.upper()})")
                    p = st.session_state["placares_rodada_atual"].get(id_mesa, [0,0,0,0,0,0,False])
                    
                    c_s1, c_s2, c_s3, c_status = st.columns([25, 25, 25, 25])
                    with c_s1:
                        s1_j1 = st.number_input(f"1º Set - {nome_j1}:", min_value=0, max_value=12, value=int(p[0]), key=f"mm_s1_j1_{id_mesa}")
                        s1_j2 = st.number_input(f"1º Set - {nome_j2}:", min_value=0, max_value=12, value=int(p[1]), key=f"mm_s1_j2_{id_mesa}")
                    with c_s2:
                        s2_j1 = st.number_input(f"2º Set - {nome_j1}:", min_value=0, max_value=12, value=int(p[2]), key=f"mm_s2_j1_{id_mesa}")
                        s2_j2 = st.number_input(f"2º Set - {nome_j2}:", min_value=0, max_value=12, value=int(p[3]), key=f"mm_s2_j2_{id_mesa}")
                    with c_s3:
                        s3_j1 = st.number_input(f"3º Set - {nome_j1}:", min_value=0, max_value=12, value=int(p[4]), key=f"mm_s3_j1_{id_mesa}")
                        s3_j2 = st.number_input(f"3º Set - {nome_j2}:", min_value=0, max_value=12, value=int(p[5]), key=f"mm_s3_j2_{id_mesa}")
                    with c_status:
                        st.write("**Status**")
                        mesa_finalizada = st.checkbox("Encerrado", value=bool(p[6]), key=f"mm_encerrada_{id_mesa}")
                        
                    novo_placar_mm = [s1_j1, s1_j2, s2_j1, s2_j2, s3_j1, s3_j2, mesa_finalizada]
                    if st.session_state["placares_rodada_atual"].get(id_mesa) != novo_placar_mm:
                        st.session_state["placares_rodada_atual"][id_mesa] = novo_placar_mm
                        salvar_estado_no_disco()
                    
                    desenhar_mesa_planta_baixa(c["j1"], c["j2"], id_mesa, s1_j1, s2_j1, s3_j1, s1_j2, s2_j2, s3_j2, tipo_jogo=tipo_partida)
                    st.markdown("---")
                
                if is_admin:
                    st.markdown('<div class="botao-grande-comando">', unsafe_allow_html=True)
                    if st.button("🏆 COMPUTAR FASE DO MATA-MATA"):
                        todas_fechadas = all(st.session_state["placares_rodada_atual"].get(conf["id_original"], [0,0,0,0,0,0,False])[6] for conf in st.session_state["confrontos_mm"])
                        
                        if not todas_fechadas:
                            st.error("⚠️ Todas as mesas do mata-mata precisam estar encerradas antes de prosseguir.")
                        else:
                            fechar_fase_matamata_web()
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # --- ABAS DE CONSULTA PÚBLICA (CLASSIFICAÇÃO & HISTÓRICO) ---
    with aba_tabela:
        st.markdown("### 📊 Classificação Geral Impulsionada (Pontos Corridos)")
        if "classificacao" in st.session_state and st.session_state["classificacao"] is not None:
            dados_classif = st.session_state["classificacao"]
            
            # Tratamento híbrido: Aceita dicionário do JSON ou DataFrame ativo na memória
            if isinstance(dados_classif, dict):
                df_exibicao = pd.DataFrame.from_dict(dados_classif, orient='index') if dados_classif else pd.DataFrame()
            else:
                df_exibicao = dados_classif

            if not df_exibicao.empty:
                df_ordenado = df_exibicao.sort_values(
                    by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos', 'Tentos_Pro'], 
                    ascending=[False, False, False, False]
                )
                st.dataframe(df_ordenado, use_container_width=True)
            else:
                st.info("A tabela de classificação estará visível assim que a primeira rodada for disparada.")
        else:
            st.info("A tabela de classificação estará visível assim que a primeira rodada for disparada.")

    with aba_historico:
        st.markdown("### 📜 Galeria de Campeões e Auditoria")
        if st.session_state.get("historico_campeoes"):
            for podio in st.session_state["historico_campeoes"]:
                st.markdown(f"""
                    <div style="background-color:#0d301b; border: 2px solid #ffb703; padding:15px; border-radius:10px; margin-bottom:12px;">
                        <h4 style="color:#ffb703; margin:0 0 5px 0;">🏆 {podio['torneio']}</h4>
                        <p style="color:#ffffff; margin:3px 0;">🥇 <b>Campeão:</b> {podio['1º Lugar']}</p>
                        <p style="color:#ffffff; margin:3px 0;">🥈 <b>Vice-Campeão:</b> {podio['2º Lugar']}</p>
                        <p style="color:#ffffff; margin:3px 0;">🥉 <b>3º Colocado:</b> {podio['3º Lugar']}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum torneio finalizado gravado no histórico até o momento.")
