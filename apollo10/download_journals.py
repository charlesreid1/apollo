#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URL for Apollo 10 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap10fj/"

# Apollo 10 Flight Journal sections with CORRECT URLs from the actual website
flight_journals = [
    # Background
    ("Background details", "as10-prep.html"),

    # Travelling from the Earth to the Moon
    ("Launch", "as10-day1-pt1.html"),
    ("Earth Orbit rev 1", "as10-day1-pt2-earthorbit-rev1.html"),
    ("Earth Orbit rev 2", "as10-day1-pt3-earthorbit-rev2.html"),
    ("TLI, Transposition, Docking", "as10-day1-pt4-tli-docking.html"),
    ("LM Extraction and S-IVB Sep", "as10-day1-pt5-lmext-sivb-sep.html"),
    ("Housekeeping and TV transmission", "as10-day1-pt6-housekeep-tv.html"),
    ("PTC concerns and sleep", "as10-day1-pt7-ptc-sleep.html"),
    ("Midcourse correction and TV transmission", "as10-day2-pt8.html"),
    ("Housekeeping, sleep and TV", "as10-day2-pt9.html"),
    ("Revision and TV in the blind", "as10-day3-pt10.html"),
    ("TV and a long, long rest", "as10-day3-pt11.html"),
    ("Lunar encounter - Approach", "as10-day4-pt12a.html"),
    ("Lunar encounter - Lunar Orbit Insertion", "as10-day4-pt12b.html"),

    # Lunar Orbit
    ("Acclimatising in lunar orbit", "as10-day4-pt13.html"),
    ("LOI-2 and entering Snoopy", "as10-day4-pt14.html"),
    ("Snoopy comm checks", "as10-day4-pt15.html"),
    ("Rest and Preparation for Solo Ops.", "as10-day4-pt16.html"),
    ("Snoopy prepares for the main event", "as10-day5-pt17.html"),
    ("Undocking & DOI, Snoopy goes solo", "as10-day5-pt18.html"),
    ("'We is down among them'", "as10-day5-pt19.html"),
    ("A surprise at staging", "as10-day5-pt20.html"),
    ("Snoopy chases Charlie Brown", "as10-day5-pt21.html"),
    ("'Snoopy and Charlie Brown are hugging each other'", "as10-day5-pt22.html"),
    ("'Snoop went some place'", "as10-day5-pt23.html"),
    ("Sleep and picture taking", "as10-day6-pt24.html"),
    ("Photos, landmarks and fuel cells", "as10-day6-pt25.html"),
    ("Lots of tracking and Snoopy makes a reappearance.", "as10-day6-pt26.html"),
    ("Tracking, snapping and napping", "as10-day6-pt27.html"),
    ("Snoopy and fuel cells cause concern", "as10-day6-pt28.html"),

    # Homeward journey to Earth
    ("Going back to Houston", "as10-day6-pt29-tei.html"),
    ("The Tom, John and Gene evening show", "as10-day7-pt30.html"),
    ("Space Pirate on TV", "as10-day7-pt31.html"),
    ("Housekeeping, navigation and comms tests", "as10-day8-pt32.html"),
    ("TV, with Charlie Brown and Snoopy", "as10-day8-pt33.html"),
    ("Awake on Splashdown day", "as10-day9-pt34.html"),
    ("Entry preparations", "as10-day9-pt35.html"),
    ("Homecoming", "as10-day9-pt36-entry-splash.html"),
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
    """Download Apollo 10 Flight Journal files."""
    print("Starting download of Apollo 10 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename based on day and part structure
        # Extract day and part from filename if possible
        day_match = re.search(r'day(\d+)', relative_url)
        part_match = re.search(r'pt(\d+)', relative_url)

        if day_match and part_match:
            day = day_match.group(1)
            part = part_match.group(1)
            # Clean up title for filename
            clean_title = title.lower().replace(' ', '_').replace(',', '').replace("'", '').replace('"', '')
            filename = f"day{day}_part{part}_{clean_title}.html"
        else:
            # For titles without day/part structure
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
    filepath = os.path.join(output_dir, "ap10fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap10fj/index.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 10 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo10 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 10 journals...\n")
    print(f"HTML files will be saved to: {output_dir}/\n")

    # Download flight journals
    flight_success = download_flight_journals(output_dir, force=args.force)

    # Download main pages
    download_main_pages(output_dir, force=args.force)

    print(f"\nTotal download complete: {flight_success}/{len(flight_journals)} journals downloaded successfully")
    print(f"All HTML files saved to: {output_dir}/")

if __name__ == "__main__":
    main()