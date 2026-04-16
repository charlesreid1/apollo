# Apollo Mission Journals Archive

A project for downloading, processing, and analyzing Apollo mission journals from the
[Apollo Lunar Surface Journal (ALSJ) website](https://www.nasa.gov/history/alsj-and-afj/).

## Overview

This project archives and processes the complete set of Apollo mission journals (Apollo 7 through Apollo 17) from the official Apollo Lunar Surface Journal website. Each mission's journals are downloaded as HTML files, processed to extract and clean content, and organized for analysis.

## Project Structure

```
apollo/
├── Makefile              # Automation for processing all missions
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── apollo7/              # Apollo 7 mission data
│   ├── download_journals.py
│   ├── process_journals.py
│   └── requirements.txt
├── apollo8/              # Apollo 8 mission data
│   ├── download_journals.py
│   ├── process_journals.py
│   └── requirements.txt
├── apollo9/              # Apollo 9 mission data
│   ├── download_journals.py
│   ├── process_journals.py
│   └── requirements.txt
├── apollo10/             # Apollo 10 mission data
│   ├── download_journals.py
│   ├── process_journals.py
│   └── requirements.txt
├── apollo11/             # Apollo 11 mission data
│   ├── download_journals.py
│   ├── process_journals.py
│   └── requirements.txt
├── apollo12/             # Apollo 12 mission data
│   ├── download_journals.py
│   ├── process_journals.py
│   └── requirements.txt
├── apollo13/             # Apollo 13 mission data
│   └── ...
├── ...                   # Apollo 14-17 directories
└── vp/                   # Virtual environment (optional)
```

## Features

- **Complete Archive**: Downloads all Apollo mission journals (7-17)
- **Automated Processing**: Makefile automates download and processing for all missions
- **Content Extraction**: Cleans HTML and extracts journal content
- **Organized Output**: Generates structured JSON/JavaScript files for analysis
- **Flexible Usage**: Process individual missions or all missions at once

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`:
  - `requests>=2.31.0`
  - `beautifulsoup4>=4.12.0`
  - `nltk>=3.8.0`
  - `lxml>=4.9.0`

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd apollo
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv vp
   source vp/bin/activate  # On Windows: vp\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

### Using the Makefile (Recommended)

The Makefile provides convenient commands for processing all missions:

```bash
# Process all Apollo missions (7-17)
make all

# Process a specific mission
make apollo7
make apollo8
make apollo9
make apollo10
make apollo11
make apollo12
# ... etc for apollo13, apollo14, apollo15, apollo16, apollo17

# Clean up generated files (html/ and json/ directories)
make clean

# Show available commands
make help
```

### Manual Processing

You can also run scripts directly in each mission directory:

```bash
# Navigate to a mission directory
cd apollo11

# Download the journals
python download_journals.py

# Process the downloaded journals
python process_journal.py
```

## What Each Script Does

### `download_journals.py`
- Downloads HTML journal pages from the Apollo Lunar Surface Journal website
- Saves raw HTML files to the `html/` subdirectory
- Handles different URL structures for each mission
- Includes error handling and rate limiting

### `process_journal.py` / `process_journals.py`
- Parses downloaded HTML files using BeautifulSoup
- Extracts and cleans journal content (text, timestamps, speaker labels)
- Converts content to structured formats (JSON, JavaScript)
- Saves processed files to the `json/` subdirectory

## Transcript Parsing and Speakers

Each processed entry is tagged with a `speaker`, a mission-elapsed `time` (e.g. `055:48:40`, negative for pre-launch), and sentence-split `tokens`. The parsers handle a few HTML dialects found across the journals:

- **Apollo Flight Journal (AFJ)**: `<div class="cc">` blocks with a `<b>HH:MM:SS Name:</b>` header, plus classless `<div>`s that follow the same header pattern (used for crew dialogue in several missions).
- **Lunar Surface Journal (LSJ)**: bare `<b>HH:MM:SS</b>` timestamps followed by sibling text `Name: ...`, and a hybrid variant where the speaker lives inside the same bold tag.
- **Commentary / PAO**: narrative blocks attributed to `Commentary` or `PAO` rather than a named crew member.

Speakers with parenthetical suffixes like `Mattingly (continued)` or `Scott (onboard)` are consolidated to the base name when that base name also appears elsewhere in the same mission, so downstream consumers see a single `Mattingly` rather than several variants.

## Generated Files

After running the scripts, each mission directory will contain:

- `html/` - Raw HTML files downloaded from the source
- `json/` - Processed JavaScript/JSON files ready for analysis
  - Typically includes files like `journal_data.js` or similar containing structured journal data

## Data Sources

All journals are sourced from the [Apollo Lunar Surface Journal (ALSJ)](https://apollojournals.org/alsj/), which provides:
- Transcripts of mission communications
- Technical commentary and explanations
- Photographs and multimedia references
- Historical context and analysis

## Mission Coverage

- **Apollo 7**: First crewed Apollo mission, Earth orbital test (Wally Schirra, Donn Eisele, Walter Cunningham)
- **Apollo 8**: First crewed mission to orbit the Moon (Frank Borman, James Lovell, William Anders)
- **Apollo 9**: First test of Lunar Module in Earth orbit (James McDivitt, David Scott, Rusty Schweickart)
- **Apollo 10**: "Dress rehearsal" for lunar landing, Lunar Module tested in lunar orbit (Thomas Stafford, John Young, Eugene Cernan)
- **Apollo 11**: First lunar landing (Neil Armstrong, Buzz Aldrin)
- **Apollo 12**: Precision landing near Surveyor 3 (Pete Conrad, Alan Bean)
- **Apollo 13**: "Successful failure" - aborted lunar landing (Jim Lovell, Fred Haise, Jack Swigert)
- **Apollo 14**: Return to the Moon after Apollo 13 (Alan Shepard, Edgar Mitchell)
- **Apollo 15**: First extended lunar mission with Lunar Rover (David Scott, James Irwin)
- **Apollo 16**: Highlands exploration (John Young, Charles Duke)
- **Apollo 17**: Final Apollo lunar mission (Eugene Cernan, Harrison Schmitt)

## License

This project is for educational and research purposes. The journal content is sourced from the Apollo Lunar Surface Journal, which is maintained by NASA and other space agencies. Please respect copyright and usage terms of the original sources.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Acknowledgments

- NASA and the Apollo Lunar Surface Journal team for preserving and making available these historical records
- The astronauts, engineers, and support personnel who made the Apollo missions possible
- The open source community for the tools used in this project

## Contact

For questions or issues, please open an issue in the project repository.
