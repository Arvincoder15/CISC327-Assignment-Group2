
"""
CISC 327 - Assignment 4
Member B: Arvin Askari

End-to-end tests for renter registration and duplicate rental
return prevention using Playwright and Chromium.
"""

import re
from uuid import uuid4

from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:5000"


def test_create_renter_success(page: Page):
    """Verify successful renter registration through the web interface."""

    # Generate unique renter information for test independence.
    unique_id = uuid4().hex[:8]
    renter_name = f"Test Renter {unique_id}"
    renter_email = f"renter_{unique_id}@example.com"

    # Open the application and navigate to the Renters page.
    page.goto(BASE_URL)
    page.get_by_role("link", name="Renters", exact=True).click()

    expect(
        page.get_by_role("heading", name="Renters", exact=True)
    ).to_be_visible()

    # Complete and submit the renter registration form.
    page.get_by_label("Name", exact=True).fill(renter_name)
    page.get_by_label("Email", exact=True).fill(renter_email)
    page.get_by_role("button", name="Add Renter").click()

    # Locate the newly created renter in the table.
    renter_row = page.get_by_role("row").filter(
        has_text=renter_email
    )

    # Verify that exactly one matching renter appears.
    expect(renter_row).to_have_count(1)
    expect(renter_row).to_be_visible()

    # Verify the displayed renter information.
    expect(
        renter_row.get_by_role("cell", name=renter_name, exact=True)
    ).to_be_visible()

    expect(
        renter_row.get_by_role("cell", name=renter_email, exact=True)
    ).to_be_visible()

    # Reload the page and verify that the renter remains registered.
    page.reload()

    expect(renter_row).to_have_count(1)
    expect(renter_row).to_be_visible()


def test_duplicate_return_does_not_increase_availability(page: Page):
    """Verify that returning a rental twice does not restore inventory twice."""

    # Generate unique data to keep this test independent.
    unique_id = uuid4().hex[:8]
    equipment_name = f"Test Mountain Bike {unique_id}"
    renter_name = f"Return Test Renter {unique_id}"
    renter_email = f"return_{unique_id}@example.com"

    # Step 1: Create equipment with two available units.
    page.goto(BASE_URL)
    page.get_by_role("link", name="Equipment", exact=True).click()

    page.get_by_label("Name", exact=True).fill(equipment_name)
    page.get_by_label("Category", exact=True).fill("Bikes")
    page.get_by_label("Total Units", exact=True).fill("2")
    page.get_by_role("button", name="Add Equipment").click()

    equipment_row = page.get_by_role("row").filter(
        has_text=equipment_name
    )

    expect(equipment_row).to_have_count(1)
    expect(equipment_row.get_by_role("cell").nth(3)).to_have_text("2")
    expect(equipment_row.get_by_role("cell").nth(4)).to_have_text("2")

    # Retrieve the generated equipment ID.
    equipment_id = (
        equipment_row.get_by_role("cell").nth(0).inner_text().strip()
    )

    # Step 2: Create a renter specifically for this test.
    page.get_by_role("link", name="Renters", exact=True).click()

    page.get_by_label("Name", exact=True).fill(renter_name)
    page.get_by_label("Email", exact=True).fill(renter_email)
    page.get_by_role("button", name="Add Renter").click()

    renter_row = page.get_by_role("row").filter(
        has_text=renter_email
    )

    expect(renter_row).to_have_count(1)
    expect(renter_row).to_be_visible()

    # Retrieve the generated renter ID.
    renter_id = (
        renter_row.get_by_role("cell").nth(0).inner_text().strip()
    )

    # Step 3: Check out the equipment to the renter.
    page.get_by_role("link", name="Rentals", exact=True).click()

    page.get_by_label("Equipment ID", exact=True).fill(equipment_id)
    page.get_by_label("Renter ID", exact=True).fill(renter_id)
    page.get_by_role("button", name="Check Out", exact=True).click()

    # Locate the rental using its equipment and renter IDs.
    rental_row = (
        page.get_by_role("row")
        .filter(
            has=page.locator("td:nth-child(2)").filter(
                has_text=re.compile(rf"^{equipment_id}$")
            )
        )
        .filter(
            has=page.locator("td:nth-child(3)").filter(
                has_text=re.compile(rf"^{renter_id}$")
            )
        )
    )

    expect(rental_row).to_have_count(1)

    rental_id = (
        rental_row.get_by_role("cell").nth(0).inner_text().strip()
    )

    # Verify the rental is active and can be returned.
    expect(rental_row.get_by_role("cell").nth(5)).to_have_text("-")

    expect(
        rental_row.get_by_role("button", name="Return", exact=True)
    ).to_be_visible()

    # Verify that checkout decreased equipment availability.
    page.get_by_role("link", name="Equipment", exact=True).click()

    expect(equipment_row.get_by_role("cell").nth(4)).to_have_text("1")

    # Step 4: Open the active rental in two browser tabs.
    page.get_by_role("link", name="Rentals", exact=True).click()

    second_page = page.context.new_page()

    try:
        second_page.goto(f"{BASE_URL}/ui/rentals")

        second_rental_row = second_page.get_by_role("row").filter(
            has=second_page.locator("td:first-child").filter(
                has_text=re.compile(rf"^{rental_id}$")
            )
        )

        expect(second_rental_row).to_have_count(1)

        expect(
            second_rental_row.get_by_role(
                "button", name="Return", exact=True
            )
        ).to_be_visible()

        # Step 5: Return the equipment using the first tab.
        rental_row.get_by_role(
            "button", name="Return", exact=True
        ).click()

        # Verify that a return date has been recorded.
        return_date_cell = rental_row.get_by_role("cell").nth(5)

        expect(return_date_cell).to_have_text(
            re.compile(r"^\d{4}-\d{2}-\d{2}$")
        )

        original_return_date = return_date_cell.inner_text().strip()

        # Verify that the Return button is no longer available.
        expect(
            rental_row.get_by_role(
                "button", name="Return", exact=True
            )
        ).to_have_count(0)

        # Verify that the first return restored availability to two.
        page.get_by_role("link", name="Equipment", exact=True).click()

        expect(
            equipment_row.get_by_role("cell").nth(4)
        ).to_have_text("2")

        # Step 6: Attempt a duplicate return using the stale second tab.
        second_rental_row.get_by_role(
            "button", name="Return", exact=True
        ).click()

        # Verify that the original return date remains unchanged.
        expect(
            second_rental_row.get_by_role("cell").nth(5)
        ).to_have_text(original_return_date)

        # Verify that the Return button is removed from the second tab.
        expect(
            second_rental_row.get_by_role(
                "button", name="Return", exact=True
            )
        ).to_have_count(0)

        # Step 7: Verify that the duplicate return did not increase inventory.
        page.reload()

        expect(
            equipment_row.get_by_role("cell").nth(3)
        ).to_have_text("2")

        expect(
            equipment_row.get_by_role("cell").nth(4)
        ).to_have_text("2")

    finally:
        second_page.close()
