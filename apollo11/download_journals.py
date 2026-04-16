#!/usr/bin/env python3
import argparse
import os
import requests
from urllib.parse import urljoin
import time
import re
from bs4 import BeautifulSoup

# Base URL for the Apollo journals
BASE_URL = "https://apollojournals.org/alsj/a11/"

# Flight journal sections and their relative URLs
flight_journals = [
    ("Apollo Flight Journal: The First Part of the Mission", "../../afj/ap11fj/01launch.html"),
    ("The First Lunar Landing", "a11.landing.html"),
    ("Post-landing Activities", "a11.postland.html"),
    ("EVA Preparations", "a11.evaprep.html"),
    ("One Small Step", "a11.step.html"),
    ("Mobility and Photography", "a11.mobility.html"),
    ("EASEP Deployment and Closeout", "a11.clsout.html"),
    ("Trying to Rest", "a11.posteva.html"),
    ("The Return to Orbit", "a11.launch.html"),
    ("Apollo Flight Journal: The Remainder of the Mission", "../../afj/ap11fj/19day6-rendezvs-dock.html")
]

# Surface journal sections - same titles but different URLs (from the main page)
# These will be downloaded from the main page links
surface_journal_titles = [
    "Apollo Flight Journal: The First Part of the Mission",
    "The First Lunar Landing",
    "Post-landing Activities",
    "EVA Preparations",
    "One Small Step",
    "Mobility and Photography",
    "EASEP Deployment and Closeout",
    "Trying to Rest",
    "The Return to Orbit",
    "Apollo Flight Journal: The Remainder of the Mission"
]

def download_journal(title, relative_url, journal_type="flight", force=False):
    """Download a journal HTML file to the html/ subdirectory."""
    # Create filename from title
    if journal_type == "surface":
        # Format: surface_00_foo_bar.html
        clean_title = title.lower().replace(":", "").replace(" ", "_").replace(".", "")
        index = surface_journal_titles.index(title)
        filename = f"surface_{index:02d}_{clean_title}.html"
    else:
        # Flight journal naming: flight_00_foo_bar.html
        clean_title = title.lower().replace(":", "").replace(" ", "_").replace(".", "")
        index = flight_journals.index((title, relative_url))
        filename = f"flight_{index:02d}_{clean_title}.html"

    html_dir = "html"
    filepath = os.path.join(html_dir, filename)
    if not force and os.path.exists(filepath):
        print(f"Skipping (already exists): {filepath}\n")
        return True

    # Construct the full URL
    if relative_url.startswith("../../"):
        # For flight journal URLs, use a different base
        full_url = urljoin("https://apollojournals.org/", relative_url)
    else:
        full_url = urljoin(BASE_URL, relative_url)

    print(f"Downloading {journal_type} journal: {title}")
    print(f"URL: {full_url}")

    try:
        # Make the request
        response = requests.get(full_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()

        # Create html subdirectory directly in current directory
        os.makedirs(html_dir, exist_ok=True)

        # Save the file to html subdirectory
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"Saved to: {filepath}")
        print(f"Size: {len(response.text)} bytes\n")

        # Be polite to the server
        time.sleep(1)

        return True

    except Exception as e:
        print(f"Error downloading {title}: {e}\n")
        return False

def extract_surface_journal_urls(html_content):
    """Extract surface journal URLs from the main page HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    surface_urls = {}

    # Find all links in the page
    for link in soup.find_all('a'):
        link_text = link.get_text().strip()
        href = link.get('href', '')

        # Check if this link text matches any of our surface journal titles
        for title in surface_journal_titles:
            if title.lower() in link_text.lower() or link_text.lower() in title.lower():
                if href and not href.startswith('#'):
                    surface_urls[title] = href
                    break

    return surface_urls

def main():
    parser = argparse.ArgumentParser(description="Download Apollo 11 journals")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files already exist")
    args = parser.parse_args()

    print("Starting download of Apollo 11 journals...\n")

    # Create html subdirectory directly in current directory
    html_dir = "html"
    os.makedirs(html_dir, exist_ok=True)

    # Download the main page to extract surface journal URLs
    print("Downloading main page to extract surface journal URLs...")
    main_page_path = os.path.join(html_dir, "a11_original_main.html")
    if not args.force and os.path.exists(main_page_path):
        print(f"Skipping (already exists): {main_page_path}")
        with open(main_page_path, 'r', encoding='utf-8') as f:
            main_page_html = f.read()
        surface_urls = extract_surface_journal_urls(main_page_html)
        print(f"Found {len(surface_urls)} surface journal links in cached main page")
    else:
        try:
            main_url = "https://apollojournals.org/alsj/a11/a11.html"
            response = requests.get(main_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            with open(main_page_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"Main page saved to: {main_page_path}")
            print(f"Size: {len(response.text)} bytes\n")

            # Extract surface journal URLs from the main page
            surface_urls = extract_surface_journal_urls(response.text)
            print(f"Found {len(surface_urls)} surface journal links in main page")

        except Exception as e:
            print(f"Error downloading main page: {e}")
            surface_urls = {}

    # Download flight journals
    print("\n=== Downloading Flight Journals ===\n")
    flight_success_count = 0
    for title, url in flight_journals:
        if download_journal(title, url, journal_type="flight", force=args.force):
            flight_success_count += 1

    print(f"\nFlight journals complete: {flight_success_count}/{len(flight_journals)} downloaded successfully")

    # Download surface journals
    print("\n=== Downloading Surface Journals ===\n")
    surface_success_count = 0
    for title in surface_journal_titles:
        if title in surface_urls:
            if download_journal(title, surface_urls[title], journal_type="surface", force=args.force):
                surface_success_count += 1
        else:
            print(f"Warning: Could not find URL for surface journal: {title}")

    print(f"\nSurface journals complete: {surface_success_count}/{len(surface_journal_titles)} downloaded successfully")

    print(f"\n=== Overall Summary ===")
    print(f"Flight journals: {flight_success_count}/{len(flight_journals)}")
    print(f"Surface journals: {surface_success_count}/{len(surface_journal_titles)}")
    print(f"Total: {flight_success_count + surface_success_count}/{len(flight_journals) + len(surface_journal_titles)}")

if __name__ == "__main__":
    main()