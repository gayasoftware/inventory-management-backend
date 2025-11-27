def test_create_item(client):
    # First login to get token (assuming admin user needed for creation based on router)
    # Register admin user
    client.post(
        "/auth/register",
        json={"username": "admin", "email": "admin@example.com", "password": "admin", "full_name": "Admin User", "role": "admin"},
    )
    login_res = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/items/",
        json={"title": "Test Item", "description": "A test item", "price": 10.5, "quantity": 100},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["price"] == 10.5

def test_read_items(client):
    # Login as normal user
    client.post(
        "/auth/register",
        json={"username": "user", "email": "user@example.com", "password": "user", "full_name": "Normal User"},
    )
    login_res = client.post(
        "/auth/token",
        data={"username": "user", "password": "user"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/items/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
