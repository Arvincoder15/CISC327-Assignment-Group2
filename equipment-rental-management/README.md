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


## Assignment 4: End-to-End Testing and Containerization

Assignment 4 extends the existing Equipment Rental Management
application with browser-based end-to-end testing using Playwright
and application containerization using Docker.

### Prerequisites

- Python 3.11 or a compatible newer version
- pip
- Git
- Playwright and Chromium
- Docker Desktop (macOS/Windows) or Docker Engine (Linux)

All commands below should be executed from the
`equipment-rental-management` directory.

### Local Application Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies and Chromium:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Start the Flask application:

```bash
python run.py
```

Open the application in a browser at:

http://127.0.0.1:5000/

### Existing Automated Tests

Run the existing unit and integration tests separately from
the browser-based E2E tests:

```bash
python -m pytest -v --ignore=tests/e2e --cov=app --cov-report=term-missing --cov-fail-under=90
```

The existing Assignment 3 test suite contains 62 tests,
with a minimum required coverage threshold of 90%.

### End-to-End Testing

The E2E tests use Playwright to automate user interactions
with the existing HTML interface through a real Chromium browser.

| Member | Scenario | Type |
|---|---|---|
| Arvin Askari | Create a renter and verify registration | Successful |
| Arvin Askari | Prevent duplicate rental returns from increasing availability twice | Boundary |
| Gunveer | Add equipment and verify its details | Successful |
| Gunveer | Attempt checkout of nonexistent equipment | Error |

Test files:

- `tests/e2e/test_a4_arvin.py`
- `tests/e2e/test_a4_gunveer.py`

Each test creates the data it requires and does not rely on
data created by other tests.

Start the Flask application in one terminal:

```bash
python run.py
```

In a second terminal, activate the virtual environment and
run all E2E tests in headed mode:

```bash
python -m pytest tests/e2e -v --headed
```

To run the tests in headless mode:

```bash
python -m pytest tests/e2e -v
```

To run an individual member's tests:

```bash
python -m pytest tests/e2e/test_a4_arvin.py -v --headed
python -m pytest tests/e2e/test_a4_gunveer.py -v --headed
```

### Docker Setup

Ensure Docker is installed and running:

```bash
docker --version
docker info
```

Build the Docker image from the application directory:

```bash
docker build -t cisc327-a4 .
```

Stop any locally running Flask application before starting
the Docker container to avoid a port conflict.

Run the container:

```bash
docker run --rm --name cisc327-a4-container -p 5000:5000 cisc327-a4
```

The containerized application listens on `0.0.0.0:5000`
and exposes port 5000 to the host machine.

Access the application at:

http://127.0.0.1:5000/

To verify that the application responds over HTTP:

```bash
curl -i http://127.0.0.1:5000/
```

To view the running container:

```bash
docker ps
```

To stop the container, press Ctrl+C in the terminal running
Docker or execute:

```bash
docker stop cisc327-a4-container
```

### Running E2E Tests Against Docker

Ensure that the local Flask server is stopped and the Docker
container is running on port 5000.

From a separate terminal, activate the local Python virtual
environment and execute:

```bash
python -m pytest tests/e2e -v --headed
```

The same E2E test suite is used for both local Flask execution
and Docker execution without modifying the test code.

### Data Persistence

The application uses an in-memory data store rather than
a persistent database.

All equipment, renter, and rental records are reset when
the Flask application or Docker container stops or restarts.

The E2E tests generate their own test data to support
independent and reproducible execution.

### Continuous Integration

GitHub Actions automatically runs two separate test jobs:

- Existing unit and integration tests with a minimum
  coverage threshold of 90%.
- Playwright E2E tests using headless Chromium and a
  running Flask application.

The workflow is located at `.github/workflows/tests.yml`
in the repository root.
