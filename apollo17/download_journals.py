#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URLs for Apollo 17 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap17fj/"
SURFACE_JOURNAL_BASE = "https://apollojournals.org/alsj/a17/"

# Apollo 17 Flight Journal sections with CORRECT URLs from the actual website
flight_journals = [
    # Travelling from the Earth to the Moon
    ("Day 1: The Launch", "01_day01_launch.html"),
    ("Day 1: Earth Orbit and Translunar Injection", "02_day01_earth_orbit_tli.html"),
    ("Day 1: Transposition, Docking and Extraction", "03_day01_tde.html"),
    ("Day 1: 'A regular human weather satellite'", "04_day01_human_weathersat.html"),
    ("Day 2: Part 1", "05_day02_part1.html"),
    ("Day 2: Part 2, Earthwatching", "06_day02_part2_earthwatching.html"),
    ("Day 3, part 1: Midcourse correction 2", "07_day03_part1_mcc2.html"),
    ("Day 3, part 2: Entering the LM", "08a_day03_part2_enter_lm.html"),
    ("Day 3, part 3: The heat flow experiment", "08b_day03_part3_heat_flow.html"),
    ("Day 4, part 1: Clock update", "09_day04_part1_clock_update.html"),
    ("Day 4, part 2: Light flash experiment", "10_day04_part2_light_flash.html"),
    ("Day 5, part 1: Approaching the Moon", "11_day05_part1_approach_moon.html"),

    # In the Vicinity of the Moon
    ("Day 5, part 2: Lunar Orbit Insertion", "12_day05_part2_loi.html"),
    ("Day 5, part 3: Descent Orbit Insertion", "13_day05_part3_doi.html"),
    ("Day 5, part 4: Settling into lunar orbit", "14_day05_part4.html"),
    ("Day 6, part 1: Waking in the descent orbit", "15_day06_part1.html"),
    ("Day 6, part 1: CSM only", "15a_day06_part1_csm.html"),
    ("Day 6, part 2: Preparations for landing", "16_day06_part2_landing_prep.html"),
    ("Day 6, part 2: CSM only", "16a_day06_part2_csm.html"),

    # The Solo Mission of CSM America
    ("Day 6, part 3: Solo operations 1", "17_day06_part3_solo_ops1.html"),
    ("Day 7: Solo operations 2, Part 1", "18_day07_solo_ops2-pt1.html"),
    ("Day 7: Solo operations 2, Part 2", "19_day07_solo_ops2-pt2.html"),
    ("Day 8: Solo operations 3, Part 1", "20_day08_solo_ops3-pt1.html"),
    ("Day 8: Solo operations 3, Part 2", "21_day08_solo_ops3-pt2.html")
]

