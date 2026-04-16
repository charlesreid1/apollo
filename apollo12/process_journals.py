#!/usr/bin/env python3
"""
Process Apollo 12 Flight and Surface Journal HTML files and convert them to JSON format.
Simple version that processes files in the current directory.
"""

import os
import json
import re
from bs4 import BeautifulSoup
from pathlib import Path

def extract_content_from_html(html_path):
    """Extract structured content from HTML file in format similar to example.json."""

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title for description
    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag else os.path.basename(html_path).replace('.html', '').replace('_', ' ').title()

    # Create transcript array similar to example.json
    transcript = []

    # Process Apollo Flight Journal format (divs with classes, plus
    # classless divs that look like crew dialogue lines).
    # Timestamps may be elapsed ("HH:MM:SS"), negative ("-HH:MM:SS"), or
    # launch-countdown ("T-HH:MM:SS"). The speaker token can be a word
    # like "Armstrong" or the AFJ placeholder "Speaker"; it may carry a
    # parenthetical qualifier like "Aldrin (onboard)".
    timestamp_re = r'T?-?\d{1,3}:\d{2}:\d{2}'
    speaker_bold_pat = re.compile(
        r'^(?:(' + timestamp_re + r')\s+)?'
        r'([A-Z][A-Za-z.\-]*(?:\s*\([^)]*\))?):\s*$'
    )
    for div in soup.find_all('div'):
        classes = div.get('class') or []
        class_name = classes[0] if classes else ''

        # Treat a classless <div> as a cc entry only if its leading <b>
        # matches a "HH:MM:SS Name:" header — this filters out layout
        # wrappers (e.g. align="center" blocks).
        if not class_name:
            first_b = div.find('b')
            if not first_b:
                continue
            if not speaker_bold_pat.match(
                ' '.join(first_b.get_text().split())
            ):
                continue
            class_name = 'cc'

        if class_name in ['pao', 'cc', 'comment']:
            # Extract anchor for time reference if available
            anchor = div.find('a', {'name': True})
            time_ref = anchor.get('name') if anchor else None

            # For cc class, extract speaker
            speaker = None
            bold_prefix = None
            if class_name == 'cc':
                speaker_tag = div.find('b')
                if speaker_tag:
                    bold_text = speaker_tag.get_text(strip=True)
                    # AFJ format: "[timestamp ]Name:" where Name may be
                    # "Speaker" (the AFJ placeholder for an unidentified
                    # voice) or an actual name with optional parenthetical.
                    m = speaker_bold_pat.match(bold_text)
                    if m:
                        if m.group(1) and not time_ref:
                            time_ref = m.group(1)
                        speaker = m.group(2).strip()
                        bold_prefix = bold_text

            # Get text and split into tokens (sentences)
            text = div.get_text(strip=True)

            # For cc entries, remove the speaker prefix from the text
            if class_name == 'cc' and speaker and bold_prefix:
                if text.startswith(bold_prefix):
                    text = text[len(bold_prefix):].strip()

            # Split text into sentences for tokens
            # Simple sentence splitting - can be improved
            sentences = re.split(r'(?<=[.!?])\s+', text)
            tokens = [' '.join(s.split()) for s in sentences if s.strip()]

            # Determine time - use anchor name or generate from context
            time = time_ref if time_ref else ""

            # Determine speaker for transcript format
            transcript_speaker = speaker if speaker else "PAO" if class_name == 'pao' else "Commentary"

            if tokens:  # Only add if we have tokens
                transcript.append({
                    'tokens': tokens,
                    'speaker': transcript_speaker,
                    'time': time
                })

    # If no AFJ format found, try Lunar Surface Journal format
    if not transcript:
        # Look for bold timestamps (LSJ format)
        for bold in soup.find_all('b'):
            bold_text = ' '.join(bold.get_text().split())
            ts_match = re.match(r'^(' + timestamp_re + r')\b', bold_text)
            if not ts_match:
                continue
            timestamp = ts_match.group(1)

            # Some LSJ variants put the speaker inside the same <b>:
            # "HH:MM:SS Name:"  — capture it so the following text
            # isn't buried under "Unknown".
            embedded_speaker = None
            embedded_match = re.match(
                r'^' + timestamp_re + r'\s+([A-Z][A-Za-z.\-]*(?:\s*\([^)]*\))?):\s*$',
                bold_text,
            )
            if embedded_match:
                embedded_speaker = embedded_match.group(1).strip()

            # Get the next sibling that contains the actual text
            next_sib = bold.next_sibling
            content_text = ""
            while next_sib and not (hasattr(next_sib, 'name') and next_sib.name in ['b', 'blockquote', 'center', 'a']):
                if isinstance(next_sib, str):
                    content_text += next_sib
                next_sib = next_sib.next_sibling

            if content_text.strip():
                if embedded_speaker:
                    speaker = embedded_speaker
                    text_content = content_text.strip()
                else:
                    # Extract speaker if present — accept either plain
                    # "Armstrong:" or "Aldrin (onboard):" style. The
                    # parenthetical qualifier is preserved on the speaker
                    # here and later collapsed to the base name by
                    # consolidate_parenthetical_speakers.
                    speaker_match = re.match(
                        r'^([A-Z][A-Za-z.\-]*(?:\s*\([^)]*\))?):\s*(.*)',
                        content_text.strip(),
                        re.DOTALL,
                    )
                    if speaker_match:
                        speaker = speaker_match.group(1).strip()
                        text_content = speaker_match.group(2)
                    else:
                        speaker = "Unknown"
                        text_content = content_text.strip()

                # Split into tokens
                sentences = re.split(r'(?<=[.!?])\s+', text_content)
                tokens = [' '.join(s.split()) for s in sentences if s.strip()]

                if tokens:
                    transcript.append({
                        'tokens': tokens,
                        'speaker': speaker,
                        'time': timestamp
                    })

    # If still no transcript, extract general content
    if not transcript:
        # Get all text and create a single entry
        all_text = soup.get_text(strip=True)
        if all_text:
            # Limit text length
            if len(all_text) > 1000:
                all_text = all_text[:1000] + "..."

            sentences = re.split(r'(?<=[.!?])\s+', all_text)
            tokens = [' '.join(s.split()) for s in sentences if s.strip()][:10]  # Limit to 10 sentences

            if tokens:
                transcript.append({
                    'tokens': tokens,
                    'speaker': "Content",
                    'time': ""
                })

    return {
        'description': title,
        'transcript': transcript,
        'source_file': os.path.basename(html_path)
    }

