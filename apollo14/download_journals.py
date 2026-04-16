#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URLs for Apollo 14 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap14fj/"
SURFACE_JOURNAL_BASE = "https://apollojournals.org/alsj/a14/"

# Apollo 14 Flight Journal sections - ACTUAL URLs from the website
# Filtered to include only the main journal sections (01-34)
flight_journals = [
    # Travelling from the Earth to the Moon
    ("Day 1, part 1: The Launch", "01_day1_launch.html"),
    ("Day 1, part 2: Earth Orbit and Translunar Injection", "02_day1_earth_orbit_tli.html"),
    ("Day 1, part 3: Transposition, Docking and Extraction", "03_day1_tde.html"),
    ("Day 1, part 4: Settling Down & Navigation", "04_day1_settling_down.html"),
    ("Day 1, part 5: TV Troubleshoot & PTC", "05_day1_tv_ptc.html"),

    # Day 2
    ("Day 2, part 1: MCC-2 Burn", "06_day2_mcc2.html"),
    ("Day 2, part 2: Sports News and More", "07_day2_sportsnews.html"),

    # Day 3
    ("Day 3, part 1: Ground Elapsed Time Update", "08_day3_get_update.html"),
    ("Day 3, part 2: TV and LM Housekeeping", "09_day3_tvlm_house.html"),

    # Into Lunar Orbit
    ("Day 4, part 1: Waking Up and Approaching the Moon", "10_day4_wakeup_approaching_moon.html"),
    ("Day 4, part 2: Midcourse Correction 4", "11_day4_mcc_4.html"),
    ("Day 4, part 3: Checking the LM EPS", "12_day4_checking_lm_eps.html"),
    ("Day 4, part 4: Apollo 14 Swings Behind the Moon", "13_day4_swing_behind_moon.html"),
    ("Day 4, part 5: Lunar Orbit Insertion and First Impressions", "14_day4_loi_first_impressions.html"),
    ("Day 4, part 6: Descent Orbit Insertion", "15_day4_descent_orbit_insertion.html"),
    ("Day 4, part 7: Orbiting the Moon", "16_day4_orbiting_moon.html"),

    # Day 5
    ("Day 5, part 1: Powering up Antares", "17_day5_powering_antares.html"),
    ("Day 5, part 2: Undocking Antares", "18_day5_preparing_to_undock.html"),
    ("Day 5, part 3: Troubleshooting the LM Computer", "19_day5_troubleshooting_lm_computer.html"),

    # Kitty Hawk Solo Operations
    ("Day 5, part 4: Kitty Hawk begins Solo Operations", "20_day5_kitty_hawk_solo_1.html"),
    ("Day 5, part 5: Command Module Solo Operations 2", "21_day5_kitty_hawk_solo_2.html"),

    # Day 6
    ("Day 6, part 1: Command Module Solo Operations 3", "22_day6_kitty_hawk_solo_3.html"),

    # Lunar Orbit Rendezvous and Trans-Earth Injection
    ("Day 6, part 2: Antares Liftoff and Rendezvous with Kitty Hawk", "23_day6_lunar_liftoff_rendezvous.html"),
    ("Day 6, part 3: Spotting Antares and Going for Docking", "24_day6_docking_a14.html"),
    ("Day 6, part 4: Packing up the Kitty Hawk and Crashing Antares", "25_day6_packing_crash_antares.html"),
    ("Day 6, part 5: Trans-Earth Injection Burn and Getting Ready to Rest", "26_day6_tei_resting.html"),

    # Earthbound Coast
    ("Day 7, part 1: MCC-5 and Trans-Earth Navigation", "27_day7_mcc5_navigation.html"),
    ("Day 7, part 2: Demonstrations on TV", "28_day7_demos_on_tv.html"),
    ("Day 8, part 1: Coasting Home", "29_day8_coasting_home.html"),
    ("Day 8, part 2: Flashing Lights Experiment and Probe Stowage", "30_day8_flashing_lights_and_probe.html"),
    ("Day 8, part 3: Press Conference On TV", "31_day8_press_conference_tv.html"),
    ("Day 8, part 4: Putting the Probe to Rest", "32_day8_probe_to_rest.html"),
    ("Day 9, part 1: Last Wakeup And Preparations for Reentry", "33_day9_last_wakeup.html"),
    ("Day 9, part 2: Kitty Hawk Returns Home - Reentry and Splashdown", "34_day9_reentry_splashdown.html")
]

# Apollo 14 Surface Journal sections - ACTUAL URLs from the website
# Filtered to include only the main journal sections
surface_journals = [
    # Landing Day
    ("Apollo 14 Flight Journal: The First Part of the Mission", "../../afj/ap14fj/index.html"),
    ("Landing at Fra Mauro", "a14.landing.html"),
    ("Post-landing Activities", "a14.postland.html"),

    # The First EVA
    ("Preparations for EVA 1", "a14.eva1prep.html"),
    ("Down the Ladder for EVA-1", "a14-prelim1.html"),
    ("ALSEP Off-Load", "a14.alsepoff.html"),
    ("ALSEP Deployment", "a14.alsepdep.html"),
    ("Return to the LM and Closeout", "a14-clsout1.html"),
    ("Ending the First Day", "a14.eva1post.html"),

    # The Second EVA
    ("Wake-up and Preparing for EVA-2", "a14.eva2prep.html"),
    ("On the Way to Cone Ridge: Geology Station A", "a14.staA.html"),
    ("Climbing Cone Ridge - Where Are We?", "a14.tocone.html"),
    ("So Near, Yet...Geology at Cone Crater", "a14.conegeo.html"),
    ("Back Down the Ridge to Station F", "a14.trvstaf.html"),
    ("Geological Activities near Weird Crater", "a14.stafg.html"),
    ("A Nice Day for a Game of Golf", "a14.clsout2.html"),
    ("Preparing for Launch", "a14.eva2post.html"),
    ("Return to Orbit", "a14.launch.html")
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
    """Download Apollo 14 Flight Journal files."""
    print("Starting download of Apollo 14 Flight Journal...\n")

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
    """Download Apollo 14 Surface Journal files."""
    print("\nStarting download of Apollo 14 Surface Journal...\n")

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
    filepath = os.path.join(output_dir, "ap14fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap14fj/index.html"
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
    filepath = os.path.join(output_dir, "a14_original_main.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            surface_main_url = "https://apollojournals.org/alsj/a14/a14.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 14 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo14 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 14 journals...\n")
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