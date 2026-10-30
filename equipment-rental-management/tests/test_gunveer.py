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


def test_equipment_availability(client):
    response = client.post("/equipment", json={
        "name": "Mountain Bike",
        "category": "Bicycle",
        "total_units": 5
    })
    equipment_id = response.get_json()["id"]

    response = client.get(f"/equipment/{equipment_id}/availability")

    assert response.status_code == 200
    data = response.get_json()
    assert data["available_units"] == 5
    assert data["total_units"] == 5
    assert data["is_available"] is True


def test_equipment_checkout(client):
    equipment = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water Sports",
        "total_units": 3
    }).get_json()

    renter = client.post("/renters", json={
        "name": "Jake",
        "email": "jake@example.com"
    }).get_json()

    response = client.post("/rentals", json={
        "equipment_id": equipment["id"],
        "renter_id": renter["id"]
    })

    assert response.status_code == 201
    rental = response.get_json()
    assert rental["equipment_id"] == equipment["id"]
    assert rental["renter_id"] == renter["id"]
    assert rental["due_date"] is not None
    assert rental["return_date"] is None

    check = client.get(f"/equipment/{equipment['id']}/availability")
    assert check.get_json()["available_units"] == 2


def test_list_rentals(client):
    equipment = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    }).get_json()

    renter = client.post("/renters", json={
        "name": "Sam",
        "email": "sam@example.com"
    }).get_json()

    client.post("/rentals", json={
        "equipment_id": equipment["id"],
        "renter_id": renter["id"]
    })

    response = client.get("/rentals")

    assert response.status_code == 200
    rentals = response.get_json()
    assert len(rentals) == 1
    assert rentals[0]["equipment_id"] == equipment["id"]
    assert rentals[0]["renter_id"] == renter["id"]


def test_filter_rentals_by_renter(client):
    equipment1 = client.post("/equipment", json={
        "name": "Bike",
        "category": "Bicycle",
        "total_units": 2
    }).get_json()

    equipment2 = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water Sports",
        "total_units": 2
    }).get_json()

    renter = client.post("/renters", json={
        "name": "Jake",
        "email": "jake@example.com"
    }).get_json()

    client.post("/rentals", json={
        "equipment_id": equipment1["id"],
        "renter_id": renter["id"]
    })

    client.post("/rentals", json={
        "equipment_id": equipment2["id"],
        "renter_id": renter["id"]
    })

    response = client.get(f"/rentals?renter_id={renter['id']}")

    assert response.status_code == 200
    rentals = response.get_json()
    assert len(rentals) == 2
    assert all(r["renter_id"] == renter["id"] for r in rentals)
