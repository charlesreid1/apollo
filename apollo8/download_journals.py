#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URL for Apollo 8 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap08fj/"

# Apollo 8 Flight Journal sections with CORRECT URLs from the actual website
flight_journals = [
    # Travelling from the Earth to the Moon
    ("Day 1: Launch and Ascent to Earth Orbit", "01launch_ascent.html"),
    ("Day 1: Earth Orbit and Translunar Injection", "02earth_orbit_tli.html"),
    ("Day 1: The Green Team and Separation", "03day1_green_sep.html"),
    ("Day 1: The Maroon Team", "04day1_maroon.html"),
    ("Day 1: The Black Team", "05day1_black.html"),
    ("Day 2: The Green Team", "06day2_green.html"),
    ("Day 2: The Maroon Team", "07day2_maroon.html"),
    ("Day 2: The Black Team", "08day2_black.html"),
    ("Day 3: The Green Team", "09day3_green.html"),
    ("Day 3: The Maroon Team", "10day3_maroon.html"),
    ("Day 3: The Black Team - Approaching the Moon", "11day3_black_approach.html"),

    # In the Moon's Embrace
    ("Day 3: Lunar Encounter", "12day3_lunar_encounter.html"),
    ("Day 4: Lunar Orbit 1", "13day4_orbit1.html"),
    ("Day 4: Lunar Orbit 2", "14day4_orbit2.html"),
    ("Day 4: Lunar Orbit 3", "15day4_orbit3.html"),
    ("Day 4: Lunar Orbit 4", "16day4_orbit4.html"),
    ("Day 4: Lunar Orbit 5", "17day4_orbit5.html"),
    ("Day 4: Lunar Orbit 6", "18day4_orbit6.html"),
    ("Day 4: Lunar Orbit 7", "19day4_orbit7.html"),
    ("Day 4: Lunar Orbit 8", "20day4_orbit8.html"),
    ("Day 4: Lunar Orbit 9", "21day4_orbit9.html"),
    ("Day 4: Final Orbit", "22a-day4_final_orbit.html"),
    ("Day 4: Trans-Earth Injection", "22b-day4_tei.html"),

    # Returning to Earth
    ("Day 4 & 5: The Black Team", "23day4-5_black.html"),
    ("Day 5: The Green Team", "24day5_green.html"),
    ("Day 5: The Maroon Team", "25day5_maroon.html"),
    ("Day 5 & 6: The Black Team", "26day5-6_black.html"),
    ("Day 6: The Green Team", "27day6_green.html"),
    ("Day 6: The Maroon Team", "28day6_maroon.html"),
    ("Day 6: Re-entry and Splashdown", "29day6_reentry.html"),
]

def clean_filename(title, prefix=""):
    """Create a clean filename from a title."""
    # Remove special characters and replace spaces with underscores
    filename = title.lower()
    filename = re.sub(r'[^\w\s-]', '', filename)  # Remove special chars
    filename = re.sub(r'[-\s]+', '_', filename)  # Replace spaces and hyphens with underscores
    filename = filename.strip('_')

    # Add prefix
    filename = prefix + filename + ".html"

    return filename

def download_journal(title, url, output_dir=".", filename=None, force=False):
    """Download a journal HTML file."""
    # Use provided filename or create one (needed for skip check)
    if not filename:
        filename = clean_filename(title)

    filepath = os.path.join(output_dir, filename)
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}\n")
        return True

    print(f"Downloading: {title}")
    print(f"URL: {url}")

    try:
        # Make the request
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()

        # Save the file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"Saved to: {filepath}")
        print(f"Size: {len(response.text)} bytes\n")

        # Be polite to the server
        time.sleep(0.5)

        return True

    except Exception as e:
        print(f"Error downloading {title}: {e}\n")
        return False

def download_flight_journals(output_dir=".", force=False):
    """Download Apollo 8 Flight Journal files."""
    print("Starting download of Apollo 8 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename: dayX_partY_description.html
        # Extract day and part from title
        match = re.match(r'Day (\d+): (.+)', title)
        if match:
            day = match.group(1)
            description = match.group(2).lower().replace(' ', '_').replace(',', '').replace("'", '').replace('&', 'and')
            filename = f"day{day}_{description}.html"
        else:
            # For titles without "Day X:" format
            match = re.match(r'Day (\d+) & (\d+): (.+)', title)
            if match:
                day1 = match.group(1)
                day2 = match.group(2)
                description = match.group(3).lower().replace(' ', '_').replace(',', '').replace("'", '').replace('&', 'and')
                filename = f"day{day1}-{day2}_{description}.html"
            else:
                # For other titles
                filename = clean_filename(title)

        full_url = urljoin(FLIGHT_JOURNAL_BASE, relative_url)
        if download_journal(title, full_url, output_dir, filename, force=force):
            success_count += 1

    print(f"Flight Journal download complete: {success_count}/{len(flight_journals)} files downloaded successfully")
    return success_count

def download_main_pages(output_dir=".", force=False):
    """Download the main index page for reference."""
    print("\nDownloading main pages...")

    # Flight Journal main page
    filepath = os.path.join(output_dir, "ap08fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap08fj/index.html"
            response = requests.get(flight_main_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"Flight Journal main page saved to: {filepath}")
            print(f"Size: {len(response.text)} bytes")

        except Exception as e:
            print(f"Error downloading Flight Journal main page: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download Apollo 8 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo8 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 8 journals...\n")
    print(f"HTML files will be saved to: {output_dir}/\n")

    # Download flight journals
    flight_success = download_flight_journals(output_dir, force=args.force)

    # Download main pages
    download_main_pages(output_dir, force=args.force)

    print(f"\nTotal download complete: {flight_success}/{len(flight_journals)} journals downloaded successfully")
    print(f"All HTML files saved to: {output_dir}/")

if __name__ == "__main__":
    main()