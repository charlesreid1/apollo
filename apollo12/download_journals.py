#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URLs for Apollo 12 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap12fj/"
SURFACE_JOURNAL_BASE = "https://apollojournals.org/alsj/a12/"

# Apollo 12 Flight Journal sections with CORRECT URLs from the actual website
flight_journals = [
    # Travelling from the Earth to the Moon
    ("Day 1, part 1: Launch and Reaching Earth Orbit", "01launch_to_earth_orbit.html"),
    ("Day 1, part 2: Earth Orbit and Translunar Injection", "02earth_orbit_tli.html"),
    ("Day 1, part 3: Transposition, Docking and Extraction", "03tde.html"),
    ("Day 1, part 4: LM Inspection", "04lm_ifld.html"),
    ("Day 1, part 5: PTC and back over to the LM", "05ptc_back_over_to_lm.html"),
    ("Day 2, part 1: Midcourse Correction 2 Burn", "06day2_mcc_2_burn.html"),
    ("Day 2, part 2: Quiet end to the day", "07day2_qettd.html"),
    ("Day 3, part 1: Day of the Tuna Fish", "08day3_dottf.html"),
    ("Day 3, part 2: TV Show", "09day3_tvs.html"),
    ("Day 4, part 1: Approaching the Moon", "10day4_approach-moon.html"),
    ("Day 4, part 2: Lunar Orbit Insertion", "11day4_loi.html"),

    # Lunar Orbit
    ("Day 4, part 3: Lunar Orbit Revolutions 1 and 2", "12day4_lunar_orbit_1_2.html"),
    ("Day 4, part 4: Lunar Orbit Revolutions 3 to 5", "13day4_lunar_orbit_3_5.html"),
    ("Day 5, part 1: Prepare for Lunar Descent", "14day5_prep_landing.html"),

    # Continued flight journal
    ("Day 5, part 2: Yankee Clipper Rev 14 to 24", "15day5_csm_rev14_24.html"),
    ("Day 6, part 1: Yankee Clipper Rev 24 to 28", "16day6_csm_rev24_28.html"),
    ("Day 6, part 2: From the Snowman to Docking", "17day6_ftstd.html"),
    ("Day 6, part 3: LM Jettison, Rev 33 to 35", "18day6_lmjett_rev33_35.html"),
    ("Day 7, part 1: Revolutions 36 to 43", "19day7_rev36_43.html"),

    # Homeward journey to Earth
    ("Day 7, part 2: Rev 44 to Trans-Earth Injection", "20day7_rev44_tei.html"),
    ("Day 8, part 1: Cislunar Navigation", "21day8_cislunar_nav.html"),
    ("Day 8, part 2: Geology Questions", "22day8_geology_q.html"),
    ("Day 9: Navigate to Question Time", "23day9_qt.html"),
    ("Day 10: Splashdown for 3 Tail Hookers", "24day10_sf3th.html")
]

# Apollo 12 Surface Journal sections with CORRECT URLs from the actual website
surface_journals = [
    # Landing Day
    ("Apollo 12 Flight Journal: The First Part of the Mission", "../../afj/ap12fj/index.html"),
    ("A Visit to the Snowman", "a12.landing.html"),
    ("Post-landing Activities", "a12.postland.html"),

    # The First EVA
    ("Preparations for EVA-1", "a12.eva1prep.html"),
    ("That may have been a small one for Neil...", "a12.eva1prelim.html"),
    ("TV Troubles", "a12.tvtrbls.html"),
    ("ALSEP Off-load", "a12.alsepoff.html"),
    ("ALSEP Deployment", "a12.alsepdep.html"),
    ("EVA-1 Closeout", "a12.clsout1.html"),
    ("Post-EVA Activities in the LM", "a12.posteva1.html"),

    # The Second EVA
    ("Wake-up and Preparations for EVA-2", "a12.eva2prep.html"),
    ("Rocking and Rolling at Head Crater", "a12.trvhead.html"),
    ("Sampling at Head Crater and Bench Crater", "a12.head_bench.html"),
    ("Sharp Crater", "a12.sharp.html"),
    ("Halo Crater", "a12.halo.html"),
    ("Surveyor Crater and Surveyor III", "a12.surveyor.html"),
    ("Return to the LM and EVA-2 Closeout", "a12.clsout2.html"),
    ("Return to Orbit", "a12.launch.html")
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
    """Download Apollo 12 Flight Journal files."""
    print("Starting download of Apollo 12 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename: dayX_partY_description.html
        # Extract day and part from title
        match = re.match(r'Day (\d+), part (\d+): (.+)', title)
        if match:
            day = match.group(1)
            part = match.group(2)
            description = match.group(3).lower().replace(' ', '_').replace(',', '')
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
    """Download Apollo 12 Surface Journal files."""
    print("\nStarting download of Apollo 12 Surface Journal...\n")

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
    filepath = os.path.join(output_dir, "ap12fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap12fj/index.html"
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
    filepath = os.path.join(output_dir, "a12_original_main.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            surface_main_url = "https://apollojournals.org/alsj/a12/a12.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 12 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo12 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 12 journals...\n")
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