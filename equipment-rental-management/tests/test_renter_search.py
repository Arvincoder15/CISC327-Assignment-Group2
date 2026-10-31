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
