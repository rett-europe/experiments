import json
from datetime import datetime

# File paths (adjust as needed)
input_filename = 'subdivisions.json'
output_filename = 'output.json'

# Read the flat JSON array from the input file
with open(input_filename, 'r', encoding='utf-8') as f:
    flat_data = json.load(f)

# Group the regions by country
country_dict = {}
for entry in flat_data:
    country = entry['country']
    region = {'code': entry['code'], 'label': entry['name']}
    country_dict.setdefault(country, []).append(region)

# Build the final structure
final_structure = {
    "created_at": datetime.utcnow().isoformat() + "Z",
    "created_by": "admin",
    "version": 1,
    "last_updated_at": datetime.utcnow().isoformat() + "Z",
    "last_updated_by": "admin",
    "is_latest": True,
    "region_level": 2,
    "is_deleted": False,
    "type": "region",
    "data": []
}

# Populate the data array with grouped regions
for country_code, regions in country_dict.items():
    final_structure["data"].append({
        "country_code": country_code,
        "regions": regions
    })

# Write the final structured JSON to the output file
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(final_structure, f, indent=4)

print(f"Converted data saved to {output_filename}")
