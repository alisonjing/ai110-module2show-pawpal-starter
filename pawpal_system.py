from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low" | "medium" | "high"
    category: str = "general"

    def is_high_priority(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str           # "dog" | "cat" | "other"
    age: int = 0
    special_needs: list[str] = field(default_factory=list)

    def get_default_tasks(self) -> list[Task]:
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: str = "08:00"   # "HH:MM"
    pet: Pet | None = None

    def get_time_budget(self) -> int:
        pass


# ---------------------------------------------------------------------------
# ScheduledTask
# ---------------------------------------------------------------------------

@dataclass
class ScheduledTask:
    task: Task
    start_time: str        # "HH:MM"
    end_time: str          # "HH:MM"
    reason: str = ""

    def to_dict(self) -> dict:
        pass


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

@dataclass
class DailyPlan:
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)

    @property
    def total_duration(self) -> int:
        pass

    def display(self) -> list[dict]:
        pass

    def explain(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, tasks: list[Task] | None = None):
        self.owner = owner
        self.tasks: list[Task] = tasks or []

    def add_task(self, task: Task) -> None:
        pass

    def generate_plan(self) -> DailyPlan:
        pass

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fits_in_budget(self, task: Task, remaining: int) -> bool:
        pass
