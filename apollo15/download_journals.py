#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re

# Base URLs for Apollo 15 journals
FLIGHT_JOURNAL_BASE = "https://apollojournals.org/afj/ap15fj/"
SURFACE_JOURNAL_BASE = "https://apollojournals.org/alsj/a15/"

# Apollo 15 Flight Journal sections with CORRECT URLs from the actual website
flight_journals = [
    # Travelling from the Earth to the Moon
    ("Launch and Reaching Earth Orbit", "01launch_to_earth_orbit.html"),
    ("Earth Orbit and Translunar Injection", "02earth_orbit_tli.html"),
    ("Transposition, Docking and Extraction", "03tde.html"),
    ("SPS Troubleshooting and the PTC", "04troubleshoot_ptc.html"),
    ("Day 2: Checking the SPS", "05day2_checking_sps.html"),
    ("Day 2: Entering the LM", "06day2_enter_lm.html"),
    ("Day 3: Flashing Lights", "07day3_flashing_lights.html"),
    ("Day 3: Leaking Water and the Top of the Hill", "08day3_leak_hilltop.html"),
    ("Day 4: Lunar Encounter", "09day4_lunar_encounter.html"),

    # In the Vicinity of the Moon
    ("Day 4, part 2: Lunar Orbits 1 & 2", "10a-day4_lunar_orbit1-2.html"),
    ("Day 4, part 3: The Descent Orbit", "10b-day4_doi-rest.html"),
    ("Day 5, part 1: Waking in the Descent Orbit", "11day5_wakeup.html"),
    ("Day 5, part 2: Trimming the Descent Orbit", "12a-day5_doi_trim.html"),
    ("Day 5, part 3: Activating the Lunar Module", "12b-day5_lm_activation.html"),
    ("Day 5, part 4: 'We didn't get a Sep'", "12c-day5_lm_undock.html"),
    ("Day 5, part 5: CSM Circularisation", "12d-day5_csm_circ.html"),
    ("Day 5, part 6: Preparations for Landing", "12e-day5_landing_prep.html"),

    # The Solo Mission of Endeavour
    ("Day 5, part 7: Solo Orbital Operations - 1", "13solo_ops1.html"),
    ("Day 6: Solo Orbital Operations - 2", "14solo_ops2.html"),
    ("Day 7: Solo Orbital Operations - 3", "15solo_ops3.html"),
    ("Day 8, part 1: Solo Orbital Operations - 4", "16solo_ops4.html"),

    # Final Days in Lunar Orbit
    ("Day 8, part 2: Rendezvous and Docking", "17rndz_dock.html"),
    ("Day 8, part 3: Leaking Tunnel and Jettison of the LM", "18tunnel_leak_lm_jett.html"),
    ("Day 9, part 1: Orbital Science and Crew Rest", "19a-day9_orbital_science.html"),
    ("Day 9, part 2: Orbital Science, Rev 62 to 64", "19b-day9_orbital_science.html"),
    ("Day 10, part 1: Orbital Science, Rev 68 & 69", "20a-day10_science-68-69.html"),
    ("Day 10, part 2: Orbital Science, Rev 70", "20b-day10_science-70.html"),
    ("Day 10, part 3: Orbital Science, Rev 71", "20c-day10_science-71.html"),
    ("Day 10, part 4: Orbital Science, Rev 72", "20d-day10_science-72.html"),

    # Homeward to Earth
    ("Day 10, part 5: Subsatellite Launch", "21a-day10_subsat.html"),
    ("Day 10, part 6: Trans-Earth Injection", "21b-day10_tei.html"),
    ("Settling down for the Journey Home", "22day10_homeward.html"),
    ("Day 11, part 1: Cislunar Science & the Sphere of Influence", "23a-day11_science-sphere.html"),
    ("Day 11, part 2: Worden's EVA", "23b-day11_worden_eva.html"),
    ("Day 11, part 3: UV Photography & P23s", "23c-day11_uv-photos-p23.html"),
    ("Day 12, part 1: P23s & UV Photography", "24a-day12_p23-uv-photos.html"),
    ("Day 12, part 2: Lunar Eclipse & a Press Conference", "24b-day12_eclipse-presser.html"),
    ("Day 12, part 3: P23s & More Cislunar Science", "24c-day12_p23-science.html"),
    ("Day 13, part 1: Approaching Earth", "25a-day13_approach-earth.html"),
    ("Day 13, part 2: Entry & Splashdown", "25b-day13_entry-splashdown.html")
]

