import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

# Page config for full-screen coolness
st.set_page_config(page_title="DNA-RNA Helix Physics Sim", layout="wide", page_icon="🧬")

# Manifesto Sidebar (Explanatory Text)
with st.sidebar:
    st.markdown("""
    # 🧬 DNA-RNA Helix Physics Manifesto
    **Explore the dynamic interplay of forces on RNA 'RA Hairs' (Ribosomal Antennae-like protrusions) invading a DNA double helix in a gel matrix.**
    
    - **DNA Helix**: Blue/purple backbone (B-form base).
    - **RNA RA Hairs**: Orange curling 'hairs' extending from one strand—responsive to physics.
    - **Gel Container**: Transparent cylinder simulating agarose electrophoresis gel—distorts under pressure/gravity.
    - **Sliders**: Real-time physics params. Watch hairs curl, vibrate, bend!
    - **FX**: Neon glows, particle sparks, volumetric distortions.
    
    **Science-Inspired Art**: Thermal noise (Brownian motion), gravity sag, inertial lag, hydrostatic pressure squeeze, sleep/wake cycles (oscillation amplitude).
    
    **Presets**: B-DNA | Active Transcription | Under Stress | Dormant.
    """)
    
    # Preset buttons
    if st.button("B-DNA Preset"):
        st.session_state.update({
            'thermal': 1.0, 'gravity': 0.5, 'inertia': 0.8, 'pressure': 1.0, 'sleep_wake': 0.5
        })
        st.rerun()
    if st.button("Active Transcription"):
        st.session_state.update({
            'thermal': 2.0, 'gravity': 0.3, 'inertia': 0.4, 'pressure': 0.8, 'sleep_wake': 1.0
        })
        st.rerun()
    if st.button("Under Stress"):
        st.session_state.update({
            'thermal': 3.0, 'gravity': 2.0, 'inertia': 1.5, 'pressure': 2.0, 'sleep_wake': 0.2
        })
        st.rerun()
    if st.button("Dormant Sleep"):
        st.session_state.update({
            'thermal': 0.2, 'gravity': 0.1, 'inertia': 1.0, 'pressure': 1.0, 'sleep_wake': 0.0
        })
        st.rerun()

# Session state init
if 'thermal' not in st.session_state:
    st.session_state.update({
        'thermal': 1.0, 'gravity': 0.5, 'inertia': 0.8, 'pressure': 1.0, 'sleep_wake': 0.5,
        'anim_time': 0.0
    })

# NEW TABS HERE – WRAPS EVERYTHING
tab1, tab2 = st.tabs(["🧬 Live Sim", "📚 Science Logic & Research"])

