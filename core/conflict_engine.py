from datetime import datetime
from typing import Dict, List


class ConflictEngine:
    """
    LIFELOOP conflict detection engine.

    Detects:
    - available-time overload
    - deadline collisions
    - task vs commitment conflicts
    """

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

    def check_time_conflicts(
        self,
        tasks: List[Dict],
        available_minutes: int
    ) -> Dict:

        pending_tasks = [
            task
            for task in tasks
            if task.get("status") != "completed"
        ]

        total_required = sum(
            task.get("duration_minutes", 0)
            for task in pending_tasks
        )

        conflicts = []

        if total_required > available_minutes:

            conflicts.append({
                "type": "time_overload",
                "severity": "high",
                "message": (
                    f"You have {total_required} minutes of work "
                    f"but only {available_minutes} minutes available."
                ),
                "required_minutes": total_required,
                "available_minutes": available_minutes
            })

        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts
        }

    def check_deadline_conflicts(
        self,
        tasks: List[Dict]
    ) -> Dict:

        conflicts = []

        tasks_with_deadlines = [
            task
            for task in tasks
            if task.get("deadline")
            and task.get("status") != "completed"
        ]

        for i in range(
            len(tasks_with_deadlines)
        ):

            for j in range(
                i + 1,
                len(tasks_with_deadlines)
            ):

                task_a = tasks_with_deadlines[i]
                task_b = tasks_with_deadlines[j]

                deadline_a = self._parse_datetime(
                    task_a["deadline"]
                )

                deadline_b = self._parse_datetime(
                    task_b["deadline"]
                )

                if deadline_a and deadline_b:

                    difference = abs(
                        (
                            deadline_a - deadline_b
                        ).total_seconds()
                    )

                    if (
                        difference <= 3600
                        and task_a["id"] != task_b["id"]
                    ):

                        conflicts.append({
                            "type": "deadline_collision",
                            "severity": "medium",
                            "tasks": [
                                task_a["title"],
                                task_b["title"]
                            ],
                            "message": (
                                f"'{task_a['title']}' and "
                                f"'{task_b['title']}' have "
                                f"very close deadlines."
                            )
                        })

        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts
        }

    def check_commitment_conflicts(
        self,
        tasks: List[Dict],
        commitments: List[Dict]
    ) -> Dict:

        conflicts = []

        for task in tasks:

            if task.get("status") == "completed":
                continue

            task_deadline = self._parse_datetime(
                task.get("deadline")
            )

            if not task_deadline:
                continue

            for commitment in commitments:

                if commitment.get("status") != "active":
                    continue

                commitment_time = self._parse_datetime(
                    commitment.get("time")
                )

                if not commitment_time:
                    continue

                # If a commitment happens before a task's
                # deadline, the commitment consumes part
                # of the available planning window.
                if commitment_time < task_deadline:

                    conflicts.append({
                        "type": "commitment_pressure",
                        "severity": "medium",
                        "task": task["title"],
                        "commitment": commitment["title"],
                        "message": (
                            f"'{commitment['title']}' occurs before "
                            f"the deadline of '{task['title']}', "
                            f"reducing the available planning time."
                        )
                    })

        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts
        }

    def check_all(
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

        time_result = self.check_time_conflicts(
            tasks,
            available_minutes
        )

        deadline_result = self.check_deadline_conflicts(
            tasks
        )

        commitment_result = (
            self.check_commitment_conflicts(
                tasks,
                commitments
            )
        )

        all_conflicts = (
            time_result["conflicts"]
            + deadline_result["conflicts"]
            + commitment_result["conflicts"]
        )

        return {
            "has_conflict": len(all_conflicts) > 0,
            "total_conflicts": len(all_conflicts),
            "conflicts": all_conflicts
        }