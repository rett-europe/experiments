import sqlite3
import uuid
import logging  # Import the logging module
from fuzzywuzzy import fuzz

class Patient:
    def __init__(self, db_connection):
        """
        Initialize the Patient class with a database connection.
        Args:
            db_connection: Active SQLite connection object.
        """
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.logger = logging.getLogger(__name__)  # Create a logger for this class

    def add_patient(self, patient_data):
        """
        Insert a new patient into the Patients table if no duplicate is found.
        Args:
            patient_data (dict): Dictionary containing patient details.
        Returns:
            persona_rett_uuid (str): UUID of the newly added patient, or None if a duplicate is found.
        """
        # First, check for potential duplicates
        existing_patient_uuid = self.find_matching_patient(patient_data)
        if existing_patient_uuid:
            self.logger.warning(f"Potential duplicate found. Skipping patient creation: {patient_data['rett_name']} {patient_data['rett_surname']}")
            print(f"Potential duplicate found. Skipping patient creation: {patient_data['rett_name']} {patient_data['rett_surname']}")
            return None

        # If no duplicates, generate a new UUID for the patient
        new_patient_uuid = str(uuid.uuid4())  # Generate a new UUID and convert it to a string
        patient_data['persona_rett_uuid'] = new_patient_uuid

        # Insert the new patient into the database
        self.cursor.execute('''
            INSERT INTO Patients 
            (rett_name, rett_surname, date_of_birth, gender, diagnosis_type, creation_date, age, age_group, region_id, persona_rett_uuid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient_data['rett_name'], 
            patient_data['rett_surname'], 
            patient_data['date_of_birth'], 
            patient_data['gender'], 
            patient_data['diagnosis_type'], 
            patient_data['creation_date'], 
            patient_data['age'], 
            patient_data['age_group'], 
            patient_data['region_id'], 
            new_patient_uuid
        ))
        self.conn.commit()
        self.logger.info(f"New patient added: {patient_data['rett_name']} {patient_data['rett_surname']} (UUID: {new_patient_uuid})")
        return new_patient_uuid

    def get_patient_by_uuid(self, persona_rett_uuid):
        """
        Retrieve a patient record by their unique UUID.
        Args:
            persona_rett_uuid (str): The unique identifier for the patient.
        Returns:
            dict: Patient record as a dictionary, or None if not found.
        """
        self.cursor.execute("SELECT * FROM Patients WHERE persona_rett_uuid = ?", (persona_rett_uuid,))
        result = self.cursor.fetchone()
        if result:
            return dict(zip([column[0] for column in self.cursor.description], result))
        return None

    def find_matching_patient(self, patient_data):
        """
        Check for potential duplicates using complex matching logic.
        Args:
            patient_data (dict): Dictionary containing patient details.
        Returns:
            str: UUID of the matching patient, or None if no match is found.
        """
        # Extract data for comparison
        rett_name = patient_data['rett_name']
        rett_surname = patient_data['rett_surname']
        birth_date = patient_data['date_of_birth']
        gender = patient_data['gender']

        # Retrieve all existing patients from the database
        self.cursor.execute("SELECT * FROM Patients")
        patients = self.cursor.fetchall()

        for patient in patients:
            # Unpack patient data (assuming column order in the schema)
            patient_name, patient_surname, patient_birth_date, patient_gender, _, _, _, _, _, patient_uuid = patient

            # Fuzzy match on the first name
            name_score = fuzz.token_sort_ratio(rett_name, patient_name)

            # Split and match on surname
            surname_score = self.fuzzy_match_surname(rett_surname, patient_surname)

            # Check exact match on birth date and gender
            birth_date_match = birth_date == patient_birth_date
            gender_match = gender == patient_gender

            # Define matching criteria
            if name_score > 80 and surname_score > 80 and birth_date_match and gender_match:
                self.logger.info(f"Matching patient found: {patient_name} {patient_surname} (UUID: {patient_uuid})")
                return patient_uuid

        self.logger.info(f"No matching patient found for: {patient_data['rett_name']} {patient_data['rett_surname']}")
        return None

    def fuzzy_match_surname(self, surnames1, surnames2):
        """
        Perform fuzzy matching on surnames by splitting them into individual words.
        Args:
            surnames1 (str): Surname(s) from patient data.
            surnames2 (str): Surname(s) from existing patient record.
        Returns:
            int: Maximum fuzzy match score.
        """
        surnames1_list = surnames1.split() if surnames1 else []
        surnames2_list = surnames2.split() if surnames2 else []

        # Compare each surname component for fuzzy match
        max_score = max([fuzz.token_sort_ratio(s1, s2) for s1 in surnames1_list for s2 in surnames2_list], default=0)
        return max_score