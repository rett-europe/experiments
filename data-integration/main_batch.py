import argparse
import pandas as pd
import logging
from manager import PatientContactManager

# 1. Set up logging to a file
logging.basicConfig(filename='output.log',  # Name of the log file
                    level=logging.INFO,      # Set the logging level
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Log format

# Create a logger object
logger = logging.getLogger()

# 2. Set up command-line arguments using argparse
parser = argparse.ArgumentParser(description="Batch load contacts and patients from a CSV file into the registry.")
parser.add_argument('input_file', type=str, help="Path to the CSV file containing contact and patient data.")
parser.add_argument('db_file_location', type=str, help="Path to the SQLite DB file containing contact and patient data.")
args = parser.parse_args()

# 3. Read the data from the provided CSV file
csv_file = args.input_file  # Take the CSV file path from the command-line argument
logger.info(f"Reading input file: {csv_file}")

try:
    df = pd.read_csv(csv_file)  # Load the CSV file into a DataFrame
    logger.info(f"Successfully read {len(df)} records from {csv_file}")
except FileNotFoundError:
    logger.error(f"File not found: {csv_file}")
    exit(1)
except pd.errors.EmptyDataError:
    logger.error(f"File is empty: {csv_file}")
    exit(1)
except pd.errors.ParserError:
    logger.error(f"Failed to parse the file: {csv_file}")
    exit(1)

# 4. Initialize the PatientContactManager with the database path
db_path = args.db_file_location
manager = PatientContactManager(db_path)

# 5. Log the start of the batch loading process
logger.info("Starting batch load of contacts and patients from the CSV file.")

# 6. Batch load the data from the CSV file
manager.batch_load_data(df)

# 7. Log completion and close the database connection
logger.info("Batch load completed successfully.")
manager.close_connection()
logger.info("Database connection closed.")