#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URL for Apollo 7 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap07fj/"

# Apollo 7 Flight Journal sections with CORRECT URLs from the actual website
# Note: Apollo 7 was Earth orbital mission, so there is no Surface Journal.
flight_journals = [
    # Day 1 sections
    ("Day 1, part 1: Launch and Ascent to Earth Orbit", "a7_01_launch_ascent.html"),
    ("Day 1, part 2: CSM/S-IVB Orbital Operations", "a7_02_s-ivb-ops.html"),
    ("Day 1, part 3: S-IVB Takeover Demonstration, Separation, and First Phasing Maneuver", "a7_03_s-ivb-safing.html"),
    ("Day 1, part 4: Remainder (preliminary)", "a7_04_day1.html"),

    # Day 2-11 (preliminary)
    ("Day 2 (preliminary)", "a7_05_day2.html"),
    ("Day 3 (preliminary)", "a7_06_day3.html"),
    ("Day 4 (preliminary)", "a7_07_day4.html"),
    ("Day 5 (preliminary)", "a7_08_day5.html"),
    ("Day 6 (preliminary)", "a7_09_day6.html"),
    ("Day 7 (preliminary)", "a7_10_day7.html"),
    ("Day 8 (preliminary)", "a7_11_day8.html"),
    ("Day 9 (preliminary)", "a7_12_day9.html"),
    ("Day 10 (preliminary)", "a7_13_day10.html"),
    ("Day 11 (preliminary)", "a7_14_day11.html"),
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
    """Download Apollo 7 Flight Journal files."""
    print("Starting download of Apollo 7 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename: dayX_partY_description.html
        # Extract day and part from title
        match = re.match(r'Day (\d+), part (\d+): (.+)', title)
        if match:
            day = match.group(1)
            part = match.group(2)
            description = match.group(3).lower().replace(' ', '_').replace(',', '').replace("'", '').replace('/', '_')
            filename = f"day{day}_part{part}_{description}.html"
        else:
            # For titles without "Day X, part Y:" format
            match_day = re.match(r'Day (\d+) \(preliminary\)', title)
            if match_day:
                day = match_day.group(1)
                filename = f"day{day}_preliminary.html"
            elif title == "The Apollo Journey Begins":
                filename = "the_apollo_journey_begins.html"
            else:
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
    filepath = os.path.join(output_dir, "ap07fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap07fj/index.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 7 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo7 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 7 journals...\n")
    print(f"HTML files will be saved to: {output_dir}/\n")

    # Download flight journals
    flight_success = download_flight_journals(output_dir, force=args.force)

    # Download main pages
    download_main_pages(output_dir, force=args.force)

    print(f"\nTotal download complete: {flight_success}/{len(flight_journals)} journals downloaded successfully")
    print(f"All HTML files saved to: {output_dir}/")

if __name__ == "__main__":
    main()