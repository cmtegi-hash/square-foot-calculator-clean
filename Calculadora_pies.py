import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ======================================================
# Configuración de la página
# ======================================================
st.set_page_config(page_title="Area & Stairs Calculator", layout="centered")
FLOORS = ["Basement", "Floor 1", "Floor 2", "Floor 3"]

# ======================================================
# Estado de sesión
# ======================================================
if "rooms" not in st.session_state:
    st.session_state.rooms = []

if "stairs" not in st.session_state:
    st.session_state.stairs = []

# Campos de Rooms
for field in ["room_name", "floor_input", "width_input", "length_input", "include_input"]:
    if field not in st.session_state:
        st.session_state[field] = True if field == "include_input" else "Basement" if field=="floor_input" else ""

# Campos de Stairs
for field in ["stair_from", "stair_to", "steps_input", "has_landing", "landing_width_input", "landing_length_input"]:
    if field not in st.session_state:
        if field == "has_landing":
            st.session_state[field] = True
        elif field in ["stair_from", "stair_to"]:
            st.session_state[field] = "Floor 1"
        else:
            st.session_state[field] = ""

if "reset_room_fields" not in st.session_state:
    st.session_state.reset_room_fields = False

if "reset_stair_fields" not in st.session_state:
    st.session_state.reset_stair_fields = False

# ======================================================
# Reset forms
# ======================================================
if st.session_state.reset_room_fields:
    st.session_state.room_name = ""
    st.session_state.floor_input = "Basement"
    st.session_state.width_input = ""
    st.session_state.length_input = ""
    st.session_state.include_input = True
    st.session_state.reset_room_fields = False
    st.rerun()

if st.session_state.reset_stair_fields:
    st.session_state.stair_from = "Floor 1"
    st.session_state.stair_to = "Floor 2"
    st.session_state.steps_input = ""
    st.session_state.has_landing = True
    st.session_state.landing_width_input = ""
    st.session_state.landing_length_input = ""
    st.session_state.reset_stair_fields = False
    st.rerun()

# ======================================================
# UI – Rooms
# ======================================================
st.title("📐 Area & Stairs Calculator")
st.markdown("## ➕ Add Room Section")

with st.form("add_room"):
    st.text_input("Room Name", key="room_name")
    st.selectbox("Floor", FLOORS, key="floor_input")
    st.text_input("Width (ft)", key="width_input")
    st.text_input("Length (ft)", key="length_input")
    st.checkbox("Include in total?", key="include_input")
    submitted = st.form_submit_button("Add Room Section")

    if submitted:
        try:
            name = st.session_state.room_name.strip()
            width = float(st.session_state.width_input)
            length = float(st.session_state.length_input)

            if name:
                st.session_state.rooms.append({
                    "name": name,
                    "floor": st.session_state.floor_input,
                    "width": width,
                    "length": length,
                    "include": st.session_state.include_input
                })
                st.session_state.reset_room_fields = True
                st.rerun()
            else:
                st.warning("Room name cannot be empty.")
        except ValueError:
            st.warning("Width and length must be valid numbers.")

# ======================================================
# Editable Rooms
# ======================================================
st.markdown("### ✏️ Room Sections")
if st.session_state.rooms:
    rooms_df = pd.DataFrame(st.session_state.rooms)
    rooms_df["area"] = rooms_df["width"] * rooms_df["length"]

    edited_rooms = st.data_editor(
        rooms_df,
        num_rows="dynamic",
        column_config={
            "include": st.column_config.CheckboxColumn("Include?", default=True),
            "area": st.column_config.NumberColumn("Area (ft²)", disabled=True, format="%d")
        },
        use_container_width=True
    )

    st.session_state.rooms = edited_rooms.to_dict(orient="records")

    if st.button("🗑️ Remove rooms not included"):
        st.session_state.rooms = [r for r in st.session_state.rooms if r["include"]]
        st.rerun()
else:
    edited_rooms = pd.DataFrame()

# ======================================================
# UI – Stairs
# ======================================================
st.markdown("## 🪜 Add Stairs")

