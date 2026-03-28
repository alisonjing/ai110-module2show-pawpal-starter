from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta


VALID_PRIORITIES  = {"low", "medium", "high"}
VALID_FREQUENCIES = {"daily", "weekly", "as-needed"}
PRIORITY_RANK     = {"high": 3, "medium": 2, "low": 1}


# ---------------------------------------------------------------------------
# Task — a single care activity belonging to a Pet
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    frequency: str          # "daily" | "weekly" | "as-needed"
    category: str = "general"
    completed: bool = False

    def __post_init__(self) -> None:
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got '{self.priority}'")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}, got '{self.frequency}'")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")

    def mark_complete(self) -> None:
        self.completed = True

    def mark_incomplete(self) -> None:
        self.completed = False

    def is_high_priority(self) -> bool:
        return self.priority == "high"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "category": self.category,
            "completed": self.completed,
        }


# ---------------------------------------------------------------------------
# Pet — stores pet details and owns a list of Tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str            # "dog" | "cat" | "other"
    age: int = 0
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.completed]

    def load_default_tasks(self) -> None:
        """Populate tasks with species-appropriate defaults."""
        defaults = _SPECIES_DEFAULTS.get(self.species, _SPECIES_DEFAULTS["other"])
        for t in defaults:
            self.tasks.append(Task(**t))
        for need in self.special_needs:
            if "med" in need.lower():
                self.tasks.append(Task(
                    title=f"Medication – {need}",
                    duration_minutes=5,
                    priority="high",
                    frequency="daily",
                    category="medication",
                ))


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and provides access to all their tasks
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: str = "08:00"   # "HH:MM"
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.available_minutes <= 0:
            raise ValueError("available_minutes must be greater than 0")

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        self.pets = [p for p in self.pets if p.name != name]

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return only incomplete tasks across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.get_pending_tasks()]

    def get_time_budget(self) -> int:
        return self.available_minutes


# ---------------------------------------------------------------------------
# ScheduledTask — one time-blocked slot in the final plan
# ---------------------------------------------------------------------------

@dataclass
class ScheduledTask:
    pet: Pet
    task: Task
    start_time: str         # "HH:MM"
    end_time: str           # "HH:MM"
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "time": f"{self.start_time} – {self.end_time}",
            "pet": self.pet.name,
            "task": self.task.title,
            "category": self.task.category,
            "duration": f"{self.task.duration_minutes} min",
            "priority": self.task.priority,
            "frequency": self.task.frequency,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# DailyPlan — output artifact produced by Scheduler
# ---------------------------------------------------------------------------

