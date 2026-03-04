"""
Carrera de Caballos — Baraja Española
App Streamlit lista para desplegar en Render
"""
import base64, os
import streamlit as st
from src.game import CarreraEspanola, TRACK_LEN
from src.model import SUITS, RANK_NAMES, Card

# ── Rutas e imágenes ───────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(".")
PNG_DIR  = os.path.join(BASE_DIR, "assets", "png_cache")
SVG_KEYS = {"Oros": "coins", "Copas": "cups", "Espadas": "swords", "Bastos": "clubs"}

def _b64(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _card_png(card: Card, size: str) -> str:
    return os.path.join(PNG_DIR, f"card_{SVG_KEYS[card.suit]}_{card.rank:02d}.svg_{size}.png")

def _back_png(size: str) -> str:
    return os.path.join(PNG_DIR, f"card_back.svg_{size}.png")

def card_img_html(card: Card, size: str, width: int, border_color: str = "#3A3A55") -> str:
    b64 = _b64(_card_png(card, size))
    if b64:
        return (f'<img src="data:image/png;base64,{b64}" width="{width}" '
                f'style="border-radius:6px;border:2px solid {border_color};display:block">')
    sym   = SUIT_SYMBOLS.get(card.suit, "?")
    color = SUIT_COLORS.get(card.suit, "#fff")
    rname = RANK_NAMES.get(card.rank, str(card.rank))
    return (f'<div style="width:{width}px;background:#1A1A24;border:1px solid {border_color};'
            f'border-radius:6px;display:flex;flex-direction:column;align-items:center;'
            f'justify-content:center;padding:8px;box-sizing:border-box">'
            f'<div style="font-size:1.8rem;color:{color}">{sym}</div>'
            f'<div style="font-size:.75rem;color:{color}">{rname}</div></div>')

def back_img_html(size: str, width: int) -> str:
    b64 = _b64(_back_png(size))
    if b64:
        return (f'<img src="data:image/png;base64,{b64}" width="{width}" '
                f'style="border-radius:6px;border:1px solid #3A3A55;display:block">')
    return (f'<div style="width:{width}px;height:{int(width*1.4)}px;background:#1A1A24;'
            f'border:1px solid #3A3A55;border-radius:6px;display:flex;align-items:center;'
            f'justify-content:center;font-size:2rem;color:#2A2A3D">🂠</div>')

# ── Constantes visuales ────────────────────────────────────────────────────
SUIT_SYMBOLS = {"Oros": "◈", "Copas": "♥", "Espadas": "⚔", "Bastos": "⌘"}
SUIT_COLORS  = {
    "Oros":    "#D4A843",
    "Copas":   "#E53E5A",
    "Espadas": "#4F8EF7",
    "Bastos":  "#10B981",
}
PLAYER_COLORS = ["#E8C84A", "#E05C7A", "#5BA8F5", "#3DD68C"]
PLAYER_LABELS = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]
MEDALS        = ["🥇", "🥈", "🥉", "4️⃣"]

# ── Configuración de página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Carrera de Caballos",
    page_icon="🐴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    background-color: #0C0C0F !important;
    color: #F0EDE8 !important;
    font-family: 'EB Garamond', Georgia, serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 1400px !important; }

/* ── Título ── */
.race-title {
    font-family: 'Cinzel', serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #D4A843;
    letter-spacing: 0.15em;
    text-align: center;
    text-shadow: 0 0 30px rgba(212,168,67,0.35);
    margin: 0; padding: 0.4rem 0 0.1rem;
}
.race-subtitle {
    color: #9D9BB5; text-align: center;
    font-style: italic; font-size: 1rem; margin-bottom: 0.6rem;
}
.gold-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, #D4A843, transparent);
    margin: 0.3rem 0 1.2rem;
}

