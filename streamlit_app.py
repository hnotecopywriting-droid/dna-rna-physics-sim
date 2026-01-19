import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Page config for full-screen coolness
st.set_page_config(page_title="DNA-RNA Helix Physics Sim", layout="wide", page_icon="🧬")

# Manifesto Sidebar
with st.sidebar:
    st.markdown("""
    # 🧬 DNA-RNA Helix Physics Manifesto
    **Explore forces on RNA 'RA Hairs' invading DNA helix in gel.**
    
    - DNA: Cyan/magenta backbones.
    - RNA Hairs: Orange curls – deform live!
    - Gel: Warping blue cylinder.
    - FX: Sparks, glows.
    
    **Presets**:""")
    
    # Preset buttons with rerun
    if st.button("B-DNA Preset"):
        st.session_state.update({'thermal': 1.0, 'gravity': 0.5, 'inertia': 0.8, 'pressure': 1.0, 'sleep_wake': 0.5, 'anim_time': 0.0})
        st.rerun()
    if st.button("Active Transcription"):
        st.session_state.update({'thermal': 2.0, 'gravity': 0.3, 'inertia': 0.4, 'pressure': 0.8, 'sleep_wake': 1.0})
        st.rerun()
    if st.button("Under Stress"):
        st.session_state.update({'thermal': 3.0, 'gravity': 2.0, 'inertia': 1.5, 'pressure': 2.0, 'sleep_wake': 0.2})
        st.rerun()
    if st.button("Dormant Sleep"):
        st.session_state.update({'thermal': 0.2, 'gravity': 0.1, 'inertia': 1.0, 'pressure': 1.0, 'sleep_wake': 0.0})
        st.rerun()

# Session state init
if 'thermal' not in st.session_state:
    st.session_state.update({
        'thermal': 1.0, 'gravity': 0.5, 'inertia': 0.8, 'pressure': 1.0, 'sleep_wake': 0.5, 'anim_time': 0.0
    })

# TABS
tab1, tab2 = st.tabs(["🧬 Live Sim", "📚 Science Logic & Research"])

