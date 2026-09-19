import copy
import streamlit as st

from core.mission_engine import MissionEngine
from core.planner import Planner
from core.conflict_engine import ConflictEngine
from core.consequence import ConsequenceEngine
from core.decision_engine import DecisionEngine
from core.mission_graph import MissionGraph
from core.change_engine import ChangeEngine


st.set_page_config(
    page_title="LIFELOOP",
    page_icon="🔄",
    layout="wide"
)


# ---------------------------------------------------------
# ENGINE INITIALIZATION
# ---------------------------------------------------------

mission_engine = MissionEngine()
planner = Planner()
conflict_engine = ConflictEngine()
consequence_engine = ConsequenceEngine()
decision_engine = DecisionEngine()
mission_graph = MissionGraph()
change_engine = ChangeEngine()


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "previous_mission" not in st.session_state:
    st.session_state.previous_mission = copy.deepcopy(
        mission_engine.get_state()
    )

if "last_change_info" not in st.session_state:
    st.session_state.last_change_info = None


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def refresh_change_detection():
    current_mission = copy.deepcopy(
        mission_engine.get_state()
    )

    previous_mission = st.session_state.previous_mission

    change_info = change_engine.analyze_change(
        previous_mission,
        current_mission
    )

    st.session_state.last_change_info = change_info

    st.session_state.previous_mission = copy.deepcopy(
        current_mission
    )

    return change_info


def format_priority(priority):
    return str(priority).upper()


# ---------------------------------------------------------
# SIDEBAR - CREATE MISSION
# ---------------------------------------------------------

st.sidebar.header("🎯 Create Your Mission")

mission_name = st.sidebar.text_input(
    "Mission name"
)

mission_objective = st.sidebar.text_area(
    "What are you trying to achieve?"
)

if st.sidebar.button(
    "Create Mission",
    use_container_width=True
):
    if mission_name.strip() and mission_objective.strip():

        mission_engine.create_mission(
            mission_name.strip(),
            mission_objective.strip()
        )

        st.session_state.previous_mission = copy.deepcopy(
            mission_engine.get_state()
        )

        st.session_state.last_change_info = None

        st.rerun()


# ---------------------------------------------------------
# SIDEBAR - ADD TASK
# ---------------------------------------------------------

st.sidebar.header("➕ Add Task")

task_name = st.sidebar.text_input(
    "Task name"
)

task_duration = st.sidebar.number_input(
    "Duration (minutes)",
    min_value=1,
    value=60,
    step=5
)

task_deadline = st.sidebar.text_input(
    "Deadline",
    placeholder="YYYY-MM-DD HH:MM"
)

task_priority = st.sidebar.selectbox(
    "Priority",
    ["critical", "high", "medium", "low"]
)

if st.sidebar.button(
    "Add Task",
    use_container_width=True
):
    if task_name.strip():

        mission_engine.add_task(
            title=task_name.strip(),
            duration_minutes=int(task_duration),
            deadline=task_deadline.strip() or None,
            priority=task_priority
        )

        refresh_change_detection()

        st.rerun()


# ---------------------------------------------------------
# SIDEBAR - UPDATE EXISTING TASK
# ---------------------------------------------------------

st.sidebar.header("🔄 Update Existing Task")

current_tasks = mission_engine.get_pending_tasks()

if current_tasks:

    task_options = {
        f"{task['id']} — {task['title']}": task
        for task in current_tasks
    }

    selected_task_label = st.sidebar.selectbox(
        "Select task",
        list(task_options.keys())
    )

    selected_task = task_options[selected_task_label]

    new_deadline = st.sidebar.text_input(
        "New deadline",
        value=selected_task.get("deadline") or ""
    )

    new_duration = st.sidebar.number_input(
        "New duration (minutes)",
        min_value=1,
        value=int(
            selected_task.get(
                "duration_minutes",
                60
            )
        ),
        step=5
    )

    priority_options = [
        "critical",
        "high",
        "medium",
        "low"
    ]

    current_priority = selected_task.get(
        "priority",
        "medium"
    )

    new_priority = st.sidebar.selectbox(
        "New priority",
        priority_options,
        index=priority_options.index(
            current_priority
        )
    )

    if st.sidebar.button(
        "Update Task",
        use_container_width=True
    ):

        mission_engine.update_task(
            task_id=selected_task["id"],
            deadline=new_deadline.strip() or None,
            duration_minutes=int(new_duration),
            priority=new_priority
        )

        change_info = refresh_change_detection()

        st.session_state.last_change_info = change_info

        st.rerun()

else:
    st.sidebar.info(
        "Add a task first."
    )


# ---------------------------------------------------------
# SIDEBAR - ADD COMMITMENT
# ---------------------------------------------------------

st.sidebar.header("🤝 Add Commitment")

