from datetime import datetime
from typing import Dict, List


class ChangeEngine:

    def _parse_datetime(self, value):
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        value = str(value).strip()

        # Handle common ISO formats
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except ValueError:
            pass

        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
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

    def compare_deadline(
        self,
        old_deadline,
        new_deadline
    ):
        old_time = self._parse_datetime(
            old_deadline
        )

        new_time = self._parse_datetime(
            new_deadline
        )

        if old_time is None or new_time is None:
            return "unknown"

        if new_time < old_time:
            return "earlier"

        if new_time > old_time:
            return "later"

        return "unchanged"

    def compare_time(
        self,
        old_value,
        new_value
    ):
        try:
            old_value = float(old_value)
            new_value = float(new_value)
        except (ValueError, TypeError):
            return "unknown"

        if new_value == old_value:
            return "unchanged"

        if new_value < old_value:
            return "decreased"

        return "increased"

    def analyze_change(
        self,
        previous_mission: Dict,
        current_mission: Dict
    ) -> Dict:

        changes: List[Dict] = []

        if not previous_mission:
            return {
                "changed": False,
                "changes": [],
                "overall_impact": "none",
                "recommended_action": "no_change"
            }

        old_tasks = {
            task.get("id"): task
            for task in previous_mission.get(
                "tasks",
                []
            )
        }

        new_tasks = {
            task.get("id"): task
            for task in current_mission.get(
                "tasks",
                []
            )
        }

        # =================================================
        # TASK ADDED
        # =================================================

        for task_id, task in new_tasks.items():

            if task_id not in old_tasks:

                changes.append({
                    "type": "task_added",
                    "task": task.get("title"),
                    "message": (
                        f"New task '{task.get('title')}' "
                        f"was added to the mission."
                    ),
                    "impact": "medium"
                })

        # =================================================
        # TASK REMOVED
        # =================================================

        for task_id, task in old_tasks.items():

            if task_id not in new_tasks:

                changes.append({
                    "type": "task_removed",
                    "task": task.get("title"),
                    "message": (
                        f"Task '{task.get('title')}' "
                        f"was removed from the mission."
                    ),
                    "impact": "medium"
                })

        # =================================================
        # EXISTING TASK CHANGES
        # =================================================

        for task_id in new_tasks:

            if task_id not in old_tasks:
                continue

            old_task = old_tasks[task_id]
            new_task = new_tasks[task_id]

            task_title = new_task.get(
                "title",
                old_task.get(
                    "title",
                    "Unknown task"
                )
            )

            # -------------------------------------------------
            # DEADLINE
            # -------------------------------------------------

            old_deadline = old_task.get(
                "deadline"
            )

            new_deadline = new_task.get(
                "deadline"
            )

            if old_deadline != new_deadline:

                deadline_change = self.compare_deadline(
                    old_deadline,
                    new_deadline
                )

                if deadline_change == "earlier":

                    changes.append({
                        "type": "deadline_changed",
                        "task": task_title,
                        "message": (
                            f"Deadline for "
                            f"'{task_title}' "
                            f"became earlier."
                        ),
                        "impact": "high"
                    })

                elif deadline_change == "later":

                    changes.append({
                        "type": "deadline_changed",
                        "task": task_title,
                        "message": (
                            f"Deadline for "
                            f"'{task_title}' "
                            f"was extended."
                        ),
                        "impact": "medium"
                    })

                else:

                    changes.append({
                        "type": "deadline_changed",
                        "task": task_title,
                        "message": (
                            f"Deadline for "
                            f"'{task_title}' "
                            f"was changed."
                        ),
                        "impact": "medium"
                    })

            # -------------------------------------------------
            # DURATION
            # -------------------------------------------------

            old_duration = old_task.get(
                "duration_minutes",
                0
            )

            new_duration = new_task.get(
                "duration_minutes",
                0
            )

            if old_duration != new_duration:

                direction = self.compare_time(
                    old_duration,
                    new_duration
                )

                changes.append({
                    "type": "duration_changed",
                    "task": task_title,
                    "message": (
                        f"Duration for '{task_title}' "
                        f"changed from {old_duration} "
                        f"to {new_duration} minutes."
                    ),
                    "impact": (
                        "high"
                        if direction == "increased"
                        else "medium"
                    )
                })

            # -------------------------------------------------
            # PRIORITY
            # -------------------------------------------------

            old_priority = old_task.get(
                "priority",
                "medium"
            )

            new_priority = new_task.get(
                "priority",
                "medium"
            )

            if old_priority != new_priority:

                changes.append({
                    "type": "priority_changed",
                    "task": task_title,
                    "message": (
                        f"Priority for '{task_title}' "
                        f"changed from {old_priority} "
                        f"to {new_priority}."
                    ),
                    "impact": "high"
                })

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            old_status = old_task.get(
                "status",
                "pending"
            )

            new_status = new_task.get(
                "status",
                "pending"
            )

            if old_status != new_status:

                changes.append({
                    "type": "status_changed",
                    "task": task_title,
                    "message": (
                        f"Status for '{task_title}' "
                        f"changed from {old_status} "
                        f"to {new_status}."
                    ),
                    "impact": "medium"
                })

        # =================================================
        # COMMITMENTS
        # =================================================

        old_commitments = {
            commitment.get("id"): commitment
            for commitment in previous_mission.get(
                "commitments",
                []
            )
        }

        new_commitments = {
            commitment.get("id"): commitment
            for commitment in current_mission.get(
                "commitments",
                []
            )
        }

        for commitment_id, commitment in new_commitments.items():

            if commitment_id not in old_commitments:

                changes.append({
                    "type": "commitment_added",
                    "commitment": commitment.get(
                        "title"
                    ),
                    "message": (
                        f"New commitment "
                        f"'{commitment.get('title')}' "
                        f"was added."
                    ),
                    "impact": "medium"
                })

        for commitment_id, commitment in old_commitments.items():

            if commitment_id not in new_commitments:

                changes.append({
                    "type": "commitment_removed",
                    "commitment": commitment.get(
                        "title"
                    ),
                    "message": (
                        f"Commitment "
                        f"'{commitment.get('title')}' "
                        f"was removed."
                    ),
                    "impact": "medium"
                })

        # =================================================
        # OVERALL IMPACT
        # =================================================

        impact_values = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "very_high": 4
        }

        if not changes:

            overall_impact = "none"
            recommended_action = "no_change"

        else:

            highest_impact = max(
                changes,
                key=lambda change: impact_values.get(
                    change.get(
                        "impact",
                        "medium"
                    ),
                    2
                )
            )

            overall_impact = highest_impact.get(
                "impact",
                "medium"
            )

            change_types = {
                change.get("type")
                for change in changes
            }

            if (
                "deadline_changed" in change_types
                and any(
                    change.get("impact") == "high"
                    for change in changes
                )
            ):

                recommended_action = (
                    "replan_immediately"
                )

            elif "commitment_added" in change_types:

                recommended_action = (
                    "replan_immediately"
                )

            elif "duration_changed" in change_types:

                recommended_action = (
                    "recalculate_capacity"
                )

            elif "priority_changed" in change_types:

                recommended_action = (
                    "recalculate_task_risk"
                )

            elif (
                "task_added" in change_types
                or "task_removed" in change_types
            ):

                recommended_action = (
                    "reoptimize_plan"
                )

            elif "status_changed" in change_types:

                recommended_action = (
                    "update_mission_state"
                )

            else:

                recommended_action = (
                    "reoptimize_plan"
                )

        return {
            "changed": len(changes) > 0,
            "changes": changes,
            "overall_impact": overall_impact,
            "recommended_action": recommended_action
        }