with tab1:
    # Sliders
    col1, col2 = st.columns(2)
    st.session_state['thermal'] = col1.slider("🌡️ Thermal Noise", 0.0, 5.0, st.session_state['thermal'], 0.1)
    st.session_state['gravity'] = col1.slider("🪨 Gravity Sag", 0.0, 3.0, st.session_state['gravity'], 0.1)
    st.session_state['inertia'] = col2.slider("⚡ Inertia Lag", 0.0, 2.0, st.session_state['inertia'], 0.1)
    st.session_state['pressure'] = col2.slider("💧 Pressure", 0.5, 2.5, st.session_state['pressure'], 0.1)
    st.session_state['sleep_wake'] = st.slider("😴 Sleep/Wake", 0.0, 2.0, st.session_state['sleep_wake'], 0.1)

    # Animate
    if st.button("🔄 Animate Cycle"):
        st.session_state['anim_time'] += 0.1
    st.session_state['anim_time'] += 0.01

    # Helix Gen (cached)
    @st.cache_data
    def generate_helix_data(_n_points=1000, _n_hairs=20):
        t = np.linspace(0, 4*np.pi, _n_points)
        r = 1.34
        p = 3.4 / (2*np.pi)
        x1 = r * np.cos(t)
        y1 = r * np.sin(t)
        z1 = p * t
        x2 = r * np.cos(t + np.pi)
        y2 = r * np.sin(t + np.pi)
        z2 = p * t
        base_x = (x1 + x2)/2
        base_y = (y1 + y2)/2
        base_z = z1
        
        # Hairs
        hair_t = np.linspace(0, np.pi, 50)
        hair_bases = t[::_n_points//_n_hairs]
        hx, hy, hz = [], [], []
        for bt in hair_bases:
            hx0 = r * np.cos(bt) * 1.5
            hy0 = r * np.sin(bt) * 1.5
            hz0 = p * bt
            hx.extend(hx0 + 0.3 * np.cos(hair_t + bt) + 0.1 * np.sin(3*hair_t))
            hy.extend(hy0 + 0.2 * np.sin(hair_t) + 0.15 * np.cos(2*hair_t))
            hz.extend(hz0 + 0.4 * hair_t)
        return (x1,y1,z1), (x2,y2,z2), (base_x,base_y,base_z), (np.array(hx), np.array(hy), np.array(hz))

    # Gel
    def gel_container(params):
        theta = np.linspace(0, 2*np.pi, 50)
        z_gel = np.linspace(-1, 15+1, 20)
        Theta, Z = np.meshgrid(theta, z_gel)
        r_gel = 3.0 * params['pressure'] * 0.8
        x_gel = r_gel * np.cos(Theta) + params['gravity'] * np.sin(Theta) * 0.2
        y_gel = r_gel * np.sin(Theta)
        return x_gel, y_gel, Z

    # Physics
    def apply_physics(hairs, params, time):
        hx, hy, hz = hairs
        segs = len(hx) // 50
        dxs, dys, dzs = [], [], []
        for i in range(segs):
            shx = hx[i*50:(i+1)*50]
            shy = hy[i*50:(i+1)*50]
            shz = hz[i*50:(i+1)*50]
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

    # Run sim
    dna1, dna2, bases, hairs = generate_helix_data()
    params = {
        'thermal': st.session_state['thermal'], 'gravity': st.session_state['gravity'],
        'inertia': st.session_state['inertia'], 'pressure': st.session_state['pressure'],
        'sleep_wake': st.session_state['sleep_wake'], 'time': st.session_state['anim_time']
    }
    dhairs = apply_physics(hairs, params, params['time'])
    gelx, gely, gelz = gel_container(params)

    # Stability
    stab = 100 * (1 - params['thermal']/5 - params['gravity']/3 + params['pressure'])
    st.metric("🧬 RNA Stability", f"{stab:.0f}%", f"{stab-50:+.0f}")

    # Fig
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=dna1[0], y=dna1[1], z=dna1[2], mode='lines', line=dict(color='cyan', width=12), name='DNA 1'))
    fig.add_trace(go.Scatter3d(x=dna2[0], y=dna2[1], z=dna2[2], mode='lines', line=dict(color='magenta', width=12), name='DNA 2'))
    fig.add_trace(go.Scatter3d(x=bases[0], y=bases[1], z=bases[2], mode='lines', line=dict(color='white', width=4), name='Bases'))
    fig.add_trace(go.Scatter3d(x=dhairs[0], y=dhairs[1], z=dhairs[2], mode='lines', line=dict(color='orange', width=6), name='RA Hairs'))

    # FIXED Sparks – Safe indexing!
    n_part = 50
    part_t = np.linspace(0, 1, n_part)
    L = len(dhairs[0]) - 1
    part_idx = np.clip((part_t * L).astype(int), 0, L)
    fig.add_trace(go.Scatter3d(
        x=dhairs[0][part_idx], y=dhairs[1][part_idx], z=dhairs[2][part_idx],
        mode='markers', marker=dict(size=8, color='yellow', symbol='star'), name='Sparks'
    ))

    fig.add_trace(go.Surface(x=gelx, y=gely, z=gelz, colorscale='Blues', opacity=0.2, showscale=False, name='Gel'))

    fig.update_layout(
        title="🧬 DNA-RNA Physics: Live RA Hairs in Gel",
        scene=dict(
            xaxis=dict(backgroundcolor="black", gridcolor="darkblue"),
            yaxis=dict(backgroundcolor="black", gridcolor="darkblue"),
            zaxis=dict(backgroundcolor="black", gridcolor="darkblue"),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)), aspectmode='cube'
        ),
        height=800, showlegend=True
    )

    st.markdown("<style>.plotly-graph-div {border: 2px solid #00ffff; border-radius: 15px; box-shadow: 0 0 20px #00ffff;}</style>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key="helix")

with tab2:
    st.markdown("""
    # 🧬 RNA Stain Logic & Research
    
    **RNA Stain**: Fluorescent R-loops (RNA hairs invading DNA).
    
    **Deform Eq**: Thermal + Gravity + Inertia×Pressure + Sleep/Wake
    
    | Factor | Effect | Bio |
    |--------|--------|-----|
    | 🌡️ Thermal | Jitter | Brownian |
    | 🪨 Gravity | Droop | Sediment |
    | ⚡ Inertia | Whip | Shear |
    | 💧 Pressure | Squish | Osmotic |
    | 😴 Sleep/Wake | Pulse | Circadian |
    
    **Research**: R-loop drugs, gel opt, ML data.
    
    Sources: R-loops (Nature), MD sims.
    """)
