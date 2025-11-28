# DAT Update Feature Design

## Overview

This document outlines the design for `rommer update`, a command to automatically download DAT files from various online sources.

## Command Interface

### Basic Usage

```bash
# Update all configured sources
rommer update

# Update specific sources
rommer update --source tosec --source no-intro

# Update and auto-import
rommer update --import

# List available sources
rommer update --list-sources

# Dry run (show what would be downloaded)
rommer update --dry-run
```

## Supported Sources

### 1. OpenGood (EASIEST TO IMPLEMENT FIRST)

**Source:** https://github.com/SnowflakePowered/opengood

**Why start here:**
- Simple GitHub releases, easy to download
- Already have local copy at `../opengood/`
- Standard Logiqx XML format (100% compatible)
- 35 platforms, ~1.4M lines of DAT data
- No authentication required
- Historical reference (April 2016 snapshot)

**Value:**
- Matches older ROM dumps not in No-Intro/TOSEC
- GoodTools naming conventions still widely used
- Complete coverage of classic cartridge systems

**Download method:**
```bash
# Clone or pull from GitHub
git clone https://github.com/SnowflakePowered/opengood.git
# or: git pull (if already exists)

# DATs are in: opengood/dats/*.dat
# 48 DAT files total (including split variants)
```

**Storage:**
```
~/.local/share/rommer/dats/
└── opengood/
    ├── Open2600.dat
    ├── OpenNES.dat
    ├── OpenSNES.dat
    └── ... (45 more)
```

### 2. TOSEC

**Source:** https://www.tosecdev.org/downloads

**Current implementation:** `update-datfiles.sh` (lines 20-48)
- Scrapes download page HTML (fragile)
- Downloads latest zip archive
- Extracts to `dats/TOSEC/`

**Challenges:**
- No stable API
- HTML scraping required
- Large downloads (hundreds of MB)
- Complex directory structure

**Recommendation:**
- Keep using shell script approach initially
- Consider TOSEC API if one becomes available
- May need to handle incremental updates

### 3. No-Intro

**Source (official):** https://datomatic.no-intro.org/

**Current implementation:** `update-datfiles.sh` (lines 50-68)
- Downloads from RomCenter mirror (outdated)
- 7z archive extraction required

**Better approach:**
- Use No-Intro daily P2P downloads (torrents available)
- Or direct HTTP downloads if available
- Check https://datomatic.no-intro.org/index.php?page=download

**Value:**
- Most authoritative for cartridge ROMs
- Covers 50+ platforms
- Actively maintained (daily updates)

### 4. Redump

**Source:** http://redump.org/downloads/

**Challenges:**
- Requires free account registration
- Need to store credentials securely
- Disc-based systems (PSX, PS2, GameCube, etc.)

**Implementation notes:**
- Use keyring library for credential storage
- Or read from config file with warning about security
- Check for cookies/session management

**Value:**
- Most authoritative for disc-based systems
- You already have 17 redump DATs locally

### 5. MAME

**Source:** https://www.mamedev.org/release.html

**Advantages:**
- Stable download URLs
- Official XML DAT files
- Updated monthly with each release

**Download pattern:**
```
https://github.com/mamedev/mame/releases/latest/download/mame0XXXlx.zip
# Extract XML from archive
```

**Value:**
- Arcade ROM preservation
- Well-documented format

### 6. FBNeo (Lower priority)

**Source:** https://github.com/libretro/FBNeo

**Value:**
- Alternative arcade database
- Complements MAME

### 7. Libretro DATs (Lower priority)

**Source:** https://github.com/libretro/libretro-database

**Value:**
- RetroArch ecosystem integration
- Alternative to No-Intro/TOSEC for some systems

## Storage Structure

