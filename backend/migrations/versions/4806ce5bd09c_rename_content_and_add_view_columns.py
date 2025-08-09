"""rename_content_and_add_view_columns

Revision ID: 4806ce5bd09c
Revises:
Create Date: 2025-03-28 15:29:23.732193

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4806ce5bd09c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # SQLite requires table recreation to effectively drop columns

    # Create new table with desired schema
    op.execute(
        """
    CREATE TABLE messages_new (
        id VARCHAR NOT NULL, 
        content VARCHAR NOT NULL,
        content_assistant_view VARCHAR NOT NULL,
        agent_role VARCHAR NOT NULL,
        agent_name VARCHAR NOT NULL,
        agent_model VARCHAR NOT NULL,
        agent_params JSON,
        project_id VARCHAR NOT NULL,
        timestamp DATETIME NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(project_id) REFERENCES projects (id)
    )
    """
    )

    # Copy data from old table to new table
    op.execute(
        """
    INSERT INTO messages_new
    SELECT id, content, content, agent_role, agent_name, agent_model, agent_params, project_id, timestamp
    FROM messages
    """
    )

    # Drop old table
    op.execute("DROP TABLE messages")

    # Rename new table to old name
    op.execute("ALTER TABLE messages_new RENAME TO messages")


def downgrade():
    # SQLite requires table recreation to revert schema changes

    # Create a new table with the old schema
    op.execute(
        """
    CREATE TABLE messages_old (
        id VARCHAR NOT NULL,
        content VARCHAR NOT NULL,
        agent_role VARCHAR NOT NULL,
        agent_name VARCHAR NOT NULL,
        agent_model VARCHAR NOT NULL,
        agent_params JSON,
        project_id VARCHAR NOT NULL,
        timestamp DATETIME NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(project_id) REFERENCES projects (id)
    )
    """
    )

    # Copy data from current table to old schema table
    op.execute(
        """
    INSERT INTO messages_old
    SELECT id, content, agent_role, agent_name, agent_model, agent_params, project_id, timestamp
    FROM messages
    """
    )

    # Drop current table
    op.execute("DROP TABLE messages")

    # Rename old schema table to original name
    op.execute("ALTER TABLE messages_old RENAME TO messages")
