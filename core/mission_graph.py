from typing import Dict, List


class MissionGraph:
    """
    Builds a connected representation of a LIFELOOP mission.

    Mission structure:
        Mission
          ├── Tasks
          ├── Commitments
          └── Relationships between mission entities
    """

    def __init__(self):
        self.nodes: List[Dict] = []
        self.relationships: List[Dict] = []

    def build_graph(self, mission: Dict) -> Dict:
        """
        Build the mission graph from the current mission state.
        """

        self.nodes = []
        self.relationships = []

        if not mission:
            return {
                "nodes": [],
                "relationships": []
            }

        mission_id = mission.get(
            "id",
            "mission"
        )

        mission_name = mission.get(
            "name",
            "Mission"
        )

        # -------------------------------------------------
        # MISSION NODE
        # -------------------------------------------------

        self.nodes.append({
            "id": mission_id,
            "type": "mission",
            "label": mission_name
        })

        # -------------------------------------------------
        # TASK NODES
        # -------------------------------------------------

        tasks = mission.get(
            "tasks",
            []
        )

        for task in tasks:

            task_id = task.get(
                "id"
            )

            if not task_id:
                continue

            task_title = task.get(
                "title",
                "Task"
            )

            self.nodes.append({
                "id": task_id,
                "type": "task",
                "label": task_title,
                "priority": task.get(
                    "priority",
                    "medium"
                ),
                "status": task.get(
                    "status",
                    "pending"
                )
            })

            # Mission -> Task
            self.relationships.append({
                "source": mission_id,
                "target": task_id,
                "type": "contains"
            })

        # -------------------------------------------------
        # COMMITMENT NODES
        # -------------------------------------------------

        commitments = mission.get(
            "commitments",
            []
        )

        for commitment in commitments:

            commitment_id = commitment.get(
                "id"
            )

            if not commitment_id:
                continue

            commitment_title = commitment.get(
                "title",
                "Commitment"
            )

            self.nodes.append({
                "id": commitment_id,
                "type": "commitment",
                "label": commitment_title,
                "importance": commitment.get(
                    "importance",
                    "medium"
                )
            })

            # Mission -> Commitment
            self.relationships.append({
                "source": mission_id,
                "target": commitment_id,
                "type": "contains"
            })

            # Commitment -> relevant tasks
            for task in tasks:

                task_id = task.get("id")

                if not task_id:
                    continue

                self.relationships.append({
                    "source": commitment_id,
                    "target": task_id,
                    "type": "constrains"
                })

        return {
            "nodes": self.nodes,
            "relationships": self.relationships
        }

    def get_graph(self) -> Dict:
        """
        Return the currently built graph.
        """

        return {
            "nodes": self.nodes,
            "relationships": self.relationships
        }

    def node_count(self) -> int:
        return len(self.nodes)

    def relationship_count(self) -> int:
        return len(self.relationships)