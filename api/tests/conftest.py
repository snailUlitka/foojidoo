import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
