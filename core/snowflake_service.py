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
    """Create a Snowflake connection using environment variables."""
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )


def test_connection():
    """Test whether LIFELOOP can connect to Snowflake."""
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