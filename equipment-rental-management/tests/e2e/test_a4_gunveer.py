from uuid import uuid4

from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:5000"


# Successful workflow: Add equipment through the web interface.
def test_add_equipment_success(page: Page):
    equipment_name = "Mountain Bike " + uuid4().hex[:8]

    page.goto(BASE_URL)
    page.get_by_role("link", name="Equipment", exact=True).click()

    # Enter equipment information.
    page.get_by_label("Name", exact=True).fill(equipment_name)
    page.get_by_label("Category").fill("Cycling")
    page.get_by_label("Total Units").fill("5")
    page.get_by_role("button", name="Add Equipment").click()

    # Verify the equipment appears with the correct information.
    row = page.get_by_role("row").filter(
        has=page.get_by_role("cell", name=equipment_name, exact=True)
    )

    expect(row).to_have_count(1)
    expect(row.locator("td").nth(1)).to_have_text(equipment_name)
    expect(row.locator("td").nth(2)).to_have_text("Cycling")
    expect(row.locator("td").nth(3)).to_have_text("5")
    expect(row.locator("td").nth(4)).to_have_text("5")


# Error workflow: Reject checkout of nonexistent equipment.
def test_checkout_nonexistent_equipment(page: Page):
    unique_id = uuid4().hex[:8]
    equipment_name = "Kayak " + unique_id
    renter_name = "Test Renter " + unique_id

    # Create equipment for this test.
    page.goto(BASE_URL)
    page.get_by_role("link", name="Equipment", exact=True).click()
    page.get_by_label("Name", exact=True).fill(equipment_name)
    page.get_by_label("Category").fill("Water Sports")
    page.get_by_label("Total Units").fill("3")
    page.get_by_role("button", name="Add Equipment").click()

    equipment_row = page.get_by_role("row").filter(
        has=page.get_by_role("cell", name=equipment_name, exact=True)
    )

    expect(equipment_row).to_have_count(1)
    expect(equipment_row.locator("td").nth(4)).to_have_text("3")

    # Create a valid renter for this test.
    page.get_by_role("link", name="Renters", exact=True).click()
    page.get_by_label("Name", exact=True).fill(renter_name)
    page.get_by_label("Email").fill(unique_id + "@example.com")
    page.get_by_role("button", name="Add Renter").click()

    renter_row = page.get_by_role("row").filter(
        has=page.get_by_role("cell", name=renter_name, exact=True)
    )

    expect(renter_row).to_have_count(1)
    renter_id = renter_row.locator("td").nth(0).inner_text()

    # Record existing rentals before attempting an invalid checkout.
    page.get_by_role("link", name="Rentals", exact=True).click()
    rental_rows = page.locator("table tr")
    original_count = rental_rows.count()
    original_rentals = rental_rows.all_text_contents()

    # Attempt checkout using an invalid equipment ID.
    page.get_by_label("Equipment ID").fill("-1")
    page.get_by_label("Renter ID").fill(renter_id)
    page.get_by_role("button", name="Check Out").click()

    # Verify that no invalid rental was created.
    expect(rental_rows).to_have_count(original_count)
    assert rental_rows.all_text_contents() == original_rentals

    # Verify that the existing equipment availability is unchanged.
    page.get_by_role("link", name="Equipment", exact=True).click()

    expect(equipment_row).to_have_count(1)
    expect(equipment_row.locator("td").nth(3)).to_have_text("3")
    expect(equipment_row.locator("td").nth(4)).to_have_text("3")
