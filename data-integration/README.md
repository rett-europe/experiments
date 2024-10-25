# Data integration flow

The objective is to move data from a staging CSV with this format (it could be a DB):

parent_name;email;relationship;resides_in_spain;country;rett_name;rett_surname;date_of_birth;gender;diagnosis_type;creation_date;age;age_group;region_id

To a data model with Contact/Patient/Relationship structure:

```mermaid
erDiagram
    Contacts {
        UUID contact_uuid PK
        TEXT parent_name
        TEXT email "Unique"
        BOOLEAN resides_in_spain
        TEXT country
        TEXT creation_date
        TEXT region_id
    }

    Patients {
        UUID persona_rett_uuid PK
        TEXT rett_name
        TEXT rett_surname
        TEXT date_of_birth
        TEXT gender
        TEXT diagnosis_type
        TEXT creation_date
        INTEGER age
        TEXT age_group
        TEXT region_id
    }

    Link_Table {
        UUID relationship_uuid PK
        UUID contact_uuid FK
        UUID persona_rett_uuid FK
        TEXT relationship
    }

    Contacts ||--o{ Link_Table : "has"
    Patients ||--o{ Link_Table : "linked to"
```

The objective is to simulate step 3 from this diagram:

![Contact/Patient/Relationship onboarding](contact-patient-onboard.png)

The main logic is executed by manager.py:

![Data integration flow](data-integration-flow.png)

# How to execute

For this to work, the first time you need to execute the script create_tables.py, to create an empty DB with the desired structure.

```bash
Python create_tables.py <name of your database>.db
```

Once the DB is created, you can execute the data integration script:

```bash
Python main_batch.py input.csv <name of your database>.db
```
