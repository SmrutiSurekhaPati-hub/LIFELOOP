import snowflake.connector

from snowflake_config import (
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_USER,
    SNOWFLAKE_PASSWORD,
    SNOWFLAKE_WAREHOUSE,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_SCHEMA,
)


def get_connection():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )


def test_connection():
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT CURRENT_VERSION()")
        result = cursor.fetchone()

        return True, result[0] if result else "Connected"

    except Exception as error:
        return False, str(error)

    finally:
        if connection:
            connection.close()


def save_mission_event(
    mission_name,
    objective,
    task_name,
    task_duration_minutes,
    task_priority,
    task_deadline,
    available_minutes,
    event_type,
    recommendation,
):
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO LIFELOOP_DB.MISSIONS.MISSION_EVENTS (
                MISSION_NAME,
                OBJECTIVE,
                TASK_NAME,
                TASK_DURATION_MINUTES,
                TASK_PRIORITY,
                TASK_DEADLINE,
                AVAILABLE_MINUTES,
                EVENT_TYPE,
                RECOMMENDATION
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                mission_name,
                objective,
                task_name,
                task_duration_minutes,
                task_priority,
                task_deadline,
                available_minutes,
                event_type,
                recommendation,
            ),
        )

        connection.commit()
        return True, "Mission event saved to Snowflake."

    except Exception as error:
        return False, str(error)

    finally:
        if connection:
            connection.close()