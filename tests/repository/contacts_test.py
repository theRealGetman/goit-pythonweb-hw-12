import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.contact import Contact
from src.db.models.user import User
from src.repository.contacts import ContactRepository
from src.schemas.contact import ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1, username="testuser", email="test@example.com", hashed_password="password"
    )


@pytest.fixture
def contact_model():
    return ContactModel(
        first_name="John",
        last_name="Doe",
        phone="1234567890",
        email="john.doe@example.com",
        date_of_birth=date(1990, 1, 1),
    )


@pytest.fixture
def contacts():
    return [
        Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            email="john.doe@example.com",
            date_of_birth=date(1990, 1, 1),
            user_id=1,
        ),
        Contact(
            id=2,
            first_name="Jane",
            last_name="Smith",
            phone="0987654321",
            email="jane.smith@example.com",
            date_of_birth=date(1992, 2, 2),
            user_id=1,
        ),
        Contact(
            id=3,
            first_name="Michael",
            last_name="Brown",
            phone="5555555555",
            email="michael.brown@example.com",
            date_of_birth=date(1985, 3, 3),
            user_id=1,
        ),
    ]


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user, contacts):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contacts
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contacts(user=user, skip=0, limit=10)

    # Assertions
    assert len(result) == 3
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"
    assert result[2].first_name == "Michael"


@pytest.mark.asyncio
async def test_get_contacts_with_search(
    contact_repository, mock_session, user, contacts
):
    # Setup mock
    filtered_contacts = [contacts[0]]  # Just John Doe
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = filtered_contacts
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method with search query
    result = await contact_repository.get_contacts(
        user=user, skip=0, limit=10, q="John"
    )

    # Assertions
    assert len(result) == 1
    assert result[0].first_name == "John"
    assert result[0].last_name == "Doe"


@pytest.mark.asyncio
async def test_get_contact(contact_repository, mock_session, user, contacts):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contacts[0]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_contact_not_found(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact(contact_id=999, user=user)

    # Assertions
    assert contact is None


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user, contact_model):
    # Setup
    # new_contact = Contact(id=4, **contact_model.model_dump(), user_id=user.id)

    # Mock session behavior
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Set up return for refresh to simulate DB saving the contact
    async def mock_refresh(obj):
        obj.id = 4  # Set an ID to simulate DB

    mock_session.refresh.side_effect = mock_refresh

    # Call method
    result = await contact_repository.create_contact(body=contact_model, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.user_id == user.id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(
    contact_repository, mock_session, user, contacts, contact_model
):
    # Setup - modify contact model for update
    updated_contact_model = ContactModel(
        first_name="Johnny",
        last_name="Doe",
        phone="1234567890",
        email="johnny.doe@example.com",
        date_of_birth=date(1990, 1, 1),
    )

    # Mock get_contact to return existing contact
    contact_repository.get_contact = AsyncMock(return_value=contacts[0])

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=updated_contact_model, user=user
    )

    # Assertions
    assert result is not None
    assert result.first_name == "Johnny"  # Updated field
    assert result.email == "johnny.doe@example.com"  # Updated field
    assert result.last_name == "Doe"  # Unchanged
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact_not_found(
    contact_repository, mock_session, user, contact_model
):
    # Mock get_contact to return None (contact not found)
    contact_repository.get_contact = AsyncMock(return_value=None)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=999, body=contact_model, user=user
    )

    # Assertions
    assert result is None
    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_contact(contact_repository, mock_session, user, contacts):
    # Mock get_contact to return existing contact
    contact_repository.get_contact = AsyncMock(return_value=contacts[0])

    # Call method
    result = await contact_repository.delete_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.first_name == "John"
    mock_session.delete.assert_awaited_once_with(contacts[0])
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_contact_not_found(contact_repository, mock_session, user):
    # Mock get_contact to return None (contact not found)
    contact_repository.get_contact = AsyncMock(return_value=None)

    # Call method
    result = await contact_repository.delete_contact(contact_id=999, user=user)

    # Assertions
    assert result is None
    mock_session.delete.assert_not_awaited()
    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_birthdays(contact_repository, mock_session, user, contacts):
    # Setup mock
    # For simplicity, let's assume all contacts have birthdays in the next few days
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contacts
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_birthdays(days=7, user=user)

    # Assertions
    assert len(result) == 3
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"
    assert result[2].first_name == "Michael"
