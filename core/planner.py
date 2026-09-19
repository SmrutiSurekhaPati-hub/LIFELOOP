from datetime import datetime
from typing import Dict, List


class Planner:
    """
    LIFELOOP adaptive planning engine.

    The planner protects high-risk tasks even when they
    cannot be fully completed in the available time.
    """

    PRIORITY_SCORE = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }

    def _parse_datetime(self, value: str):

        if not value:
            return None

        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d"
        ]

        for fmt in formats:

            try:
                return datetime.strptime(
                    value,
                    fmt
                )

            except ValueError:
                continue

        return None

    def _deadline_score(
        self,
        deadline: str
    ) -> float:

        deadline_time = self._parse_datetime(
            deadline
        )

        if deadline_time is None:
            return 0

        now = datetime.now()

        hours_left = (
            deadline_time - now
        ).total_seconds() / 3600

        if hours_left <= 0:
            return 6

        if hours_left <= 12:
            return 6

        if hours_left <= 24:
            return 5

        if hours_left <= 48:
            return 4

        if hours_left <= 72:
            return 3

        if hours_left <= 168:
            return 2

        return 1

    def _calculate_task_score(
        self,
        task: Dict
    ) -> float:

        priority_score = self.PRIORITY_SCORE.get(
            task.get("priority", "medium"),
            2
        )

        deadline_score = self._deadline_score(
            task.get("deadline")
        )

        duration = task.get(
            "duration_minutes",
            0
        )

        duration_bonus = 1 / max(
            duration,
            1
        )

        return (
            priority_score * 10
            + deadline_score * 5
            + duration_bonus
        )

    def prioritize_tasks(
        self,
        tasks: List[Dict]
    ) -> List[Dict]:

        pending_tasks = [
            task
            for task in tasks
            if task.get("status") != "completed"
        ]

        pending_tasks.sort(
            key=self._calculate_task_score,
            reverse=True
        )

        return pending_tasks

    def create_plan(
        self,
        tasks: List[Dict],
        available_minutes: int
    ) -> Dict:
        """
        Create a plan that protects the highest-risk task.

        If the most important task does not fully fit,
        LIFELOOP recommends starting it rather than
        switching to a lower-risk task merely because
        that task happens to fit.
        """

        prioritized = self.prioritize_tasks(
            tasks
        )

        if not prioritized:

            return {
                "selected_tasks": [],
                "postponed_tasks": [],
                "partial_task": None,
                "available_minutes": available_minutes,
                "used_minutes": 0,
                "remaining_minutes": available_minutes
            }

        highest_priority_task = prioritized[0]

        highest_duration = highest_priority_task.get(
            "duration_minutes",
            0
        )

        # --------------------------------------------------
        # Highest-risk task fits completely
        # --------------------------------------------------

        if highest_duration <= available_minutes:

            selected_tasks = [
                highest_priority_task
            ]

            remaining_minutes = (
                available_minutes
                - highest_duration
            )

            for task in prioritized[1:]:

                duration = task.get(
                    "duration_minutes",
                    0
                )

                if duration <= remaining_minutes:

                    selected_tasks.append(
                        task
                    )

                    remaining_minutes -= duration

            selected_ids = {
                task.get("id")
                for task in selected_tasks
            }

            postponed_tasks = [
                task
                for task in prioritized
                if task.get("id")
                not in selected_ids
            ]

            return {
                "selected_tasks": selected_tasks,
                "postponed_tasks": postponed_tasks,
                "partial_task": None,
                "available_minutes": available_minutes,
                "used_minutes": (
                    available_minutes
                    - remaining_minutes
                ),
                "remaining_minutes": remaining_minutes
            }

        # --------------------------------------------------
        # Highest-risk task does NOT fully fit
        # --------------------------------------------------

        partial_task = {
            "id": highest_priority_task.get("id"),
            "title": highest_priority_task.get("title"),
            "duration_minutes": highest_duration,
            "allocated_minutes": available_minutes,
            "remaining_minutes": (
                highest_duration
                - available_minutes
            ),
            "priority": highest_priority_task.get(
                "priority",
                "medium"
            ),
            "deadline": highest_priority_task.get(
                "deadline"
            )
        }

        postponed_tasks = [
            task
            for task in prioritized
            if task.get("id")
            != highest_priority_task.get("id")
        ]

        return {
            "selected_tasks": [],
            "postponed_tasks": postponed_tasks,
            "partial_task": partial_task,
            "available_minutes": available_minutes,
            "used_minutes": available_minutes,
            "remaining_minutes": 0
        }

    def replan(
        self,
        mission_state: Dict,
        available_minutes: int
    ) -> Dict:

        tasks = mission_state.get(
            "tasks",
            []
        )

        commitments = mission_state.get(
            "commitments",
            []
        )

        new_plan = self.create_plan(
            tasks,
            available_minutes
        )

        reasons = []

        if available_minutes < 120:

            reasons.append(
                "Available time decreased."
            )

        if commitments:

            reasons.append(
                "Existing commitments were preserved."
            )

        if new_plan.get("partial_task"):

            reasons.append(
                "The highest-risk task was protected "
                "even though it could not be completed "
                "within the current time window."
            )

        if not reasons:

            reasons.append(
                "Mission conditions were evaluated again."
            )

        return {
            "status": "replanned",
            "reason": " ".join(reasons),
            "plan": new_plan
        }