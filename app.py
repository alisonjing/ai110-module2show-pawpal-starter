import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner — powered by smart scheduling.")

st.divider()

# ---------------------------------------------------------------------------
# Session state vault
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

# ---------------------------------------------------------------------------
# Step 1 — Owner & Pet setup
# ---------------------------------------------------------------------------
st.subheader("Step 1: Add a Pet")

with st.form("setup_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        owner_name  = st.text_input("Your name", value="Jordan")
        available   = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=90)
        start_time  = st.text_input("Preferred start time (HH:MM)", value="08:00")
    with col_b:
        pet_name    = st.text_input("Pet name", value="Mochi")
        species     = st.selectbox("Species", ["dog", "cat", "other"])
        use_default = st.checkbox("Load default tasks for this species", value=True)
    saved = st.form_submit_button("💾 Save owner & pet")

if saved:
    pet = Pet(name=pet_name, species=species)
    if use_default:
        pet.load_default_tasks()
    owner = Owner(name=owner_name, available_minutes=int(available), preferred_start_time=start_time)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet   = pet
    st.success(f"Saved! Owner: **{owner_name}** · Pet: **{pet_name}** ({species}) · Budget: **{available} min**")

# ---------------------------------------------------------------------------
# Step 2 — Add tasks
# ---------------------------------------------------------------------------
if st.session_state.owner is not None:
    st.divider()
    st.subheader("Step 2: Schedule a Task")

    with st.form("task_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_title = st.text_input("Task title", value="Evening walk")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        with col4:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        add_task = st.form_submit_button("➕ Add task")

    if add_task:
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
        )
        st.session_state.pet.add_task(new_task)
        st.success(f"Task added: **{task_title}** ({priority} priority, {duration} min)")

    # Task list with colour-coded priority badge
    all_tasks = st.session_state.pet.tasks
    if all_tasks:
        PRIORITY_COLOUR = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        st.markdown(f"**{st.session_state.pet.name}'s tasks ({len(all_tasks)}):**")
        st.dataframe(
            [
                {
                    "": PRIORITY_COLOUR.get(t.priority, "⚪"),
                    "Title": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                    "Category": t.category,
                    "Done": "✅" if t.completed else "⬜",
                }
                for t in all_tasks
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No tasks yet — add one above.")

    # ---------------------------------------------------------------------------
    # Step 3 — Generate schedule
    # ---------------------------------------------------------------------------
    st.divider()
    st.subheader("Step 3: See Today's Tasks")

    if st.button("📅 Generate schedule", use_container_width=True):
        scheduler = Scheduler(owner=st.session_state.owner)
        plan      = scheduler.generate_plan()

        if plan.scheduled_tasks:
            # Summary metrics
            budget   = st.session_state.owner.available_minutes
            used     = plan.total_duration
            skipped  = len(plan.skipped_tasks)
            m1, m2, m3 = st.columns(3)
            m1.metric("Tasks scheduled", len(plan.scheduled_tasks))
            m2.metric("Time used", f"{used} / {budget} min")
            m3.metric("Tasks skipped", skipped)

            st.markdown("#### Today's Schedule")
            PRIORITY_COLOUR = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            sorted_slots = plan.sort_by_time()
            st.dataframe(
                [
                    {
                        "": PRIORITY_COLOUR.get(s.task.priority, "⚪"),
                        "Time": s.start_time + " – " + s.end_time,
                        "Pet": s.pet.name,
                        "Task": s.task.title,
                        "Duration": f"{s.task.duration_minutes} min",
                        "Priority": s.task.priority,
                        "Category": s.task.category,
                    }
                    for s in sorted_slots
                ],
                use_container_width=True,
                hide_index=True,
            )

            # Conflict warnings
            conflicts = plan.detect_conflicts()
            if conflicts:
                st.markdown("#### ⚠️ Conflicts Detected")
                for msg in conflicts:
                    st.warning(msg)
            else:
                st.success("No scheduling conflicts detected.")

            with st.expander("💬 Why was each task chosen?"):
                st.markdown(plan.explain())

        else:
            st.warning("No tasks to schedule — add some tasks in Step 2 first.")

        if plan.skipped_tasks:
            st.markdown("#### Skipped Tasks")
            st.dataframe(
                [
                    {
                        "Pet": p.name,
                        "Task": t.title,
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": t.priority,
                        "Reason": "Did not fit in time budget",
                    }
                    for p, t in plan.skipped_tasks
                ],
                use_container_width=True,
                hide_index=True,
            )
