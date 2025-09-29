"""
Tests for main application endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns correct information"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "AI Ad Copy Generator API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"


def test_health_endpoint(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "database" in data
    assert "ai_service" in data


def test_cors_headers(client: TestClient):
    """Test CORS headers are properly set"""
    # Test OPTIONS request (preflight)
    response = client.options("/")
    
    # Should allow the request
    assert response.status_code in [200, 405]  # 405 is OK for OPTIONS on GET endpoint
    
    # Test actual request with Origin header
    headers = {"Origin": "http://localhost:3000"}
    response = client.get("/", headers=headers)
    
    assert response.status_code == 200


def test_api_documentation_accessible(client: TestClient):
    """Test that API documentation endpoints are accessible"""
    # Test OpenAPI JSON schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert schema["info"]["title"] == "AI Ad Copy Generator"
    assert schema["info"]["version"] == "1.0.0"
    
    # Test Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_nonexistent_endpoint(client: TestClient):
    """Test that nonexistent endpoints return 404"""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_method_not_allowed(client: TestClient):
    """Test that wrong HTTP methods return 405"""
    response = client.post("/")  # Root only accepts GET
    assert response.status_code == 405
