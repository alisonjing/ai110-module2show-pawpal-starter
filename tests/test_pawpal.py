import pytest
from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


## Task tests

def test_mark_complete_changes_task_status():
    task = Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True

def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high", frequency="daily"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily"))
    assert len(pet.tasks) == 2

def test_task_is_high_priority():
    task = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily")
    assert task.is_high_priority() is True

def test_task_is_not_high_priority():
    task = Task(title="Bath", duration_minutes=20, priority="low", frequency="weekly")
    assert task.is_high_priority() is False

def test_task_invalid_priority_raises():
    with pytest.raises(ValueError):
        Task(title="Bad", duration_minutes=10, priority="urgent", frequency="daily")

def test_task_invalid_frequency_raises():
    with pytest.raises(ValueError):
        Task(title="Bad", duration_minutes=10, priority="high", frequency="sometimes")

def test_task_invalid_duration_raises():
    with pytest.raises(ValueError):
        Task(title="Bad", duration_minutes=0, priority="high", frequency="daily")

def test_task_to_dict_keys():
    task = Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily", category="feeding")
    d = task.to_dict()
    assert set(d.keys()) == {"title", "duration_minutes", "priority", "frequency", "category", "completed"}



## Pet tests

def test_pet_add_and_get_pending_tasks():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high", frequency="daily"))
    assert len(pet.get_pending_tasks()) == 1

def test_pet_mark_complete_removes_from_pending():
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily")
    pet.add_task(task)
    task.mark_complete()
    assert len(pet.get_pending_tasks()) == 0
    assert len(pet.get_completed_tasks()) == 1

def test_pet_remove_task():
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily"))
    pet.remove_task("Feeding")
    assert len(pet.tasks) == 0

def test_pet_load_default_tasks_dog():
    pet = Pet(name="Rex", species="dog")
    pet.load_default_tasks()
    titles = [t.title for t in pet.tasks]
    assert "Morning walk" in titles
    assert "Feeding" in titles

def test_pet_load_default_tasks_injects_medication():
    pet = Pet(name="Mochi", species="dog", special_needs=["daily medication"])
    pet.load_default_tasks()
    titles = [t.title for t in pet.tasks]
    assert any("Medication" in t for t in titles)


## Owner tests

def test_owner_invalid_budget_raises():
    with pytest.raises(ValueError):
        Owner(name="Jordan", available_minutes=0)

def test_owner_add_and_remove_pet():
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Mochi", species="dog"))
    assert len(owner.pets) == 1
    owner.remove_pet("Mochi")
    assert len(owner.pets) == 0

