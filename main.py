from pawpal_system import Task, Pet, Owner, Scheduler

## --- Create two pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

## --- Add tasks to Mochi ---
mochi.add_task(Task(title="Morning walk",  duration_minutes=30, priority="high",   frequency="daily",  category="exercise"))
mochi.add_task(Task(title="Feeding",       duration_minutes=10, priority="high",   frequency="daily",  category="feeding"))
mochi.add_task(Task(title="Bath",          duration_minutes=20, priority="low",    frequency="weekly", category="grooming"))

## --- Add tasks to Luna ---
luna.add_task(Task(title="Litter box",     duration_minutes=5,  priority="high",   frequency="daily",  category="hygiene"))
luna.add_task(Task(title="Feeding",        duration_minutes=10, priority="high",   frequency="daily",  category="feeding"))
luna.add_task(Task(title="Playtime",       duration_minutes=15, priority="medium", frequency="daily",  category="enrichment"))

## --- Create owner and register pets ---
jordan = Owner(name="Jordan", available_minutes=90, preferred_start_time="08:00")
jordan.add_pet(mochi)
jordan.add_pet(luna)

## --- Generate schedule ---
plan = Scheduler(owner=jordan).generate_plan()

## --- Print Today's Schedule ---
print("=" * 45)
print("        TODAY'S SCHEDULE FOR JORDAN")
print("=" * 45)

for row in plan.display():
    print(f"{row['time']}  [{row['pet']}] {row['task']}")
    print(f"              {row['duration']} · {row['priority']} priority · {row['reason']}")
    print()

if plan.skipped_tasks:
    print("--- Skipped (did not fit in budget) ---")
    for pet, task in plan.skipped_tasks:
        print(f"  [{pet.name}] {task.title} ({task.duration_minutes} min, {task.priority})")
    print()

print(f"Total: {plan.total_duration} min scheduled of {jordan.available_minutes} min available.")
print("=" * 45)
