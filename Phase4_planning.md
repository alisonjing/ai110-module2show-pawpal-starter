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
