import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="dna rna hysics Sim", layout="wide", page_icon="🧬")

with st.sidebar:
    st.markdown("# 🧬 Physics Manifesto\n**RNA RA Hairs deform in gel!**")
    if st.button("B-DNA"): st.session_state.update({'thermal':1.0,'gravity':0.5,'inertia':0.8,'pressure':1.0,'sleep_wake':0.5,'anim_time':0.0}); st.rerun()
    if st.button("Transcription"): st.session_state.update({'thermal':2.0,'gravity':0.3,'inertia':0.4,'pressure':0.8,'sleep_wake':1.0}); st.rerun()
    if st.button("Stress"): st.session_state.update({'thermal':3.0,'gravity':2.0,'inertia':1.5,'pressure':2.0,'sleep_wake':0.2}); st.rerun()
    if st.button("Dormant"): st.session_state.update({'thermal':0.2,'gravity':0.1,'inertia':1.0,'pressure':1.0,'sleep_wake':0.0}); st.rerun()

if 'thermal' not in st.session_state:
    st.session_state.update({'thermal':1.0,'gravity':0.5,'inertia':0.8,'pressure':1.0,'sleep_wake':0.5,'anim_time':0.0})

tab1, tab2 = st.tabs(["🧬 Live Sim", "📚 Science"])

