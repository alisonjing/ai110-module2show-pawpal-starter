## Phase 4: Algorithmic Layer
In this phase, you'll test and verify that your PawPal+ system works as intended. You'll write and run simple tests to confirm that your classes, algorithms, and scheduling logic behave correctly, and use AI to help generate, explain, and review those tests.

### Step 1: Plan What to Test
**Review your pawpal_system.py and list 3–5 core behaviors to verify.**

Here's an honest review of where the logic is manual or overly simple:

1. Tasks are hardcoded, not loaded from defaults
Every task is typed out by hand. In the real app a user picks a species and gets defaults automatically via load_default_tasks() — but main.py never calls it. The demo doesn't test that path at all.


**What main.py does (manual)**
mochi.add_task(Task(title="Morning walk", duration_minutes=30, ...))

**What the app actually does**
mochi.load_default_tasks()   # never called here

2. The time budget is never tight enough to show real tradeoffs
With 90 minutes and only 6 tasks totalling 90 minutes exactly, nothing ever gets skipped. The scheduler's most important behavior — choosing what to drop and force-including high-priority overruns — is never exercised in the happy path.

3. No multi-day simulation
reset_daily_tasks() exists but is never called. The demo only shows one snapshot. There's no "mark some tasks complete → reset → run again" loop to show that the system actually tracks state across a day.

4. Both pets have balanced, clean task lists
Mochi has 3 tasks, Luna has 3 tasks, no conflicts, no special needs, no medication. The demo never tests:

A pet with special_needs that injects a medication task
Two high-priority tasks that both exceed the remaining budget
A pet with zero tasks

5. The owner's preferred_start_time is always "08:00"
There's no test showing that changing the start time actually shifts all the scheduled slots. The feature exists but the demo doesn't verify it.

6. Output format isn't checked, just printed
The reason field on every row is printed but never inspected. If generate_plan() returned an empty reason string or wrong time, the demo would still look fine visually.
  
Summary
| Area | What's missing |
|---|---|
| Data setup | `load_default_tasks()` never called |
| Budget | Always fits perfectly — skipping logic never triggered |
| State | No mark-complete → reset → re-run cycle |
| Edge cases | No special needs, no over-budget high-priority clash |
| Start time | Never varied to verify time shifting works |
| Output | Printed but not verified programmatically |

### Step 2: Build the Automated Test Suite

**1. The sorting correctness test is already in place at line 163. Here's how it works:**

test_scheduled_tasks_are_in_chronological_order (lines 163–173)


def test_scheduled_tasks_are_in_chronological_order():
    plan = Scheduler(owner=make_owner(minutes=90)).generate_plan()
    start_times = [
        datetime.strptime(st.start_time, "%H:%M")
        for st in plan.scheduled_tasks
    ]
    assert start_times == sorted(start_times)
What it verifies:

Generates a full plan with 90 minutes of budget (enough to schedule all three tasks: Morning walk → Feeding → Playtime)
Parses each start_time string ("HH:MM") into a real datetime object so string comparison pitfalls (e.g. "09:00" < "10:00" but "9:00" > "10:00") are avoided
Asserts the list equals its own sorted version — any out-of-order slot will fail with a message showing the actual time sequence
Why this exercises the right behavior: generate_plan() assigns times sequentially by walking current_dt forward, so the sort order of the output is entirely driven by the priority sort in _sort_by_priority(). The test catches any regression where a task is inserted at the wrong position and breaks the timeline.

**2. Build the Automated Test Suite**

The recurrence logic test is already written at lines 178–196. Here's a breakdown of exactly what it does and why each assertion matters:

test_daily_task_reappears_after_reset (lines 178–196)


def test_daily_task_reappears_after_reset():
    owner = make_owner()
    scheduler = Scheduler(owner=owner)

    # Step 1 – complete the task
    scheduler.mark_complete("Mochi", "Feeding")
    pending_after_complete = [t.title for _, t in scheduler.get_all_pending()]
    assert "Feeding" not in pending_after_complete

    # Step 2 – simulate the next day
    scheduler.reset_daily_tasks()
    pending_after_reset = [t.title for _, t in scheduler.get_all_pending()]
    assert "Feeding" in pending_after_reset

| Step | Real-world action | Code under test |
|---|---|---|
| 1 | Owner marks feeding done today | `scheduler.mark_complete("Mochi", "Feeding")` |
| 2 | Intermediate check | `get_all_pending()` — confirms task is gone, not still pending |
| 3 | Midnight rollover / new day | `reset_daily_tasks()` — restores `completed = False` on all `frequency="daily"` tasks |


**Why two assertions, not one:**

The first assert (task is absent after completion) guards against a silent no-op — if mark_complete did nothing, the second assert would still pass and the test would give a false green. Checking both states makes the test meaningful in both directions.

What reset_daily_tasks() deliberately does not do:

It only resets frequency="daily" tasks. A "weekly" task that was completed will remain completed. You can verify this with a companion test if needed — Bath (weekly) should stay completed after reset while Feeding (daily) reappears.


**3. Conflict Detection: Verify that the Scheduler flags duplicate times.**
Two conflict detection tests are in place at lines 201–227. Here's how each one works:

Test 1 — test_scheduler_produces_no_duplicate_start_times (lines 201–211)

start_times = [st.start_time for st in plan.scheduled_tasks]
assert len(start_times) == len(set(start_times))
Collects every start_time string, deduplicates it with set(), and asserts the count is unchanged. If any two tasks share the same start time, the set will be shorter than the list and the test fails — printing the full list so the duplicate is immediately visible.

Test 2 — test_scheduler_no_overlapping_time_slots (lines 214–227)


for i in range(len(slots) - 1):
    end_dt   = datetime.strptime(slots[i].end_time,       "%H:%M")
    start_dt = datetime.strptime(slots[i + 1].start_time, "%H:%M")
    assert end_dt <= start_dt
Walks every consecutive pair and checks that task i's end_time does not bleed into task i+1's start_time. It uses real datetime objects (not raw strings) to avoid lexicographic comparison bugs.

Why two tests instead of one:
| Test | What it catches |
|---|---|
| Duplicate start times | Two tasks stamped with the exact same `"HH:MM"` — a direct collision |
| Overlapping slots | Task A ends at `09:30`, Task B starts at `09:15` — a partial overlap that the first test would miss |
