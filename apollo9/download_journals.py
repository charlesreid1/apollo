#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URL for Apollo 9 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap09fj/"

# Apollo 9 Flight Journal sections with CORRECT URLs from the actual website
flight_journals = [
    # Background
    ("Preparations for Launch", "000_preparations.html"),

    # Day 1
    ("Launch", "001_day01_launch.html"),
    ("Orbit 1 - In Earth Orbit", "002_day01_rev001.html"),
    ("Orbit 2 - Transposition & Docking", "003_day01_rev002.html"),
    ("Orbit 3 - Separation & Ejection", "004_day01_rev003.html"),
    ("Orbit 4 - SPS-1", "005_day01_rev004.html"),
    ("Orbit 5 - Daylight Star Check", "006_day01_rev005.html"),
    ("Orbit 6 - Preparing for Sleep", "007_day01_rev006.html"),
    ("Orbits 7-11 - Rest Period", "008_day01_rev007.html"),

    # Days 2-11 (Preliminary)
    ("Day 2 - Preliminary", "009_day02.html"),
    ("Day 3 - Preliminary", "010_day03.html"),
    ("Day 4 - Preliminary", "011_day04.html"),
    ("Day 5 - Preliminary", "012_day05.html"),
    ("Day 6 - Preliminary", "013_day06.html"),
    ("Day 7 - Preliminary", "014_day07.html"),
    ("Day 8 - Preliminary", "015_day08.html"),
    ("Day 9 - Preliminary", "016_day09.html"),
    ("Day 10 - Preliminary", "017_day10.html"),
    ("Day 11 - Preliminary", "018_day11.html"),
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
    """Download Apollo 9 Flight Journal files."""
    print("Starting download of Apollo 9 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename based on title
        # For Apollo 9, we have a simpler naming convention
        if "Preparations for Launch" in title:
            filename = "preparations_for_launch.html"
        elif "Day" in title and "Preliminary" in title:
            # Extract day number for preliminary days
            match = re.match(r'Day (\d+) - Preliminary', title)
            if match:
                day = match.group(1)
                filename = f"day{day}_preliminary.html"
            else:
                filename = clean_filename(title)
        elif "Orbit" in title:
            # Extract orbit number and description
            match = re.match(r'Orbit (\d+) - (.+)', title)
            if match:
                orbit = match.group(1)
                description = match.group(2).lower().replace(' ', '_').replace('&', 'and')
                filename = f"orbit{orbit}_{description}.html"
            else:
                match = re.match(r'Orbits (\d+-\d+) - (.+)', title)
                if match:
                    orbits = match.group(1).replace('-', '_to_')
                    description = match.group(2).lower().replace(' ', '_')
                    filename = f"orbits{orbits}_{description}.html"
                else:
                    filename = clean_filename(title)
        elif "Launch" in title:
            filename = "launch.html"
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
    filepath = os.path.join(output_dir, "ap09fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap09fj/index.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 9 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo9 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 9 journals...\n")
    print(f"HTML files will be saved to: {output_dir}/\n")

    # Download flight journals
    flight_success = download_flight_journals(output_dir, force=args.force)

    # Download main pages
    download_main_pages(output_dir, force=args.force)

    print(f"\nTotal download complete: {flight_success}/{len(flight_journals)} journals downloaded successfully")
    print(f"All HTML files saved to: {output_dir}/")

if __name__ == "__main__":
    main()