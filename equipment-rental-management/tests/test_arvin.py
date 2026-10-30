# Tests for Renter Management and Rental Operations
# Arvin - Member 2

def test_create_renter(client):
    response = client.post("/renters", json={
        "name": "Alex",
        "email": "alex@example.com"
    })

    assert response.status_code == 201
    renter = response.get_json()
    assert renter["name"] == "Alex"
    assert renter["email"] == "alex@example.com"
    assert isinstance(renter["id"], int)

    saved = client.get(f"/renters/{renter['id']}")
    assert saved.status_code == 200
    assert saved.get_json()["name"] == "Alex"


def test_list_renters(client):
    client.post("/renters", json={
        "name": "Alex", "email": "alex@example.com"
    })
    client.post("/renters", json={
        "name": "Sam", "email": "sam@example.com"
    })

    response = client.get("/renters")
    assert response.status_code == 200
    renters = response.get_json()

    assert len(renters) == 2
    assert {r["name"] for r in renters} == {"Alex", "Sam"}


def test_get_renter_by_id(client):
    renter = client.post("/renters", json={
        "name": "Alex", "email": "alex@example.com"
    }).get_json()

    response = client.get(f"/renters/{renter['id']}")
    assert response.status_code == 200
    assert response.get_json()["email"] == "alex@example.com"


def test_get_nonexistent_renter(client):
    response = client.get("/renters/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"