with st.form("add_stairs"):
    st.selectbox("From Floor", FLOORS, key="stair_from")
    st.selectbox("To Floor", FLOORS, key="stair_to")
    st.text_input("Total Steps", key="steps_input")
    st.checkbox("Has Landing?", key="has_landing")
    if st.session_state.has_landing:
        st.text_input("Landing Width (ft)", key="landing_width_input")
        st.text_input("Landing Length (ft)", key="landing_length_input")

    submitted_stairs = st.form_submit_button("Add Stairs")

    if submitted_stairs:
        try:
            steps = int(st.session_state.steps_input)
            landing_area = 0
            if st.session_state.has_landing:
                lw = float(st.session_state.landing_width_input)
                ll = float(st.session_state.landing_length_input)
                landing_area = int(round(lw * ll))  # redondeado a entero

            st.session_state.stairs.append({
                "name": f"{st.session_state.stair_from} → {st.session_state.stair_to}",
                "from": st.session_state.stair_from,
                "to": st.session_state.stair_to,
                "steps": steps,
                "landing_area": landing_area
            })
            st.session_state.reset_stair_fields = True
            st.rerun()
        except ValueError:
            st.warning("Steps must be integer and landing width/length must be numbers.")

# ======================================================
# Editable Stairs
# ======================================================
st.markdown("### ✏️ Stairs List")
if st.session_state.stairs:
    stairs_df = pd.DataFrame(st.session_state.stairs)

    edited_stairs = st.data_editor(
        stairs_df,
        num_rows="dynamic",
        column_config={
            "steps": st.column_config.NumberColumn("Steps", format="%d"),
            "landing_area": st.column_config.NumberColumn("Landing Area (ft²)", format="%d")
        },
        use_container_width=True
    )

    st.session_state.stairs = edited_stairs.to_dict(orient="records")
else:
    edited_stairs = pd.DataFrame()

# ======================================================
# Calculations
# ======================================================
room_area_total = 0
if not edited_rooms.empty:
    included_rooms = edited_rooms[edited_rooms["include"]].copy()
    included_rooms["area"] = (included_rooms["width"] * included_rooms["length"]).round().astype(int)
    room_area_total = included_rooms["area"].sum()

stairs_steps_total = 0
stairs_landing_total = 0
if not edited_stairs.empty:
    stairs_steps_total = edited_stairs["steps"].sum()
    stairs_landing_total = edited_stairs["landing_area"].sum()

grand_total_area = room_area_total + stairs_landing_total

# ======================================================
# Metrics
# ======================================================
st.divider()
st.metric("📐 Total Area (including landings)", f"{grand_total_area} ft²")
st.metric("🪜 Total Steps", stairs_steps_total)

# ======================================================
# Summary
# ======================================================
summary_lines = [
    f"Total Area: {grand_total_area} ft²",
    f"Total Steps: {stairs_steps_total}\n"
]

# Agrupar y mostrar habitaciones
if not edited_rooms.empty:
    grouped_rooms = included_rooms.groupby(["floor", "name"], as_index=False)["area"].sum()
    floor_order = {f: i for i, f in enumerate(FLOORS)}
    grouped_rooms["floor_order"] = grouped_rooms["floor"].map(floor_order)
    grouped_rooms = grouped_rooms.sort_values(["floor_order", "name"])

    for floor in FLOORS:
        floor_data = grouped_rooms[grouped_rooms["floor"] == floor]
        if not floor_data.empty:
            summary_lines.append(f"{floor}:")
            for _, row in floor_data.iterrows():
                summary_lines.append(f"{row['name'].capitalize()}: {row['area']} ft²")
            summary_lines.append("")

# Mostrar escaleras ordenadas por piso de origen
if not edited_stairs.empty:
    stairs_df["from_order"] = stairs_df["from"].map({f: i for i, f in enumerate(FLOORS)})
    stairs_df = stairs_df.sort_values("from_order")
    summary_lines.append("Stairs:")
    for _, row in stairs_df.iterrows():
        line = f"{row['name']}: {row['steps']} steps"
        if row["landing_area"] > 0:
            line += f", landing {row['landing_area']} ft²"
        summary_lines.append(line)
    summary_lines.append("")
    summary_lines.append(f"Total landing area: {stairs_landing_total} ft²")

summary = "\n".join(summary_lines).strip()

# ======================================================
# Summary text area + Copy button
# ======================================================
st.markdown("## 📋 Final Summary")
st.text_area("You can copy or review:", summary, height=300)

components.html(
    f"""
    <button
        id="copyBtn"
        style="
            padding:8px 16px;
            font-size:16px;
            background-color:#1f77b4;
            color:white;
            border:none;
            border-radius:4px;
            cursor:pointer;
        "
        onclick="
            navigator.clipboard.writeText(`{summary}`);
            const btn = document.getElementById('copyBtn');
            btn.innerText = '✓ Copied';
            btn.style.backgroundColor = '#2ca02c';
        "
    >
        📎 Copy Summary
    </button>
    """,
    height=50
)
