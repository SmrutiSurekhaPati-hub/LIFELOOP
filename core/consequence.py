from typing import Dict, List


class ConsequenceEngine:
    """
    LIFELOOP consequence analysis engine.

    Determines what may happen if a task is delayed,
    based on priority, deadline, and relationships
    with other mission tasks.
    """

    IMPACT_SCORE = {
        "very_high": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }

    def _get_base_impact(
        self,
        task: Dict
    ) -> str:

        priority = task.get(
            "priority",
            "medium"
        )

        deadline = task.get(
            "deadline"
        )

        if priority == "critical":
            return "very_high"

        if priority == "high":
            return "high"

        if deadline:
            return "medium"

        return "low"

    def analyze_task_delay(
        self,
        task: Dict,
        all_tasks: List[Dict]
    ) -> Dict:
        """
        Analyze the consequences of delaying one task.
        """

        impact = self._get_base_impact(
            task
        )

        affected_tasks = []

        task_deadline = task.get(
            "deadline"
        )

        # Find other tasks that also have deadlines.
        # These tasks may become more difficult to
        # complete if the current task is delayed.
        for other_task in all_tasks:

            if other_task.get("status") == "completed":
                continue

            if other_task.get("id") == task.get("id"):
                continue

            if other_task.get("deadline"):
                affected_tasks.append(
                    other_task["title"]
                )

        if (
            impact == "medium"
            and len(affected_tasks) >= 2
        ):
            impact = "high"

        if impact == "very_high":

            explanation = (
                "Delaying this task creates a very high "
                "risk because it has critical importance."
            )

        elif impact == "high":

            explanation = (
                "Delaying this task could put important "
                "mission objectives or nearby deadlines at risk."
            )

        elif impact == "medium":

            explanation = (
                "Delaying this task reduces the available "
                "time for completing the mission."
            )

        else:

            explanation = (
                "Delaying this task is unlikely to create "
                "an immediate major consequence."
            )

        return {
            "task": task.get(
                "title",
                "Unknown task"
            ),
            "impact": impact,
            "deadline": task_deadline,
            "affected_tasks": affected_tasks,
            "explanation": explanation
        }

    def analyze_all(
        self,
        tasks: List[Dict]
    ) -> List[Dict]:
        """
        Analyze consequences for every pending task.
        """

        results = []

        for task in tasks:

            if task.get("status") == "completed":
                continue

            result = self.analyze_task_delay(
                task,
                tasks
            )

            results.append(
                result
            )

        return results

    def find_highest_risk(
        self,
        tasks: List[Dict]
    ) -> Dict:
        """
        Find the task whose delay creates
        the greatest mission risk.
        """

        results = self.analyze_all(
            tasks
        )

        if not results:

            return {
                "task": None,
                "impact": "none",
                "affected_tasks": [],
                "explanation": (
                    "There are no pending tasks."
                )
            }

        highest = max(
            results,
            key=lambda item:
            self.IMPACT_SCORE.get(
                item["impact"],
                0
            )
        )

        return highest