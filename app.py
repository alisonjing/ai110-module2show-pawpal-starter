import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ---------------------------------------------------------------------------
# Session state vault — initialise keys once, persist across every rerun
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None   # will hold the Owner object after setup

if "pet" not in st.session_state:
    st.session_state.pet = None     # will hold the Pet object after setup

# ---------------------------------------------------------------------------
# Step 1 — Add a Pet (creates Owner + Pet, stores both in session state)
# ---------------------------------------------------------------------------
st.subheader("Step 1: Add a Pet")

with st.form("setup_form"):
    owner_name  = st.text_input("Your name", value="Jordan")
    available   = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=90)
    start_time  = st.text_input("Preferred start time (HH:MM)", value="08:00")
    pet_name    = st.text_input("Pet name", value="Mochi")
    species     = st.selectbox("Species", ["dog", "cat", "other"])
    use_default = st.checkbox("Load default tasks for this species", value=True)
    saved       = st.form_submit_button("Save")

if saved:
    # Build Pet via Pet() and optionally call load_default_tasks()
    pet = Pet(name=pet_name, species=species)
    if use_default:
        pet.load_default_tasks()

    # Build Owner via Owner() and call add_pet()
    owner = Owner(name=owner_name, available_minutes=int(available), preferred_start_time=start_time)
    owner.add_pet(pet)

    # Store both objects in the session state vault
    st.session_state.owner = owner
    st.session_state.pet   = pet
    st.success(f"Saved! Owner: {owner_name}  ·  Pet: {pet_name} ({species})")

# ---------------------------------------------------------------------------
# Step 2 — Schedule a Task (only visible once an owner exists)
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
        add_task = st.form_submit_button("Add task")

    if add_task:
        # Build a real Task object and call pet.add_task()
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
        )
        st.session_state.pet.add_task(new_task)
        st.success(f"Added: {task_title}")

    # Display current task list from the Pet object in session state
    all_tasks = [t.to_dict() for t in st.session_state.pet.tasks]
    if all_tasks:
        st.write(f"**{st.session_state.pet.name}'s tasks ({len(all_tasks)}):**")
        st.table(all_tasks)
    else:
        st.info("No tasks yet — add one above.")

    # ---------------------------------------------------------------------------
    # Step 3 — See Today's Tasks (generate and display the schedule)
    # ---------------------------------------------------------------------------
    st.divider()
    st.subheader("Step 3: See Today's Tasks")

    if st.button("Generate schedule"):
        # Call Scheduler.generate_plan() with the Owner from session state
        scheduler = Scheduler(owner=st.session_state.owner)
        plan = scheduler.generate_plan()

        if plan.scheduled_tasks:
            st.success(f"{len(plan.scheduled_tasks)} tasks scheduled · {plan.total_duration} min used "
                       f"of {st.session_state.owner.available_minutes} min available")
            st.table(plan.display())
            with st.expander("Why was each task chosen?"):
                st.markdown(plan.explain())
        else:
            st.warning("No tasks to schedule — add some tasks first.")

        if plan.skipped_tasks:
            skipped_names = ", ".join(t.title for _, t in plan.skipped_tasks)
            st.info(f"Skipped (didn't fit in budget): {skipped_names}")
