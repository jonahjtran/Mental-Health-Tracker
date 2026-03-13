import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def test_main_import_registers_expected_routes() -> None:
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "JWT_SECRET": "test-jwt-secret",
            "JWT_EXPIRES_MINUTES": "60",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "GOOGLE_REDIRECT_URI": "http://localhost:8000/api/v1/auth/callback/google",
            "FRONTEND_URL": "http://frontend.test",
            "INSIGHTS_MODEL": "test-model",
            "INSIGHTS_API_KEY": "test-key",
        }
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import backend.app.main as m; "
                "paths = sorted(set(getattr(r, 'path', None) for r in m.app.routes)); "
                "print('\\n'.join(paths))"
            ),
        ],
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "/api/v1/auth/login/google" in result.stdout
    assert "/api/v1/me/journals" in result.stdout
    assert "/api/v1/insights/me/journals/{journal_id}/insights" in result.stdout
    assert "/api/v1/health" in result.stdout
