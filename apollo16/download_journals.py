#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URLs for Apollo 16 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap16fj/"
SURFACE_JOURNAL_BASE = "https://apollojournals.org/alsj/a16/"

# Apollo 16 Flight Journal sections with CORRECT URLs from the actual website
flight_journals = [
    # Travelling from the Earth to the Moon
    ("Day 1: Launch and Ascent to Earth Orbit", "01_Day1_Pt1.html"),
    ("Day 1: First Earth Orbit", "02_Day1_Pt2.html"),
    ("Day 1: Second Earth Orbit and Trans-Lunar Injection", "03_Day1_Pt3.html"),
    ("Day 1: Transposition, Docking and Extraction", "04_Day1_Pt4.html"),
    ("Day 1: Translunar Cruise", "05_Day1_Pt5.html"),
    ("Day 2: Electrophoresis Experiment and Midcourse Correction Burn", "06_Day2_Pt1.html"),
    ("Day 2: LM Entry and Checks", "07_Day2_Pt2.html"),
    ("Day 3: ALFMED Experiment", "08_Day3_Pt1.html"),
    ("Day 3: Lunar Module Activation and Checkout", "09_Day3_Pt2.html"),
    ("Day 4: Arrival at the Moon", "10_Day4_Pt1.html"),

    # In Lunar Orbit
    ("Day 4: Lunar Orbit Insertion", "11_Day4_Pt2.html"),
    ("Day 4: Descent Orbit Insertion, Revs 3 to 9", "12_Day4_Pt3.html"),
    ("Day 5: Transfer to Lunar Module, Revs 10 and 11", "13_Day5_Pt1.html"),
    ("Day 5: Lunar Module Undocking and Preparation, Revs 11 and 12", "14_Day5_Pt2.html"),
    ("Day 5: \"I be a sorry bird\". LM and CM Problems, Rev 12 and 13", "15_Day5_pt3.html"),
    ("Day 5: Rendezvous and Waiting. Revs 13 to 15", "16_Day5_Pt4.html"),
    ("Day 5: LM Powered Descent Initiation Clearance and Landing, Revs 15 to 16", "17_Day5_Pt5.html"),
    ("Day 5: Lunar Observation and Rest, Revs 16 to 21", "18_Day5_Pt6.html"),
    ("Day 6: Lunar Observation, Revs 21 to 27", "19_Day6_Pt1.html"),
    ("Day 6: Lunar Observation, Revs 27 to 34", "20_Day6_Pt2.html"),
    ("Day 7: Lunar Observation, Revs 35 to 45", "21_Day7.html"),
    ("Day 8 Part 1: Lunar Observation, Revs 46 to 51", "22_Day8_Pt1.html"),
    ("Day 8 Part 2: LM Liftoff and Rendezvous, Revs 52 to 58", "23_Day8_Pt2.html"),
    ("Day 9 Part 1: Preparation for LM Jettison, Revs 59 to 62", "24_Day9_Pt1.html"),
    ("Day 9 Part 2: LM Jettison and Trans-Earth Injection", "25_Day9_Pt2.html"),

    # Returning To Earth
    ("Day 10 Part 1: Preparation for EVA", "26_Day10_Pt1.html"),
    ("Day 10 Part 2: EVA and Housekeeping", "27_Day10_Pt2.html"),
    ("Day 11 Part 1: Geology, Experiments and Guidance Fault Investigation", "28_Day11_Pt1.html"),
    ("Day 11 Part 2: Press Conference, Experiments and House-Keeping", "29_Day11_Pt2.html"),
    ("Day 12: Entry and Splashdown", "30_Day12.html")
]

