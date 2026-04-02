import csv
import json
import os
from datetime import datetime, timedelta
from functools import lru_cache
import urllib.request
import subprocess



# Define the paths
CSV_FILE = 'seminars.csv'
OUTPUT_DIR = 'content/seminars'

import re

def is_latex(text: str):
    """
    Checks if a string contains common LaTeX patterns.
    """
    if not isinstance(text, str) or not text.strip():
        return False

    # Patterns to look for:
    patterns = [
        r'\\[a-zA-Z]+',             # Commands: \section, \textbf, etc.
        r'\$.*?\$',                 # Inline math: $x + y$
        r'\\\(.*?\\\)',             # Escaped inline math: \( x + y \)
        r'\\\[.*?\\\]',             # Display math: \[ x + y \]
        r'\\begin\{.*?\}.*?\\end\{.*?\}', # Environments: \begin{itemize}
        r'\{.*?\}',                 # Curly brace grouping
        r'\d+\^\{.*?\}',            # Superscripts: 10^{2}
        r'\\frac\{.*?\}\{.*?\}'     # Fractions: \frac{a}{b}
    ]
    
    # Combine patterns into a single regex for efficiency
    combined_pattern = re.compile('|'.join(patterns), re.DOTALL)
    
    return bool(combined_pattern.search(text))


@lru_cache
def get_reader_data():
    # Your specific Google Sheet details
    SHEET_ID = '1uyCNW7m8-qgLgDUd1FLfyARYy8C2zksQUzmI-VL9zh0'
    GID = '0'

    # The special export URL format
    export_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

    # Where to save the file so Hugo can use it
    # Saving it to the 'data' folder is best practice for Hugo
    response = urllib.request.urlopen(export_url)
    lines = [line.decode('utf-8') for line in response.readlines()]

    # 3. Pass the text lines directly into the CSV module
    return lines
    # reader = csv.DictReader(lines)
    # return reader




def place_to_link(place: str) -> str:
    """Returns a Google Maps URL based on the room name."""
    if not place:
        return ""
        
    place_lower = place.lower()
    if 'mlh' in place_lower or "main lecture hall" in place_lower or 'aurora' in place_lower:
        return "https://www.google.com/maps/dir//GSSI+-+Gran+Sasso+Science+Institute/@42.3448045,13.3960726"
    elif "auditorium" in place_lower or 'polaris' in place_lower:
        return "https://www.google.com/maps/dir//Rettorato+GSSI+-+Palazzo+ex+GIL/@42.3442241,13.3968818"
    elif "inps" in place_lower or 'zenith' in place_lower:
        return "https://www.google.com/maps/dir//Gran+Sasso+Science+Institute+(Ex-INPS+Building)/@42.3452616,13.3175938"
        
    return "" # Return empty if no match is found

def get_slug(start_string, speaker):
    """Helper function to guarantee the file name and the URL match perfectly."""
    date_str = start_string.split(' ')[0]  # Grabs just the YYYY-MM-DD
    # Creates a safe string with only letters and hyphens
    safe_name = "".join([c for c in speaker if c.isalpha() or c.isspace()]).replace(" ", "-").lower()
    return f"{date_str}-{safe_name}"

def generate_mds():
    # Create the seminars folder if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        # reader = csv.DictReader(file)
        
    reader = csv.DictReader(get_reader_data())
    for row in reader:
        # print(row)
        # Use the helper function to get the base name

        speaker = row.get('speaker', '')
        if not speaker.strip():
            continue

        slug = get_slug(row['start'], row['speaker'])
        filename = f"{slug}.md"
        
        # Parse tags
        tags = [tag.strip() for tag in row.get('tags', '').split(';') if tag.strip()]
        tags_formatted = json.dumps(tags) 
        
        # Safely escape the abstract for the front matter!
        raw_abstract = row.get('abstract', '')
        abstract_safe = json.dumps(raw_abstract)
        title = row.get('title', "TBA")
        title_safe = json.dumps(title)
        
        # Get the place name and generate the Google Maps link
        place_name = row.get('place', 'TBA')
        place_link = place_to_link(place_name)
        zoom_link: str = row.get("zoom_link", "")
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Write the Hugo Markdown file
        with open(filepath, 'w', encoding='utf-8') as md_file:
            # FRONT MATTER
            md_file.write("---\n")
            md_file.write(f"title: {title_safe}\n")
            md_file.write(f"date: {row['start']}:00\n") 
            md_file.write(f"speaker: \"{row['speaker']}\"\n")
            md_file.write(f"place: \"{place_name}\"\n")
            if is_latex(title) or is_latex(abstract_safe):
                md_file.write("mathjax: true\n")
            else:
                md_file.write("mathjax: false\n")

            if zoom_link:
                md_file.write("zoom_link: \"{zoom_link}\"\n")



            
            # Add the map link to front matter if it exists
            if place_link:
                md_file.write(f"place_url: \"{place_link}\"\n")
                
            md_file.write(f"tags: {tags_formatted}\n")
            
            # Write the safely escaped abstract to the front matter
            md_file.write(f"abstract: {abstract_safe}\n")
            md_file.write("---\n\n")


            
            # We also leave the raw abstract in the body for the single page to render easily
            md_file.write(f"{raw_abstract}\n")

    print("Successfully generated clean Hugo markdown files for all seminars!")

def generate_calendar_events():
    all_events = []
    start = "start"

    # Open your CSV file
    # with open(CSV_FILE, mode='r', encoding='utf-8') as csv_file:
    #     csv_reader = csv.DictReader(csv_file)
        
    reader = csv.DictReader(get_reader_data())
    for row in reader:
        try:
            start_str = row.get(start, '').strip()
            end_str = row.get('end', '').strip()
            
            if not start_str:
                continue
                
            start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M")

            if end_str:
                end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            else:
                end_date = start_date + timedelta(hours=1)
                end_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

            start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%S")
            end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%S")

            # Get the exact slug to build the clickable Hugo URL
            slug = get_slug(start_str, row.get('speaker', ''))
            speaker = row.get('speaker', '')

            if not speaker.strip():
                continue

            _title = row.get('title', 'TBA')
            title = f"{speaker} - {_title}"
            hugo_url = f"/seminars/{slug}/"
            
            all_events.append({
                "title": title,
                "start": start_iso,
                "end": end_iso,
                "allDay": False,
                "description": row.get('abstract', ''),
                "color": row.get('color', '#990011'),
                "url": hugo_url 
            })
        except ValueError as e:
            print(f"Skipping row due to date formatting error ({row.get('title', 'Unknown')}): {e}")

    output_json_path = 'static/all_events.json'
    os.makedirs('static', exist_ok=True)
    
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_events, json_file, indent=4)

    print(f"Success! {len(all_events)} seminars exported to {output_json_path}.")

if __name__ == "__main__":
    _ = subprocess.run("rm content/seminars/20*", shell=True)
    generate_mds()
    generate_calendar_events()
