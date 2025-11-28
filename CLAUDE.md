# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rommer is a command-line tool for managing collections of binary ROM files used in emulation. It maintains a SQLite database to track ROM checksums, DAT files, and match ROMs against known game databases.

**Key design principles:**
- Command-line driven with subcommand architecture
- Cross-platform (Python 3.6+)
- SQLite3 database for persistent storage
- DAT file parsing for game metadata (No-Intro, TOSEC, etc.)
- Checksum-based ROM validation (CRC32, MD5, SHA1)

## Project Management

This project uses **uv** for dependency management and task execution. All commands should be prefixed with `uv run`.

### Development Commands

**Setup:**
```bash
# Install uv if needed: https://docs.astral.sh/uv/getting-started/installation/
uv sync  # Install dependencies
```

**Code Quality:**
```bash
make lint          # Run formatters and linters (auto-fixes issues)
uv run ruff check  # Check for linting issues only
uv run ruff format # Format code only
uv run validate-pyproject pyproject.toml  # Validate project config
```

**Testing:**
```bash
make test                              # Run all tests
uv run python -m pytest -v            # Run pytest directly
uv run python -m pytest -v tests/test_foo.py  # Run specific test file
uv run python -m pytest -v tests/test_foo.py::test_bar  # Run specific test
```

**Running the Application:**
```bash
uv run rommer -h              # Show help
uv run rommer import <path>   # Import DAT files
uv run rommer report <path>   # Generate ROM matching report
uv run rommer diff <path>...  # Compare binary file similarity
```

**Build:**
```bash
make dist   # Generate release archives
make clean  # Remove build artifacts
```

## Architecture

### Database Schema

Rommer uses SQLAlchemy ORM with a SQLite database stored at `~/.config/rommer/rommer.db` (override with `ROMMER_CONFIG` environment variable).

**Core models (defined in `src/rommer/__init__.py`):**

- **File**: Tracks binary files with checksums and metadata
  - `path`, `mtime`, `size`, `crc`, `md5`, `sha1`
  - `calculate_checksums()` computes/updates checksums
  - `is_dirty()` checks if file has changed since last scan

- **Dat**: Represents a game database (e.g., No-Intro DAT file)
  - `name`, `description`, `version`, `date`, `author`, `url`
  - `file_id` references the DAT file itself
  - One-to-many relationship with Game

- **Game**: Represents a game entry within a DAT
  - `name`, `description`
  - `dat_id` foreign key to Dat
  - One-to-many relationship with Rom

- **Rom**: Known ROM metadata from DAT files
  - `name`, `size`, `crc`, `md5`, `sha1`
  - `game_id` foreign key to Game
  - Matched against File records for reporting

**Relationship hierarchy:** `Dat` → `Game` → `Rom`

### Command Architecture

Commands are auto-discovered plugins in `src/rommer/commands/`. Each command module must define:

- `blurb` (str): Short description for help listing
- `description` (str, optional): Longer description for subcommand help
- `configure(parser)`: Configure argparse subparser
- `run(args)`: Execute the command, return exit code

**Main entry point (`src/rommer/__main__.py`):**
- Uses `pkgutil.walk_packages()` to dynamically load command modules
- Creates argparse subparsers for each command
- Dispatches to appropriate command's `run()` function

### Current Commands

**`import`** (`src/rommer/commands/import.py`):
- Scans for `.dat` files (XML format)
- Parses DAT metadata and game/ROM entries using `xml.dom.minidom`
- Handles reimport of changed DATs (checks `File.is_dirty()`)
- Commits in batches of 10,000 rows to avoid large transactions

**`report`** (`src/rommer/commands/report.py`):
- Scans ROM files and computes checksums
- Matches ROMs against DAT database using 4-way join (sha1, md5, crc, size)
- Outputs percentage of matched ROMs per DAT
- Supports flags: `--have`, `--miss`, `--unmatched`

**`diff`** (`src/rommer/commands/diff.py`):
- Experimental binary similarity comparison
- Uses hierarchical hash aggregation of 24-bit byte triples
- Computes similarity percentage for all file pairs

## Key Patterns and Utilities

**File discovery (`find_files()` in `src/rommer/__init__.py`):**
- Accepts list of paths (files or directories)
- Recursively searches directories for matching suffix
- Returns list of `pathlib.Path` objects

**Database session (`session()` in `src/rommer/__init__.py`):**
- Global singleton pattern using `sessionmaker`
- Initializes database schema on first call
- Models are defined dynamically inside `session()` function (unusual pattern)

**Checksum calculation:**
- Files use `calculate_checksums()` which checks `is_dirty()` first
- Reads entire file into memory (may not scale for huge files)
- Computes CRC32 (zlib), MD5, and SHA1 in single pass

## Development Notes

- Database models (File, Dat, Game, Rom) are global variables set inside `session()`
- Import transactions commit every 10,000 rows or when complete
- Report command commits every ~10 seconds during file scanning
- DAT parsing assumes XML format with `<header>`, `<game>`/`<machine>`, and `<rom>` elements
- The `dl.py` module contains incomplete/commented code for future download features
