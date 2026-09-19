import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class MissionEngine:

    def __init__(self):

        self.data_file = os.path.join(
            "data",
            "missions.json"
        )

        self.mission = self._load_mission()

    # ======================================================
    # TIME
    # ======================================================

    def _now(self) -> str:

        return datetime.now().isoformat(
            timespec="seconds"
        )

    # ======================================================
    # DEFAULT MISSION
    # ======================================================

    def _default_mission(self) -> Dict:

        return {
            "name": "",
            "objective": "",
            "status": "active",
            "created_at": self._now(),
            "updated_at": self._now(),
            "constraints": [],
            "goals": [],
            "tasks": [],
            "commitments": [],
            "resources": {},
            "events": []
        }

    # ======================================================
    # LOAD
    # ======================================================

    def _load_mission(self) -> Dict:

        try:

            if os.path.exists(
                self.data_file
            ):

                with open(
                    self.data_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(
                        file
                    )

                    if isinstance(
                        data,
                        dict
                    ):

                        return data

        except (
            json.JSONDecodeError,
            OSError
        ):

            pass

        return self._default_mission()

    # ======================================================
    # SAVE
    # ======================================================

    def _save_mission(self) -> None:

        os.makedirs(
            os.path.dirname(
                self.data_file
            ),
            exist_ok=True
        )

        with open(
            self.data_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.mission,
                file,
                indent=4,
                ensure_ascii=False
            )

    # ======================================================
    # CREATE MISSION
    # ======================================================

    def create_mission(
        self,
        name: str,
        objective: str
    ) -> Dict:

        self.mission["name"] = name

        self.mission["objective"] = objective

        self.mission["status"] = "active"

        self.mission["updated_at"] = (
            self._now()
        )

        self._log_event(
            "mission_created",
            f"Mission '{name}' created."
        )

        self._save_mission()

        return self.get_state()

    # ======================================================
    # ADD GOAL
    # ======================================================

    def add_goal(
        self,
        title: str,
        deadline: Optional[str] = None,
        priority: str = "medium"
    ) -> Dict:

        goal = {
            "id": len(
                self.mission["goals"]
            ) + 1,
            "title": title,
            "deadline": deadline,
            "priority": priority,
            "status": "pending"
        }

        self.mission["goals"].append(
            goal
        )

        self._touch()

        self._save_mission()

        return goal

    # ======================================================
    # ADD TASK
    # ======================================================

    def add_task(
        self,
        title: str,
        duration_minutes: int,
        deadline: Optional[str] = None,
        priority: str = "medium"
    ) -> Dict:

        task = {
            "id": len(
                self.mission["tasks"]
            ) + 1,
            "title": title,
            "duration_minutes": duration_minutes,
            "deadline": deadline,
            "priority": priority,
            "status": "pending"
        }

        self.mission["tasks"].append(
            task
        )

        self._touch()

        self._log_event(
            "task_added",
            f"Task '{title}' added."
        )

        self._save_mission()

        return task

    # ======================================================
    # UPDATE TASK
    # ======================================================

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        deadline: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Dict]:

        for task in self.mission["tasks"]:

            if task["id"] != task_id:
                continue

            old_task = task.copy()

            if title is not None:
                task["title"] = title

            if duration_minutes is not None:
                task["duration_minutes"] = (
                    duration_minutes
                )

            if deadline is not None:
                task["deadline"] = deadline

            if priority is not None:
                task["priority"] = priority

            if status is not None:
                task["status"] = status

            self._touch()

            self._log_event(
                "task_updated",
                (
                    f"Task '{old_task['title']}' "
                    f"was updated."
                )
            )

            self._save_mission()

            return task

        return None

    # ======================================================
    # ADD COMMITMENT
    # ======================================================

    def add_commitment(
        self,
        title: str,
        time: Optional[str] = None,
        importance: str = "medium"
    ) -> Dict:

        commitment = {
            "id": len(
                self.mission["commitments"]
            ) + 1,
            "title": title,
            "time": time,
            "importance": importance,
            "status": "active"
        }

        self.mission["commitments"].append(
            commitment
        )

        self._touch()

        self._log_event(
            "commitment_added",
            f"Commitment '{title}' added."
        )

        self._save_mission()

        return commitment

    # ======================================================
    # UPDATE COMMITMENT
    # ======================================================

    def update_commitment(
        self,
        commitment_id: int,
        status: str
    ) -> bool:

        for commitment in self.mission["commitments"]:

            if commitment["id"] == commitment_id:

                commitment["status"] = status

                self._touch()

                self._log_event(
                    "commitment_updated",
                    (
                        f"Commitment "
                        f"{commitment_id} "
                        f"changed to {status}."
                    )
                )

                self._save_mission()

                return True

        return False

    # ======================================================
    # ADD CONSTRAINT
    # ======================================================

    def add_constraint(
        self,
        constraint: str
    ) -> None:

        self.mission["constraints"].append(
            constraint
        )

        self._touch()

        self._save_mission()

    # ======================================================
    # SET RESOURCE
    # ======================================================

    def set_resource(
        self,
        name: str,
        value
    ) -> None:

        self.mission["resources"][name] = value

        self._touch()

        self._save_mission()

    # ======================================================
    # UPDATE TASK STATUS
    # ======================================================

    def update_task_status(
        self,
        task_id: int,
        status: str
    ) -> bool:

        for task in self.mission["tasks"]:

            if task["id"] == task_id:

                task["status"] = status

                self._touch()

                self._log_event(
                    "task_updated",
                    (
                        f"Task {task_id} "
                        f"changed to {status}."
                    )
                )

                self._save_mission()

                return True

        return False

    # ======================================================
    # STATE
    # ======================================================

    def get_state(self) -> Dict:

        return self.mission

    # ======================================================
    # PENDING TASKS
    # ======================================================

    def get_pending_tasks(
        self
    ) -> List[Dict]:

        return [
            task
            for task in self.mission["tasks"]
            if task["status"] != "completed"
        ]

    # ======================================================
    # TOUCH
    # ======================================================

    def _touch(self) -> None:

        self.mission["updated_at"] = (
            self._now()
        )

    # ======================================================
    # EVENT LOG
    # ======================================================

    def _log_event(
        self,
        event_type: str,
        description: str
    ) -> None:

        self.mission["events"].append({

            "timestamp": self._now(),

            "type": event_type,

            "description": description

        })