# 🐴 Carrera de Caballos — Baraja Española

App web multijugador (2-4 jugadores) hecha con Streamlit.

---

## 🚀 Despliegue en Render

### Paso 1 — Sube a GitHub

1. Crea un repo en [github.com](https://github.com) → **New repository**  
   - Nombre: `carrera-caballos`  
   - Visibilidad: **Public**  
   - Sin README (lo tienes ya)

2. En tu terminal dentro de la carpeta del proyecto:
```bash
git init
git add .
git commit -m "carrera de caballos"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/carrera-caballos.git
git push -u origin main
```

### Paso 2 — Configura Render

1. Ve a [render.com](https://render.com) → crea cuenta gratis
2. **New +** → **Web Service**
3. Conecta tu GitHub y selecciona `carrera-caballos`
4. Completa estos campos:

| Campo | Valor |
|---|---|
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |
| Plan | `Free` |

5. **Create Web Service** → espera ~2 min
6. Tu URL quedará algo como: `https://carrera-caballos.onrender.com`

---

## 🗂 Estructura del proyecto

```
carrera-caballos/
├── app.py              ← Interfaz web Streamlit
├── requirements.txt    ← Solo necesita streamlit
├── README.md
└── src/
    ├── __init__.py
    ├── model.py        ← Cartas y mazo (baraja española 40 cartas)
    └── game.py         ← Lógica de la carrera
```

---

## ▶ Correr localmente

```bash
pip install streamlit
streamlit run app.py
```
