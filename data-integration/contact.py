import sqlite3
import uuid  # Import the UUID module
import logging  # Import the logging module

class Contact:
    def __init__(self, db_connection):
        """
        Initialize the Contact class with a database connection.
        Args:
            db_connection: Active SQLite connection object.
        """
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.logger = logging.getLogger(__name__)  # Create a logger for this class

    def add_contact(self, contact_data):
        """
        Add a new contact if no duplicate is found based on email.
        Args:
            contact_data (dict): Dictionary containing contact details.
        Returns:
            str: UUID of the newly added contact, or None if a duplicate is found.
        """
        if self.check_duplicate_contact(contact_data['email']):
            self.logger.warning(f"Contact already exists: {contact_data['email']}. Skipping creation.")
            return None

        # If no duplicate is found, generate a new UUID for the contact
        new_contact_uuid = str(uuid.uuid4())  # Generate a new UUID
        contact_data['contact_uuid'] = new_contact_uuid

        # Insert the new contact into the database
        self.cursor.execute('''
            INSERT INTO Contacts 
            (parent_name, email, resides_in_spain, country, creation_date, region_id, contact_uuid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            contact_data['parent_name'], 
            contact_data['email'], 
            contact_data['resides_in_spain'], 
            contact_data['country'], 
            contact_data['creation_date'], 
            contact_data['region_id'], 
            new_contact_uuid
        ))
        self.conn.commit()
        self.logger.info(f"New contact added: {contact_data['parent_name']} ({contact_data['email']}) (UUID: {new_contact_uuid})")
        return new_contact_uuid

    def get_contact_by_email(self, email):
        """
        Retrieve a contact by their email address.
        Args:
            email (str): The email of the contact.
        Returns:
            dict: Contact record as a dictionary, or None if not found.
        """
        self.cursor.execute("SELECT * FROM Contacts WHERE email = ?", (email,))
        result = self.cursor.fetchone()
        if result:
            return dict(zip([column[0] for column in self.cursor.description], result))
        self.logger.warning(f"No contact found with email: {email}")
        return None

    def get_contact_by_uuid(self, contact_uuid):
        """
        Retrieve a contact by their UUID.
        Args:
            contact_uuid (str): Unique identifier of the contact.
        Returns:
            dict: Contact record as a dictionary, or None if not found.
        """
        self.cursor.execute("SELECT * FROM Contacts WHERE contact_uuid = ?", (contact_uuid,))
        result = self.cursor.fetchone()
        if result:
            return dict(zip([column[0] for column in self.cursor.description], result))
        self.logger.warning(f"No contact found with UUID: {contact_uuid}")
        return None

    def update_contact(self, contact_uuid, new_data):
        """
        Update the details of an existing contact.
        Args:
            contact_uuid (str): Unique identifier of the contact to update.
            new_data (dict): Dictionary with the updated data.
        """
        columns = ", ".join(f"{key} = ?" for key in new_data.keys())
        values = list(new_data.values()) + [contact_uuid]
        
        self.cursor.execute(f"UPDATE Contacts SET {columns} WHERE contact_uuid = ?", values)
        self.conn.commit()
        self.logger.info(f"Contact updated: {contact_uuid}")

    def delete_contact(self, contact_uuid):
        """
        Delete a contact by their UUID.
        Args:
            contact_uuid (str): Unique identifier of the contact to delete.
        """
        self.cursor.execute("DELETE FROM Contacts WHERE contact_uuid = ?", (contact_uuid,))
        self.conn.commit()
        self.logger.info(f"Contact deleted: {contact_uuid}")

    def check_duplicate_contact(self, email):
        """
        Check if a contact with the given email already exists.
        Args:
            email (str): The email address to check.
        Returns:
            bool: True if a duplicate contact is found, False otherwise.
        """
        self.cursor.execute("SELECT * FROM Contacts WHERE email = ?", (email,))
        exists = self.cursor.fetchone() is not None
        if exists:
            self.logger.info(f"Duplicate contact found for email: {email}")
            print(f"Duplicate contact found for email: {email}")
        return exists

    def validate_contact_data(self, contact_data):
        """
        Validate incoming contact data for completeness.
        Args:
            contact_data (dict): Dictionary containing contact details.
        Returns:
            bool: True if data is valid, False otherwise.
        """
        required_fields = ['parent_name', 'email']
        for field in required_fields:
            if field not in contact_data or not contact_data[field]:
                self.logger.error(f"Invalid data: {field} is missing or empty.")
                return False
        return True