# Apollo 15 Surface Journal sections with CORRECT URLs from the actual website
surface_journals = [
    # Landing Day
    ("Apollo 15 Flight Journal: The First Part of the Mission", "../../afj/ap15fj/index.html"),
    ("Landing at Hadley", "a15.landing.html"),
    ("Post-landing Activities", "a15.postland.html"),

    # Stand-Up EVA
    ("Preparations for the Stand-Up EVA", "a15.sevaprep.html"),
    ("Stand-Up EVA", "a15.seva.html"),
    ("Post-SEVA Activities", "a15.postseva.html"),

    # The First EVA
    ("Wake-up for EVA-1", "a15.eva1wake.html"),
    ("Preparations for EVA-1", "a15.eva1prep.html"),
    ("Deploying the Lunar Roving Vehicle", "a15.lrvdep.html"),
    ("Loading the Rover", "a15.lrvload.html"),
    ("Preparations for the First Rover Traverse", "a15.trv1prep.html"),
    ("Driving to Elbow Crater", "a15.elbowtrv.html"),
    ("Geology Station 1 at Elbow Crater", "a15.elbow.html"),
    ("Driving to Station 2", "a15.trvsta2.html"),
    ("Geology Station 2 on Mt. Hadley Delta", "a15.sta2.html"),
    ("Return to the LM", "a15.trvlm1.html"),
    ("ALSEP Off-load", "a15.alsepoff.html"),
    ("Drilling Troubles", "a15.alsepdep.html"),
    ("EVA-1 Closeout", "a15.clsout1.html"),
    ("Post-EVA-1 Activities", "a15.eva1post.html"),

    # The Second EVA
    ("Wake-up for EVA-2", "a15.eva2wake.html"),
    ("Planning Discussions for EVA-2", "a15.eva2plan.html"),
    ("Preparations for EVA-2", "a15.eva2prep.html"),
    ("Getting the Rover Loaded for EVA-2", "a15.eva2prelim.html"),
    ("Driving to Station 6 on Mt. Hadley Delta", "a15.trvsta6.html"),
    ("Working above the Rover at Station 6", "a15.sta6abv.html"),
    ("Working below the Rover in the Station 6 crater", "a15.sta6crtr.html"),
    ("Traverse to Station 6a", "a15.trvsta6a.html"),
    ("The Green Boulder at Station 6a", "a15.sta6a.html"),
    ("The Genesis Rock", "a15.spur.html"),
    ("Dune Crater", "a15.trvsta4.html"),
    ("Return to the LM", "a15.trvlm2.html"),
    ("Heat Flow Reprise", "a15.heatflow2.html"),
    ("The Dreaded Station 8", "a15.sta8.html"),
    ("EVA-2 Closeout", "a15.clsout2.html"),
    ("Post-EVA-2 Activities", "a15.eva2post.html"),

    # The Third EVA
    ("Preparations for EVA-3", "a15.eva3prep.html"),
    ("Preparing the Rover for the trip to the Rille", "a15.eva3prelim.html"),
    ("Extracting the Core and Losing the North Complex", "a15.coreextract.html"),
    ("Irwin's Dunes", "a15.trvsta9.html"),
    ("Instant Rock at Station 9", "a15.sta9.html"),
    ("Hadley Rille", "a15.rille.html"),
    ("Stereo Photography at Station 10", "a15.sta10.html"),
    ("Return to the LM", "a15.trvlm3.html"),
    ("The Hammer and the Feather", "a15.clsout3.html"),
    ("Post-EVA-3 Activities", "a15.eva3post.html"),
    ("Return to Orbit", "a15.launch.html")
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
    """Download Apollo 15 Flight Journal files."""
    print("Starting download of Apollo 15 Flight Journal...\n")

    success_count = 0
    for i, (title, relative_url) in enumerate(flight_journals, 1):
        # Create filename: dayX_partY_description.html
        # Extract day and part from title
        match = re.match(r'Day (\d+)(?:, part (\d+))?: (.+)', title)
        if match:
            day = match.group(1)
            part = match.group(2) or "1"
            description = match.group(3).lower().replace(' ', '_').replace(',', '').replace("'", "").replace('"', '')
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
    """Download Apollo 15 Surface Journal files."""
    print("\nStarting download of Apollo 15 Surface Journal...\n")

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
    filepath = os.path.join(output_dir, "ap15fj_index.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            flight_main_url = "https://apollojournals.org/afj/ap15fj/index.html"
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
    filepath = os.path.join(output_dir, "a15_original_main.html")
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}")
    else:
        try:
            surface_main_url = "https://apollojournals.org/alsj/a15/a15.html"
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
    parser = argparse.ArgumentParser(description="Download Apollo 15 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    # Ensure we're in the apollo15 directory
    output_dir = "html"

    # Create html directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting download of Apollo 15 journals...\n")
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