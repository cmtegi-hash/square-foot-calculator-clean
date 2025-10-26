import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(page_title="Area Calculator", layout="centered")

# Initialize room list
if "rooms" not in st.session_state:
    st.session_state.rooms = []

# Initialize form fields
for field in ["room_name", "width_input", "length_input", "include_input"]:
    if field not in st.session_state:
        st.session_state[field] = "" if field != "include_input" else True

# Flag to reset fields
if "reset_fields" not in st.session_state:
    st.session_state.reset_fields = False

# Reset fields before rendering widgets
if st.session_state.reset_fields:
    st.session_state.room_name = ""
    st.session_state.width_input = ""
    st.session_state.length_input = ""
    st.session_state.include_input = True
    st.session_state.reset_fields = False
    st.rerun()

st.title("📏 Room Area Calculator (in feet)")
st.markdown("### ➕ Add a Room")

# Form
with st.form("add_room"):
    st.text_input("Room Name", key="room_name")
    st.text_input("Width (ft)", key="width_input")
    st.text_input("Length (ft)", key="length_input")
    st.checkbox("Include in total?", key="include_input")
    submitted = st.form_submit_button("Add")

    if submitted:
        try:
            name = st.session_state.room_name
            width = float(st.session_state.width_input)
            length = float(st.session_state.length_input)
            include = st.session_state.include_input

            if name.strip():
                new_room = {"name": name.strip(), "width": width, "length": length, "include": include}
                st.session_state.rooms.append(new_room)
                st.session_state.reset_fields = True
                st.rerun()
            else:
                st.warning("Room name cannot be empty.")
        except ValueError:
            st.warning("Width and length must be valid numbers.")

# Editable list
st.markdown("### ✏️ Room List")

if st.session_state.rooms:
    df = pd.DataFrame(st.session_state.rooms)
    df["area"] = df["width"] * df["length"]

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        column_config={
            "include": st.column_config.CheckboxColumn("Include?", default=True),
            "area": st.column_config.NumberColumn("Area (ft²)", disabled=True, format="%.2f")
        },
        use_container_width=True
    )

    st.session_state.rooms = edited_df.to_dict(orient="records")

    # Remove excluded rooms
    if st.button("🗑️ Remove rooms not included"):
        st.session_state.rooms = [r for r in st.session_state.rooms if r["include"]]
        st.rerun()

    # Calculate total
    total = sum(r["width"] * r["length"] for r in st.session_state.rooms if r["include"])

    st.divider()
    st.metric("📐 Total Area", f"{total:.2f} ft²")

    # Final summary
    summary = f"Total: {total:.2f} ft²\n\nDetails:\n" + "\n".join(
        f"{r['name']}: {r['width']}ft x {r['length']}ft = {r['width'] * r['length']:.2f} ft²"
        for r in st.session_state.rooms if r["include"]
    )

    st.markdown("### 📋 Final Summary")
    st.text_area("You can copy or review:", summary, height=200)

    # Copy button
    components.html(f"""
        <button style="padding:8px 16px;font-size:16px;" onclick="navigator.clipboard.writeText(`{summary}`)">
            📎 Copy Summary
        </button>
    """, height=50)
else:
    st.info("Add at least one room to begin.")
