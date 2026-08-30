import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

import server


class SecurityRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        server.DB_PATH = str(root / "tracker.db")
        server.SECRET_FP = str(root / ".secret_key")
        server._FAILS.clear()
        server.init_db()

        con = sqlite3.connect(server.DB_PATH)
        con.execute(
            "INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) "
            "VALUES(?,?,?,?,?,?)",
            ("admin", generate_password_hash("admin-password"), 1, "A", server.now_iso(),
             json.dumps({"done": {"P1-01": 1700000000000}, "evidence": {"P1-01": "private-admin"}})),
        )
        con.execute(
            "INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) "
            "VALUES(?,?,?,?,?,?)",
            ("operator", generate_password_hash("operator-password"), 0, "O", server.now_iso(),
             json.dumps({"done": {"P1-02": 1700000000000}, "evidence": {"P1-02": "private-user"}})),
        )
        con.commit()
        con.close()

        self.app = server.create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def login(self, username, password):
        response = self.client.post("/api/login", json={"username": username, "password": password})
        self.assertEqual(response.status_code, 200)
        return response.get_json()["csrf"]

    def test_ordinary_user_only_receives_own_private_progress(self):
        self.login("operator", "operator-password")
        state = self.client.get("/api/state").get_json()
        self.assertIn("progress", state["users"]["2"])
        self.assertNotIn("progress", state["users"]["1"])
        self.assertNotIn("evidence", state["users"]["1"])
        self.assertIn("trophyCount", state["users"]["1"])

    def test_admin_can_receive_progress_for_account_management(self):
        self.login("admin", "admin-password")
        state = self.client.get("/api/state").get_json()
        self.assertIn("progress", state["users"]["1"])
        self.assertIn("progress", state["users"]["2"])

    def test_password_change_invalidates_existing_session(self):
        csrf = self.login("operator", "operator-password")
        changed = self.client.post(
            "/api/me/password",
            json={"old": "operator-password", "new": "new-operator-password"},
            headers={"X-CSRF-Token": csrf},
        )
        self.assertEqual(changed.status_code, 200)
        self.assertTrue(changed.get_json()["relogin"])
        self.assertEqual(self.client.get("/api/state").status_code, 401)

    def test_legacy_import_creates_non_admin_account_with_unknown_password(self):
        csrf = self.login("admin", "admin-password")
        response = self.client.post(
            "/api/admin/import-legacy",
            json={"users": {"legacy": {"name": "legacy-admin", "isAdmin": True, "progress": {}}}},
            headers={"X-CSRF-Token": csrf},
        )
        self.assertEqual(response.status_code, 200)
        con = sqlite3.connect(server.DB_PATH)
        row = con.execute(
            "SELECT password_hash,is_admin FROM users WHERE username=?", ("legacy-admin",)
        ).fetchone()
        con.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], 0)
        self.assertFalse(check_password_hash(row[0], "legacy-admin"))

    def test_login_throttle_is_bounded_and_has_per_ip_limit(self):
        for i in range(server._MAXFAIL_IP):
            server.note_fail("203.0.113.9", f"name-{i}")
        self.assertTrue(server.throttled("203.0.113.9", "another-name"))
        for i in range(server._MAX_THROTTLE_KEYS + 50):
            server.note_fail(f"198.51.{i // 256}.{i % 256}", f"unique-{i}")
        self.assertLessEqual(len(server._FAILS), server._MAX_THROTTLE_KEYS)

    def test_invalid_login_json_types_fail_closed(self):
        response = self.client.post("/api/login", json={"username": ["not", "text"], "password": 7})
        self.assertEqual(response.status_code, 401)

    def test_malformed_imported_config_is_normalized_without_breaking_state(self):
        csrf = self.login("admin", "admin-password")
        response = self.client.put(
            "/api/config",
            json={
                "overrides": {"P1-01": {"xp": "not-a-number"}},
                "customTasks": [{"id": ["bad"], "xp": {"bad": True}}, "invalid"],
                "customTrophies": [{"id": "safe", "rule": []}],
                "challenges": [{"id": "weekly", "taskIds": "not-a-list", "days": {}}],
            },
            headers={"X-CSRF-Token": csrf},
        )
        self.assertEqual(response.status_code, 200)
        state = self.client.get("/api/state")
        self.assertEqual(state.status_code, 200)
        config = state.get_json()["config"]
        self.assertEqual(config["overrides"]["P1-01"], {"xp": 0})
        self.assertEqual(config["challenges"][0]["taskIds"], [])

    def test_admin_password_reset_revokes_target_sessions(self):
        operator = self.app.test_client()
        logged_in = operator.post(
            "/api/login", json={"username": "operator", "password": "operator-password"}
        )
        self.assertEqual(logged_in.status_code, 200)

        admin = self.app.test_client()
        admin_login = admin.post(
            "/api/login", json={"username": "admin", "password": "admin-password"}
        ).get_json()
        reset = admin.post(
            "/api/admin/users/2/password",
            json={"password": "replacement-password"},
            headers={"X-CSRF-Token": admin_login["csrf"]},
        )
        self.assertEqual(reset.status_code, 200)
        self.assertEqual(operator.get("/api/state").status_code, 401)

    def test_existing_database_gets_auth_version_migration(self):
        migrated = Path(self.tmp.name) / "old.db"
        con = sqlite3.connect(migrated)
        con.executescript("""
            CREATE TABLE users(
              id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT,
              is_admin INTEGER, avatar TEXT, created_at TEXT, progress TEXT
            );
            CREATE TABLE config(id INTEGER PRIMARY KEY, data TEXT);
            INSERT INTO config(id,data) VALUES(1,'{}');
        """)
        con.commit(); con.close()
        server.DB_PATH = str(migrated)
        server.init_db()
        con = sqlite3.connect(migrated)
        columns = {row[1] for row in con.execute("PRAGMA table_info(users)")}
        con.close()
        self.assertIn("auth_version", columns)


if __name__ == "__main__":
    unittest.main()
