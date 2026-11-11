
# Assignment 3 - Notification Tests
# Gunveer - Member A

from unittest.mock import patch

from app import store


def test_checkout_notification_success_stub(client, monkeypatch):
    # Make the notification service report success.
    monkeypatch.setattr(
        "app.routes.rentals.send_notification",
        lambda recipient, subject, message: True
    )

    equipment = client.post("/equipment", json={
        "name": "Mountain Bike",
        "category": "Bicycle",
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
    assert rental["notification_sent"] is True

    # The checkout must be saved and equipment units reduced.
    assert len(store.rentals) == 1

    check = client.get(f"/equipment/{equipment['id']}")
    assert check.get_json()["available_units"] == 2


def test_checkout_notification_correct_details_mock(client):
    equipment = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water Sports",
        "total_units": 2
    }).get_json()

    renter = client.post("/renters", json={
        "name": "Sam",
        "email": "sam@example.com"
    }).get_json()

    # Check the notification recipient, subject, and message.
    with patch(
        "app.routes.rentals.send_notification",
        return_value=True
    ) as mock_send:

        response = client.post("/rentals", json={
            "equipment_id": equipment["id"],
            "renter_id": renter["id"]
        })

    assert response.status_code == 201

    rental = response.get_json()
    assert rental["renter_id"] == renter["id"]
    assert rental["notification_sent"] is True

    mock_send.assert_called_once_with(
        "sam@example.com",
        "[Trailside Outdoor Gear Rental] Checkout Confirmation",
        f"Your rental for equipment {equipment['id']} "
        f"has been confirmed. Due date: {rental['due_date']}."
    )

    # Verify that the checkout still updated the application.
    assert len(store.rentals) == 1

    check = client.get(f"/equipment/{equipment['id']}")
    assert check.get_json()["available_units"] == 1



# Task 3 - Coverage-Directed Tests
# Gunveer - Member A

def test_update_nonexistent_equipment(client):
    response = client.put("/equipment/999", json={
        "name": "Mountain Bike"
    })

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"


def test_delete_nonexistent_equipment(client):
    response = client.delete("/equipment/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"


def test_change_status_nonexistent_equipment(client):
    response = client.patch("/equipment/999/status", json={
        "is_available": False
    })

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"


def test_availability_nonexistent_equipment(client):
    response = client.get("/equipment/999/availability")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"



# Task 3 - Coverage-Directed Tests for Views

def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<html" in response.data.lower()


def test_equipment_page_lists_equipment(client):
    equipment = client.post("/equipment", json={
        "name": "Mountain Bike",
        "category": "Bicycle",
        "total_units": 3
    }).get_json()

    response = client.get("/ui/equipment")

    assert response.status_code == 200
    assert b"Mountain Bike" in response.data
    assert equipment["id"] in store.equipment


def test_equipment_page_adds_equipment(client):
    response = client.post("/ui/equipment", data={
        "name": "Camping Tent",
        "category": "Camping",
        "total_units": "4"
    })

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/ui/equipment")

    assert len(store.equipment) == 1
    item = next(iter(store.equipment.values()))
    assert item.name == "Camping Tent"
    assert item.total_units == 4
    assert item.available_units == 4


def test_delete_equipment_page(client):
    equipment = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water Sports",
        "total_units": 2
    }).get_json()

    response = client.post(
        f"/ui/equipment/{equipment['id']}/delete"
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/ui/equipment")
    assert equipment["id"] not in store.equipment


def test_rentals_page_lists_rentals(client):
    equipment = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    }).get_json()

    renter = client.post("/renters", json={
        "name": "Jake",
        "email": "jake@example.com"
    }).get_json()

    client.post("/rentals", json={
        "equipment_id": equipment["id"],
        "renter_id": renter["id"]
    })

    response = client.get("/ui/rentals")

    assert response.status_code == 200
    assert len(store.rentals) == 1
    assert str(equipment["id"]).encode() in response.data


def test_rentals_page_checkout(client):
    equipment = client.post("/equipment", json={
        "name": "Mountain Bike",
        "category": "Bicycle",
        "total_units": 3
    }).get_json()

    renter = client.post("/renters", json={
        "name": "Sam",
        "email": "sam@example.com"
    }).get_json()

    response = client.post("/ui/rentals", data={
        "equipment_id": str(equipment["id"]),
        "renter_id": str(renter["id"])
    })

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/ui/rentals")

    assert len(store.rentals) == 1
    rental = next(iter(store.rentals.values()))
    assert rental.equipment_id == equipment["id"]
    assert rental.renter_id == renter["id"]

    assert store.equipment[equipment["id"]].available_units == 2


def test_rentals_page_nonexistent_equipment(client):
    renter = client.post("/renters", json={
        "name": "Jake",
        "email": "jake@example.com"
    }).get_json()

    response = client.post("/ui/rentals", data={
        "equipment_id": "999",
        "renter_id": str(renter["id"])
    })

    assert response.status_code == 302
    assert len(store.rentals) == 0
