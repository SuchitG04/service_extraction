#!/usr/bin/env python3
import json

def extract_info(input_file):
    entries = []
    current_entry = {}
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines or separator lines
            if not line or line.startswith('----'):
                # If we have a complete entry, add it
                if current_entry and 'filename' in current_entry and 'code_summary' in current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                continue
                
            # If line contains a file path (starts with /)
            if line.startswith('/'):
                if 'twenty-main' in line:
                    parts = line.split('twenty-main')
                    filename = f"twenty{parts[1]}"
                else:
                    filename = line
                current_entry['filename'] = filename
            # If line starts with 'Code summary:'
            elif line.startswith('Code summary:'):
                current_entry['code_summary'] = line[len('Code summary:'):].strip()
    
    # Add the last entry if complete
    if current_entry and 'filename' in current_entry and 'code_summary' in current_entry:
        entries.append(current_entry)
    
    return entries

def main():
    input_file = 'data_sinks.txt'
    entries = extract_info(input_file)
    
    # Write output to a file as JSON
    with open('sink_files.json', 'w') as f:
        json.dump(entries, f, indent=2)

if __name__ == "__main__":
    main()
