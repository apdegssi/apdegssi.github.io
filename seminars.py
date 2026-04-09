import csv
import codecs
import random
import re
import json
import os
from datetime import datetime, timedelta
from functools import lru_cache
import urllib.request
import urllib.parse
import subprocess
from dateutil.parser import parse
import unicodedata



# Define the paths
CSV_FILE = 'seminars.csv'
OUTPUT_DIR = 'content/seminars'
BASE_URL = "https://apde.gssi.it"





def decode_unicode(text):
    if not text: 
        return text
    try: 
        return codecs.decode(text, 'unicode_escape')
    except Exception: 
        return text 

def get_ordinal_suffix(day):
    if 11 <= (day % 100) <= 13: return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

def generate_mailto_url(speaker, title, abstract, dt_object, location, info_url, to_email=""):
    """Returns ONLY the raw, encoded mailto string with dynamic subject warnings."""
    speaker = decode_unicode(speaker)
    title = decode_unicode(title)

    # 1. Check for standard schedule/location
    unusual_aspects = []
    if dt_object.weekday() != 1: unusual_aspects.append("DAY")
    if not (dt_object.hour == 14 and dt_object.minute == 30): unusual_aspects.append("TIME")
    if location.strip() != "GSSI Main Lecture Hall": unusual_aspects.append("LOCATION")
        
    # 2. Format the warning list cleanly (e.g., "DAY", "DAY & TIME", "DAY, TIME & LOCATION")
    if unusual_aspects:
        if len(unusual_aspects) == 1:
            aspect_str = unusual_aspects[0]
        elif len(unusual_aspects) == 2:
            aspect_str = f"{unusual_aspects[0]} & {unusual_aspects[1]}"
        else:
            aspect_str = f"{unusual_aspects[0]}, {unusual_aspects[1]} & {unusual_aspects[2]}"
            
        body_warning = f"PLEASE NOTE THE UNUSUAL {aspect_str}\n\n"
        subject_warning = f" (UNUSUAL {aspect_str})"
    else:
        body_warning = ""
        subject_warning = ""

    # 3. Format dates and times for BODY
    date_str_body = dt_object.strftime("%B %d, %Y")
    start_time_body = dt_object.strftime("%I:%M%p").lower().lstrip('0')
    end_time = (dt_object + timedelta(hours=1)).strftime("%I:%M%p").lower().lstrip('0')

    # 4. Format dates and times for SUBJECT
    month_abbr = dt_object.strftime("%b")
    day_val = dt_object.day
    subject_date_str = f"{month_abbr} {day_val}{get_ordinal_suffix(day_val)}, {dt_object.strftime('%I:%M').lstrip('0')}-{end_time}"

    # 5. Build the plain text body
    body_text = f"""{body_warning}Dear all,

a gentle reminder about our next Analysis & PDE seminar (info below).

Analysis & PDE Seminar
{date_str_body} - {start_time_body}-{end_time}
{location.strip()}

Speaker: {speaker}

Title: {title}

Abstract: {abstract}

More info: {info_url}

Best wishes,"""

    # 6. Build and Encode Subject and Body
    subject_text = f"GSSI Analysis & PDE Seminar - {subject_date_str}{subject_warning}"
    
    subject = urllib.parse.quote(subject_text)
    # body_encoded = urllib.parse.quote(body_text, encoding="latin-1")
    # body_encoded = urllib.parse.quote(body_text.encode('latin-1', errors='ignore'))
    body_encoded = urllib.parse.quote(body_text, safe=':/', encoding='latin-1', errors='ignore')

    return f"mailto:{to_email}?subject={subject}&body={body_encoded}"



def create_mailto_link(subject, body=None):
    # Base mailto string (leaving recipient empty)
    base_url = "mailto:?"
    
    # Define the parameters
    params = {'subject': subject}
    if body:
        params['body'] = body
    
    # urlencode handles the special characters and spaces
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    
    return base_url + query_string


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
    
    # 1. Translate German umlauts first so 'ö' becomes 'oe'
    umlauts = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'}
    for search, replace in umlauts.items():
        speaker = speaker.replace(search, replace)
        
    # 2. Normalize any other accents globally (e.g., 'é' becomes 'e', 'ç' becomes 'c')
    speaker = unicodedata.normalize('NFKD', speaker).encode('ascii', 'ignore').decode('ascii')
    
    # 3. Create a safe string with only letters and hyphens
    safe_name = "".join([c for c in speaker if c.isalpha() or c.isspace()]).strip().replace(" ", "-").lower()
    
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
        start_dt = parse(row['start'])
        
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
        
        # filepath = os.path.join(OUTPUT_DIR, filename)
        rand_int = random.randint(1,100_000)

        filepath_rand = os.path.join(OUTPUT_DIR, slug + f"-r{rand_int}.md")
        info_url = f"{BASE_URL}/seminars/{slug}"
        # info_url = urllib.parse.quote(info_url.encode('latin-1', errors='ignore'))

        
        # Write the Hugo Markdown file
        with open(filepath_rand, 'w', encoding='utf-8') as md_file:
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

            if title and title.upper() != "TBA":
                mailto_link = generate_mailto_url(speaker=speaker, title=title, abstract=raw_abstract, location=place_name, info_url=info_url, dt_object=start_dt)

                md_file.write(f"share: {mailto_link}\n")



            
            # Add the map link to front matter if it exists
            if place_link:
                md_file.write(f"place_url: \"{place_link}\"\n")
                
            md_file.write(f"tags: {tags_formatted}\n")
            
            # Write the safely escaped abstract to the front matter
            md_file.write(f"abstract: {abstract_safe}\n")
            md_file.write(f"""aliases:
- /seminars/{slug}/
- /seminars/{slug}-r{rand_int}/
""")
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