```
~/.local/share/rommer/
└── dats/
    ├── opengood/          # GitHub repo or extracted DATs
    │   ├── Open2600.dat
    │   ├── OpenNES.dat
    │   └── ...
    ├── tosec/
    │   └── TOSEC-v2024-12-01/
    │       └── [hundreds of DAT files]
    ├── no-intro/
    │   ├── Nintendo - Nintendo Entertainment System (Headered).dat
    │   └── ...
    ├── redump/
    │   ├── Sony - PlayStation.dat
    │   └── ...
    └── mame/
        └── mame0261.xml
```

## Implementation Plan

### Phase 1: OpenGood (Minimal Viable Implementation)

```python
# src/rommer/sources/opengood.py

def update(data_dir, dry_run=False):
    """Download/update OpenGood DATs from GitHub."""
    import subprocess

    target = data_dir / "opengood"

    if target.exists():
        # Update existing repo
        if not dry_run:
            subprocess.run(["git", "pull"], cwd=target)
    else:
        # Clone repo
        if not dry_run:
            subprocess.run([
                "git", "clone",
                "https://github.com/SnowflakePowered/opengood.git",
                str(target)
            ])

    # Return list of DAT files
    return list((target / "dats").glob("*.dat"))
```

**Why start here:**
- Single git command
- No authentication needed
- Fast download (~10MB repo)
- Immediate value for historical ROM matching

### Phase 2: MAME

- Download latest release from GitHub
- Extract XML DAT file
- Simple, stable URLs

### Phase 3: No-Intro

- Investigate daily download mechanism
- Implement torrent or HTTP download
- Handle individual DAT files vs. archives

### Phase 4: TOSEC

- Refactor `update-datfiles.sh` logic into Python
- Consider caching/version tracking to avoid redundant downloads

### Phase 5: Redump (requires authentication)

- Implement credential management
- Session handling for downloads

## Database Schema Addition

Add version tracking table to avoid redundant downloads:

```python
class DatSource(Base):
    """Track DAT source metadata and versions."""
    __tablename__ = "dat_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String)  # "opengood", "tosec", "no-intro", etc.
    version = Column(String)  # Version or commit hash
    last_updated = Column(Integer)  # Unix timestamp
    url = Column(String)  # Source URL
```

## Configuration File

`~/.config/rommer/sources.conf` (TOML format):

```toml
[sources.opengood]
enabled = true
auto_import = true

[sources.tosec]
enabled = true
auto_import = false  # Too large, import selectively

[sources.no-intro]
enabled = true
auto_import = true

[sources.redump]
enabled = false  # Requires authentication
username = ""
password = ""  # Or use keyring

[sources.mame]
enabled = false  # Arcade-focused, opt-in
```

## Progress Reporting

Use `tqdm` (already imported in report.py):

```python
from tqdm import tqdm

for source in tqdm(sources, desc="Updating DAT sources"):
    source.update(...)
```

## Error Handling

- One source failure should not stop others
- Log errors but continue
- Report summary at end:
  ```
  Updated: opengood, mame
  Failed: tosec (connection timeout)
  Skipped: redump (not configured)
  ```

## Integration with Import

When `--import` flag is used:

```python
if args.do_import:
    from rommer.commands import import as import_cmd

    for dat_file in downloaded_dats:
        import_args = argparse.Namespace(path=[dat_file], verbose=args.verbose)
        import_cmd.run(import_args)
```

## Testing Strategy

1. **Unit tests:** Mock HTTP/git operations
2. **Integration tests:** Test with small sample DATs
3. **Manual testing:** Verify each source downloads correctly

## Recommended Implementation Order

1. **OpenGood** - Easiest, immediate value
2. **MAME** - Simple, stable URLs
3. **No-Intro** - High value, moderate complexity
4. **TOSEC** - High complexity (HTML scraping)
5. **Redump** - Authentication required

## Questions to Resolve

1. Should we vendor `../opengood/` into the rommer repo, or always fetch from GitHub?
2. Shallow git clone for OpenGood to save bandwidth?
3. How to handle TOSEC's huge directory tree? (Selective import?)
4. P2P/torrent support for No-Intro daily downloads?
