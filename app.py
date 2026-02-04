import streamlit as st
import pandas as pd
import plotly.express as px
from poliastro.bodies import Sun
from poliastro.twobody import Orbit
from poliastro.plotting import OrbitPlotter2D
import astropy.units as u

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Asteroid Mining Planner MVP", layout="wide")

# ── Load data (placeholder — replace with real merged dataset) ───────────────
@st.cache_data
def load_asteroids():
    # For MVP: use a small public Kaggle-like CSV
    # In reality: download from https://ssd.jpl.nasa.gov/tools/sbdb_query.html (CSV export)
    # or https://www.kaggle.com/datasets/sakhawat18/asteroid-dataset
    # Here we simulate with dummy data — replace with your Parquet/CSV
    data = {
        'name': ['16 Psyche', 'Ryugu', 'Bennu', '1 Ceres', '4 Vesta', '433 Eros'],
        'a': [2.92, 1.19, 1.13, 2.77, 2.36, 1.46],  # semi-major axis (AU)
        'e': [0.14, 0.19, 0.20, 0.08, 0.10, 0.22],  # eccentricity
        'i': [7.0, 5.9, 6.0, 10.6, 7.1, 10.8],     # inclination (deg)
        'diameter_km': [226, 0.9, 0.49, 946, 525, 16.8],
        'est_value_billion_usd': [10000, 8.8, 0.67, 1000, 500, 0.1],  # rough estimates
        'spectral_type': ['M', 'C', 'B', 'C', 'V', 'S'],
        'delta_v_km_s': [5.5, 4.6, 5.1, 9.0, 7.8, 5.8]  # approximate Earth transfer
    }
    df = pd.DataFrame(data)
    return df

df = load_asteroids()

# ── UI ──────────────────────────────────────────────────────────────────────
st.title("Asteroid Mining Mission Planner (MVP)")
st.caption("Filter main-belt / NEO asteroids • Rough value estimates • Basic orbit view")

# Filters (sidebar)
with st.sidebar:
    st.header("Filters")
    
    selected_types = st.multiselect(
        "Spectral Type",
        options=df['spectral_type'].unique(),
        default=df['spectral_type'].unique()
    )
    
    min_diam = st.slider("Min Diameter (km)", 0.1, 1000.0, 0.5)
    min_value = st.slider("Min Est. Value (billion USD)", 0.1, 20000.0, 1.0)
    max_dv = st.slider("Max Delta-V to reach (km/s)", 4.0, 15.0, 7.0)

# Apply filters
df_filt = df[
    (df['spectral_type'].isin(selected_types)) &
    (df['diameter_km'] >= min_diam) &
    (df['est_value_billion_usd'] >= min_value) &
    (df['delta_v_km_s'] <= max_dv)
]

# ── Display results ─────────────────────────────────────────────────────────
st.subheader(f"Filtered Asteroids ({len(df_filt)} found)")

# Table
st.dataframe(
    df_filt[['name', 'diameter_km', 'est_value_billion_usd', 'delta_v_km_s', 'spectral_type']],
    use_container_width=True,
    hide_index=True
)

# Profit bands (simple Monte Carlo style)
st.subheader("Profit Estimates (rough)")
for _, row in df_filt.iterrows():
    base_value = row['est_value_billion_usd']
    low = base_value * 0.6   # ±40% band example
    high = base_value * 1.4
    st.metric(
        row['name'],
        f"${base_value:,.0f}B",
        f"(${low:,.0f}B – ${high:,.0f}B)"
    )

# ── Basic orbit plot (Poliastro 2D) ────────────────────────────────────────
st.subheader("Orbital Positions (selected asteroids)")

if not df_filt.empty:
    fig = px.scatter(
        df_filt,
        x='a',
        y='i',
        size='diameter_km',
        color='spectral_type',
        hover_name='name',
        title="Semi-major Axis vs Inclination (size = diameter)",
        labels={'a': 'Semi-major Axis (AU)', 'i': 'Inclination (deg)'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Poliastro simple 2D orbits (placeholder — one at a time)
    selected = st.selectbox("Plot orbit for:", df_filt['name'].tolist(), index=0)
    row = df_filt[df_filt['name'] == selected].iloc[0]

    # Dummy orbit (replace with real elements from your dataset)
    orb = Orbit.circular(Sun, 1 * u.AU)  # placeholder Earth-like
    plotter = OrbitPlotter2D()
    plotter.plot(orb, label=selected)
    st.plotly_chart(plotter.fig, use_container_width=True)
else:
    st.info("No asteroids match your filters.")