def test_owner_get_all_pending_tasks_across_pets():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi.add_task(Task(title="Walk",    duration_minutes=30, priority="high", frequency="daily"))
    luna.add_task( Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    assert len(owner.get_all_pending_tasks()) == 2


# Scheduler tests

def make_owner(minutes: int = 90) -> Owner:
    owner = Owner(name="Jordan", available_minutes=minutes, preferred_start_time="08:00")
    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high",   frequency="daily"))
    mochi.add_task(Task(title="Feeding",      duration_minutes=10, priority="high",   frequency="daily"))
    mochi.add_task(Task(title="Playtime",     duration_minutes=15, priority="low",    frequency="daily"))
    owner.add_pet(mochi)
    return owner

def test_scheduler_generates_daily_plan():
    plan = Scheduler(owner=make_owner()).generate_plan()
    assert isinstance(plan, DailyPlan)

def test_scheduler_high_priority_tasks_always_scheduled():
    plan = Scheduler(owner=make_owner(minutes=5)).generate_plan()
    scheduled_titles = [st.task.title for st in plan.scheduled_tasks]
    assert "Morning walk" in scheduled_titles
    assert "Feeding" in scheduled_titles

def test_scheduler_low_priority_skipped_when_over_budget():
    plan = Scheduler(owner=make_owner(minutes=40)).generate_plan()
    skipped_titles = [t.title for _, t in plan.skipped_tasks]
    assert "Playtime" in skipped_titles

def test_scheduler_respects_preferred_start_time():
    owner = make_owner()
    owner.preferred_start_time = "09:30"
    plan = Scheduler(owner=owner).generate_plan()
    assert plan.scheduled_tasks[0].start_time == "09:30"

def test_scheduler_mark_complete():
    owner = make_owner()
    scheduler = Scheduler(owner=owner)
    scheduler.mark_complete("Mochi", "Feeding")
    pending_titles = [t.title for _, t in scheduler.get_all_pending()]
    assert "Feeding" not in pending_titles

def test_scheduler_reset_daily_tasks():
    owner = make_owner()
    scheduler = Scheduler(owner=owner)
    scheduler.mark_complete("Mochi", "Feeding")
    scheduler.reset_daily_tasks()
    pending_titles = [t.title for _, t in scheduler.get_all_pending()]
    assert "Feeding" in pending_titles

def test_plan_total_duration():
    plan = Scheduler(owner=make_owner(minutes=90)).generate_plan()
    expected = sum(st.task.duration_minutes for st in plan.scheduled_tasks)
    assert plan.total_duration == expected


# --- Sorting Correctness ---------------------------------------------------

def test_scheduled_tasks_are_in_chronological_order():
    """Scheduled tasks must be emitted in ascending start-time order."""
    plan = Scheduler(owner=make_owner(minutes=90)).generate_plan()
    start_times = [
        datetime.strptime(st.start_time, "%H:%M")
        for st in plan.scheduled_tasks
    ]
    assert start_times == sorted(start_times), (
        "Scheduled tasks are not in chronological order: "
        + str([st.start_time for st in plan.scheduled_tasks])
    )


# --- Recurrence Logic -------------------------------------------------------

def test_daily_task_reappears_after_reset():
    """
    Marking a daily task complete then calling reset_daily_tasks() should
    restore it to pending — modelling 'a new instance for the following day'.
    """
    owner = make_owner()
    scheduler = Scheduler(owner=owner)

    scheduler.mark_complete("Mochi", "Feeding")
    pending_after_complete = [t.title for _, t in scheduler.get_all_pending()]
    assert "Feeding" not in pending_after_complete, (
        "Feeding should be absent from pending after mark_complete()"
    )

    scheduler.reset_daily_tasks()
    pending_after_reset = [t.title for _, t in scheduler.get_all_pending()]
    assert "Feeding" in pending_after_reset, (
        "Feeding should reappear in pending after reset_daily_tasks() (daily recurrence)"
    )


# --- Conflict Detection -----------------------------------------------------

def test_scheduler_produces_no_duplicate_start_times():
    """
    The scheduler must not assign the same start time to two different tasks.
    Duplicate start times indicate a scheduling conflict.
    """
    owner = make_owner(minutes=90)
    plan = Scheduler(owner=owner).generate_plan()
    start_times = [st.start_time for st in plan.scheduled_tasks]
    assert len(start_times) == len(set(start_times)), (
        "Duplicate start times detected — scheduling conflict: " + str(start_times)
    )


def test_scheduler_no_overlapping_time_slots():
    """
    Each task's end time must be <= the next task's start time.
    Any overlap is a scheduling conflict.
    """
    plan = Scheduler(owner=make_owner(minutes=90)).generate_plan()
    slots = plan.scheduled_tasks
    for i in range(len(slots) - 1):
        end_dt   = datetime.strptime(slots[i].end_time,       "%H:%M")
        start_dt = datetime.strptime(slots[i + 1].start_time, "%H:%M")
        assert end_dt <= start_dt, (
            f"Overlap detected: '{slots[i].task.title}' ends at {slots[i].end_time} "
            f"but '{slots[i+1].task.title}' starts at {slots[i+1].start_time}"
        )
