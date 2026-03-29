# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite covers three core scheduling behaviors:

| Area | Test(s) | What is verified |
|---|---|---|
| **Sorting Correctness** | `test_scheduled_tasks_are_in_chronological_order` | All scheduled tasks are returned in ascending `start_time` order — no task is inserted out of sequence |
| **Recurrence Logic** | `test_daily_task_reappears_after_reset` | Marking a `frequency="daily"` task complete removes it from pending; calling `reset_daily_tasks()` restores it, modelling a new task for the following day |
| **Conflict Detection** | `test_scheduler_produces_no_duplicate_start_times`, `test_scheduler_no_overlapping_time_slots` | No two tasks share the same start time, and no task's end time bleeds into the next task's start time |

<div align="center"><img src="27Tests.png" alt="Testing" width="100%"></div>

Confidence Level: ★★★★☆ (4/5)

27/27 tests pass. Here's the reasoning behind the rating:

| Factor | Assessment |
|---|---|
| **Core logic** | All task, pet, owner, and scheduler behaviors verified — strong foundation |
| **Happy-path coverage** | Sorting, recurrence, conflict detection all confirmed working |
| **Input validation** | Invalid priority, frequency, duration, and budget all raise correctly |
| **What keeps it from 5 stars** | No tests for multi-pet conflict detection, `weekly` task reset isolation, midnight-rollover edge cases, or the Streamlit UI layer — gaps identified in `Phase4_planning.md` remain untested |

| Layer | Tests | Result |
|---|---|---|
| Task model | 8 | All pass |
| Pet model | 5 | All pass |
| Owner model | 3 | All pass |
| Scheduler / DailyPlan | 8 | All pass |
| Sorting correctness | 1 | All pass |
| Recurrence logic | 1 | All pass |
| Conflict detection | 2 | All pass |
| **Total** | **27** | **27/27** |


