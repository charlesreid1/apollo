#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URL for Apollo 13 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap13fj/"

# Apollo 13 Flight Journal sections with CORRECT URLs from the actual website
# Note: Apollo 13 did not land on the Moon, so there is no Surface Journal.
flight_journals = [
    # Travelling from the Earth to the Moon
    ("Day 1, part 1: Launch and Reaching Earth Orbit", "01launch_ascent.html"),
    ("Day 1, part 2: Earth Orbit and Translunar Injection", "02earth_orbit_tli.html"),
    ("Day 1, part 3: Transposition, Docking and Extraction", "03tde.html"),
    ("Day 1, part 4: Settling Down for the Flight", "04day1-end.html"),
    ("Day 2, part 1: Midcourse Correction 2 on TV", "05day2-mcc2-tv.html"),
    ("Day 2, part 2: Housekeeping and Updates", "06day2-end.html"),
    ("Day 3, part 1: Before the Storm", "07day3-before-the-storm.html"),

    # The Rescue, Day 3
    ("Day 3, part 2: 'Houston, we've had a problem'", "08day3-problem.html"),
    ("Day 3, part 3: Aquarius Becomes a Lifeboat", "09day3-lifeboat.html"),
    ("Day 3, part 4: Free Return", "10day3-free-return.html"),
    ("Day 3, part 5: Minimising Power", "11day3-minimise-power.html"),

    # The Rescue, Day 4
    ("Day 4, part 1: Approaching the Moon", "12day4-approach-moon.html"),
    ("Day 4, part 2: Leaving the Moon", "13day4-leaving-moon.html"),
    ("Day 4, part 3: Heading Homeward", "14day4-homeward.html"),
    ("Day 4, part 4: Building The CO2 Adapter", "15day4-mailbox.html"),
    ("Day 4, part 5: Checking Odyssey", "16day4-checkingodyssey.html"),

    # The Rescue, Day 5
    ("Day 5, part 1: A Thump and Snowflakes in Space", "17day5-thumpandsnowflakes.html"),
    ("Day 5, part 2: Feeling the Cold", "18day5-feelingthecold.html"),
    ("Day 5, part 3: The Manual Course Correction Burn", "19day5-themanualcoursecorrection.html"),
    ("Day 5, part 4: Wobbles and Bursts", "20day5-wobblesandbursts.html"),
    ("Day 5, part 5: Starting the Battery Charge", "21day5-batterycharge.html"),

    # The Rescue, Day 6
    ("Day 6, part 1: Packing Up", "22day6-packingup.html"),
    ("Day 6, part 2: The Reactivation Checklist", "23day6-thereactivationchecklist.html"),
    ("Day 6, part 3: Worn Out Crew", "24day6-wornoutcrew.html"),
    ("Day 6, part 4: The Last Course Correction", "25day6-thelastcoursecorrection.html"),
    ("Day 6, part 5: Service Module Separation", "26day6-servicemoduleseparation.html"),
    ("Day 6, part 6: Odyssey Resurrected", "27day6-odysseyresurrected.html"),
    ("Day 6, part 7: Farewell, Aquarius", "28day6-farewellaquarius.html"),
    ("Day 6, part 8: The Blackout, Splashdown and Recovery", "29day6-returnhome.html"),
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
    """Download Apollo 13 Flight Journal files."""
    print("Starting download of Apollo 13 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename: dayX_partY_description.html
        # Extract day and part from title
        match = re.match(r'Day (\d+), part (\d+): (.+)', title)
        if match:
            day = match.group(1)
            part = match.group(2)
            description = match.group(3).lower().replace(' ', '_').replace(',', '').replace("'", '')
            filename = f"day{day}_part{part}_{description}.html"
        else:
            # For titles without "Day X, part Y:" format
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
    filepath = os.path.join(output_dir, "ap13fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap13fj/index.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 13 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo13 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 13 journals...\n")
    print(f"HTML files will be saved to: {output_dir}/\n")

    # Download flight journals
    flight_success = download_flight_journals(output_dir, force=args.force)

    # Download main pages
    download_main_pages(output_dir, force=args.force)

    print(f"\nTotal download complete: {flight_success}/{len(flight_journals)} journals downloaded successfully")
    print(f"All HTML files saved to: {output_dir}/")

if __name__ == "__main__":
    main()