with tab1:
    # Main Sliders (with session state for reactivity)
    col1, col2 = st.columns(2)
    st.session_state['thermal'] = col1.slider("🌡️ Thermal Noise (Vibration)", 0.0, 5.0, st.session_state['thermal'], 0.1)
    st.session_state['gravity'] = col1.slider("🪨 Gravity (Sag/Bend)", 0.0, 3.0, st.session_state['gravity'], 0.1)
    st.session_state['inertia'] = col2.slider("⚡ Inertia (Lag/Momentum)", 0.0, 2.0, st.session_state['inertia'], 0.1)
    st.session_state['pressure'] = col2.slider("💧 Pressure (Compress/Expand)", 0.5, 2.5, st.session_state['pressure'], 0.1)
    st.session_state['sleep_wake'] = st.slider("😴 Sleep/Wake Cycle (Oscillate)", 0.0, 2.0, st.session_state['sleep_wake'], 0.1)

    # Animate button
    col3, col4 = st.columns(2)
    if col3.button("🔄 Animate Cycle"):
        st.session_state['anim_time'] += 0.1
    col4.button("⏹️ Pause", disabled=True)  # Placeholder

    st.session_state['anim_time'] += 0.01  # Auto-advance slowly

    # Core Helix Generation Function (cached)
    @st.cache_data
    def generate_helix_data(n_points=1000, n_hairs=20):
        t = np.linspace(0, 4*np.pi, n_points)
        radius_base = 1.34  # B-DNA
        pitch = 3.4 / (2*np.pi)
        
        # DNA Strand 1
        x1 = radius_base * np.cos(t)
        y1 = radius_base * np.sin(t)
        z1 = pitch * t
        
        # DNA Strand 2
        x2 = radius_base * np.cos(t + np.pi)
        y2 = radius_base * np.sin(t + np.pi)
        z2 = pitch * t
        
        # Base Pairs
        base_x = (x1 + x2)/2
        base_y = (y1 + y2)/2
        base_z = z1
        
        # RNA RA Hairs
        hair_t = np.linspace(0, np.pi, 50)
        hair_bases = t[::n_points//n_hairs]
        hair_x, hair_y, hair_z = [], [], []
        for base_t in hair_bases:
            hx0 = radius_base * np.cos(base_t) * 1.5
            hy0 = radius_base * np.sin(base_t) * 1.5
            hz0 = pitch * base_t
            
            hx = hx0 + 0.3 * np.cos(hair_t + base_t) + 0.1 * np.sin(3*hair_t)
            hy = hy0 + 0.2 * np.sin(hair_t) + 0.15 * np.cos(2*hair_t)
            hz = hz0 + 0.4 * hair_t
            
            hair_x.extend(hx)
            hair_y.extend(hy)
            hair_z.extend(hz)
        
        return (x1,y1,z1), (x2,y2,z2), (base_x,base_y,base_z), (np.array(hair_x), np.array(hair_y), np.array(hair_z))

    # Gel Container
    def gel_container(params):
        theta = np.linspace(0, 2*np.pi, 50)
        z_gel = np.linspace(-1, params['zmax']+1, 20)
        Theta, Z = np.meshgrid(theta, z_gel)
        
        r_gel = 3.0 * params['pressure'] * 0.8
        x_gel = r_gel * np.cos(Theta) + params['gravity'] * np.sin(Theta) * 0.2
        y_gel = r_gel * np.sin(Theta)
        z_gel_flat = Z
        
        return x_gel, y_gel, z_gel_flat

    # Apply Physics
    def apply_physics(hairs, params, time):
        hx, hy, hz = hairs
        segments = len(hx) // 50
        deformed_x, deformed_y, deformed_z = [], [], []
        
        for i in range(segments):
            seg_hx = hx[i*50:(i+1)*50]
            seg_hy = hy[i*50:(i+1)*50]
            seg_hz = hz[i*50:(i+1)*50]
            
            noise = params['thermal'] * 0.05 * (np.sin(time*5 + seg_hz*10) + np.cos(time*3 + seg_hx*8))
            grav_bend = params['gravity'] * (seg_hz - np.mean(seg_hz)) * 0.1
            inertia_lag = params['inertia'] * 0.02 * np.cumsum(np.sin(time + seg_hz))**2
            pressure_scale = 1 + (params['pressure'] - 1) * 0.3
            wake_wave = params['sleep_wake'] * 0.15 * np.sin(time*2 + seg_hz*4 + i)
            
            dx = seg_hx * pressure_scale + noise + grav_bend + inertia_lag + wake_wave
            dy = seg_hy * pressure_scale + noise * 0.5 + wake_wave
            dz = seg_hz + grav_bend * 0.5
            
            deformed_x.extend(dx)
            deformed_y.extend(dy)
            deformed_z.extend(dz)
        
        return np.array(deformed_x), np.array(deformed_y), np.array(deformed_z)

    # Generate & Deform
    dna1, dna2, bases, hairs = generate_helix_data()
    params = {
        'thermal': st.session_state['thermal'],
        'gravity': st.session_state['gravity'],
        'inertia': st.session_state['inertia'],
        'pressure': st.session_state['pressure'],
        'sleep_wake': st.session_state['sleep_wake'],
        'time': st.session_state['anim_time'],
        'zmax': 15.0
    }
    deformed_hairs = apply_physics(hairs, params, params['time'])
    gel_x, gel_y, gel_z = gel_container(params)

    # Stability Metric
    stability = 100 * (1 - params['thermal']/5 - params['gravity']/3 + params['pressure'])
    st.metric("🧬 RNA Hybrid Stability", f"{stability:.0f}%", delta=f"{stability-50:+.0f}")

    # Figure
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=dna1[0], y=dna1[1], z=dna1[2], mode='lines', line=dict(color='cyan', width=12), name='DNA Strand 1'))
    fig.add_trace(go.Scatter3d(x=dna2[0], y=dna2[1], z=dna2[2], mode='lines', line=dict(color='magenta', width=12), name='DNA Strand 2'))
    fig.add_trace(go.Scatter3d(x=bases[0], y=bases[1], z=bases[2], mode='lines', line=dict(color='white', width=4), name='Base Pairs'))
    fig.add_trace(go.Scatter3d(x=deformed_hairs[0], y=deformed_hairs[1], z=deformed_hairs[2], mode='lines', line=dict(color='orange', width=6), name='RNA RA Hairs'))
    fig.add_trace(go.Surface(x=gel_x, y=gel_y, z=gel_z, colorscale='Blues', opacity=0.2, showscale=False, name='Gel Matrix'))

    # Particles
    n_particles = 50
    part_t = np.linspace(0, len(deformed_hairs[0]), n_particles)
    fig.add_trace(go.Scatter3d(x=deformed_hairs[0][part_t.astype(int)], y=deformed_hairs[1][part_t.astype(int)], z=deformed_hairs[2][part_t.astype(int)],
                               mode='markers', marker=dict(size=8, color='yellow', symbol='star'), name='Sparks'))

    fig.update_layout(
        title="🧬 DNA-RNA Physics Sim: RA Hairs in Gel | Live Deformations",
        scene=dict(xaxis=dict(backgroundcolor="black", gridcolor="darkblue"), yaxis=dict(backgroundcolor="black", gridcolor="darkblue"), zaxis=dict(backgroundcolor="black", gridcolor="darkblue"),
                   camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)), aspectmode='cube'),
        height=800
    )

    # CSS Glow
    st.markdown("<style>.plotly-graph-div { border: 2px solid #00ffff; border-radius: 15px; box-shadow: 0 0 20px #00ffff; }</style>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("""
    # 🧬 RNA Stain Dynamics: Clean Logic, Impacts & Research Frontiers
    
    ## 1. **What is 'RNA Stain' in DNA Helix Context?**
    **RNA Stain** refers to **fluorescently stained RNA strands/protrusions** (visualized as glowing 'RA Hairs' – *Ribosomal Antennae* or R-loop extensions) invading or hybridizing with the DNA double helix. 
    - **Biology Basis**: RNA forms **R-loops** during transcription. Stains like SYBR Green light up RNA.
    - **In Model**: Orange hairs from DNA strand 1, deforming in gel.
    
    **Equation**: RNA Deform = Thermal + Gravity + Inertia × Pressure + Sleep/Wake
    
    ## 2. **Factor Impacts**
    | Factor | Analogy | Hair Effect | Gel Impact |
    |--------|---------|-------------|------------|
    | 🌡️ Thermal | Brownian | Jitter/curl | Sparks boil |
    | 🪨 Gravity | Sedimentation | Droop | Warp bottom |
    | ⚡ Inertia | Flow shear | Lag/whip | Stretch |
    | 💧 Pressure | Osmotic | Squeeze | Shrink |
    | 😴 Sleep/Wake | Circadian | Pulse | Oscillate |
    
    ## 3. **Research Ideas**
    - R-Loop stability thresholds for drugs.
    - Gel electrophoresis optimization.
    - Drug screening, viral sims, ML datasets.
    
    **Extend**: Add BioPython PDB loads. Publish on GitHub!
    
    Sources: R-loop papers, MD sims.
    """)