# Apollo 17 Surface Journal sections with CORRECT URLs from the actual website
# Note: Some sections share the same HTML file with anchors
surface_journals = [
    # Landing Day
    ("Landing Day", "a17.prepdi.html"),
    ("The Trip to Lunar Orbit and Preparations for the Descent", "a17.prepdi.html"),
    ("Apollo 17 Flight Journal: The First Part of the Mission", "../../afj/ap17fj/index.html"),
    ("Landing at Taurus-Littrow", "a17.landing.html"),
    ("Post-landing Activities", "a17.postland.html"),

    # The First EVA
    ("Preparations for EVA 1", "a17.eva1prep.html"),
    ("Down the Ladder", "a17.1ststep.html"),
    ("Rover Deployment", "a17.lrvdep.html"),
    ("Loading the Rover", "a17.lrvload.html"),
    ("Flag Deployment and ALSEP Off-Load", "a17.alsepoff.html"),
    ("ALSEP Deployment", "a17.alsepdep.html"),
    ("Deep Core and ALSEP Completion", "a17.deepcore.html"),
    ("Traverse to Geology Station 1 near Steno Crater", "a17.trvsta1.html"),
    ("Geology Station 1", "a17.sta1.html"),
    ("Return to the LM and SEP Deployment", "a17.trvlm1.html"),
    ("EVA-1 Close-out", "a17.clsout1.html"),
    ("Ending the First Day", "a17.eva1post.html"),

    # The Second EVA
    ("EVA-2 Wake-up", "a17.eva2wake.html"),
    ("Preparations for EVA-2", "a17.eva2prep.html"),
    ("The First Half of the Traverse to Geology Station 2", "a17.outcam.html"),
    ("Traverse from Camelot to Geology Station 2", "a17.trvsta2.html"),
    ("Geology Station 2 at the base of the South Massif", "a17.sta2.html"),
    ("Traverse to Geology Station 3", "a17.trvsta3.html"),
    ("Geology Station 3 at Ballet Crater", "a17.trvsta4.html"),
    ("Orange Soil on the Moon: Geology Station 4 at Shorty Crater", "a17.sta4.html"),
    ("Traverse to Geology Station 5", "a17.trvsta5.html"),
    ("Geology Station 5 at Camelot Crater", "a17.sta5.html"),
    ("Return to the LM and Close-out", "a17.clsout2.html"),
    ("Ending the Second Day", "a17.eva2post.html"),

    # The Third EVA
    ("Wake-up and Preparing for EVA-3", "a17.eva3prep.html"),
    ("Traverse to Geology Station 6 at Tracy's Rock", "a17.trvsta6.html"),
    ("Geology Station 6", "a17.sta6.html"),
    ("Geology Station 7", "a17.sta7.html"),
    ("Geology Station 8 at the base of the Sculptured Hills", "a17.sta8.html"),
    ("Traverse to Geology Station 9 at Van Serg Crater", "a17.trvsta9.html"),
    ("Geology Station 9", "a17.sta9.html"),
    ("Return to the LM", "a17.trvlm3.html"),
    ("Close-out", "a17.clsout3.html"),
    ("Ending the Third Day", "a17.eva3post.html"),

    # Completing the Mission
    ("Return to Orbit", "a17.launch.html"),
    ("Return to Earth", "a17.homeward.html")
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
    """Download Apollo 17 Flight Journal files."""
    print("Starting download of Apollo 17 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename: dayX_partY_description.html
        # Extract day and part from title
        match = re.match(r'Day (\d+)(?:, part (\d+))?: (.+)', title)
        if match:
            day = match.group(1)
            part = match.group(2) or "1"
            description = match.group(3).lower().replace(' ', '_').replace(',', '').replace("'", "")
            filename = f"day{day}_part{part}_{description}.html"
        else:
            # For titles without "Day X, part Y:" format
            filename = clean_filename(title)

        full_url = urljoin(FLIGHT_JOURNAL_BASE, relative_url)
        if download_journal(title, full_url, output_dir, filename, force=force):
            success_count += 1

    print(f"Flight Journal download complete: {success_count}/{len(flight_journals)} files downloaded successfully")
    return success_count

def download_surface_journals(output_dir=".", force=False):
    """Download Apollo 17 Surface Journal files."""
    print("\nStarting download of Apollo 17 Surface Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(surface_journals, 1):
        # Create filename: surface_XX_description.html where XX is 01-18
        section_num = str(i).zfill(2)

        # Clean the description part
        description = title.lower()
        description = re.sub(r'[^\w\s-]', '', description)  # Remove special chars
        description = re.sub(r'[-\s]+', '_', description)  # Replace spaces and hyphens with underscores
        description = description.strip('_')

        filename = f"surface_{section_num}_{description}.html"

        # Handle special case for first item (links to flight journal index)
        if relative_url.startswith("../../"):
            full_url = urljoin("https://apollojournals.org/", relative_url)
        else:
            full_url = urljoin(SURFACE_JOURNAL_BASE, relative_url)

        if download_journal(title, full_url, output_dir, filename, force=force):
            success_count += 1

    print(f"Surface Journal download complete: {success_count}/{len(surface_journals)} files downloaded successfully")
    return success_count

def download_main_pages(output_dir=".", force=False):
    """Download the main index pages for reference."""
    print("\nDownloading main pages...")

    # Flight Journal main page
    filepath = os.path.join(output_dir, "ap17fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap17fj/index.html"
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

    # Surface Journal main page
    filepath = os.path.join(output_dir, "a17_original_main.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            surface_main_url = "https://apollojournals.org/alsj/a17/a17.html"
            response = requests.get(surface_main_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"Surface Journal main page saved to: {filepath}")
            print(f"Size: {len(response.text)} bytes")

        except Exception as e:
            print(f"Error downloading Surface Journal main page: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download Apollo 17 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo17 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 17 journals...\n")
    print(f"HTML files will be saved to: {output_dir}/\n")

    # Download flight journals
    flight_success = download_flight_journals(output_dir, force=args.force)

    # Download surface journals
    surface_success = download_surface_journals(output_dir, force=args.force)

    # Download main pages
    download_main_pages(output_dir, force=args.force)

    print(f"\nTotal download complete: {flight_success + surface_success}/{len(flight_journals) + len(surface_journals)} journals downloaded successfully")
    print(f"All HTML files saved to: {output_dir}/")

if __name__ == "__main__":
    main()