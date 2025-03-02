import csv
import json
from collections import defaultdict

def transform_csv_to_separated_json(csv_file, output_prefix):
    # Initialize dictionaries for each level: country_code -> list of regions
    level1 = defaultdict(list)
    level2 = defaultdict(list)
    level3 = defaultdict(list)
    
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            country_code = row["Country code"].strip()
            nuts_code = row["NUTS Code"].strip()
            nuts_label = row["NUTS label"].strip()
            nuts_level = row["NUTS level"].strip()  # Expected to be "1", "2", or "3"
            
            if not country_code:
                continue  # Skip rows without a country code
            
            # Prepare the region entry
            entry = {"code": nuts_code, "label": nuts_label}
            
            # Append the entry to the appropriate level dictionary
            if nuts_level == "1":
                level1[country_code].append(entry)
            elif nuts_level == "2":
                level2[country_code].append(entry)
            elif nuts_level == "3":
                level3[country_code].append(entry)
            else:
                continue  # Skip rows with an unexpected NUTS level

    # Build the final JSON structure for each level
    def build_output(level_dict):
        data = []
        for country_code, regions in level_dict.items():
            data.append({
                "country_code": country_code,
                "regions": regions
            })
        return {"data": data}

    output1 = build_output(level1)
    output2 = build_output(level2)
    output3 = build_output(level3)
    
    # Write each level to a separate JSON file
    with open(f"{output_prefix}_level1.json", "w", encoding="utf-8") as f1:
        json.dump(output1, f1, ensure_ascii=False, indent=4)
    with open(f"{output_prefix}_level2.json", "w", encoding="utf-8") as f2:
        json.dump(output2, f2, ensure_ascii=False, indent=4)
    with open(f"{output_prefix}_level3.json", "w", encoding="utf-8") as f3:
        json.dump(output3, f3, ensure_ascii=False, indent=4)
    
    print(f"JSON files '{output_prefix}_level1.json', '{output_prefix}_level2.json', and '{output_prefix}_level3.json' generated successfully.")

if __name__ == "__main__":
    # Update the CSV file path and desired output prefix as needed.
    transform_csv_to_separated_json("c:/rettx/experiments/NUTS_converter/nuts.csv", "nuts_master_europe")