commitment_name = st.sidebar.text_input(
    "Commitment"
)

commitment_time = st.sidebar.text_input(
    "Time",
    placeholder="YYYY-MM-DD HH:MM"
)

commitment_importance = st.sidebar.selectbox(
    "Importance",
    ["critical", "high", "medium", "low"]
)

if st.sidebar.button(
    "Add Commitment",
    use_container_width=True
):

    if commitment_name.strip():

        mission_engine.add_commitment(
            title=commitment_name.strip(),
            time=commitment_time.strip() or None,
            importance=commitment_importance
        )

        refresh_change_detection()

        st.rerun()


# ---------------------------------------------------------
# LOAD CURRENT MISSION
# ---------------------------------------------------------

mission = mission_engine.get_state()

tasks = mission.get(
    "tasks",
    []
)

commitments = mission.get(
    "commitments",
    []
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🔄 LIFELOOP")

st.subheader(
    "Adaptive AI Life Management Assistant"
)

st.write(
    "LIFELOOP connects your goals, tasks, deadlines "
    "and commitments into one adaptive plan."
)


# ---------------------------------------------------------
# CURRENT MISSION
# ---------------------------------------------------------

st.header("🎯 Current Mission")

if mission.get("name"):

    st.write(
        f"**Mission:** {mission.get('name')}"
    )

    st.write(
        f"**Objective:** {mission.get('objective')}"
    )

else:

    st.info(
        "Create a mission from the sidebar to begin."
    )


# ---------------------------------------------------------
# CURRENT SITUATION
# ---------------------------------------------------------

st.header("⏱️ Current Situation")

available_minutes = st.slider(
    "How much time do you have available right now?",
    min_value=15,
    max_value=600,
    value=120,
    step=15
)


# ---------------------------------------------------------
# ADAPTIVE ENGINE PIPELINE
# ---------------------------------------------------------

conflict_result = conflict_engine.check_all(
    mission,
    available_minutes
)

conflicts = conflict_result.get(
    "conflicts",
    []
)


consequence_results = consequence_engine.analyze_all(
    tasks
)


change_info = st.session_state.last_change_info


# ---------------------------------------------------------
# DECISION ENGINE
# ---------------------------------------------------------

decision = decision_engine.make_decision(
    tasks=tasks,
    consequences=consequence_results,
    available_minutes=available_minutes,
    conflicts=conflicts,
    change_info=change_info
)


# ---------------------------------------------------------
# PLANNER
# ---------------------------------------------------------

plan = planner.create_plan(
    tasks,
    available_minutes
)


# ---------------------------------------------------------
# AUTOMATIC REPLAN WHEN MISSION CHANGES
# ---------------------------------------------------------

replan_result = None

if change_info:

    recommended_action = change_info.get(
        "recommended_action"
    )

    if recommended_action in [
        "replan_immediately",
        "protect_task",
        "reoptimize_plan",
        "recalculate_task_risk",
        "recalculate_capacity",
        "update_mission_state"
    ]:

        replan_result = planner.replan(
            mission,
            available_minutes
        )

        plan = replan_result.get(
            "plan",
            plan
        )


# ---------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

pending_tasks = [
    task for task in tasks
    if task.get("status") != "completed"
]

active_commitments = [
    commitment
    for commitment in commitments
    if commitment.get("status") == "active"
]

with col1:
    st.metric(
        "Pending Tasks",
        len(pending_tasks)
    )

with col2:
    st.metric(
        "Available Time",
        f"{available_minutes} min"
    )

with col3:
    st.metric(
        "Conflicts",
        len(conflicts)
    )

with col4:
    st.metric(
        "Commitments",
        len(active_commitments)
    )


# ---------------------------------------------------------
# CHANGE DETECTION
# ---------------------------------------------------------

if change_info:

    changes = change_info.get(
        "changes",
        []
    )

    if changes:

        st.header("🔄 Adaptive Change Detection")

        st.warning(
            f"LIFELOOP detected {len(changes)} "
            f"mission change(s)."
        )

        for change in changes:

            st.write(
                f"**{change.get('type', 'Change')}** — "
                f"{change.get('message', '')}"
            )

        overall_impact = change_info.get(
            "overall_impact",
            "medium"
        )

        recommended_action = change_info.get(
            "recommended_action",
            "recalculate_plan"
        )

        st.write(
            f"**Impact:** {overall_impact.upper()}"
        )

        st.write(
            f"**Adaptive action:** "
            f"{recommended_action.replace('_', ' ').title()}"
        )

        if replan_result:

            st.info(
                "LIFELOOP recommends recalculating "
                "the current plan."
            )


# ---------------------------------------------------------
# DECISION
# ---------------------------------------------------------

st.header("🧠 LIFELOOP Decision")

decision_status = decision.get(
    "status",
    "recommended"
)

if decision_status == "critical":
    st.error("🔴")

elif decision_status == "high":
    st.warning("🟠")

else:
    st.success("🟢")


st.write("### RECOMMENDED ACTION")

st.write(
    f"**Decision:** "
    f"{decision.get('decision', 'No decision available.')}"
)

st.write(
    f"**Reason:** "
    f"{decision.get('reason', 'Mission conditions were evaluated.')}"
)


recommended_focus = decision.get(
    "recommended_focus"
)

if recommended_focus:

    st.write(
        f"Recommended focus: **{recommended_focus}**"
    )


# ---------------------------------------------------------
# MISSION GRAPH
# ---------------------------------------------------------

st.header("🕸️ Mission Graph")

st.write(
    "LIFELOOP represents your situation as connected "
    "mission entities instead of isolated tasks."
)


try:

    graph = mission_graph.build_graph(
        mission
    )

    nodes = graph.get(
        "nodes",
        []
    )

    relationships = graph.get(
        "relationships",
        []
    )

except Exception:

    nodes = []
    relationships = []


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Graph Nodes",
        len(nodes)
    )

