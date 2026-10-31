# Tests for Renter Management and Rental Operations
# Arvin - Member 2

from datetime import date, timedelta

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
    

def test_update_renter(client):
    renter = client.post("/renters", json={
        "name": "Alex",
        "email": "alex@example.com"
    }).get_json()

    response = client.put(f"/renters/{renter['id']}", json={
        "name": "Alexander"
    })

    assert response.status_code == 200
    assert response.get_json()["name"] == "Alexander"

    saved = client.get(f"/renters/{renter['id']}").get_json()
    assert saved["name"] == "Alexander"
    assert saved["email"] == "alex@example.com"


def test_update_nonexistent_renter(client):
    response = client.put("/renters/999", json={
        "name": "Nobody"
    })

    assert response.status_code == 404


def test_delete_renter(client):
    renter = client.post("/renters", json={
        "name": "Alex",
        "email": "alex@example.com"
    }).get_json()

    response = client.delete(f"/renters/{renter['id']}")
    assert response.status_code == 204

    check = client.get(f"/renters/{renter['id']}")
    assert check.status_code == 404


def test_delete_nonexistent_renter(client):
    response = client.delete("/renters/999")
    assert response.status_code == 404

# ---------- RENTAL TEST HELPER ----------

def create_test_rental(client):
    equipment = client.post("/equipment", json={
        "name": "Camping Tent",
        "category": "Camping",
        "total_units": 2
    }).get_json()

    renter = client.post("/renters", json={
        "name": "Alex",
        "email": "alex@example.com"
    }).get_json()

    response = client.post("/rentals", json={
        "equipment_id": equipment["id"],
        "renter_id": renter["id"],
        "deposit_amount": 50.0
    })

    assert response.status_code == 201

    return equipment["id"], response.get_json()["id"]


# ---------- RETURN RENTAL ----------

def test_return_restores_equipment(client):
    equipment_id, rental_id = create_test_rental(client)

    before = client.get(
        f"/equipment/{equipment_id}"
    ).get_json()
    assert before["available_units"] == 1

    response = client.put(f"/rentals/{rental_id}/return")

    assert response.status_code == 200
    assert response.get_json()["return_date"] is not None

    after = client.get(
        f"/equipment/{equipment_id}"
    ).get_json()
    assert after["available_units"] == 2


def test_cannot_return_twice(client):
    _, rental_id = create_test_rental(client)

    first = client.put(f"/rentals/{rental_id}/return")
    second = client.put(f"/rentals/{rental_id}/return")

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.get_json()["error"] == "Rental already returned"


# ---------- EXTEND RENTAL ----------

def test_extend_rental(client):
    _, rental_id = create_test_rental(client)

    response = client.put(
        f"/rentals/{rental_id}/extend",
        json={"days": 2}
    )

    assert response.status_code == 200

    expected_due_date = date.today() + timedelta(days=9)

    assert response.get_json()["due_date"] == (
        expected_due_date.isoformat()
    )


def test_cannot_extend_returned_rental(client):
    _, rental_id = create_test_rental(client)

    client.put(f"/rentals/{rental_id}/return")

    response = client.put(
        f"/rentals/{rental_id}/extend",
        json={"days": 2}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Rental already returned"


# ---------- RELEASE RENTAL DEPOSIT ----------

def test_cannot_release_deposit_before_return(client):
    _, rental_id = create_test_rental(client)

    response = client.put(
        f"/rentals/{rental_id}/deposit/release"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Equipment has not been returned yet"
    )


def test_deposit_release_persists(client):
    _, rental_id = create_test_rental(client)

    client.put(f"/rentals/{rental_id}/return")

    response = client.put(
        f"/rentals/{rental_id}/deposit/release"
    )

    assert response.status_code == 200
    assert response.get_json()["deposit_released"] is True

    rentals = client.get("/rentals").get_json()
    saved_rental = next(
        rental for rental in rentals
        if rental["id"] == rental_id
    )

    assert saved_rental["deposit_released"] is True


# R4: Search renters by name

def create_search_renters(client):
    renters = [
        {"name": "Alex Johnson", "email": "alex@example.com"},
        {"name": "Samantha Lee", "email": "sam@example.com"},
        {"name": "Alexander Smith", "email": "alexander@example.com"}
    ]

    for renter in renters:
        response = client.post("/renters", json=renter)
        assert response.status_code == 201

def test_search_renters_by_partial_name(client):
    create_search_renters(client)
    response = client.get("/renters?name=Alex")
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 2
    names = {renter["name"] for renter in results}
    assert names == {"Alex Johnson", "Alexander Smith"}

def test_search_renters_case_insensitive(client):
    create_search_renters(client)
    response = client.get("/renters?name=SAMANTHA")
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 1
    assert results[0]["name"] == "Samantha Lee"


def test_search_renters_no_matches(client):
    create_search_renters(client)
    response = client.get("/renters?name=Michael")
    assert response.status_code == 200
    assert response.get_json() == []

def test_list_renters_without_search_filter(client):
    create_search_renters(client)
    response = client.get("/renters")
    assert response.status_code == 200
    assert len(response.get_json()) == 3