with tab1:
    col1, col2 = st.columns(2)
    st.session_state['thermal'] = col1.slider("🌡️ Thermal", 0.0, 5.0, st.session_state['thermal'], 0.1)
    st.session_state['gravity'] = col1.slider("🪨 Gravity", 0.0, 3.0, st.session_state['gravity'], 0.1)
    st.session_state['inertia'] = col2.slider("⚡ Inertia", 0.0, 2.0, st.session_state['inertia'], 0.1)
    st.session_state['pressure'] = col2.slider("💧 Pressure", 0.5, 2.5, st.session_state['pressure'], 0.1)
    st.session_state['sleep_wake'] = st.slider("😴 Sleep/Wake", 0.0, 2.0, st.session_state['sleep_wake'], 0.1)

    if st.button("🔄 Animate"): st.session_state['anim_time'] += 0.1
    st.session_state['anim_time'] += 0.01

    @st.cache_data
    def generate_helix():
        t = np.linspace(0, 4*np.pi, 1000)
        r, p = 1.34, 3.4 / (2*np.pi)
        x1, y1, z1 = r*np.cos(t), r*np.sin(t), p*t
        x2, y2, z2 = r*np.cos(t+np.pi), r*np.sin(t+np.pi), p*t
        bx, by, bz = (x1+x2)/2, (y1+y2)/2, z1
        hx, hy, hz = [], [], []
        hair_t = np.linspace(0, np.pi, 50)
        for bt in t[::50]:
            hx0 = r * np.cos(bt) * 1.5
            hy0 = r * np.sin(bt) * 1.5
            hz0 = p * bt
            hx.extend(hx0 + 0.3*np.cos(hair_t + bt) + 0.1*np.sin(3*hair_t))
            hy.extend(hy0 + 0.2*np.sin(hair_t) + 0.15*np.cos(2*hair_t))
            hz.extend(hz0 + 0.4*hair_t)
        return (x1,y1,z1), (x2,y2,z2), (bx,by,bz), (np.array(hx), np.array(hy), np.array(hz))

    def gel(params):
        theta = np.linspace(0, 2*np.pi, 50)
        zgel = np.linspace(-1, 16, 20)
        Theta, Z = np.meshgrid(theta, zgel)
        rg = 3.0 * params['pressure'] * 0.8
        xg = rg * np.cos(Theta) + params['gravity'] * np.sin(Theta) * 0.2
        yg = rg * np.sin(Theta)
        return xg, yg, Z

    def physics(hairs, params, time):
        hx, hy, hz = hairs
        dxs, dys, dzs = [], [], []
        for i in range(20):
            start = i*50
            shx, shy, shz = hx[start:start+50], hy[start:start+50], hz[start:start+50]
            noise = params['thermal'] * 0.05 * (np.sin(time*5 + shz*10) + np.cos(time*3 + shx*8))
            grav = params['gravity'] * (shz - np.mean(shz)) * 0.1
            inrt = params['inertia'] * 0.02 * np.cumsum(np.sin(time + shz))**2
            pscale = 1 + (params['pressure'] - 1)*0.3
            wake = params['sleep_wake'] * 0.15 * np.sin(time*2 + shz*4 + i)
            dx = shx * pscale + noise + grav + inrt + wake
            dy = shy * pscale + noise*0.5 + wake
            dz = shz + grav*0.5
            dxs.extend(dx); dys.extend(dy); dzs.extend(dz)
        return np.array(dxs), np.array(dys), np.array(dzs)

    dna1, dna2, bases, hairs = generate_helix()
    params = {'thermal':st.session_state['thermal'],'gravity':st.session_state['gravity'],'inertia':st.session_state['inertia'],'pressure':st.session_state['pressure'],'sleep_wake':st.session_state['sleep_wake'],'time':st.session_state['anim_time']}
    dhairs = physics(hairs, params, params['time'])
    gelx, gely, gelz = gel(params)

    stab = 100 * (1 - params['thermal']/5 - params['gravity']/3 + params['pressure'])
    st.metric("🧬 RNA Stability", f"{stab:.0f}%", f"{stab-50:+.0f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=dna1[0], y=dna1[1], z=dna1[2], mode='lines', line=dict(color='cyan', width=12), name='DNA 1'))
    fig.add_trace(go.Scatter3d(x=dna2[0], y=dna2[1], z=dna2[2], mode='lines', line=dict(color='magenta', width=12), name='DNA 2'))
    fig.add_trace(go.Scatter3d(x=bases[0], y=bases[1], z=bases[2], mode='lines', line=dict(color='white', width=4), name='Bases'))
    fig.add_trace(go.Scatter3d(x=dhairs[0], y=dhairs[1], z=dhairs[2], mode='lines', line=dict(color='orange', width=6), name='RA Hairs'))
    fig.add_trace(go.Surface(x=gelx, y=gely, z=gelz, colorscale='Blues', opacity=0.2, showscale=False, name='Gel'))

    # FIXED Sparks: Safe 3D circle markers
    npart = 50
    L = len(dhairs[0]) - 1
    idx = np.clip(np.linspace(0, L, npart).astype(int), 0, L)
    fig.add_trace(go.Scatter3d(x=dhairs[0][idx], y=dhairs[1][idx], z=dhairs[2][idx],
                               mode='markers', marker=dict(size=8, color='yellow', symbol='circle'), name='Sparks'))

    fig.update_layout(title="🧬 DNA-RNA Physics Sim", scene=dict(
        xaxis=dict(backgroundcolor="black", gridcolor="darkblue"),
        yaxis=dict(backgroundcolor="black", gridcolor="darkblue"),
        zaxis=dict(backgroundcolor="black", gridcolor="darkblue"),
        camera=dict(eye=dict(x=1.5,y=1.5,z=1.5)), aspectmode='cube'), height=800)
    st.markdown("<style>.plotly-graph-div{border:2px solid #00ffff;border-radius:15px;box-shadow:0 0 20px #00ffff;}</style>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("""
# 🧬 RNA Stain Logic
**RNA Stain**: Fluorescent R-loops invading DNA.

**Deform**: Thermal(Noise) + Gravity(Sag) + Inertia(Lag)×Pressure + Sleep/Wake(Wave)

| Factor | Effect | Biology |
|--------|--------|---------|
| 🌡️ Thermal | Jitter | Brownian |
| 🪨 Gravity | Droop | Sediment |
| ⚡ Inertia | Whip | Shear |
| 💧 Pressure | Squish | Osmotic |
| 😴 Sleep/Wake | Pulse | Circadian |

**Research**: R-loop drugs, gel opt, ML datasets.
    """)