with col2:
    st.metric(
        "Relationships",
        len(relationships)
    )

with col3:
    st.metric(
        "Active Commitments",
        len(active_commitments)
    )


if nodes:

    highest_priority_task = None

    if pending_tasks:

        priority_order = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }

        highest_priority_task = max(
            pending_tasks,
            key=lambda task: priority_order.get(
                task.get("priority", "medium"),
                2
            )
        )

    highest_name = (
        highest_priority_task.get("title")
        if highest_priority_task
        else "None"
    )

    st.caption(
        f"Mission: {mission.get('name', 'Unnamed')} | "
        f"Active tasks: {len(pending_tasks)} | "
        f"Active commitments: {len(active_commitments)} | "
        f"Connected relationships: {len(relationships)} | "
        f"Highest priority task: {highest_name}"
    )

    with st.expander(
        "🔎 View Mission Graph Details"
    ):

        st.json({
            "nodes": nodes,
            "relationships": relationships
        })


# ---------------------------------------------------------
# RECOMMENDED PLAN
# ---------------------------------------------------------

st.header("📋 LIFELOOP Recommended Plan")

selected_tasks = plan.get(
    "selected_tasks",
    []
)

partial_task = plan.get(
    "partial_task"
)

postponed_tasks = plan.get(
    "postponed_tasks",
    []
)


if selected_tasks:

    for index, task in enumerate(
        selected_tasks,
        start=1
    ):

        st.write(
            f"{index}. "
            f"{task.get('title')} — "
            f"{task.get('duration_minutes')} min — "
            f"{format_priority(task.get('priority'))}"
        )

elif partial_task:

    st.write(
        f"1. {partial_task.get('title')} — "
        f"{partial_task.get('allocated_minutes')} min "
        f"of {partial_task.get('duration_minutes')} min — "
        f"{format_priority(partial_task.get('priority'))}"
    )

    st.info(
        f"This task is partially protected because "
        f"{partial_task.get('remaining_minutes')} minutes "
        f"would still remain."
    )

else:

    st.info(
        "No task fits the current available time."
    )


# ---------------------------------------------------------
# POSTPONED / RECONSIDERED TASKS
# ---------------------------------------------------------

if postponed_tasks:

    st.header("⏳ Tasks to Reconsider")

    for task in postponed_tasks:

        st.write(
            f"{task.get('title')} — "
            f"{task.get('duration_minutes')} min — "
            f"{format_priority(task.get('priority'))}"
        )


# ---------------------------------------------------------
# CONFLICT DETECTION
# ---------------------------------------------------------

st.header("⚠️ Conflict Detection")

if conflicts:

    for conflict in conflicts:

        st.write(
            conflict.get(
                "message",
                "Conflict detected."
            )
        )

else:

    st.success(
        "No active conflicts detected."
    )


# ---------------------------------------------------------
# CONSEQUENCE ANALYSIS
# ---------------------------------------------------------

st.header("🔍 Consequence Analysis")

if consequence_results:

    for result in consequence_results:

        st.write(
            f"**{result.get('task')}** → "
            f"Delay impact: "
            f"**{result.get('impact', 'unknown').upper()}**"
        )

else:

    st.info(
        "No pending tasks available for consequence analysis."
    )


# ---------------------------------------------------------
# ACTIVE COMMITMENTS
# ---------------------------------------------------------

st.header("🤝 Active Commitments")

if active_commitments:

    for commitment in active_commitments:

        st.write(
            f"**{commitment.get('title')}** — "
            f"{commitment.get('time')} — "
            f"{format_priority(commitment.get('importance'))}"
        )

else:

    st.info(
        "No active commitments."
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "LIFELOOP — Plans are static. Life isn't."
)