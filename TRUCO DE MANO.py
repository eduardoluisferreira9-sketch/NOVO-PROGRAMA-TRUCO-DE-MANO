import streamlit as st
import pandas as pd
import random
import os
import json
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ==========================================
# CONFIGURAÇÕES INICIAIS E BACKUP
# ==========================================
CHAVE_ADMINISTRADOR = "TRUCO2026"  # Chave Master para o Diretor
ARQUIVO_BANCO_DADOS = "banco_torneio_truco.json"

st.set_page_config(page_title="Sistema de Gerenciamento de Truco", layout="wide")

def salvar_estado_no_disco():
    """Garante a persistência segura dos dados do torneio eliminando objetos complexos"""
    estado_copia = {}
    for chave, valor in st.session_state.items():
        if chave == "classificacao" and valor is not None:
            if isinstance(valor, pd.DataFrame):
                estado_copia[chave] = valor.to_dict(orient='index')
            else:
                estado_copia[chave] = valor
        elif chave == "jogadores_no_chapeu":
            estado_copia[chave] = list(valor)
        elif chave in ["hora_inicio_rodada"] and isinstance(valor, datetime):
            estado_copia[chave] = valor.isoformat()
        else:
            estado_copia[chave] = valor
    
    with open(ARQUIVO_BANCO_DADOS, "w", encoding="utf-8") as f:
        json.dump(estado_copia, f, ensure_ascii=False, indent=4)

