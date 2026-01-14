import os
import pytest
import sqlite3
import tempfile
import shutil
from unittest.mock import patch

# Set environment variable to use a test database
@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_radar.db")
    
    # Patch the config directly
    with patch("radar.config.DATABASE_PATH", db_path):
        # Also patch storage.db.DATABASE_PATH just in case it was imported
        with patch("radar.storage.db.DATABASE_PATH", db_path):
            yield db_path
    
    shutil.rmtree(temp_dir)

@pytest.fixture
def db_conn(test_db_setup):
    from radar.storage.db import init_db, get_connection
    # Ensure tables are created in the test DB
    init_db()
    conn = get_connection()
    yield conn
    conn.close()
