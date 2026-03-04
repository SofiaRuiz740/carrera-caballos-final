# app.py
import os
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Ajusta imports según tu estructura.
# Si app.py está al nivel del paquete, puede ser:
# from game import CarreraEspanola, TRACK_LEN
# from model import SUITS, Card
# Si app.py está dentro del paquete (mismo nivel que __init__.py), puede ser:
from src.game import CarreraEspanola, TRACK_LEN
from src.model import SUITS, Card


# ============================================================
# PALETA (igual que tu Tkinter)
# ============================================================
C_BG         = "#0C0C0F"
C_SURFACE    = "#13131A"
C_PANEL      = "#1A1A24"
C_PANEL2     = "#22222F"
C_BORDER     = "#2A2A3D"
C_BORDER2    = "#3A3A55"
C_GOLD       = "#D4A843"
C_GOLD_LIGHT = "#F0C96A"
C_GOLD_DIM   = "#7A5E20"
C_EMERALD    = "#10B981"
C_CRIMSON    = "#E53E5A"
C_SAPPHIRE   = "#4F8EF7"
C_TEXT       = "#F0EDE8"
C_TEXT2      = "#9D9BB5"
C_TEXT3      = "#5A5875"
C_BTN        = "#1E1E2C"
C_BTN_H      = "#2A2A3D"
C_CANVAS     = "#0A0A0D"
C_LANE       = "#141420"

SUIT_COLORS = {
    "Oros":    "#D4A843",
    "Copas":   "#E53E5A",
    "Espadas": "#4F8EF7",
    "Bastos":  "#10B981",
}
SUIT_SYMBOLS = {
    "Oros":    "◈",
    "Copas":   "♥",
    "Espadas": "⚔",
    "Bastos":  "⌘",
}
SVG_SUIT_KEY = {
    "Oros": "coins", "Copas": "cups",
    "Espadas": "swords", "Bastos": "clubs",
}

PLAYER_COLORS = ["#E8C84A", "#E05C7A", "#5BA8F5", "#3DD68C"]
PLAYER_LABELS = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]