# Apollo 16 Surface Journal sections with CORRECT URLs from the actual website
surface_journals = [
    # Landing Day
    ("Apollo 16 Flight Journal: The First Part of the Mission", "../../afj/ap16fj/index.html"),
    ("Landing at Descartes", "a16.landing.html"),
    ("Post-landing Activities", "a16.postland.html"),
    ("Window Geology", "a16.window.html"),

    # The First EVA
    ("Wake-up for EVA-1", "a16.eva1wake.html"),
    ("Preparations for EVA-1", "a16.eva1prep.html"),
    ("Back in the Briar Patch", "a16.eva1prelim.html"),
    ("Deploying the Rover", "a16.lrvdep.html"),
    ("Loading the Rover", "a16.lrvload.html"),
    ("ALSEP Off-load", "a16.alsepoff.html"),
    ("Losing the Heat Flow Experiment", "a16.heatflow.html"),
    ("Drilling the Deep Core", "a16.deepcore.html"),
    ("Thumper/Geophone Experiment", "a16.thumper.html"),
    ("Geology Preparations for the EVA-1 Traverse", "a16.geoprep1.html"),
    ("Traverse to Station 1", "a16.trvsta1.html"),
    ("Station 1 at Plum Crater", "a16.sta1.html"),
    ("Traverse to Station 2", "a16.trvsta2.html"),
    ("Station 2 at Buster Crater", "a16.sta2.html"),
    ("Grand Prix", "a16.trvlm1.html"),
    ("EVA-1 Closeout", "a16.clsout1.html"),
    ("Post-EVA-1 Activities", "a16.eva1post.html"),
    ("Debrief and Goodnight", "a16.debrief1.html"),
    ("Mattingly About the Landing Site", "a16.CMP-site.html"),

    # The Second EVA
    ("Wake-up for EVA-2", "a16.eva2wake.html"),
    ("Preparations for EVA-2", "a16.eva2prep.html"),
    ("Down the Ladder for EVA-2", "a16.eva2prelim.html"),
    ("Traverse to Station 4", "a16.trvsta4.html"),
    ("Geology Station 4 at the Stone Mountain Cincos", "a16.sta4.html"),
    ("Geology Station 5", "a16.sta5.html"),
    ("Geology Station 6", "a16.sta6.html"),
    ("Traverse from Station 6 to Station 8", "a16.trv6to8.html"),
    ("Geology Station 8", "a16.sta8.html"),
    ("Traverse to Station 9", "a16.trvsta9.html"),
    ("The Great Sneak", "a16.sta9.html"),
    ("Return to the LM", "a16.trvlm2.html"),
    ("Geology Station 10 Near the ALSEP Site", "a16.sta10.html"),
    ("EVA-2 Closeout", "a16.clsout2.html"),
    ("Post-EVA-2 Activities", "a16.eva2post.html"),

    # The Third EVA
    ("Wake-up for EVA-3", "a16.eva3wake.html"),
    ("Preparations for EVA-3", "a16.eva3prep.html"),
    ("Down the Ladder for EVA-3", "a16.eva3prelim.html"),
    ("Traverse to Station 11", "a16.trvsta11.html"),
    ("Station 11 and North Ray Crater", "a16.sta11.html"),
    ("House Rock", "a16.house_rock.html"),
    ("Traverse to Station 13", "a16.trvsta13.html"),
    ("Station 13 At Shadow Rock", "a16.sta13.html"),
    ("Return to the LM", "a16.trvlm3.html"),
    ("Station 10-Prime", "a16.sta10prime.html"),
    ("EVA-3 Closeout", "a16.clsout3.html"),
    ("VIP Site", "a16.vip.html"),
    ("Post-EVA-3 Activities", "a16.eva3post.html"),
    ("Return to Orbit", "a16.launch.html")
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
    """Download Apollo 16 Flight Journal files."""
    print("Starting download of Apollo 16 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename: dayX_partY_description.html
        # Extract day and part from title
        match = re.match(r'Day (\d+)(?: Part (\d+))?: (.+)', title)
        if match:
            day = match.group(1)
            part = match.group(2) or "1"  # Default to part 1 if not specified
            description = match.group(3).lower().replace(' ', '_').replace(',', '').replace('"', '')
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
    """Download Apollo 16 Surface Journal files."""
    print("\nStarting download of Apollo 16 Surface Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(surface_journals, 1):
        # Create filename: surface_XX_description.html where XX is 01-48
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
    filepath = os.path.join(output_dir, "ap16fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap16fj/index.html"
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
    filepath = os.path.join(output_dir, "a16_original_main.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            surface_main_url = "https://apollojournals.org/alsj/a16/a16.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 16 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo16 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 16 journals...\n")
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