def consolidate_parenthetical_speakers(contents):
    """
    Merge speakers like "Mattingly (continued)" or "Scott (onboard)" into
    their base name when the base name also appears as a speaker somewhere
    in the same mission. Mutates ``contents`` in place.
    """
    paren_pat = re.compile(r'^(.+?)\s*\([^)]*\)\s*$')
    base_names = set()
    for content in contents:
        for entry in content.get('transcript', []):
            s = entry.get('speaker', '')
            if s and not paren_pat.match(s):
                base_names.add(s)
    for content in contents:
        for entry in content.get('transcript', []):
            s = entry.get('speaker', '')
            m = paren_pat.match(s)
            if m and m.group(1) in base_names:
                entry['speaker'] = m.group(1)

def process_journal_files():
    """Process all HTML files in html/ directory and create corresponding JSON files in json/ directory."""

    html_dir = Path('html')
    json_dir = Path('json')

    # Create json directory if it doesn't exist
    json_dir.mkdir(exist_ok=True)

    if not html_dir.exists():
        print("html/ directory not found.")
        print("Please run download script first to download the journal files.")
        return

    # Get all HTML files in the html directory
    html_files = list(html_dir.glob('*.html'))

    # Filter out main index files and any other non-journal files
    exclude_files = ['ap12fj_index.html', 'a12_original_main.html', 'flight_journal_links.txt', 'surface_journal_links.txt']
    html_files = [f for f in html_files if f.name not in exclude_files]

    if not html_files:
        print("No HTML files found in html/ directory.")
        print("Please run download script first to download the journal files.")
        return

    print(f"Found {len(html_files)} HTML files to process...\n")
    print(f"Reading HTML files from: {html_dir}/")
    print(f"Saving JSON files to: {json_dir}/\n")

    extracted = []
    for html_path in html_files:
        html_file = html_path.name
        print(f"Processing {html_file}...")
        content = extract_content_from_html(html_path)
        json_name = html_file.replace('.html', '.json')
        extracted.append((json_dir / json_name, content))

    consolidate_parenthetical_speakers([c for _, c in extracted])

    for json_path, content in extracted:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"  Created {json_path}")

    print("\nProcessing complete!")
    print(f"All JSON files saved to: {json_dir}/")

if __name__ == '__main__':
    process_journal_files()