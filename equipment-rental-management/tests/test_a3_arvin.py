
"""Assignment 3 coverage-directed tests - Member B (Arvin)."""

from datetime import date

from app import store
from app.models.equipment import Equipment
from app.models.renter import Renter
from app.models.rental import Rental


# ---------------------------------------------------------
# Helpers for creating isolated test data
# ---------------------------------------------------------

def add_equipment(equipment_id=1, available_units=2):
    item = Equipment(
        id=equipment_id,
        name="Camping Tent",
        category="Camping",
        total_units=2,
        available_units=available_units,
    )
    store.equipment[equipment_id] = item
    return item


def add_renter(renter_id=1):
    renter = Renter(
        id=renter_id,
        name="Alex Smith",
        email="alex@example.com",
    )
    store.renters[renter_id] = renter
    return renter


def add_rental(rental_id=1, equipment_id=1, renter_id=1):
    rental = Rental(
        id=rental_id,
        equipment_id=equipment_id,
        renter_id=renter_id,
        due_date=Rental.default_due_date(),
    )
    store.rentals[rental_id] = rental
    return rental


# ---------------------------------------------------------
# Task 3 — views.py: renters_page()
# ---------------------------------------------------------

def test_ui_renters_page_displays_existing_renter(client):
    add_renter()

    response = client.get("/ui/renters")

    assert response.status_code == 200
    assert b"Alex Smith" in response.data


def test_ui_renters_page_creates_renter(client):
    response = client.post(
        "/ui/renters",
        data={
            "name": "Jordan Lee",
            "email": "jordan@example.com",
        },
    )

    assert response.status_code == 302
    assert len(store.renters) == 1

    renter = next(iter(store.renters.values()))
    assert renter.name == "Jordan Lee"
    assert renter.email == "jordan@example.com"


# ---------------------------------------------------------
# Task 3 — views.py: delete_renter_page()
# ---------------------------------------------------------

def test_ui_delete_existing_renter(client):
    add_renter()

    response = client.post("/ui/renters/1/delete")

    assert response.status_code == 302
    assert 1 not in store.renters


def test_ui_delete_nonexistent_renter(client):
    add_renter()

    response = client.post("/ui/renters/999/delete")

    assert response.status_code == 302
    assert 1 in store.renters
    assert len(store.renters) == 1


# ---------------------------------------------------------
# Task 3 — views.py: return_rental_page()
# ---------------------------------------------------------

def test_ui_return_rental_restores_equipment(client):
    item = add_equipment(available_units=1)
    rental = add_rental()

    response = client.post("/ui/rentals/1/return")

    assert response.status_code == 302
    assert rental.return_date == date.today()
    assert item.available_units == 2


def test_ui_return_rental_twice_does_not_restore_twice(client):
    item = add_equipment(available_units=1)
    rental = add_rental()

    first = client.post("/ui/rentals/1/return")
    second = client.post("/ui/rentals/1/return")

    assert first.status_code == 302
    assert second.status_code == 302
    assert rental.return_date == date.today()
    assert item.available_units == 2


def test_ui_return_nonexistent_rental(client):
    item = add_equipment(available_units=1)

    response = client.post("/ui/rentals/999/return")

    assert response.status_code == 302
    assert item.available_units == 1
    assert len(store.rentals) == 0


def test_ui_return_rental_with_missing_equipment(client):
    rental = add_rental(equipment_id=999)

    response = client.post("/ui/rentals/1/return")

    assert response.status_code == 302
    assert rental.return_date == date.today()
    assert len(store.equipment) == 0


# ---------------------------------------------------------
# Task 3 — rentals.py: uncovered API branches
# ---------------------------------------------------------

def test_api_list_rentals_filters_by_equipment(client):
    add_equipment(equipment_id=1)
    add_equipment(equipment_id=2)
    add_rental(rental_id=1, equipment_id=1)
    add_rental(rental_id=2, equipment_id=2)

    response = client.get("/rentals?equipment_id=2")

    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 1
    assert results[0]["equipment_id"] == 2


def test_api_checkout_missing_equipment(client):
    response = client.post(
        "/rentals",
        json={"equipment_id": 999, "renter_id": 1},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"
    assert len(store.rentals) == 0


def test_api_return_nonexistent_rental(client):
    response = client.put("/rentals/999/return")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Rental not found"
    assert len(store.rentals) == 0


def test_api_extend_nonexistent_rental(client):
    response = client.put(
        "/rentals/999/extend",
        json={"days": 3},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Rental not found"
    assert len(store.rentals) == 0


def test_api_release_deposit_nonexistent_rental(client):
    response = client.put("/rentals/999/deposit/release")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Rental not found"
    assert len(store.rentals) == 0


def test_api_release_deposit_before_return(client):
    rental = add_rental()

    response = client.put("/rentals/1/deposit/release")

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Equipment has not been returned yet"
    )
    assert rental.deposit_released is False
