from core.snowflake_service import save_mission_event


success, message = save_mission_event(
    mission_name="Exam & Scholarship Mission",
    objective="Complete scholarship application and prepare for exams.",
    task_name="Scholarship application",
    task_duration_minutes=90,
    task_priority="CRITICAL",
    task_deadline="2026-09-16 23:59:00",
    available_minutes=120,
    event_type="TEST",
    recommendation="Protect scholarship application first.",
)

print("SAVED:", success)
print("RESULT:", message)