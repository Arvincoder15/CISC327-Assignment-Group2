# Equipment Rental Management (ERM)

A small Flask REST API for tracking equipment, renters, and rentals. Data is
stored **in memory** (plain Python objects, no database) and is reset every
time the app restarts — this project is meant to run before you've covered
databases.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The API runs at `http://127.0.0.1:5000`.

## Web UI

Open `http://127.0.0.1:5000/` in a browser for a basic HTML front end (plain
forms and tables, no JavaScript) to add/delete equipment and renters, and
check equipment in/out:

| Page | Path |
|---|---|
| Home | `/` |
| Equipment | `/ui/equipment` |
| Renters | `/ui/renters` |
| Rentals | `/ui/rentals` |

This UI is separate from the JSON API below — it's there so you can see the
app working without a REST client, and calls the same in-memory store.

## Entities

- **Equipment**: `id, name, category, total_units, available_units`
- **Renter**: `id, name, email, membership_date`
- **Rental**: `id, equipment_id, renter_id, rental_date, due_date, return_date`

## JSON API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/equipment` | List all equipment |
| POST | `/equipment` | Add an equipment item |
| GET | `/equipment/<id>` | Get one equipment item |
| PUT | `/equipment/<id>` | Update an equipment item |
| DELETE | `/equipment/<id>` | Delete an equipment item |
| GET | `/renters` | List all renters |
| GET | `/renters?name=<search_term>` | Search renters by full or partial name (case-insensitive). Returns matching renters or an empty list. |
| POST | `/renters` | Create a renter |
| GET | `/renters/<id>` | Get one renter |
| PUT | `/renters/<id>` | Update a renter |
| DELETE | `/renters/<id>` | Delete a renter |
| POST | `/rentals` | Check out equipment (`equipment_id`, `renter_id`). Rejects out-of-service equipment (`is_available: false`) with HTTP 400 and `"Equipment is out of service"`. |
| PUT | `/rentals/<id>/return` | Return rented equipment |
| GET | `/rentals?renter_id=&equipment_id=` | Look up rentals |

## R4: Search Renters by Name

Staff can search for renters by using the optional `name` query parameter
on the existing `GET /renters` endpoint.

**Example request:**

```http
GET /renters?name=alex
```

The search supports partial-name matching and is case-insensitive.
For example, searching for `alex` can return both "Alex Johnson"
and "Alexander Smith".

**Search behaviour:**
- If matching renters exist, the API returns their records as a JSON list.
- If no renters match, the API returns an empty list (`[]`).
- If no name is provided, the API returns all renters.
- Successful requests return HTTP 200.

**Automated tests:** `tests/test_arvin.py`

## R7: Prevent Checkout of Out-of-Service Equipment

The system prevents equipment marked as out of service from being rented by checking its `is_available` status before processing a checkout through the existing `POST /rentals` endpoint.

### Example Request

```http
POST /rentals
Content-Type: application/json
```

```json
{
  "equipment_id": 2,
  "renter_id": 1
}
```

### Checkout Behaviour

- If `is_available` is `false`, the API rejects the checkout with HTTP 400 and the error message `"Equipment is out of service"`.
- Rejected checkouts do not create rental records or decrease available equipment units.
- If the equipment is serviceable and available, the checkout proceeds normally and creates a rental record.
- Successful checkouts return HTTP 201.
- If the equipment ID does not exist, the API returns HTTP 404.

### Automated Tests

The following tests are implemented in `tests/test_gunveer.py`:

- `test_cannot_checkout_out_of_service_equipment`
- `test_checkout_serviceable_equipment`

**Test results:** 2 passed, 0 failed.

## Tests

```bash
pytest
```