/* ── Sección ── */
.section-title {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    color: #D4A843;
    letter-spacing: 0.22em;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

/* ── Checkpoint ── */
.cp-card {
    background: #1A1A24;
    border: 1px solid #3A3A55;
    border-radius: 6px;
    min-height: 90px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 6px 4px;
    box-shadow: 3px 4px 10px rgba(0,0,0,0.5);
    position: relative;
}
.cp-card .cp-num {
    font-size: 0.58rem; color: #7A5E20;
    position: absolute; bottom: 4px;
}
.cp-suit-sym { font-size: 1.6rem; font-weight: bold; line-height: 1.1; }
.cp-rank     { font-size: 0.7rem; margin-top: 2px; }

/* ── Carril ── */
.lane-row {
    display: flex; align-items: center;
    background: #111118; border-radius: 5px;
    padding: 4px 6px; margin-bottom: 6px;
    gap: 2px;
}
.lane-label {
    min-width: 80px; display: flex; flex-direction: column;
    align-items: flex-end; padding-right: 8px;
}
.lane-cell {
    flex: 1; height: 40px;
    display: flex; align-items: center; justify-content: center;
    border-right: 1px solid #1E1E2C;
    font-size: 0.6rem; color: #2A2A3D;
    position: relative;
}
.lane-cell:last-child { border-right: 3px solid #D4A843; }
.lane-cell.horse { font-size: 1.4rem; }
.lane-cell.meta  { font-size: 0.5rem; color: #D4A843;
                   font-family: 'Cinzel',serif; letter-spacing: 0.08em; }

/* ── Carta actual ── */
.card-display {
    background: #1A1A24;
    border: 1px solid #3A3A55;
    border-radius: 10px;
    padding: 1.4rem 1rem;
    text-align: center;
    min-height: 160px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}
.card-sym-big { font-size: 3.2rem; line-height: 1; margin-bottom: 0.3rem; }
.card-name    { font-size: 1.1rem; font-weight: 600; color: #F0EDE8; }
.card-suit-name { font-size: 0.85rem; font-style: italic; color: #9D9BB5; }

/* ── Panel jugador ── */
.player-card {
    background: #1A1A24; border-radius: 8px;
    padding: 0.7rem 0.9rem; margin-bottom: 0.6rem;
    border-left: 4px solid;
}
.progress-bar-bg {
    background: #2A2A3D; border-radius: 4px;
    height: 8px; overflow: hidden;
}
.progress-bar-fill { height: 8px; border-radius: 4px; }

/* ── Log ── */
.log-box {
    background: #1A1A24; border: 1px solid #2A2A3D;
    border-radius: 6px; padding: 0.8rem;
    height: 240px; overflow-y: auto;
    font-family: 'Courier New', monospace; font-size: 0.8rem;
}
.log-entry   { padding: 1px 0; border-bottom: 1px solid #13131A; }
.log-header  { color: #D4A843; font-weight: 600; }
.log-event   { color: #9D9BB5; }
.log-cp      { color: #4F8EF7; }
.log-penalty { color: #E53E5A; }
.log-winner  { color: #10B981; font-weight: 700; }

/* ── Botones ── */
.stButton > button {
    background: #D4A843 !important; color: #0C0C0F !important;
    font-family: 'Cinzel', serif !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; border: none !important;
    border-radius: 4px !important; padding: 0.6rem 1.5rem !important;
}
.stButton > button:hover { background: #F0C96A !important; }
.btn-sec > button {
    background: #1E1E2C !important; color: #9D9BB5 !important;
}
.btn-sec > button:hover {
    background: #2A2A3D !important; color: #F0EDE8 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #13131A !important;
    border-right: 1px solid #2A2A3D !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p { color: #9D9BB5 !important; }
div[data-baseweb="select"] > div {
    background-color: #1A1A24 !important;
    border-color: #3A3A55 !important; color: #F0EDE8 !important;
}
input[type="text"] {
    background-color: #1A1A24 !important;
    border-color: #3A3A55 !important; color: #F0EDE8 !important;
}

/* ── Banner ganador ── */
.winner-banner {
    background: linear-gradient(135deg,#1A1A24,#0F0F18);
    border: 2px solid #D4A843; border-radius: 12px;
    padding: 1.8rem; text-align: center; margin-bottom: 1rem;
}
.winner-title {
    font-family: 'Cinzel', serif; color: #D4A843;
    font-size: 0.9rem; letter-spacing: 0.3em; margin-bottom: 0.4rem;
}
.winner-name  { font-family: 'Cinzel', serif; font-size: 2.2rem; font-weight: 900; }
.winner-horse { font-size: 1.1rem; color: #9D9BB5; font-style: italic; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# Estado de sesión
# ══════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "game":           None,
        "players":        [],
        "suit_to_player": {},
        "log":            [],
        "last_card":      None,
        "setup_done":     False,
        "game_over":      False,
        "winner_suit":    None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ══════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════
def add_log(msg: str, tag: str = "event"):
    st.session_state.log.append((msg, tag))


def progress_html(pos: int, color: str) -> str:
    pct = int(pos / TRACK_LEN * 100)
    return (f'<div class="progress-bar-bg">'
            f'<div class="progress-bar-fill" style="width:{pct}%;background:{color}"></div>'
            f'</div>'
            f'<div style="font-size:0.75rem;color:#5A5875;margin-top:2px">{pos} / {TRACK_LEN}</div>')


# ══════════════════════════════════════════════════════════════════════════
# Sidebar — configuración de partida
# ══════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="section-title">⚑ NUEVA PARTIDA</div>',
                    unsafe_allow_html=True)

        n_players = st.radio("Jugadores", [2, 3, 4], horizontal=True,
                             key="sb_npl")
        n_horses  = st.radio("Caballos", [3, 4], horizontal=True,
                             key="sb_nh",
                             help="Con 3 caballos, uno queda fuera de la carrera")

        st.markdown('<div class="section-title" style="margin-top:1rem">JUGADORES</div>',
                    unsafe_allow_html=True)

        players_cfg = []
        used_suits  = []
        valid       = True

        for i in range(n_players):
            color = PLAYER_COLORS[i]
            st.markdown(
                f'<span style="color:{color};font-family:Cinzel,serif;'
                f'font-size:0.8rem;font-weight:700">◆ J{i+1}</span>',
                unsafe_allow_html=True)

            name = st.text_input("Nombre", value=PLAYER_LABELS[i],
                                 key=f"sb_name_{i}",
                                 label_visibility="collapsed")

            available = [s for s in SUITS if s not in used_suits]
            if not available:
                st.warning("No hay palos disponibles")
                valid = False
                break

            suit = st.selectbox("Caballo", available,
                                key=f"sb_suit_{i}",
                                label_visibility="collapsed")
            used_suits.append(suit)
            players_cfg.append({
                "name":  name.strip() or PLAYER_LABELS[i],
                "suit":  suit,
                "color": color,
            })

        st.markdown("---")

        if valid:
            if st.button("⚑  INICIAR CARRERA", use_container_width=True):
                _start_game(players_cfg, n_horses)
                st.rerun()

        if st.session_state.setup_done:
            st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
            if st.button("↺  Reiniciar partida", use_container_width=True):
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


def _start_game(players_cfg: list, n_horses: int):
    chosen_suits = [p["suit"] for p in players_cfg]

    if n_horses == 4:
        active_suits = set(SUITS)
    else:
        active_suits = set(chosen_suits)
        for s in SUITS:
            if len(active_suits) >= 3:
                break
            active_suits.add(s)

    game = CarreraEspanola()
    game.reset(active_suits=active_suits)

    st.session_state.game           = game
    st.session_state.players        = players_cfg
    st.session_state.suit_to_player = {p["suit"]: p for p in players_cfg}
    st.session_state.log            = []
    st.session_state.last_card      = None
    st.session_state.setup_done     = True
    st.session_state.game_over      = False
    st.session_state.winner_suit    = None

    add_log(f"Partida iniciada — Caballos: {', '.join(sorted(active_suits))}", "header")
    for p in players_cfg:
        sym = SUIT_SYMBOLS.get(p["suit"], "")
        add_log(f"  {sym} {p['suit']}  ←  {p['name']}", "event")


# ══════════════════════════════════════════════════════════════════════════
# Tablero — Checkpoints
# ══════════════════════════════════════════════════════════════════════════
def render_checkpoints(game: CarreraEspanola):
    st.markdown('<div class="section-title">CHECKPOINTS</div>',
                unsafe_allow_html=True)
    cols = st.columns(TRACK_LEN)
    for i in range(TRACK_LEN):
        with cols[i]:
            if game.revealed[i]:
                card  = game.checkpoints[i]
                color = SUIT_COLORS.get(card.suit, "#fff")
                img   = card_img_html(card, "88x124", 80, color + "99")
            else:
                img = back_img_html("88x124", 80)

            st.markdown(
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px">'
                f'{img}'
                f'<div style="font-size:0.6rem;color:#7A5E20;font-family:Cinzel,serif">{i+1}</div>'
                f'</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# Tablero — Carriles
# ══════════════════════════════════════════════════════════════════════════
def render_lanes(game: CarreraEspanola, suit_to_player: dict):
    st.markdown('<div class="section-title" style="margin-top:1.2rem">CARRILES</div>',
                unsafe_allow_html=True)

    active_suits = [s for s in SUITS if s in game.active_suits]

    for suit in active_suits:
        color = SUIT_COLORS[suit]
        sym   = SUIT_SYMBOLS[suit]
        pos   = game.positions.get(suit, 0)
        owner = suit_to_player.get(suit)

        owner_html = (
            f'<span style="color:{owner["color"]};font-size:0.72rem;font-style:italic">'
            f'← {owner["name"]}</span>'
            if owner else
            '<span style="color:#3A3A55;font-size:0.7rem;font-style:italic">sin dueño</span>'
        )

        label_col, *cell_cols = st.columns([1.2] + [1] * (TRACK_LEN + 1))

        with label_col:
            st.markdown(
                f'<div style="text-align:right;padding-right:6px;line-height:1.3">'
                f'<span style="color:{color};font-size:1.3rem;font-weight:bold">{sym}</span><br>'
                f'<span style="color:{color};font-size:0.8rem;font-weight:600">{suit}</span><br>'
                f'{owner_html}</div>',
                unsafe_allow_html=True)

        for p, col in enumerate(cell_cols):
            with col:
                is_horse = (p == pos)
                is_meta  = (p == TRACK_LEN)

                if is_horse and not is_meta:
                    horse_card = Card(rank=11, suit=suit)
                    b64 = _b64(_card_png(horse_card, "64x90"))
                    if b64:
                        content = (f'<img src="data:image/png;base64,{b64}" width="34" '
                                   f'style="border-radius:4px;display:block">')
                    else:
                        content = f'<div style="font-size:1.4rem">{sym}</div>'
                    bg = f"background:{color}33"
                elif is_meta:
                    bg      = f"background:{color}22;border-left:3px solid {color}"
                    content = f'<div style="font-size:0.5rem;color:{color};font-family:Cinzel,serif">META</div>'
                else:
                    bg      = ""
                    content = f'<div style="color:#2A2A3D;font-size:0.58rem">{p}</div>'

                st.markdown(
                    f'<div style="height:44px;display:flex;align-items:center;'
                    f'justify-content:center;border-right:1px solid #1E1E2C;'
                    f'border-radius:3px;{bg}">{content}</div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# Panel lateral — Jugadores
# ══════════════════════════════════════════════════════════════════════════
def render_players_panel(game: CarreraEspanola, players: list):
    st.markdown('<div class="section-title">JUGADORES</div>',
                unsafe_allow_html=True)
    positions  = game.positions
    leader_pos = max(positions.values()) if positions else 0

    for p in players:
        suit  = p["suit"]
        color = p["color"]
        sym   = SUIT_SYMBOLS.get(suit, "")
        sc    = SUIT_COLORS.get(suit, "#fff")
        pos   = positions.get(suit, 0)
        glow  = f"box-shadow:0 0 10px {color}44;" if pos == leader_pos and pos > 0 else ""
        bw    = "4px" if pos == leader_pos and pos > 0 else "3px"

        st.markdown(f"""
        <div class="player-card" style="border-left:{bw} solid {color};{glow}">
            <div style="font-size:1rem;font-weight:700;color:{color}">{p['name']}</div>
            <div style="font-size:0.8rem;color:#9D9BB5;margin-bottom:4px">
                {sym} <span style="color:{sc}">{suit}</span>
            </div>
            {progress_html(pos, color)}
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# Panel lateral — Última carta
# ══════════════════════════════════════════════════════════════════════════
def render_last_card(card):
    st.markdown('<div class="section-title">ÚLTIMA CARTA</div>',
                unsafe_allow_html=True)
    if card is None:
        st.markdown(
            f'<div style="text-align:center">{back_img_html("240x340", 180)}</div>',
            unsafe_allow_html=True)
        return

    color = SUIT_COLORS.get(card.suit, "#fff")
    rname = RANK_NAMES.get(card.rank, str(card.rank))
    img   = card_img_html(card, "240x340", 180, color + "99")

    st.markdown(
        f'<div style="text-align:center">{img}'
        f'<div style="font-size:1rem;font-weight:600;color:#F0EDE8;margin-top:6px">'
        f'{rname} de {card.suit}</div></div>',
        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# Panel lateral — Registro
# ══════════════════════════════════════════════════════════════════════════
def render_log(log_entries: list):
    st.markdown('<div class="section-title" style="margin-top:1rem">REGISTRO</div>',
                unsafe_allow_html=True)

    tag_cls = {
        "header":  "log-header",
        "event":   "log-event",
        "cp":      "log-cp",
        "penalty": "log-penalty",
        "winner":  "log-winner",
    }
    rows = "".join(
        f'<div class="log-entry {tag_cls.get(t,"log-event")}">{m}</div>'
        for m, t in reversed(log_entries[-50:])
    )
    st.markdown(f'<div class="log-box">{rows}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# Banner ganador
# ══════════════════════════════════════════════════════════════════════════
def render_winner_banner(winner_suit: str, game: CarreraEspanola,
                         players: list, suit_to_player: dict):
    color   = SUIT_COLORS.get(winner_suit, "#fff")
    sym     = SUIT_SYMBOLS.get(winner_suit, "")
    owner   = suit_to_player.get(winner_suit)
    name    = owner["name"] if owner else winner_suit
    p_color = owner["color"] if owner else color

    st.markdown(f"""
    <div class="winner-banner">
        <div class="winner-title">★ CARRERA FINALIZADA ★</div>
        <div class="winner-name" style="color:{p_color}">{name}</div>
        <div class="winner-horse" style="color:{color}">{sym}  {winner_suit}</div>
    </div>""", unsafe_allow_html=True)

    if players:
        st.markdown('<div class="section-title">CLASIFICACIÓN FINAL</div>',
                    unsafe_allow_html=True)
        sorted_p = sorted(players,
                          key=lambda p: game.positions.get(p["suit"], 0),
                          reverse=True)
        for rank, p in enumerate(sorted_p):
            pos   = game.positions.get(p["suit"], 0)
            sym_p = SUIT_SYMBOLS.get(p["suit"], "")
            sc    = SUIT_COLORS.get(p["suit"], "#fff")
            medal = MEDALS[rank] if rank < len(MEDALS) else f"{rank+1}."
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:5px 8px;
                 background:#1A1A24;border-radius:6px;margin-bottom:4px">
                <span style="font-size:1.1rem">{medal}</span>
                <span style="color:{p['color']};font-weight:700">{p['name']}</span>
                <span style="color:{sc};font-size:0.85rem">{sym_p} {p['suit']}</span>
                <span style="color:#5A5875;font-size:0.82rem;margin-left:auto">
                    casilla {pos}
                </span>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# Acción: voltear carta
# ══════════════════════════════════════════════════════════════════════════
def do_step():
    game           = st.session_state.game
    suit_to_player = st.session_state.suit_to_player

    try:
        info = game.step()
    except Exception as e:
        st.error(str(e))
        return

    st.session_state.last_card = info.drawn
    sym = SUIT_SYMBOLS.get(info.drawn.suit, "")

    if info.advanced_suit:
        owner  = suit_to_player.get(info.advanced_suit)
        suffix = f" ({owner['name']})" if owner else ""
        add_log(f"  {sym} {info.drawn.name}  →  avanza {info.advanced_suit}{suffix}", "event")
    else:
        add_log(f"  {info.drawn.name}  →  (palo inactivo)", "event")

    if info.revealed_checkpoint_index is not None and info.revealed_card is not None:
        idx = info.revealed_checkpoint_index + 1
        add_log(f"  ◉ Checkpoint #{idx}: {info.revealed_card.name}", "cp")
        if info.penalty_suit:
            owner  = suit_to_player.get(info.penalty_suit)
            suffix = f" ({owner['name']})" if owner else ""
            add_log(f"  ⚠ Penalidad: {info.penalty_suit}{suffix} retrocede 1", "penalty")

    if info.winner:
        owner = suit_to_player.get(info.winner)
        wsym  = SUIT_SYMBOLS.get(info.winner, "")
        if owner:
            add_log(f"  ★ GANADOR: {wsym} {info.winner}  ←  {owner['name']}", "winner")
        else:
            add_log(f"  ★ GANADOR: {wsym} {info.winner}", "winner")
        st.session_state.game_over  = True
        st.session_state.winner_suit = info.winner


# ══════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════
def main():
    render_sidebar()

    st.markdown('<div class="race-title">⚑ CARRERA DE CABALLOS</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="race-subtitle">Baraja Española · 40 cartas</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)

    if not st.session_state.setup_done:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#5A5875">
            <div style="font-size:4rem;margin-bottom:1rem">🐴</div>
            <div style="font-family:Cinzel,serif;font-size:1.1rem;color:#7A5E20;
                 letter-spacing:0.1em">
                Configura la partida en el panel izquierdo
            </div>
        </div>""", unsafe_allow_html=True)
        return

    game           = st.session_state.game
    players        = st.session_state.players
    suit_to_player = st.session_state.suit_to_player

    col_board, col_side = st.columns([3, 1], gap="large")

    with col_board:
        if st.session_state.game_over:
            render_winner_banner(
                st.session_state.winner_suit, game, players, suit_to_player)

        render_checkpoints(game)
        render_lanes(game, suit_to_player)

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        if not st.session_state.game_over:
            if st.button("▶  VOLTEAR CARTA", use_container_width=False):
                do_step()
                st.rerun()
        else:
            st.info("🏁 Carrera finalizada — inicia una nueva desde el panel izquierdo")

    with col_side:
        render_players_panel(game, players)
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        render_last_card(st.session_state.last_card)
        render_log(st.session_state.log)


if __name__ == "__main__":
    main()