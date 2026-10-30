# Tests for Equipment Rental Management
# Gunveer - Member 1

def test_add_equipment(client):
    response = client.post("/equipment", json={
        "name": "Mountain Bike",
        "category": "Bicycle",
        "total_units": 5
    })

    assert response.status_code == 201

    data = response.get_json()
    assert data["name"] == "Mountain Bike"
    assert data["category"] == "Bicycle"
    assert data["total_units"] == 5
    assert data["available_units"] == 5


def test_list_equipment(client):
    client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water Sports",
        "total_units": 3
    })

    response = client.get("/equipment")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Kayak"
    assert data[0]["available_units"] == 3


def test_get_equipment_by_id(client):
    response = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    })

    equipment_id = response.get_json()["id"]

    response = client.get(f"/equipment/{equipment_id}")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Tent"
    assert response.get_json()["total_units"] == 2


def test_get_nonexistent_equipment(client):
    response = client.get("/equipment/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"


def test_update_equipment(client):
    response = client.post("/equipment", json={
        "name": "Bike",
        "category": "Bicycle",
        "total_units": 5
    })
    equipment_id = response.get_json()["id"]

    response = client.put(f"/equipment/{equipment_id}", json={
        "name": "Mountain Bike",
        "category": "Bicycle",
        "total_units": 8
    })

    assert response.status_code == 200
    assert response.get_json()["name"] == "Mountain Bike"
    assert response.get_json()["total_units"] == 8

    updated = client.get(f"/equipment/{equipment_id}")
    assert updated.get_json()["name"] == "Mountain Bike"


def test_delete_equipment(client):
    response = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    })
    equipment_id = response.get_json()["id"]

    response = client.delete(f"/equipment/{equipment_id}")

    assert response.status_code in (200, 204)

    check = client.get(f"/equipment/{equipment_id}")
    assert check.status_code == 404


def test_change_equipment_status(client):
    response = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water Sports",
        "total_units": 1
    })
    equipment_id = response.get_json()["id"]

    response = client.patch(
        f"/equipment/{equipment_id}/status",
        json={"is_available": False}
    )

    assert response.status_code == 200
    assert response.get_json()["is_available"] is False

    check = client.get(f"/equipment/{equipment_id}/availability")
    assert check.status_code == 200
    assert check.get_json()["is_available"] is False
