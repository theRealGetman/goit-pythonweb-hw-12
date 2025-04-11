from datetime import date


contact_data = {
    "first_name": "Bruce",
    "last_name": "Wayne",
    "phone": "1234567890",
    "email": "bruce.wayne@example.com",
    "date_of_birth": str(date(1980, 1, 15)),
}

updated_contact_data = {
    "first_name": "Batman",
    "last_name": "Wayne",
    "phone": "0987654321",
    "email": "batman@example.com",
    "date_of_birth": str(date(1980, 1, 15)),
}


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["email"] == contact_data["email"]
    assert "id" in data


def test_create_contact_unauthorized(client):
    response = client.post("/api/contacts/", json=contact_data)

    assert response.status_code == 401, response.text
    data = response.json()
    assert "detail" in data


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts/", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Should have at least the contact we created
    assert data[0]["first_name"] == contact_data["first_name"]


def test_get_contacts_with_search(client, get_token):
    response = client.get(
        "/api/contacts/?q=Bruce", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["first_name"] == "Bruce"


def test_get_contact_by_id(client, get_token):
    # First get all contacts to get an id
    response = client.get(
        "/api/contacts/", headers={"Authorization": f"Bearer {get_token}"}
    )
    contacts = response.json()
    contact_id = contacts[0]["id"]

    # Then get the specific contact
    response = client.get(
        f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == contact_id
    assert data["first_name"] == contact_data["first_name"]


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/9999",  # Assuming this ID doesn't exist
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_update_contact(client, get_token):
    # First get all contacts to get an id
    response = client.get(
        "/api/contacts/", headers={"Authorization": f"Bearer {get_token}"}
    )
    contacts = response.json()
    contact_id = contacts[0]["id"]

    # Then update the contact
    response = client.put(
        f"/api/contacts/{contact_id}",
        json=updated_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == contact_id
    assert data["first_name"] == updated_contact_data["first_name"]
    assert data["email"] == updated_contact_data["email"]


def test_delete_contact(client, get_token):
    # First get all contacts to get an id
    response = client.get(
        "/api/contacts/", headers={"Authorization": f"Bearer {get_token}"}
    )
    contacts = response.json()
    contact_id = contacts[0]["id"]

    # Then delete the contact
    response = client.delete(
        f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == contact_id

    # Verify it's deleted
    response = client.get(
        f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text


# def test_get_upcoming_birthdays(client, get_token):
#     # Create a contact with birthday in next few days
#     today = date.today()
#     upcoming_birthday_date = date(today.year, today.month, today.day + 2).isoformat()

#     upcoming_contact = {
#         "first_name": "Clark",
#         "last_name": "Kent",
#         "phone": "5555555555",
#         "email": "superman@example.com",
#         "date_of_birth": upcoming_birthday_date,
#     }

#     client.post(
#         "/api/contacts",
#         json=upcoming_contact,
#         headers={"Authorization": f"Bearer {get_token}"},
#     )

#     # Get upcoming birthdays
#     response = client.get(
#         "/api/contacts/birthdays?days=7",
#         headers={"Authorization": f"Bearer {get_token}"},
#     )

#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, list)

#     # Check if our contact with upcoming birthday is in the response
#     found = False
#     for contact in data:
#         if contact["first_name"] == "Clark" and contact["last_name"] == "Kent":
#             found = True
#             break

#     assert found, "Contact with upcoming birthday not found in response"
