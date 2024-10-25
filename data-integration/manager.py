import sqlite3
import logging
import uuid
from patient import Patient
from contact import Contact

class PatientContactManager:
    def __init__(self, db_path):
        """
        Initialize the manager class with the path to the SQLite database.
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Initialize the Contact and Patient classes
        self.contact_manager = Contact(self.conn)
        self.patient_manager = Patient(self.conn)

        # Set up a logger for the manager
        self.logger = logging.getLogger(__name__)

    def add_contact_and_patient(self, contact_data, patient_data, relationship):
        """
        Add or update a contact and their associated patient, and link them together.
        Args:
            contact_data (dict): Contact details.
            patient_data (dict): Patient details.
            relationship (str): Type of relationship (e.g., "Father", "Mother").
        """
        self.logger.info(f"Processing contact: {contact_data['parent_name']} ({contact_data['email']}) and associated patient: {patient_data['rett_name']} {patient_data['rett_surname']}")

        # Step 1: Add or update the contact
        contact_uuid = self.contact_manager.add_contact(contact_data)
        if not contact_uuid:
            # If a duplicate contact is found, use the existing contact's UUID
            contact_record = self.contact_manager.get_contact_by_email(contact_data['email'])
            contact_uuid = contact_record['contact_uuid']
            self.logger.info(f"Using existing contact UUID: {contact_uuid} for {contact_data['parent_name']}")

        # Step 2: Add or update the patient
        patient_uuid = self.patient_manager.add_patient(patient_data)
        if not patient_uuid:
            # If a duplicate patient is found, retrieve the existing patient UUID
            patient_record = self.patient_manager.find_matching_patient(patient_data)
            patient_uuid = patient_record if patient_record else None
            self.logger.info(f"Using existing patient UUID: {patient_uuid} for {patient_data['rett_name']} {patient_data['rett_surname']}")

        # Step 3: Link the contact and patient in the Link_Table
        if patient_uuid:
            self.link_contact_to_patient(contact_uuid, patient_uuid, relationship)
        else:
            self.logger.warning(f"No patient was linked for contact {contact_data['parent_name']} ({contact_data['email']})")

    def link_contact_to_patient(self, contact_uuid, persona_rett_uuid, relationship_type):
        """
        Link an existing contact and patient using the relationship type.
        Args:
            contact_uuid (str): UUID of the contact.
            persona_rett_uuid (str): UUID of the patient.
            relationship_type (str): Type of relationship (e.g., "Father", "Mother").
        """
        relationship_uuid = str(uuid.uuid4())
        self.cursor.execute('''
            INSERT INTO Link_Table (relationship_uuid, relationship, contact_uuid, persona_rett_uuid)
            VALUES (?, ?, ?, ?)
        ''', (relationship_uuid, relationship_type, contact_uuid, persona_rett_uuid))
        self.conn.commit()
        self.logger.info(f"Linked contact {contact_uuid} to patient {persona_rett_uuid} with relationship {relationship_type} and relationship_uuid {relationship_uuid}")

    def batch_load_data(self, df):
        """
        Process a DataFrame to add multiple contacts and patients.
        Args:
            df (DataFrame): A pandas DataFrame containing contact and patient data.
        """
        self.logger.info("Starting batch processing of contacts and patients.")
        for index, row in df.iterrows():
            contact_data = {
                'parent_name': row['parent_name'],
                'email': row['email'],
                'resides_in_spain': row['resides_in_spain'],
                'country': row['country'],
                'creation_date': row['creation_date'],
                'region_id': row['region_id']
            }
            patient_data = {
                'rett_name': row['rett_name'],
                'rett_surname': row['rett_surname'],
                'date_of_birth': row['date_of_birth'],
                'gender': row['gender'],
                'diagnosis_type': row['diagnosis_type'],
                'creation_date': row['creation_date'],
                'age': row['age'],
                'age_group': row['age_group'],
                'region_id': row['region_id']
            }
            relationship = row['relationship']

            self.logger.info(f"Processing row {index + 1}: {contact_data['parent_name']} -> {patient_data['rett_name']}")
            self.add_contact_and_patient(contact_data, patient_data, relationship)

        self.logger.info("Batch processing completed successfully.")

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()
        self.logger.info("Database connection closed.")