def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _blend(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return (f"#{int(r1+(r2-r1)*t):02x}"
            f"{int(g1+(g2-g1)*t):02x}"
            f"{int(b1+(b2-b1)*t):02x}")


# ============================================================
# Estado / utilidades
# ============================================================
@dataclass
class PlayerCfg:
    name: str
    suit: str
    color: str

@dataclass
class StepInfoLite:
    drawn_name: str
    drawn_suit: str
    advanced_suit: Optional[str]
    revealed_checkpoint_index: Optional[int]
    revealed_card_name: Optional[str]
    penalty_suit: Optional[str]
    winner: Optional[str]


def _root_dir() -> str:
    # Similar a tu Tkinter: root_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.dirname(os.path.dirname(__file__))

def _assets_dirs() -> Tuple[str, str]:
    rd = _root_dir()
    svg_dir = os.path.join(rd, "assets", "svg")
    png_cache_dir = os.path.join(rd, "assets", "png_cache")
    os.makedirs(png_cache_dir, exist_ok=True)
    return svg_dir, png_cache_dir


def _svg_name(card: Card) -> str:
    return f"card_{SVG_SUIT_KEY[card.suit]}_{card.rank:02d}.svg"

def _svg_to_png(svg_path: str, png_path: str, size: Tuple[int, int]) -> None:
    w, h = size
    drawing = svg2rlg(svg_path)
    if drawing.width and drawing.height:
        sx, sy = w / drawing.width, h / drawing.height
        drawing.scale(sx, sy)
        drawing.width, drawing.height = w, h
    renderPM.drawToFile(drawing, png_path, fmt="PNG")

def _get_pil_from_svg(svg_filename: str, size: Tuple[int, int]) -> Optional[Image.Image]:
    svg_dir, png_cache_dir = _assets_dirs()
    svg_path = os.path.join(svg_dir, svg_filename)
    if not os.path.exists(svg_path):
        return None

    w, h = size
    key = f"{svg_filename}_{w}x{h}"
    cache: Dict[str, Image.Image] = st.session_state.setdefault("pil_img_cache", {})

    if key in cache:
        return cache[key]

    png_path = os.path.join(png_cache_dir, f"{key}.png")
    if not os.path.exists(png_path):
        _svg_to_png(svg_path, png_path, size)

    img = Image.open(png_path).convert("RGBA")
    cache[key] = img
    return img

def _get_card_pil(card: Card, size: Tuple[int, int]) -> Optional[Image.Image]:
    return _get_pil_from_svg(_svg_name(card), size)

def _get_back_pil(size: Tuple[int, int]) -> Optional[Image.Image]:
    p = _get_pil_from_svg("card_back.svg", size)
    return p or _get_pil_from_svg("back.svg", size)


def _ensure_game():
    if "game" not in st.session_state:
        st.session_state.game = CarreraEspanola()
    if "players" not in st.session_state:
        st.session_state.players: List[PlayerCfg] = []
    if "suit_to_player" not in st.session_state:
        st.session_state.suit_to_player = {}
    if "log" not in st.session_state:
        st.session_state.log = []
    if "last_card" not in st.session_state:
        st.session_state.last_card = None  # Card
    if "status" not in st.session_state:
        st.session_state.status = "Presiona “Voltear carta”"


def _log(msg: str):
    st.session_state.log.append(msg)

def _reset_match(active_suits: set, players: List[PlayerCfg]):
    st.session_state.game.reset(active_suits=active_suits)
    st.session_state.players = players
    st.session_state.suit_to_player = {p.suit: {"name": p.name, "color": p.color, "suit": p.suit} for p in players}
    st.session_state.log = []
    st.session_state.last_card = None
    active_str = ", ".join(sorted(st.session_state.game.active_suits))
    _log(f"▸ Partida iniciada — Caballos: {active_str}")
    for p in players:
        sym = SUIT_SYMBOLS.get(p.suit, "")
        _log(f"  {sym} {p.suit}  ←  {p.name}")


# ============================================================
# Render tablero (PIL)
# ============================================================
def _draw_board_image(
    width: int = 980,
    height: int = 640,
    cp_size: Tuple[int, int] = (88, 124),
    horse_size: Tuple[int, int] = (64, 90),
) -> Image.Image:
    game: CarreraEspanola = st.session_state.game

    img = Image.new("RGBA", (width, height), _hex_to_rgb(C_CANVAS) + (255,))
    draw = ImageDraw.Draw(img)

    # Fonts (fallback a default)
    try:
        font_hdr = ImageFont.truetype("DejaVuSans.ttf", 16)
        font_sm  = ImageFont.truetype("DejaVuSans.ttf", 12)
        font_xs  = ImageFont.truetype("DejaVuSans.ttf", 11)
    except Exception:
        font_hdr = ImageFont.load_default()
        font_sm  = ImageFont.load_default()
        font_xs  = ImageFont.load_default()

    pad = 32
    label_w = 96
    cp_y = 120
    cp_w, cp_h = cp_size
    half_cp = cp_w // 2
    cp_x0 = pad + label_w + half_cp
    usable_w = width - cp_x0 - pad - half_cp
    cp_gap = int(usable_w / max(TRACK_LEN - 1, 1))

    def pos_to_x(pos: int) -> int:
        x0 = cp_x0
        x1 = cp_x0 + cp_gap * (TRACK_LEN - 1) + cp_w // 2
        step = (x1 - x0) / TRACK_LEN
        return int(x0 + pos * step)

    lanes_y0 = cp_y + cp_h // 2 + 72
    active_suits = [s for s in SUITS if s in game.active_suits]
    lane_gap = max(80, int((height - lanes_y0 - 28) / max(len(active_suits), 1)))

    # Headers
    draw.text((pad, 10), "CHECKPOINTS", fill=_hex_to_rgb(C_GOLD), font=font_hdr)
    draw.text((pad + 160, 12),
              "— se revelan cuando todos los caballos superan la posición",
              fill=_hex_to_rgb(C_TEXT3), font=font_xs)

    # Checkpoints row
    back = _get_back_pil(cp_size)
    for i in range(TRACK_LEN):
        x = cp_x0 + i * cp_gap
        y = cp_y

        # slot
        draw.rectangle((x-half_cp+5, y-cp_h//2+6, x+half_cp+5, y+cp_h//2+6), fill=_hex_to_rgb("#06060A"))
        draw.rectangle((x-half_cp-4, y-cp_h//2-4, x+half_cp+4, y+cp_h//2+4), outline=_hex_to_rgb(C_GOLD_DIM), width=1)
        draw.rectangle((x-half_cp, y-cp_h//2, x+half_cp, y+cp_h//2), outline=_hex_to_rgb(C_BORDER2), width=1, fill=_hex_to_rgb(C_PANEL))

        # number
        draw.text((x-4, y+cp_h//2+8), str(i+1), fill=_hex_to_rgb(C_GOLD_DIM), font=font_xs, anchor="mt")

        # card image or placeholder
        if game.revealed[i]:
            c = game.checkpoints[i]
            card_img = _get_card_pil(c, cp_size)
            if card_img:
                img.alpha_composite(card_img, (x-half_cp, y-cp_h//2))
            else:
                draw.text((x, y), c.short(), fill=_hex_to_rgb(C_TEXT), font=font_sm, anchor="mm")
        else:
            if back:
                img.alpha_composite(back, (x-half_cp, y-cp_h//2))
            else:
                draw.text((x, y), "?", fill=_hex_to_rgb(C_TEXT), font=font_sm, anchor="mm")

    # Separator
    sep_y = cp_y + cp_h // 2 + 28
    draw.line((pad, sep_y, width - pad, sep_y), fill=_hex_to_rgb(C_BORDER), width=1)

    # Lanes header
    lane_hdr_y = lanes_y0 - 34
    draw.text((pad, lane_hdr_y), "CARRILES", fill=_hex_to_rgb(C_GOLD), font=font_hdr)
    draw.text((pad + 110, lane_hdr_y + 2), "— avanza con cada carta del palo",
              fill=_hex_to_rgb(C_TEXT3), font=font_xs)

    label_x = pad + label_w
    track_x0 = pos_to_x(0)
    track_x1 = pos_to_x(TRACK_LEN)

    # Bands + lanes
    for idx, suit in enumerate(active_suits):
        y = lanes_y0 + idx * lane_gap
        band_fill = C_LANE if idx % 2 == 0 else _blend(C_LANE, "#000000", 0.3)
        draw.rectangle((label_x, y - lane_gap//2 + 2, width - pad, y + lane_gap//2 - 2),
                       fill=_hex_to_rgb(band_fill))

    # Finish line
    mx = track_x1
    lane_top = lanes_y0 - lane_gap//2 + 2
    lane_bottom = lanes_y0 + (len(active_suits)-1)*lane_gap + lane_gap//2 - 2 if active_suits else lanes_y0 + lane_gap//2
    draw.rectangle((mx-4, lane_top, mx+4, lane_bottom), fill=_hex_to_rgb(C_GOLD))
    draw.text((mx, lane_top - 16), "META", fill=_hex_to_rgb(C_GOLD_LIGHT), font=font_sm, anchor="mm")

    # Draw each lane lines, ticks, labels, horse token
    for idx, suit in enumerate(active_suits):
        y = lanes_y0 + idx * lane_gap
        color = SUIT_COLORS[suit]
        sym = SUIT_SYMBOLS[suit]

        # main line
        draw.line((track_x0, y, mx, y), fill=_hex_to_rgb(_blend(color, "#000000", 0.65)), width=2)

        # ticks
        for p in range(TRACK_LEN + 1):
            tx = pos_to_x(p)
            tick_color = C_GOLD_DIM if p == TRACK_LEN else C_BORDER2
            draw.line((tx, y-20, tx, y+20), fill=_hex_to_rgb(tick_color), width=1)

        # labels on left
        lx = label_x - 8
        draw.text((lx, y-12), sym, fill=_hex_to_rgb(color), font=font_hdr, anchor="rm")
        draw.text((lx, y+8), suit, fill=_hex_to_rgb(_blend(color, C_TEXT3, 0.35)), font=font_xs, anchor="rm")

        owner = st.session_state.suit_to_player.get(suit)
        if owner:
            draw.text((lx, y+22), owner["name"], fill=_hex_to_rgb(owner["color"]), font=font_xs, anchor="rm")

        # horse
        pos = st.session_state.game.positions.get(suit, 0)
        hx = pos_to_x(pos) - horse_size[0]//2
        hy = y - horse_size[1]//2
        horse_card = Card(rank=11, suit=suit)
        horse_img = _get_card_pil(horse_card, horse_size)
        if horse_img:
            img.alpha_composite(horse_img, (hx, hy))
        else:
            # fallback circle
            r = 22
            cx = pos_to_x(pos)
            draw.ellipse((cx-r, y-r, cx+r, y+r),
                         fill=_hex_to_rgb(_blend(color, "#000000", 0.55)),
                         outline=_hex_to_rgb(color), width=2)
            draw.text((cx, y), sym, fill=_hex_to_rgb(color), font=font_sm, anchor="mm")

    return img


# ============================================================
# UI (Streamlit)
# ============================================================
def _inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {C_BG};
            color: {C_TEXT};
        }}
        div[data-testid="stSidebar"] {{
            background: {C_SURFACE};
        }}
        .topbar {{
            background: {C_SURFACE};
            border-top: 3px solid {C_GOLD};
            border-bottom: 1px solid {C_GOLD_DIM};
            padding: 14px 18px;
            border-radius: 14px;
        }}
        .pill {{
            display:inline-block;
            background:{C_PANEL};
            color:{C_TEXT2};
            padding:6px 12px;
            border-radius: 999px;
            margin-left: 12px;
            font-style: italic;
            border: 1px solid {C_BORDER};
        }}
        .card {{
            background:{C_PANEL};
            border: 1px solid {C_BORDER2};
            border-radius: 14px;
            padding: 14px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _setup_sidebar():
    st.sidebar.markdown(f"### ⚑ Carrera de Caballos\n<span style='color:{C_TEXT3}'>Baraja Española</span>", unsafe_allow_html=True)
    st.sidebar.divider()

    with st.sidebar.expander("Nueva partida", expanded=("configured" not in st.session_state)):
        n_players = st.radio("Jugadores", [2, 3, 4], horizontal=True, key="ui_n_players")
        n_horses = st.radio("Caballos en carrera", [3, 4], horizontal=True, key="ui_n_horses")

        # Inputs por jugador
        names = []
        suits = []
        for i in range(4):
            if i >= n_players:
                continue
            c = PLAYER_COLORS[i]
            st.markdown(f"<div style='margin-top:8px;color:{c};font-weight:700'>Jugador {i+1}</div>", unsafe_allow_html=True)
            name = st.text_input("Nombre", value=PLAYER_LABELS[i], key=f"ui_name_{i}")
            suit = st.selectbox("Caballo (palo)", SUITS, index=i % len(SUITS), key=f"ui_suit_{i}")
            names.append(name.strip() or PLAYER_LABELS[i])
            suits.append(suit)

        # Validaciones iguales
        dupes = len(suits) != len(set(suits))
        invalid_3horses = (n_horses == 3 and n_players > 3)

        if dupes:
            st.warning("⚠ Dos jugadores no pueden elegir el mismo caballo.")
        if invalid_3horses:
            st.warning("⚠ Con 3 caballos puede haber máximo 3 jugadores.")

        can_start = (not dupes) and (not invalid_3horses)

        if st.button("⚑ INICIAR CARRERA", type="primary", disabled=not can_start):
            players = [
                PlayerCfg(name=names[i], suit=suits[i], color=PLAYER_COLORS[i])
                for i in range(n_players)
            ]

            if n_horses == 4:
                active_suits = set(SUITS)
            else:
                active_suits = set(suits)
                for s in SUITS:
                    if len(active_suits) >= 3:
                        break
                    active_suits.add(s)

            _reset_match(active_suits=active_suits, players=players)
            st.session_state.configured = True
            st.session_state.status = "Nueva partida lista — presiona “Voltear carta”"
            st.rerun()

    st.sidebar.divider()

    # Panel jugadores + caballos (en sidebar, estilo similar)
    if st.session_state.get("configured"):
        st.sidebar.markdown("#### Jugadores en carrera")
        game: CarreraEspanola = st.session_state.game
        players: List[PlayerCfg] = st.session_state.players

        # jugadores
        leader = max(game.positions.values()) if game.positions else 0
        for p in players:
            pos = game.positions.get(p.suit, 0)
            sym = SUIT_SYMBOLS.get(p.suit, "")
            st.sidebar.markdown(
                f"""
                <div class="card" style="border-left:6px solid {p.color}; margin-bottom:10px;">
                  <div style="font-weight:800; color:{p.color}; font-size:16px;">
                    {p.name}
                    <span style="color:{SUIT_COLORS.get(p.suit, C_TEXT)}; font-weight:700;">
                      &nbsp; {sym} {p.suit}
                    </span>
                  </div>
                  <div style="color:{C_TEXT3}; font-size:12px; margin-top:6px;">
                    {pos} / {TRACK_LEN}
                    {"<span style='color:"+C_GOLD_LIGHT+"; font-weight:800;'>&nbsp;— líder</span>" if (pos==leader and pos>0) else ""}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.sidebar.progress(pos / TRACK_LEN)

        st.sidebar.markdown("#### Todos los caballos")
        for suit in SUITS:
            if suit not in game.active_suits:
                continue
            pos = game.positions.get(suit, 0)
            owner = st.session_state.suit_to_player.get(suit)
            owner_txt = f"← {owner['name']}" if owner else "Sin dueño"
            owner_color = owner["color"] if owner else C_TEXT3
            st.sidebar.markdown(
                f"<div style='display:flex; align-items:center; gap:8px;'>"
                f"<div style='width:24px; color:{SUIT_COLORS[suit]}; font-size:18px; font-weight:900;'>{SUIT_SYMBOLS[suit]}</div>"
                f"<div style='width:78px; color:{SUIT_COLORS[suit]}; font-weight:800;'>{suit}</div>"
                f"<div style='color:{C_TEXT3}; width:26px;'>{pos}</div>"
                f"<div style='color:{owner_color}; font-style:italic; font-size:12px;'>{owner_txt}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.sidebar.progress(pos / TRACK_LEN)


def _step_game():
    game: CarreraEspanola = st.session_state.game
    info = game.step()  # usa tu lógica original

    st.session_state.last_card = info.drawn
    sym = SUIT_SYMBOLS.get(info.drawn.suit, "")
    st.session_state.status = f"{sym}  {info.drawn.name}"

    if info.advanced_suit:
        owner = st.session_state.suit_to_player.get(info.advanced_suit)
        suffix = f" ({owner['name']})" if owner else ""
        _log(f"  {sym} {info.drawn.name}  →  avanza {info.advanced_suit}{suffix}")
    else:
        _log(f"  {info.drawn.name}  →  (palo inactivo)")

    if info.revealed_checkpoint_index is not None and info.revealed_card is not None:
        idx = info.revealed_checkpoint_index + 1
        _log(f"  ◉ Checkpoint #{idx} revelado: {info.revealed_card.name}")
        if info.penalty_suit:
            owner = st.session_state.suit_to_player.get(info.penalty_suit)
            suffix = f" ({owner['name']})" if owner else ""
            _log(f"  ⚠ Penalidad: {info.penalty_suit}{suffix} retrocede 1 casilla")

    if info.winner:
        _log("  ★ CARRERA FINALIZADA ★")
        st.session_state.winner = info.winner
    else:
        st.session_state.winner = None


def main():
    st.set_page_config(page_title="Carrera de Caballos — Baraja Española", layout="wide")
    _inject_css()
    _ensure_game()

    # Top bar
    st.markdown(
        f"""
        <div class="topbar">
          <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size:28px; color:{C_GOLD};">⚑</div>
            <div style="line-height:1.1">
              <div style="font-weight:900; font-size:18px; color:{C_TEXT};">CARRERA DE CABALLOS</div>
              <div style="color:{C_GOLD}; font-style:italic; font-size:12px;">Baraja Española</div>
            </div>
            <div class="pill">{st.session_state.get("status","")}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    _setup_sidebar()

    if not st.session_state.get("configured"):
        st.info("Configura la partida en la barra lateral y pulsa **INICIAR CARRERA**.")
        return

    # Acciones principales
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if st.button("▶  VOLTEAR CARTA", type="primary", use_container_width=True):
            try:
                _step_game()
                st.rerun()
            except Exception as e:
                st.error(str(e))
    with c2:
        if st.button("↺  Nueva partida", use_container_width=True):
            # volver a setup sin perder inputs
            st.session_state.configured = False
            st.session_state.winner = None
            st.session_state.log = []
            st.session_state.last_card = None
            st.session_state.status = "Configura una nueva partida"
            st.rerun()

    # Layout principal: tablero + panel derecha
    left, right = st.columns([2.2, 1])

    with left:
        st.markdown(f"#### TABLERO  <span style='color:{C_TEXT3}; font-style:italic; font-size:14px'>— Checkpoints arriba · Carriles abajo</span>", unsafe_allow_html=True)
        board_img = _draw_board_image(width=1100, height=700)
        try:
            st.image(board_img, use_container_width=True)
        except TypeError:
            st.image(board_img, use_column_width=True)

    with right:
        # Última carta
        st.markdown("#### ÚLTIMA CARTA")
        last = st.session_state.last_card
        if last is None:
            back = _get_back_pil((240, 340))
            if back:
                st.image(back, use_container_width=True)
            else:
                st.markdown(f"<div class='card' style='text-align:center;color:{C_TEXT3};font-style:italic;'>Voltea una carta<br/>para comenzar</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{C_TEXT2};font-style:italic;'>— ninguna —</div>", unsafe_allow_html=True)
        else:
            card_img = _get_card_pil(last, (240, 340))
            if card_img:
                st.image(card_img, use_container_width=True)
            st.markdown(f"<div style='color:{C_TEXT2};font-style:italic; font-size:16px'>{last.name}</div>", unsafe_allow_html=True)

        st.divider()

        # Registro
        st.markdown("#### REGISTRO DE EVENTOS")
        if st.button("Limpiar registro"):
            st.session_state.log = []
            st.rerun()
        st.text_area("", value="\n".join(st.session_state.log[-250:]), height=260)

        # Ganador
        winner = st.session_state.get("winner")
        if winner:
            owner = st.session_state.suit_to_player.get(winner)
            if owner:
                st.success(f"★ Ganó: {owner['name']} ({winner})")
            else:
                st.success(f"★ Ganó: {winner}")

            # Ranking
            players: List[PlayerCfg] = st.session_state.players
            game: CarreraEspanola = st.session_state.game
            sorted_p = sorted(players, key=lambda p: game.positions.get(p.suit, 0), reverse=True)
            medals = ["🥇", "🥈", "🥉", "4."]
            st.markdown("**Clasificación**")
            for i, p in enumerate(sorted_p):
                pos = game.positions.get(p.suit, 0)
                sym = SUIT_SYMBOLS.get(p.suit, "")
                medal = medals[i] if i < len(medals) else f"{i+1}."
                st.markdown(f"- {medal} **{p.name}**  ·  {sym} {p.suit}  ·  casilla {pos}")


if __name__ == "__main__":
    main()