def carregar_estado_do_disco():
    """Restaura o estado do torneio hidratando as coleções do Streamlit"""
    if os.path.exists(ARQUIVO_BANCO_DADOS):
        try:
            with open(ARQUIVO_BANCO_DADOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
            for chave, valor in dados.items():
                if chave == "classificacao" and valor is not None:
                    st.session_state[chave] = pd.DataFrame.from_dict(valor, orient='index')
                elif chave == "jogadores_no_chapeu":
                    st.session_state[chave] = set(valor)
                elif chave == "hora_inicio_rodada" and valor:
                    st.session_state[chave] = datetime.fromisoformat(valor)
                else:
                    st.session_state[chave] = valor
        except Exception:
            pass

# Inicialização de Estados Mandatórios
valores_padrao = {
    "jogadores": [],
    "torneio_iniciado": False,
    "rodada_atual": 1,
    "historico_rodadas": {},
    "placares_rodada_atual": {},
    "confrontos": [],
    "jogadores_no_chapeu": set(),
    "classificacao": None,
    "admin_logado": False,
    "cronometro_ativo": False,
    "hora_inicio_rodada": None,
    "em_matamata": False,
    "fase_matamata": "",
    "confrontos_mm": [],
    "historico_campeoes": [],
    "nome_torneio": "Torneio de Truco",
    "semente_reset": 1
}

for k, v in valores_padrao.items():
    if k not in st.session_state:
        st.session_state[k] = v

carregar_estado_do_disco()

def limpar_placares_memoria():
    st.session_state["placares_rodada_atual"] = {}

# ==========================================
# RECALCULADOR MATRIZ E CHAVES (PARTE 2)
# ==========================================

def reconstruir_classificacao_global():
    """Gera novamente a tabela de classificação oficial limpando qualquer inconsistência"""
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
                    st.session_state["classificacao"].loc[j1_nome, ['Vitorias', 'Sets_Ganhos', 'Tentos_Pro']] += [1, 3, 72]
            else:
                j1, j2 = dados["j1"], dados["j2"]
                j1_nome = (j1["nome"] if isinstance(j1, dict) else j1).strip().upper()
                j2_nome = (j2["nome"] if isinstance(j2, dict) else j2).strip().upper()
                
                s1, s2 = dados.get("s1", 0), dados.get("s2", 0)
                t1, t2 = dados.get("t1", 0), dados.get("t2", 0)
                f1, f2 = dados.get("f1", 0), dados.get("f2", 0)
                
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
    """Executa o emparceiramento oficial baseado no modelo Suíço de alta performance"""
    limpar_placares_memoria()
    
    if st.session_state["rodada_atual"] == 1:
        lista_rodada = list(st.session_state["jogadores"])
        random.shuffle(lista_rodada)
    else:
        df_ord = st.session_state["classificacao"].sort_values(
            by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos', 'Flores'], 
            ascending=False
        )
        mapa_jogadores = {j["nome"].strip().upper(): j for j in st.session_state["jogadores"] if isinstance(j, dict)}
        lista_rodada = [mapa_jogadores[nome] for nome in df_ord.index if nome in mapa_jogadores]

    st.session_state["confrontos"] = []
    
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

def fechar_rodada_web():
    """Fecha a rodada suíça e consolida no histórico de rodadas"""
    r_atual = str(st.session_state["rodada_atual"])
    st.session_state["historico_rodadas"][r_atual] = {}
    
    cont_m = 1
    for j1, j2 in st.session_state["confrontos"]:
        if j2 == "CHAPÉU (Folga)":
            st.session_state["historico_rodadas"][r_atual][f"chapeu_{cont_m}"] = {
                "j1": j1, "j2": "CHAPÉU (Folga)", "is_chapeu": True
            }
        else:
            p = st.session_state["placares_rodada_atual"].get(str(cont_m), [0,0,0,0,0,0,False])
            # No modelo simplificado por set da arena, o saldo real é consolidado
            # Se J1 ganhou mais sets, s1 recebe 2, etc. Para critérios de ranking:
            tot_sets_j1 = (1 if p[0]>p[1] else 0) + (1 if p[2]>p[3] else 0) + (1 if p[4]>p[5] and (p[0]!=0 or p[2]!=0) else 0)
            tot_sets_j2 = (1 if p[1]>p[0] else 0) + (1 if p[3]>p[2] else 0) + (1 if p[5]>p[4] and (p[0]!=0 or p[2]!=0) else 0)
            
            s1_final = 2 if tot_sets_j1 > tot_sets_j2 else (1 if tot_sets_j1 == tot_sets_j2 else 0)
            s2_final = 2 if tot_sets_j2 > tot_sets_j1 else (1 if tot_sets_j2 == tot_sets_j1 else 0)
            
            t1_final = p[0] + p[2] + p[4]
            t2_final = p[1] + p[3] + p[5]
            
            st.session_state["historico_rodadas"][r_atual][str(cont_m)] = {
                "j1": j1, "j2": j2, "s1": s1_final, "s2": s2_final,
                "t1": t1_final, "t2": t2_final, "f1": 0, "f2": 0, "is_chapeu": False
            }
            cont_m += 1
            
    reconstruir_classificacao_global()
    st.session_state["rodada_atual"] += 1
    gerar_rodada_web()

def fechar_fase_matamata_web():
    """Conclui a rodada eliminatória vigente"""
    passaportes = []
    eliminados = []
    
    # Avaliação simples dos vencedores baseados no somatório de sets da mesa
    for c in st.session_state["confrontos_mm"]:
        p = st.session_state["placares_rodada_atual"].get(c["id_original"], [0,0,0,0,0,0,False])
        sets_j1 = (1 if p[0]>p[1] else 0) + (1 if p[2]>p[3] else 0) + (1 if p[4]>p[5] else 0)
        sets_j2 = (1 if p[1]>p[0] else 0) + (1 if p[3]>p[2] else 0) + (1 if p[5]>p[4] else 0)
        
        if sets_j1 > sets_j2:
            passaportes.append(c["j1"])
            eliminados.append(c["j2"])
        else:
            passaportes.append(c["j2"])
            eliminados.append(c["j1"])
            
    f_atual = st.session_state["fase_matamata"]
    if f_atual == "QUARTAS DE FINAL":
        iniciar_fase_matamata(passaportes, "SEMIFINAL")
    elif f_atual == "SEMIFINAL":
        limpar_placares_memoria()
        st.session_state["fase_matamata"] = "FINAL E TERCEIRO"
        st.session_state["confrontos_mm"] = [
            {"id_original": "1", "tipo": "final", "j1": passaportes[0], "j2": passaportes[1]},
            {"id_original": "2", "tipo": "3place", "j1": eliminados[0], "j2": eliminados[1]}
        ]
        st.session_state["placares_rodada_atual"]["1"] = [0,0,0,0,0,0,False]
        st.session_state["placares_rodada_atual"]["2"] = [0,0,0,0,0,0,False]
        salvar_estado_no_disco()
    elif f_atual == "FINAL E TERCEIRO":
        p_f = st.session_state["placares_rodada_atual"].get("1", [0,0,0,0,0,0,False])
        p_3 = st.session_state["placares_rodada_atual"].get("2", [0,0,0,0,0,0,False])
        
        sf1 = (1 if p_f[0]>p_f[1] else 0) + (1 if p_f[2]>p_f[3] else 0) + (1 if p_f[4]>p_f[5] else 0)
        sf2 = (1 if p_f[1]>p_f[0] else 0) + (1 if p_f[3]>p_f[2] else 0) + (1 if p_f[5]>p_f[4] else 0)
        
        st3_1 = (1 if p_3[0]>p_3[1] else 0) + (1 if p_3[2]>p_3[3] else 0) + (1 if p_3[4]>p_3[5] else 0)
        st3_2 = (1 if p_3[1]>p_3[0] else 0) + (1 if p_3[3]>p_3[2] else 0) + (1 if p_3[5]>p_3[4] else 0)
        
        c1 = st.session_state["confrontos_mm"][0]
        c2 = st.session_state["confrontos_mm"][1]
        
        campeao = c1["j1"] if sf1 > sf2 else c1["j2"]
        vice = c1["j2"] if sf1 > sf2 else c1["j1"]
        terceiro = c2["j1"] if st3_1 > st3_2 else c2["j2"]
        
        def limpar_nome_p(j):
            return j["nome"] if isinstance(j, dict) else str(j)

        st.session_state["historico_campeoes"].append({
            "torneio": st.session_state["nome_torneio"],
            "1º Lugar": limpar_nome_p(campeao),
            "2º Lugar": limpar_nome_p(vice),
            "3º Lugar": limpar_nome_p(terceiro)
        })
        st.session_state["torneio_iniciado"] = False
        st.session_state["em_matamata"] = False
        salvar_estado_no_disco()

def desenhar_mesa_planta_baixa(j1, j2, mesa_num, s1, t1, f1, s2, t2, f2, tipo_jogo="normal"):
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
    elif (s1 == 2 or s2 == 2 or f1 == 12 or f2 == 12):
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

# ==========================================
# SIDEBAR E CONTEXTO DE VISUALIZAÇÃO (PARTE 3)
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Painel do Diretor")
    if not st.session_state["admin_logado"]:
        senha = st.text_input("Chave Master:", type="password", key="diretor_senha_master")
        if st.button("🔓 Autenticar", key="diretor_btn_autenticar"):
            if senha == CHAVE_ADMINISTRADOR:
                st.session_state["admin_logado"] = True
                st.rerun()
            else: 
                st.sidebar.error("Incorreta!")
    else:
        st.success("⚡ Modo Diretor Ativo")
        if st.button("🔒 Sair do Modo Adm", key="diretor_btn_deslogar"):
            st.session_state["admin_logado"] = False
            st.rerun()
            
    is_admin = st.session_state["admin_logado"]
    st.markdown("---")
    
    if is_admin:
        if st.button("⏱️ Iniciar Cronômetro (45m)", key="diretor_btn_start_crono"):
            st.session_state["hora_inicio_rodada"] = datetime.now()
            st.session_state["cronometro_ativo"] = True
            salvar_estado_no_disco()
            st.rerun()
        if st.button("⏹️ Pausar Cronômetro", key="diretor_btn_stop_crono"):
            st.session_state["cronometro_active"] = False
            salvar_estado_no_disco()
            st.rerun()
            
        st.markdown("---")
        st.markdown("### ⚠️ Zona de Perigo")
        if st.button("🚨 RESETAR TODO O TORNEIO", type="primary", use_container_width=True, key="diretor_btn_danger_reset"):
            st.session_state["jogadores"] = []
            st.session_state["torneio_iniciado"] = False
            st.session_state["cronometro_ativo"] = False
            st.session_state["hora_inicio_rodada"] = None
            st.session_state["em_matamata"] = False
            st.session_state["rodada_atual"] = 1
            st.session_state["jogadores_no_chapeu"] = set()
            st.session_state["historico_rodadas"] = {}
            st.session_state["placares_rodada_atual"] = {}
            st.session_state["confrontos"] = []
            st.session_state["classificacao"] = None
            st.session_state["semente_reset"] += 1
            salvar_estado_no_disco()
            st.rerun()

# --- INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align:center; color:#ffb703; font-weight:900; margin-top:0;'>🃏 {st.session_state.get('nome_torneio', 'Torneio de Truco')}</h1>", unsafe_allow_html=True)

modo_exibicao = st.radio("Selecione o Modo de Visualização da Tela:", ["Arena de Gerenciamento", "🖥️ MODO TELÃO DE PROJETOR (Automático)"], horizontal=True, key="seletor_modo_exibicao")

if modo_exibicao == "🖥️ MODO TELÃO DE PROJETOR (Automático)":
    st.markdown("<h2 style='text-align:center; color:#ffb703; margin-bottom:20px;'>📺 QUADRO OFICIAL DE CONFRONTOS</h2>", unsafe_allow_html=True)
    
    if st.session_state["cronometro_ativo"] and st.session_state["hora_inicio_rodada"]:
        tl = st.session_state["hora_inicio_rodada"] + timedelta(minutes=45)
        tr = tl - datetime.now()
        if tr.total_seconds() > 0:
            st.markdown(f'<div class="cronometro-box-gigante"><span style="color:#ffffff; font-size:1.1rem; font-weight:bold; text-transform:uppercase; letter-spacing:2px; display:block; margin-bottom:5px;">⏱️ Tempo Restante de Jogo</span><div class="cronometro-tempo">{int(tr.total_seconds()//60):02d}:{int(tr.total_seconds()%60):02d}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cronometro-box-gigante" style="border-color:#ff3232;"><div class="cronometro-tempo" style="color:#ff3232 !important;">⏰ TEMPO ESGOTADO</div></div>', unsafe_allow_html=True)
    
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
            nome_t = st.text_input("Nome do Evento:", value=st.session_state["nome_torneio"], key="nome_torneio_input")
            
            abas_internas = ["👤 Cadastro Unificado", "📋 Importar Lista/Excel"]
            if is_admin:
                abas_internas.extend(["✏️ Editar Competidor", "❌ Excluir Competidor"])
                
            abas_cadastro = st.tabs(abas_internas)

            # --- ABA 1: CADASTRO UNIFICADO ---
            with abas_cadastro[0]:
                if is_admin:
                    st.caption("⚡ Você está cadastrando como Administrador")
                else:
                    st.caption("👋 Bem-vindo! Digite seus dados abaixo para se inscrever no torneio.")
                    
                col_nj, col_ctg = st.columns([60, 40])
                with col_nj:
                    nj = st.text_input("Nome do Competidor:", key="input_cad_unico_nome")
                with col_ctg:
                    nctg = st.text_input("Entidade / CTG (Opcional):", key="input_cad_unico_ctg")
                
                if st.button("➕ Confirmar Inscrição", type="secondary", key="btn_cad_individual"):
                    if nj.strip():
                        nome_limpo = str(nj).upper().strip()
                        ctg_limpo = str(nctg).upper().strip() if nctg.strip() else "AVULSO"
                        
                        nomes_existentes = [j["nome"] for j in st.session_state["jogadores"]]
                        if nome_limpo not in nomes_existentes:
                            novo_id = len(st.session_state["jogadores"]) + 1
                            st.session_state["jogadores"].append({
                                "id": novo_id, "nome": nome_limpo, "entidade": ctg_limpo
                            })
                            salvar_estado_no_disco()
                            st.success(f"🎉 {nome_limpo} de [{ctg_limpo}] foi inscrito com sucesso!")
                            st.rerun()
                        else:
                            st.warning("Este competidor já está cadastrado.")
                    else:
                        st.error("O nome do competidor não pode ficar vazio.")
                        
            # --- ABA 2: IMPORTAR EXCEL ---
            with abas_cadastro[1]:
                st.info("💡 Cole as colunas de Nome e CTG vindas do seu Excel. Aceita formato 'Nome;CTG' ou um nome por linha.")
                lista_colada = st.text_area("Dados Copiados:", height=120, placeholder="JOÃO SILVA;CTG SENTINELA\nPEDRO SOUZA;AVULSO", key="txt_area_excel_direto")
                
                if st.button("📥 Processar e Inserir Lista", type="primary", key="btn_processar_excel_direto"):
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
                                        "id": novo_id, "nome": c_nome, "entidade": c_ctg
                                    })
                                    nomes_existentes.append(c_nome)
                                    cont_importados += 1
                        
                        if cont_importados > 0:
                            salvar_estado_no_disco()
                            st.success(f"✔️ {cont_importados} competidores importados!")
                            st.rerun()

            if is_admin:
                # --- ABA 3: EDITAR JOGADOR ---
                with abas_cadastro[2]:
                    if st.session_state["jogadores"]:
                        opcoes_edicao = {f"{j['nome']} [{j['entidade']}]": j for j in st.session_state["jogadores"]}
                        selecionado_edicao = st.selectbox("Selecione quem deseja modificar:", list(opcoes_edicao.keys()), key="sb_editar_jogador")
                        jogador_alvo = opcoes_edicao[selecionado_edicao]
                        
                        col_ed_n, col_ed_c = st.columns([60, 40])
                        with col_ed_n:
                            novo_nome_input = st.text_input("Corrigir Nome:", value=jogador_alvo["nome"], key="edit_nome_field")
                        with col_ed_c:
                            nova_ent_input = st.text_input("Corrigir Entidade:", value=jogador_alvo["entidade"], key="edit_ent_field")
                            
                        if st.button("💾 Salvar Alterações", type="primary", key="btn_salvar_edicao"):
                            if novo_nome_input.strip():
                                for j in st.session_state["jogadores"]:
                                    if j["id"] == jogador_alvo["id"]:
                                        j["nome"] = str(novo_nome_input).upper().strip()
                                        j["entidade"] = str(nova_ent_input).upper().strip() if nova_ent_input.strip() else "AVULSO"
                                salvar_estado_no_disco()
                                st.success("Alterações salvas!")
                                st.rerun()
                    else:
                        st.info("Nenhum competidor registrado para editar.")

                # --- ABA 4: EXCLUIR JOGADOR ---
                with abas_cadastro[3]:
                    if st.session_state["jogadores"]:
                        opcoes_exclusao = {f"{j['nome']} [{j['entidade']}]": j for j in st.session_state["jogadores"]}
                        selecionado_exclusao = st.selectbox("Selecione quem deseja remover do torneio:", list(opcoes_exclusao.keys()), key="sb_deletar_jogador")
                        jogador_remover = opcoes_exclusao[selecionado_exclusao]
                        
                        st.warning(f"⚠️ Tem certeza que deseja remover permanentemente {jogador_remover['nome']}?")
                        if st.button("❌ Confirmar Exclusão", type="primary", key="btn_confirmar_exclusao"):
                            st.session_state["jogadores"] = [j for j in st.session_state["jogadores"] if j["id"] != jogador_remover["id"]]
                            for idx, j in enumerate(st.session_state["jogadores"]):
                                j["id"] = idx + 1
                            salvar_estado_no_disco()
                            st.success("Competidor removido com sucesso!")
                            st.rerun()
                    else:
                        st.info("Nenhum competidor registrado para excluir.")

            st.markdown("---")
            st.write(f"### 📋 Lista de Inscritos Registrados ({len(st.session_state['jogadores'])}):")
            if st.session_state["jogadores"]:
                for j in st.session_state["jogadores"]:
                    st.markdown(f"**{j['id']}.** {j['nome']} — *{j['entidade']}*")
            else:
                st.info("Nenhum competidor inscrito até o momento.")
                
            if is_admin and len(st.session_state["jogadores"]) >= 4:
                st.markdown("---")
                if st.button("🃏 GERAR CHAVES E DISPARAR TORNEIO", key="btn_disparar_torneio"):
                    st.session_state["nome_torneio"] = nome_t
                    jogadores_limpos = [str(j["nome"]).upper().strip() for j in st.session_state["jogadores"]]
                    st.session_state["classificacao"] = pd.DataFrame({
                        'Jogador': jogadores_limpos, 'Vitorias': 0, 'Sets_Ganhos': 0, 
                        'Tentos_Pro': 0, 'Tentos_Contra': 0, 'Saldo_Tentos': 0, 'Flores': 0
                    }).set_index('Jogador')
                    st.session_state["torneio_iniciado"] = True
                    gerar_rodada_web()
                    st.rerun()
        
        # ==========================================
        # ARENA DE CONFRONTOS E MATAMATA (PARTE 4)
        # ==========================================
        else:
            def obter_nome_limpo(objeto_jogador):
                if isinstance(objeto_jogador, dict):
                    return str(objeto_jogador.get("nome", "")).strip().upper()
                return str(objeto_jogador).strip().upper()

            sem_id = st.session_state.get("semente_reset", 1)

            if not st.session_state["em_matamata"]:
                st.markdown(f"### ⚔️ Rodada Atual: **{st.session_state['rodada_atual']}**")
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
                        
                        c_set1, c_set2, c_set3, c_status = st.columns([25, 25, 25, 25])
                        with c_set1:
                            s1_j1 = st.number_input(f"1º Set - Tentos de {nome_j1}:", min_value=0, max_value=12, value=int(p[0]), key=f"s1_j1_{cont_m}_r{sem_id}")
                            s1_j2 = st.number_input(f"1º Set - Tentos de {nome_j2}:", min_value=0, max_value=12, value=int(p[1]), key=f"s1_j2_{cont_m}_r{sem_id}")
                        with c_set2:
                            s2_j1 = st.number_input(f"2º Set - Tentos de {nome_j1}:", min_value=0, max_value=12, value=int(p[2]), key=f"s2_j1_{cont_m}_r{sem_id}")
                            s2_j2 = st.number_input(f"2º Set - Tentos de {nome_j2}:", min_value=0, max_value=12, value=int(p[3]), key=f"s2_j2_{cont_m}_r{sem_id}")
                        with c_set3:
                            s3_j1 = st.number_input(f"3º Set - Tentos de {nome_j1}:", min_value=0, max_value=12, value=int(p[4]), key=f"s3_j1_{cont_m}_r{sem_id}")
                            s3_j2 = st.number_input(f"3º Set - Tentos de {nome_j2}:", min_value=0, max_value=12, value=int(p[5]), key=f"s3_j2_{cont_m}_r{sem_id}")
                        with c_status:
                            st.write("**Situação da Mesa**")
                            mesa_finalizada = st.checkbox("Mesa Encerrada", value=bool(p[6]), key=f"encerrada_{cont_m}_r{sem_id}")
                        
                        novo_placar = [s1_j1, s1_j2, s2_j1, s2_j2, s3_j1, s3_j2, mesa_finalizada]
                        if st.session_state["placares_rodada_atual"].get(str(cont_m)) != novo_placar:
                            st.session_state["placares_rodada_atual"][str(cont_m)] = novo_placar
                            salvar_estado_no_disco()
                        
                        desenhar_mesa_planta_baixa(j1, j2, str(cont_m), s1_j1, s2_j1, s3_j1, s1_j2, s2_j2, s3_j2, tipo_jogo="normal")
                        st.markdown("---")
                        cont_m += 1
                
                if is_admin:
                    if st.button("🏁 COMPUTAR RESULTADOS E AVANÇAR", key="btn_computar_suico_avancar"):
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
                            
                # Botão adicional ativado para o Diretor migrar para eliminatórias
                if is_admin and st.session_state["rodada_atual"] >= 3:
                    st.markdown("### 🛑 Encerrar Fase de Classificação")
                    if st.button("🏆 ENTRAR NO MATA-MATA (Top 8)", key="btn_trigger_matamata_quartas"):
                        df_class = st.session_state["classificacao"].sort_values(by=['Vitorias', 'Sets_Ganhos', 'Saldo_Tentos'], ascending=False)
                        mapa_jogadores = {j["nome"].strip().upper(): j for j in st.session_state["jogadores"]}
                        top_8 = [mapa_jogadores[nome] for nome in df_class.index[:8] if nome in mapa_jogadores]
                        iniciar_fase_matamata(top_8, "QUARTAS DE FINAL")
                        st.rerun()
            else:
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
                        s1_j1 = st.number_input(f"1º Set - {nome_j1}:", min_value=0, max_value=12, value=int(p[0]), key=f"mm_s1_j1_{id_mesa}_r{sem_id}")
                        s1_j2 = st.number_input(f"1º Set - {nome_j2}:", min_value=0, max_value=12, value=int(p[1]), key=f"mm_s1_j2_{id_mesa}_r{sem_id}")
                    with c_s2:
                        s2_j1 = st.number_input(f"2º Set - {nome_j1}:", min_value=0, max_value=12, value=int(p[2]), key=f"mm_s2_j1_{id_mesa}_r{sem_id}")
                        s2_j2 = st.number_input(f"2º Set - {nome_j2}:", min_value=0, max_value=12, value=int(p[3]), key=f"mm_s2_j2_{id_mesa}_r{sem_id}")
                    with c_s3:
                        s3_j1 = st.number_input(f"3º Set - {nome_j1}:", min_value=0, max_value=12, value=int(p[4]), key=f"mm_s3_j1_{id_mesa}_r{sem_id}")
                        s3_j2 = st.number_input(f"3º Set - {nome_j2}:", min_value=0, max_value=12, value=int(p[5]), key=f"mm_s3_j2_{id_mesa}_r{sem_id}")
                    with c_status:
                        st.write("**Status**")
                        mesa_finalizada = st.checkbox("Encerrado", value=bool(p[6]), key=f"mm_encerrada_{id_mesa}_r{sem_id}")
                        
                    novo_placar_mm = [s1_j1, s1_j2, s2_j1, s2_j2, s3_j1, s3_j2, mesa_finalizada]
                    if st.session_state["placares_rodada_atual"].get(id_mesa) != novo_placar_mm:
                        st.session_state["placares_rodada_atual"][id_mesa] = novo_placar_mm
                        salvar_estado_no_disco()
                    
                    desenhar_mesa_planta_baixa(c["j1"], c["j2"], id_mesa, s1_j1, s2_j1, s3_j1, s1_j2, s2_j2, s3_j2, tipo_jogo=tipo_partida)
                    st.markdown("---")
                
                if is_admin:
                    if st.button("🏆 COMPUTAR FASE DO MATA-MATA", key="btn_computar_matamata_fase"):
                        todas_fechadas = all(st.session_state["placares_rodada_atual"].get(conf["id_original"], [0,0,0,0,0,0,False])[6] for conf in st.session_state["confrontos_mm"])
                        
                        if not todas_fechadas:
                            st.error("⚠️ Todas as mesas do mata-mata precisam estar encerradas antes de prosseguir.")
                        else:
                            fechar_fase_matamata_web()
                            st.rerun()

    # --- ABAS DE CONSULTA PÚBLICA ---
    with aba_tabela:
        st.markdown("### 📊 Classificação Geral Impulsionada (Pontos Corridos)")
        if "classificacao" in st.session_state and st.session_state["classificacao"] is not None:
            dados_classif = st.session_state["classificacao"]
            
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
