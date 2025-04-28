import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------
# Constants & Setup
# -----------------------
plate_dims = {
    '6-well': (2, 3),
    '12-well': (3, 4),
    '24-well': (4, 6),
    '48-well': (6, 8),
    '96-well': (8, 12)
}

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="Treat Yo' Cell", layout="wide")

# -----------------------
# Background & Styling
# -----------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Consolas&display=swap');

    .stApp {
        background: url('https://i.imgur.com/5B1ti2U.jpg') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Consolas', monospace;
        color: #556b2f;
        font-weight: bold;
    }

    section.main > div {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        animation: fadeIn 2s ease-in;
    }

    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(8px);
        border-right: 2px solid rgba(255, 255, 255, 0.2);
        font-family: 'Consolas', monospace;
        color: white;
        font-weight: bold;
        font-size: 20px;
    }

    [data-testid="stSidebar"] label {
        font-family: 'Consolas', monospace;
        color: white;
        font-weight: bold;
        font-size: 20px;
    }

    button {
        font-family: 'Consolas', monospace;
        font-size: 20px;
        font-weight: bold;
        color: black !important;
        background-color: #F0FFF0 !important;
        border: 2px solid #556b2f;
        padding: 10px 20px;
        border-radius: 12px;
    }

    button:hover {
        background-color: #6b8e23 !important;
        color: white !important;
        transform: scale(1.02);
        transition: all 0.3s ease;
    }

    /* Style the selectbox */
    .css-2b097c-container, .css-1hwfws3, .css-1wa3eu0-placeholder {
        font-family: 'Consolas', monospace;
        font-size: 30px;
        font-weight: bold;
        color: #556b2f;
    }

    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }

    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.05);
        z-index: -1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------
# Show Banner
# -----------------------
def show_banner():
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <h1 style='font-family: "Consolas"; font-size: 60px; color: #556b2f;'>Treat Yo' Cell</h1>
        <h4 style='font-family: "Consolas"; font-style: normal; font-weight: bold; color: #556b2f;'>Because "Ops! Wrong Well!" isn't an experimental variable!</h4>
    </div>
    """, unsafe_allow_html=True)

# -----------------------
# Main App Layout
# -----------------------
with st.spinner('Setting Up Wells in Style...'):
    show_banner()

    st.markdown("<h2 style='text-align: center; font-family: Consolas, monospace; font-size:48px; color:#556b2f;'>Select Plate Type</h2>", unsafe_allow_html=True)
    plate_type = st.selectbox("", list(plate_dims.keys()), index=4)

    n_rows, n_cols = plate_dims[plate_type]
    rows = [chr(i) for i in range(65, 65 + n_rows)]
    cols = list(range(1, n_cols + 1))
    well_ids = [f"{r}{c}" for r in rows for c in cols]

    if "plate" not in st.session_state:
        st.session_state.plate = pd.DataFrame('', index=rows, columns=cols)
        st.session_state.colors = pd.DataFrame('white', index=rows, columns=cols)
        st.session_state.notes = pd.DataFrame('', index=rows, columns=cols)

    plate = st.session_state.plate
    colors = st.session_state.colors
    notes = st.session_state.notes

    # Sidebar Controls
    with st.sidebar:
        st.header("Define Compounds")
        compounds = [st.text_input(f"Compound {i+1}") for i in range(4)]

        st.header("🎨 Customize Wells")
        selection_mode = st.radio("Selection Mode:", ["Single Wells", "Entire Rows", "Entire Columns"])

        if selection_mode == "Single Wells":
            selected_wells = st.multiselect("Select wells:", well_ids)
        elif selection_mode == "Entire Rows":
            selected_rows = st.multiselect("Select row(s):", rows)
            selected_wells = [f"{r}{c}" for r in selected_rows for c in cols]
        else:
            selected_cols = st.multiselect("Select column(s):", cols)
            selected_wells = [f"{r}{c}" for r in rows for c in selected_cols]

        selected_compounds = st.multiselect("Select Compounds to Apply:", [c for c in compounds if c])
        note_input = st.text_input("Optional Note:", "")
        custom_color = st.color_picker("Well Color", "#F2D5DA")

        if st.button("✅ Apply to Selected Wells"):
            if selected_wells:
                for well in selected_wells:
                    row, col = well[0], int(well[1:])
                    if row in rows and col in cols:
                        merged_label = "<br>".join(selected_compounds)
                        plate.loc[row, col] = merged_label
                        colors.loc[row, col] = custom_color
                        notes.loc[row, col] = note_input

        if st.button("🧹 Clear Entire Plate"):
            for r in rows:
                for c in cols:
                    plate.loc[r, c] = ''
                    colors.loc[r, c] = 'white'
                    notes.loc[r, c] = ''

    # Plate Visualization
    fig = go.Figure()
    well_padding = 0.15

    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            x_center = j + 1
            y_center = n_rows - i

            if plate.loc[r, c]:
                num_lines = plate.loc[r, c].count('<br>') + 1
                if num_lines <= 1:
                    font_size = 10
                elif num_lines <= 3:
                    font_size = 8
                else:
                    font_size = 6
            else:
                font_size = 8

            fig.add_shape(
                type="circle",
                xref="x",
                yref="y",
                x0=x_center - 0.5 + well_padding,
                y0=y_center - 0.5 + well_padding,
                x1=x_center + 0.5 - well_padding,
                y1=y_center + 0.5 - well_padding,
                fillcolor=colors.loc[r, c],
                line_color="black"
            )

            fig.add_annotation(
                x=x_center,
                y=y_center,
                text=plate.loc[r, c],
                showarrow=False,
                font=dict(family="Times New Roman, serif", size=font_size, color="black"),
                align="center",
                textangle=0
            )

    fig.update_layout(
        width=800,
        height=800 * (n_rows/n_cols),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(
            visible=False,
            range=[0, n_cols + 1]
        ),
        yaxis=dict(
            visible=False,
            range=[0, n_rows + 1],
            scaleanchor="x"
        ),
        plot_bgcolor="#b8c1a1",
        paper_bgcolor="#b8c1a1"
    )

    st.plotly_chart(fig, use_container_width=True)

    # About Me Section
    st.markdown(f"""
    <hr style='margin-top: 50px; margin-bottom: 20px;'>
    <div style='background-color: rgba(255,255,255,0.85); padding: 20px; border-radius: 20px;'>
    <h2 style='text-align: center; font-family: "Consolas", monospace; color: #556b2f;'>About Me</h2>
    <p style='text-align: center; font-family: "Consolas", monospace; color: #556b2f;'>Love science!</p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <div style='text-align: center; font-size: 20px; color: #556b2f; margin-top: 40px;'>
        Crafted with 🎨 by Nisha, a PhD student at NC State University
    </div>
    """, unsafe_allow_html=True)