@dataclass
class DailyPlan:
    owner: Owner
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[tuple[Pet, Task]] = field(default_factory=list)

    @property
    def total_duration(self) -> int:
        return sum(st.task.duration_minutes for st in self.scheduled_tasks)

    def display(self) -> list[dict]:
        """Return rows ready for st.table() / st.dataframe()."""
        return [st.to_dict() for st in self.scheduled_tasks]

    def explain(self) -> str:
        pet_names = ", ".join(p.name for p in self.owner.pets) or "your pet"
        lines = [f"**{self.owner.name}'s daily plan for {pet_names}**\n"]

        if self.scheduled_tasks:
            lines.append("**Scheduled tasks:**")
            for st in self.scheduled_tasks:
                lines.append(
                    f"- **[{st.pet.name}] {st.task.title}** "
                    f"({st.start_time} – {st.end_time}): {st.reason}"
                )
        else:
            lines.append("No tasks were scheduled.")

        if self.skipped_tasks:
            lines.append("\n**Skipped tasks** (did not fit in the time budget):")
            for pet, task in self.skipped_tasks:
                lines.append(
                    f"- [{pet.name}] {task.title} "
                    f"({task.duration_minutes} min, {task.priority} priority)"
                )

        lines.append(
            f"\n**Total time scheduled:** {self.total_duration} min "
            f"of {self.owner.available_minutes} min available."
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler — the "brain" that retrieves, organizes, and manages tasks
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    # --- Task retrieval -----------------------------------------------------

    def get_all_pending(self) -> list[tuple[Pet, Task]]:
        """Pull every incomplete task from every pet the owner has."""
        return self.owner.get_all_pending_tasks()

    # --- Task management ----------------------------------------------------

    def mark_complete(self, pet_name: str, task_title: str) -> None:
        """Mark a specific task on a specific pet as done."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                for task in pet.tasks:
                    if task.title == task_title:
                        task.mark_complete()
                        return

    def reset_daily_tasks(self) -> None:
        """Reset completion status for all daily tasks (run at start of each day)."""
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.frequency == "daily":
                    task.mark_incomplete()

    # --- Plan generation ----------------------------------------------------

    def generate_plan(self) -> DailyPlan:
        """
        Scheduling logic:
          1. Collect all pending tasks across all pets.
          2. Sort by priority (high → medium → low); use duration as tiebreaker.
          3. Greedily fit tasks into the owner's time budget.
          4. High-priority tasks are force-included even if over budget.
        """
        pending = self.get_all_pending()
        sorted_pairs = self._sort_by_priority(pending)

        remaining = self.owner.get_time_budget()
        current_dt = datetime.strptime(self.owner.preferred_start_time, "%H:%M")

        scheduled: list[ScheduledTask] = []
        skipped: list[tuple[Pet, Task]] = []

        for pet, task in sorted_pairs:
            fits = self._fits_in_budget(task, remaining)

            if fits or task.is_high_priority():
                start_str = current_dt.strftime("%H:%M")
                current_dt += timedelta(minutes=task.duration_minutes)
                end_str = current_dt.strftime("%H:%M")

                if fits:
                    reason = (
                        f"{task.priority.capitalize()} priority, {task.frequency}; "
                        f"fits within remaining {remaining} min."
                    )
                    remaining -= task.duration_minutes
                else:
                    reason = (
                        f"High priority — included even though it exceeds "
                        f"the remaining {remaining} min budget."
                    )
                    remaining = 0

                scheduled.append(ScheduledTask(pet, task, start_str, end_str, reason))
            else:
                skipped.append((pet, task))

        return DailyPlan(owner=self.owner, scheduled_tasks=scheduled, skipped_tasks=skipped)

    # --- Internal helpers ---------------------------------------------------

    def _sort_by_priority(
        self, pairs: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        return sorted(
            pairs,
            key=lambda pt: (PRIORITY_RANK.get(pt[1].priority, 0), -pt[1].duration_minutes),
            reverse=True,
        )

    def _fits_in_budget(self, task: Task, remaining: int) -> bool:
        return task.duration_minutes <= remaining


# ---------------------------------------------------------------------------
# Species default task templates
# ---------------------------------------------------------------------------

_SPECIES_DEFAULTS: dict[str, list[dict]] = {
    "dog": [
        {"title": "Morning walk",  "duration_minutes": 30, "priority": "high",   "frequency": "daily",     "category": "exercise"},
        {"title": "Feeding",       "duration_minutes": 10, "priority": "high",   "frequency": "daily",     "category": "feeding"},
        {"title": "Evening walk",  "duration_minutes": 20, "priority": "medium", "frequency": "daily",     "category": "exercise"},
        {"title": "Playtime",      "duration_minutes": 15, "priority": "low",    "frequency": "daily",     "category": "enrichment"},
        {"title": "Bath",          "duration_minutes": 30, "priority": "low",    "frequency": "weekly",    "category": "grooming"},
    ],
    "cat": [
        {"title": "Feeding",       "duration_minutes": 10, "priority": "high",   "frequency": "daily",     "category": "feeding"},
        {"title": "Litter box",    "duration_minutes":  5, "priority": "high",   "frequency": "daily",     "category": "hygiene"},
        {"title": "Playtime",      "duration_minutes": 15, "priority": "medium", "frequency": "daily",     "category": "enrichment"},
        {"title": "Brushing",      "duration_minutes": 10, "priority": "low",    "frequency": "weekly",    "category": "grooming"},
    ],
    "other": [
        {"title": "Feeding",       "duration_minutes": 10, "priority": "high",   "frequency": "daily",     "category": "feeding"},
        {"title": "Health check",  "duration_minutes": 10, "priority": "medium", "frequency": "as-needed", "category": "health"},
    ],
}
