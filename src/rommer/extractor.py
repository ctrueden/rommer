"""
Metadata extraction from ROM titles.

This module provides the MetadataExtractor class which uses regex patterns
to extract structured metadata from ROM filenames and DAT entries.
"""

import re
from typing import Optional

from rommer.metadata import RegexPatterns


class MetadataExtractor:
    """
    Extracts structured metadata from ROM title strings.

    This class uses comprehensive regex patterns to parse ROM filenames
    and extract information such as regions, languages, versions, dump
    status, and more.
    """

    def __init__(self, patterns: Optional[RegexPatterns] = None):
        """
        Initialize the metadata extractor.

        Args:
            patterns: RegexPatterns instance. If None, creates a new instance.
        """
        self.patterns = patterns if patterns is not None else RegexPatterns()

    def extract_metadata(self, title: str) -> dict:
        """
        Extract all available metadata from a ROM title string.

        Args:
            title: The ROM title string to parse.

        Returns:
            Dictionary containing extracted metadata fields:
                - regions: List of region strings (e.g., ['USA', 'Europe'])
                - primary_region: First/main region
                - languages: List of language codes (e.g., ['En', 'Fr'])
                - version: Version string (e.g., 'v1.2')
                - revision: Revision string (e.g., 'Rev 1')
                - status: Production status (e.g., 'Alpha', 'Beta', 'Production')
                - dump_status: Dump quality (e.g., 'verified', 'bad', 'good')
                - video_standard: Video format (e.g., 'NTSC', 'PAL')
                - category: ROM category (e.g., 'Games', 'Demo', 'BIOS')
                - product_code: Console-specific ID
                - disc_info: Disc/side information
                - edition: Edition type (e.g., 'OEM', 'Not for Resale')
                - date: Release date if present
                - short_name: Normalized short name
                - group_name: Name for grouping variants
                - region_free_name: Title without region tags
        """
        return {
            'regions': self._extract_regions(title),
            'primary_region': self._get_primary_region(title),
            'languages': self._extract_languages(title),
            'version': self._extract_version(title),
            'revision': self._extract_revision(title),
            'status': self._extract_status(title),
            'dump_status': self._extract_dump_status(title),
            'video_standard': self._extract_video_standard(title),
            'category': self._extract_category(title),
            'product_code': self._extract_product_code(title),
            'disc_info': self._extract_disc_info(title),
            'edition': self._extract_edition(title),
            'date': self._extract_date(title),
            'short_name': self._generate_short_name(title),
            'group_name': self._generate_group_name(title),
            'region_free_name': self._generate_region_free_name(title),
        }

    def _extract_regions(self, title: str) -> list[str]:
        """Extract all regions from the title."""
        match = self.patterns.region_pattern.search(title)
        if match:
            # Extract all captured region groups
            regions = [g for g in match.groups() if g is not None]
            return regions
        return []

    def _get_primary_region(self, title: str) -> Optional[str]:
        """Get the first/primary region."""
        regions = self._extract_regions(title)
        return regions[0] if regions else None

    def _extract_languages(self, title: str) -> list[str]:
        """Extract language codes from the title."""
        match = self.patterns.language_pattern.search(title)
        if match:
            # Get the full language string and split by comma
            lang_str = match.group(1)
            return [lang.strip() for lang in lang_str.split(',')]
        return []

    def _extract_version(self, title: str) -> Optional[str]:
        """Extract version information."""
        # Try standard version pattern first
        match = self.patterns.version.search(title)
        if match:
            return match.group(0).strip('()')

        # Try long version pattern
        match = self.patterns.long_version.search(title)
        if match:
            return match.group(0).strip()

        return None

    def _extract_revision(self, title: str) -> Optional[str]:
        """Extract revision information."""
        match = self.patterns.revision.search(title)
        if match:
            return match.group(0).strip('()')

        # Check for build number
        match = self.patterns.build.search(title)
        if match:
            return match.group(0).strip('()')

        return None

    def _extract_status(self, title: str) -> str:
        """Determine the production status."""
        if self.patterns.alpha.search(title):
            return 'Alpha'
        elif self.patterns.beta.search(title):
            return 'Beta'
        elif self.patterns.proto.search(title):
            return 'Proto'
        elif self.patterns.preprod.search(title):
            return 'Pre-production'
        elif self.patterns.dev.search(title):
            return 'Dev'
        else:
            return 'Production'

    def _extract_dump_status(self, title: str) -> Optional[str]:
        """Determine the dump quality status."""
        if self.patterns.verified.search(title):
            return 'verified'
        elif self.patterns.bad_dump.search(title):
            return 'bad'
        elif self.patterns.good_dump.search(title):
            return 'good'
        elif self.patterns.overdump.search(title):
            return 'overdump'
        return None

    def _extract_video_standard(self, title: str) -> Optional[str]:
        """Extract video standard information."""
        if self.patterns.pal_60.search(title):
            return 'PAL 60Hz'
        elif self.patterns.pal.search(title):
            return 'PAL'
        elif self.patterns.ntsc.search(title):
            return 'NTSC'
        elif self.patterns.mpal.search(title):
            return 'MPAL'
        elif self.patterns.secam.search(title):
            return 'SECAM'
        return None

    def _extract_category(self, title: str) -> str:
        """Determine the ROM category."""
        if self.patterns.bios.search(title):
            return 'BIOS'
        elif self.patterns.demo.search(title) or self.patterns.sample.search(title):
            return 'Demo'
        elif self.patterns.programs.search(title):
            return 'Program'
        elif self.patterns.video.search(title):
            return 'Video'
        elif self.patterns.multimedia.search(title):
            return 'Multimedia'
        elif self.patterns.manuals.search(title):
            return 'Manual'
        elif self.patterns.promotional.search(title):
            return 'Promotional'
        else:
            return 'Games'

    def _extract_product_code(self, title: str) -> Optional[str]:
        """Extract console-specific product codes."""
        # PlayStation codes
        for pattern in [
            self.patterns.ps1_2_id,
            self.patterns.ps3_id,
            self.patterns.ps3_digital_id,
            self.patterns.ps4_id,
            self.patterns.ps5_id,
            self.patterns.psp_id,
            self.patterns.ps_vita_id,
        ]:
            match = pattern.search(title)
            if match:
                return match.group(0).strip('()')

        # Nintendo codes
        for pattern in [
            self.patterns.nintendo_mastering_code,
            self.patterns.nintendo_3ds_product_code,
        ]:
            match = pattern.search(title)
            if match:
                return match.group(0).strip('()')

        # Sega codes
        for pattern in [
            self.patterns.sega_panasonic_ring_code,
            self.patterns.sega_ringedge_serial,
        ]:
            match = pattern.search(title)
            if match:
                return match.group(0).strip('()')

        # Other console codes
        for pattern in [
            self.patterns.nec_mastering_code,
            self.patterns.dreamcast_version,
        ]:
            match = pattern.search(title)
            if match:
                return match.group(0).strip('()')

        return None

    def _extract_disc_info(self, title: str) -> Optional[str]:
        """Extract disc/side information."""
        match = self.patterns.disc.search(title)
        if match:
            return match.group(0).strip('()')

        match = self.patterns.side.search(title)
        if match:
            return match.group(0).strip('()')

        return None

    def _extract_edition(self, title: str) -> Optional[str]:
        """Extract edition type information."""
        if self.patterns.not_for_resale.search(title):
            return 'Not for Resale'
        elif self.patterns.oem.search(title):
            return 'OEM'
        elif self.patterns.rerelease.search(title):
            return 'Rerelease'
        elif self.patterns.aftermarket.search(title):
            return 'Aftermarket'
        return None

    def _extract_date(self, title: str) -> Optional[str]:
        """Extract release date if present."""
        for pattern in self.patterns.dates:
            match = pattern.search(title)
            if match:
                return match.group(0).strip('()')
        return None

    def _generate_short_name(self, title: str) -> str:
        """
        Generate a normalized short name for matching.

        Removes regions, languages, versions, and other variant info,
        but keeps disc/side information for multi-disc games.
        """
        name = title

        # Remove region tags
        name = self.patterns.region_pattern.sub('', name)

        # Remove language tags
        name = self.patterns.language_pattern.sub('', name)

        # Remove version/revision
        name = self.patterns.version.sub('', name)
        name = self.patterns.long_version.sub('', name)
        name = self.patterns.revision.sub('', name)
        name = self.patterns.build.sub('', name)

        # Remove video standards
        name = self.patterns.ntsc.sub('', name)
        name = self.patterns.pal.sub('', name)
        name = self.patterns.mpal.sub('', name)
        name = self.patterns.secam.sub('', name)

        # Remove dump status
        name = self.patterns.verified.sub('', name)
        name = self.patterns.bad_dump.sub('', name)
        name = self.patterns.good_dump.sub('', name)

        # Remove product codes
        for pattern in [
            self.patterns.ps1_2_id,
            self.patterns.ps3_id,
            self.patterns.ps4_id,
            self.patterns.ps5_id,
            self.patterns.psp_id,
        ]:
            name = pattern.sub('', name)

        # Clean up whitespace and normalize
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'\s*\(\s*\)', '', name)  # Remove empty parentheses

        return name.lower()

    def _generate_group_name(self, title: str) -> str:
        """
        Generate a group name for identifying all variants of a game.

        This removes disc/side information in addition to what short_name removes,
        so all discs of a multi-disc game are grouped together.
        """
        name = self._generate_short_name(title)

        # Remove disc/side information
        name = self.patterns.disc.sub('', name)
        name = self.patterns.side.sub('', name)

        # Remove alternate markers
        name = self.patterns.alt.sub('', name)

        # Clean up again
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'\s*\(\s*\)', '', name)

        return name

    def _generate_region_free_name(self, title: str) -> str:
        """
        Generate a name with regions removed but other tags intact.

        Useful for displaying titles without region clutter.
        """
        name = self.patterns.region_pattern.sub('', title)

        # Clean up whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'\s*\(\s*\)', '', name)

        return name
