from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_main():
    response = client.post(
        "/reports/",
        json={"file_path": "assets/financellc.pdf", "company_name": "FinanceLLC"},
    )
    assert response.status_code == 200
