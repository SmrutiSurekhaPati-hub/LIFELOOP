from typing import Dict, List


class DecisionEngine:
    """
    LIFELOOP Decision Engine

    Converts mission state, consequences, conflicts and
    detected changes into a clear action decision.
    """

    PRIORITY_WEIGHT = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }

    IMPACT_WEIGHT = {
        "very_high": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
        "none": 0
    }

    def _priority_score(self, priority: str) -> int:
        return self.PRIORITY_WEIGHT.get(
            str(priority).lower(),
            2
        )

    def _impact_score(self, impact: str) -> int:
        return self.IMPACT_WEIGHT.get(
            str(impact).lower(),
            2
        )

    def _get_conflict_count(self, conflicts) -> int:
        """
        Supports both:
        - list of conflicts
        - dictionary containing a 'conflicts' list
        """

        if isinstance(conflicts, list):
            return len(conflicts)

        if isinstance(conflicts, dict):
            conflict_list = conflicts.get(
                "conflicts",
                []
            )

            if isinstance(conflict_list, list):
                return len(conflict_list)

            return 0

        return 0

    def _get_conflict_list(self, conflicts) -> List[Dict]:
        """
        Normalize conflicts into a list.
        """

        if isinstance(conflicts, list):
            return conflicts

        if isinstance(conflicts, dict):
            conflict_list = conflicts.get(
                "conflicts",
                []
            )

            if isinstance(conflict_list, list):
                return conflict_list

        return []

    def _calculate_task_score(
        self,
        task: Dict,
        consequence: Dict = None
    ) -> float:
        """
        Calculate a task risk/importance score.
        """

        priority = task.get(
            "priority",
            "medium"
        )

        score = self._priority_score(
            priority
        ) * 10

        if consequence:
            impact = consequence.get(
                "impact",
                "medium"
            )

            score += (
                self._impact_score(impact) * 5
            )

        if task.get("status") == "completed":
            score = 0

        return score

    def _find_consequence(
        self,
        task: Dict,
        consequences: List[Dict]
    ):
        """
        Find consequence information for a task.
        """

        task_id = task.get("id")
        task_title = task.get("title")

        for consequence in consequences:
            if consequence.get("task_id") == task_id:
                return consequence

            if consequence.get("task") == task_title:
                return consequence

            if consequence.get("title") == task_title:
                return consequence

        return None

    def _select_priority_task(
        self,
        tasks: List[Dict],
        consequences: List[Dict]
    ):
        """
        Select the task with the strongest combination
        of priority and consequence impact.
        """

        pending_tasks = [
            task
            for task in tasks
            if task.get("status", "pending") != "completed"
        ]

        if not pending_tasks:
            return None

        scored_tasks = []

        for task in pending_tasks:
            consequence = self._find_consequence(
                task,
                consequences
            )

            score = self._calculate_task_score(
                task,
                consequence
            )

            scored_tasks.append(
                (
                    score,
                    task
                )
            )

        scored_tasks.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return scored_tasks[0][1]

    def _calculate_total_work(
        self,
        tasks: List[Dict]
    ) -> int:
        """
        Calculate total remaining work.
        """

        total = 0

        for task in tasks:
            if task.get("status", "pending") == "completed":
                continue

            duration = task.get(
                "duration_minutes",
                0
            )

            try:
                total += int(duration)
            except (
                ValueError,
                TypeError
            ):
                pass

        return total

    def _calculate_deadline_pressure(
        self,
        task: Dict
    ) -> str:
        """
        Return a simple textual deadline pressure.
        """

        priority = str(
            task.get(
                "priority",
                "medium"
            )
        ).lower()

        if priority == "critical":
            return "very_high"

        if priority == "high":
            return "high"

        if priority == "medium":
            return "medium"

        return "low"

    def _change_summary(
        self,
        change_info: Dict
    ) -> str:
        """
        Convert change information into a human-readable
        explanation.
        """

        if not change_info:
            return ""

        changes = change_info.get(
            "changes",
            []
        )

        if not changes:
            return ""

        first_change = changes[0]

        return first_change.get(
            "message",
            "Mission state changed."
        )

    def make_decision(
        self,
        tasks: List[Dict],
        consequences: List[Dict],
        available_minutes: int,
        conflicts,
        change_info: Dict = None
    ) -> Dict:
        """
        Generate the main LIFELOOP decision.
        """

        if tasks is None:
            tasks = []

        if consequences is None:
            consequences = []

        if change_info is None:
            change_info = {}

        conflict_count = self._get_conflict_count(
            conflicts
        )

        conflict_list = self._get_conflict_list(
            conflicts
        )

        total_work = self._calculate_total_work(
            tasks
        )

        pending_tasks = [
            task
            for task in tasks
            if task.get(
                "status",
                "pending"
            ) != "completed"
        ]

        selected_task = self._select_priority_task(
            pending_tasks,
            consequences
        )

        change_detected = bool(
            change_info.get(
                "changed",
                False
            )
        )

        overall_impact = change_info.get(
            "overall_impact",
            "none"
        )

        recommended_action = change_info.get(
            "recommended_action",
            "no_change"
        )

        # -------------------------------------------------
        # NO PENDING TASKS
        # -------------------------------------------------

        if not pending_tasks:

            return {
                "decision": "Mission work is complete.",
                "recommended_task": None,
                "recommended_minutes": 0,
                "reason": (
                    "There are no pending tasks "
                    "remaining in the mission."
                ),
                "risk_level": "low",
                "conflict_count": conflict_count,
                "total_work_minutes": total_work,
                "available_minutes": available_minutes,
                "change_detected": change_detected,
                "change_impact": overall_impact,
                "recommended_action": recommended_action,
                "change_summary": self._change_summary(
                    change_info
                )
            }

        # -------------------------------------------------
        # SELECTED TASK
        # -------------------------------------------------

        task_title = selected_task.get(
            "title",
            "Unknown task"
        )

        task_duration = selected_task.get(
            "duration_minutes",
            0
        )

        try:
            task_duration = int(
                task_duration
            )
        except (
            ValueError,
            TypeError
        ):
            task_duration = 0

        priority = str(
            selected_task.get(
                "priority",
                "medium"
            )
        ).upper()

        deadline_pressure = (
            self._calculate_deadline_pressure(
                selected_task
            )
        )

        # -------------------------------------------------
        # DETECTED CHANGE
        # -------------------------------------------------

        if change_detected:

            if overall_impact == "very_high":
                risk_level = "very_high"

            elif overall_impact == "high":
                risk_level = "high"

            else:
                risk_level = "medium"

            if (
                recommended_action
                == "replan_immediately"
            ):
                decision_text = (
                    f"Replan immediately and "
                    f"protect '{task_title}'."
                )

                reason = (
                    f"LIFELOOP detected a significant "
                    f"mission change. '{task_title}' "
                    f"currently has the strongest "
                    f"combination of priority, deadline "
                    f"pressure and mission risk."
                )

            elif (
                recommended_action
                == "recalculate_capacity"
            ):
                decision_text = (
                    f"Recalculate capacity and "
                    f"prioritize '{task_title}'."
                )

                reason = (
                    f"The workload changed, so LIFELOOP "
                    f"recalculated the available capacity. "
                    f"'{task_title}' currently carries "
                    f"the highest task importance."
                )

            elif (
                recommended_action
                == "recalculate_task_risk"
            ):
                decision_text = (
                    f"Recalculate task risk and "
                    f"focus on '{task_title}'."
                )

                reason = (
                    f"A task priority changed. "
                    f"LIFELOOP recalculated mission risk "
                    f"and selected '{task_title}' as the "
                    f"current priority."
                )

            else:
                decision_text = (
                    f"Update the mission plan and "
                    f"focus on '{task_title}'."
                )

                reason = (
                    f"The mission state changed. "
                    f"LIFELOOP updated the decision using "
                    f"the current task priorities, "
                    f"deadlines and consequences."
                )

        # -------------------------------------------------
        # CAPACITY IS NOT ENOUGH
        # -------------------------------------------------

        elif total_work > available_minutes:

            risk_level = "high"

            if task_duration > available_minutes:

                decision_text = (
                    f"Prioritize '{task_title}' now."
                )

                reason = (
                    f"'{task_title}' requires "
                    f"{task_duration} minutes, while only "
                    f"{available_minutes} minutes are "
                    f"currently available. LIFELOOP "
                    f"protects the highest-risk task "
                    f"rather than spreading time across "
                    f"lower-priority work."
                )

            else:

                decision_text = (
                    f"Complete '{task_title}' first."
                )

                reason = (
                    f"There are {total_work} minutes of "
                    f"remaining work but only "
                    f"{available_minutes} minutes available. "
                    f"LIFELOOP therefore prioritizes the "
                    f"highest-risk task first."
                )

        # -------------------------------------------------
        # ENOUGH CAPACITY
        # -------------------------------------------------

        else:

            risk_level = (
                "high"
                if priority in ["CRITICAL", "HIGH"]
                else "medium"
            )

            decision_text = (
                f"Work on '{task_title}' now."
            )

            reason = (
                f"'{task_title}' has the strongest "
                f"combination of priority, deadline "
                f"pressure and consequence impact."
            )

        # -------------------------------------------------
        # CONFLICT INFORMATION
        # -------------------------------------------------

        if conflict_count > 0:

            if conflict_count == 1:
                conflict_note = (
                    "1 active conflict was detected."
                )
            else:
                conflict_note = (
                    f"{conflict_count} active conflicts "
                    f"were detected."
                )

            reason += (
                f" {conflict_note} LIFELOOP keeps these "
                f"constraints in the decision."
            )

        # -------------------------------------------------
        # RECOMMENDED MINUTES
        # -------------------------------------------------

        if available_minutes <= 0:
            recommended_minutes = 0

        elif task_duration <= available_minutes:
            recommended_minutes = task_duration

        else:
            recommended_minutes = available_minutes

        # -------------------------------------------------
        # FINAL DECISION
        # -------------------------------------------------

        return {
            "decision": decision_text,
            "recommended_task": task_title,
            "recommended_task_id": selected_task.get(
                "id"
            ),
            "recommended_minutes": (
                recommended_minutes
            ),
            "task_duration": task_duration,
            "task_priority": priority,
            "deadline_pressure": deadline_pressure,
            "reason": reason,
            "risk_level": risk_level,
            "conflict_count": conflict_count,
            "conflicts": conflict_list,
            "total_work_minutes": total_work,
            "available_minutes": available_minutes,
            "remaining_minutes": max(
                total_work - available_minutes,
                0
            ),
            "change_detected": change_detected,
            "change_impact": overall_impact,
            "recommended_action": recommended_action,
            "change_summary": self._change_summary(
                change_info
            )
        }