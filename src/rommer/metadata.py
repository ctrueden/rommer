"""
Metadata extraction patterns for ROM titles.

This module provides comprehensive regex patterns for extracting metadata from
ROM filenames and DAT entries. Patterns are adapted from the retool project:
https://github.com/unexpectedpanda/retool

The patterns handle various naming conventions from No-Intro, Redump, TOSEC, and
other ROM preservation groups.
"""

import re
from re import Pattern


class RegexPatterns:
    """
    Compiled regular expression patterns for ROM metadata extraction.

    All patterns are precompiled for performance. The patterns match
    standardized tags commonly found in ROM filenames, particularly those
    following No-Intro and Redump naming conventions.
    """

    def __init__(self):
        """Initialize all regex patterns."""

        # === REGIONS ===
        # Common region tags: (USA), (Europe), (Japan), etc.
        # Build a comprehensive region pattern from common regions
        self.regions: tuple[str, ...] = (
            'Argentina',
            'Asia',
            'Australia',
            'Austria',
            'Belgium',
            'Brazil',
            'Canada',
            'China',
            'Croatia',
            'Czech',
            'Denmark',
            'Europe',
            'Finland',
            'France',
            'Germany',
            'Greece',
            'Hong Kong',
            'Hungary',
            'India',
            'Ireland',
            'Israel',
            'Italy',
            'Japan',
            'Korea',
            'Latin America',
            'Mexico',
            'Netherlands',
            'New Zealand',
            'Norway',
            'Poland',
            'Portugal',
            'Russia',
            'Scandinavia',
            'Singapore',
            'Slovakia',
            'South Africa',
            'Spain',
            'Sweden',
            'Switzerland',
            'Taiwan',
            'Turkey',
            'UK',
            'Ukraine',
            'Unknown',
            'USA',
            'World',
        )

        # Create regex pattern for regions
        region_str = '|'.join(self.regions)
        self.region_pattern: Pattern[str] = re.compile(
            f'\\(({region_str})(?:, ?({region_str}))*\\)'
        )

        # === LANGUAGES ===
        # Language codes: (En), (Fr), (De), (En,Fr), etc.
        self.languages: tuple[str, ...] = (
            'Ar',  # Arabic
            'Bg',  # Bulgarian
            'Ca',  # Catalan
            'Cs',  # Czech
            'Da',  # Danish
            'De',  # German
            'El',  # Greek
            'En',  # English
            'Es',  # Spanish
            'Fi',  # Finnish
            'Fr',  # French
            'Ga',  # Irish
            'He',  # Hebrew
            'Hi',  # Hindi
            'Hr',  # Croatian
            'Hu',  # Hungarian
            'Is',  # Icelandic
            'It',  # Italian
            'Ja',  # Japanese
            'Ko',  # Korean
            'Lt',  # Lithuanian
            'Lv',  # Latvian
            'Nl',  # Dutch
            'No',  # Norwegian
            'Pl',  # Polish
            'Pt',  # Portuguese
            'Ro',  # Romanian
            'Ru',  # Russian
            'Sk',  # Slovak
            'Sl',  # Slovenian
            'Sr',  # Serbian
            'Sv',  # Swedish
            'Th',  # Thai
            'Tr',  # Turkish
            'Uk',  # Ukrainian
            'Zh',  # Chinese
        )

        lang_str = '|'.join(self.languages)
        self.language_pattern: Pattern[str] = re.compile(
            f'\\((({lang_str})(?:,\\s?({lang_str}))*)\\)'
        )

        # === PREPRODUCTION STATUS ===
        self.alpha: Pattern[str] = re.compile(r'\((?:\w*?\s)*Alpha(?:\s\d+)?\)', flags=re.I)
        self.beta: Pattern[str] = re.compile(r'\((?:\w*?\s)*Beta(?:\s\d+)?\)', flags=re.I)
        self.proto: Pattern[str] = re.compile(
            r'\((?:\w*?\s)*Proto(?:type)?(?:\s\d+)?\)', flags=re.I
        )
        self.preprod: Pattern[str] = re.compile(r'\((?:Pre-production|Prerelease)\)', flags=re.I)
        self.dev: Pattern[str] = re.compile(r'\((?:DEV|DEBUG|Debug Build)\)', flags=re.I)
        self.preproduction: tuple[Pattern[str], ...] = (
            self.alpha,
            self.beta,
            self.proto,
            self.preprod,
            self.dev,
        )

        # === VERSIONS AND REVISIONS ===
        self.version: Pattern[str] = re.compile(r'\(v[\.\d].*?\)', flags=re.I)
        self.long_version: Pattern[str] = re.compile(
            r'\s?(?!Version Vol\.|Version \(|Version$|Version -|Version \d-)'
            r'(?: - )?\(?(?:\((?:\w[\.\-]?\s*)*|)'
            r'(?:[Vv]ers(?:ion|ao)|[Vv]er\.)\s(?:[\d]+[\.\-a-zA-Z]*\)?|\s?[A-Za-z](?:$|\s|\)))+|\s[Vv]\(?(?:[\dv]+[\.\-]*)+[A-Za-z]*?\)?'
        )
        self.revision: Pattern[str] = re.compile(r'\(R[eE][vV](?:[ -][0-9A-Z].*?)?\)', flags=re.I)
        self.build: Pattern[str] = re.compile(r'\(Build [0-9].*?\)', flags=re.I)

        # === CONSOLE-SPECIFIC PRODUCT CODES ===
        # PlayStation product codes
        self.ps1_2_id: Pattern[str] = re.compile(r'\([LSPT][ABCDEILRSTU][ACEKPTUXZ][ACDHJLMNSX]-\d{5}\)')
        self.ps3_id: Pattern[str] = re.compile(r'\([XBM][CLR][AEJKTU][BCDMSTVXZ]-\d{5}\)')
        self.ps3_digital_id: Pattern[str] = re.compile(r'\([N][P][EHIJKMNOPQUVWX][A-Z]-\d{5}\)')
        self.ps4_id: Pattern[str] = re.compile(r'\([CP][CLU][ACJKS][ABMSZ]-\d{5}\)')
        self.ps5_id: Pattern[str] = re.compile(r'\([EP][CLP][AJS][AMS]-\d{5}\)')
        self.psp_id: Pattern[str] = re.compile(r'\(U[CLMT][ADEJKUS][BDMPSTX]-\d{5}\)')
        self.ps_vita_id: Pattern[str] = re.compile(r'\([PV][CLS][CAJKS][ABCDEFGHIMSX]-\d{5}\)')
        self.ps_firmware: Pattern[str] = re.compile(r'\(FW[0-9].*?\)', flags=re.I)

        # Nintendo product codes
        self.nintendo_mastering_code: Pattern[str] = re.compile(
            r'\((?:(?:A[BDEFHLNPSXY]|B[58DFJLNPRT]|C[BX]|FT|JE|K[ADFIKMRXZ]|LB|PN|QA|RC|S[KN]|T[ABCJQ]|V[BEJKLMVW]|Y[XW])[A-Z0-9][ADEJPVXYZ])\)'
        )
        self.nintendo_3ds_product_code: Pattern[str] = re.compile(
            r'\(?:[CT][TW][LR]-[NP]-[AK][7E]A[EV]\)'
        )

        # Sega product codes
        self.sega_panasonic_ring_code: Pattern[str] = re.compile(
            r'\((?:(?:[0-9]{1,2}[ABCMRS][0-9]?,? ?)+[B0-9]*?|R[E]?[-]?[0-9]*)\)'
        )
        self.sega_ringedge_serial: Pattern[str] = re.compile(r'\(DVR-\d{4,4}\)')

        # Other console codes
        self.dreamcast_version: Pattern[str] = re.compile(r'V[0-9]{2,2} L[0-9]{2,2}')
        self.famicom_disk_system_version: Pattern[str] = re.compile(r'\(DV [0-9].*?\)', flags=re.I)
        self.hyperscan_version: Pattern[str] = re.compile(r'\(USE[0-9]\)')
        self.nec_mastering_code: Pattern[str] = re.compile(r'\((?:(?:F|S)A[A-F][ABTS](?:, )?)+\)')

        # === VIDEO STANDARDS ===
        self.ntsc: Pattern[str] = re.compile(r'(?:-)?\s?\(?\bNTSC\b\)?', flags=re.I)
        self.pal: Pattern[str] = re.compile(r'(?:-)?\s?\(?\bPAL\b(?:\s[a-zA-Z]+|\s50[Hh]z)?\)?', flags=re.I)
        self.pal_60: Pattern[str] = re.compile(r'\(PAL 60[Hh]z\)')
        self.mpal: Pattern[str] = re.compile(r'(?:-)?\s?\(?\bMPAL\b\)?', flags=re.I)
        self.secam: Pattern[str] = re.compile(r'(?:-)?\s?\(?\bSECAM\b\)?', flags=re.I)

        # === DUMP STATUS ===
        self.bad_dump: Pattern[str] = re.compile(r'\[b\]', flags=re.I)
        self.verified: Pattern[str] = re.compile(r'\[!\]')
        self.good_dump: Pattern[str] = re.compile(r'\[a\]', flags=re.I)
        self.overdump: Pattern[str] = re.compile(r'\[o\]', flags=re.I)

        # === CATEGORIES ===
        self.bios: Pattern[str] = re.compile(r'\[BIOS\]|\(Enhancement Chip\)', flags=re.I)
        self.demo: Pattern[str] = re.compile(
            r'\((?:\w[-.]?\s*)*Demo(?:(?:,?\s|-)?[\w0-9\.]*)*\)|'
            r'\b(?:Taikenban|Cheheompan|Trial|Sample|Kiosk)\b',
            flags=re.I
        )
        self.sample: Pattern[str] = re.compile(r'\(Sample(?:\s[0-9]*|\s\d{4}-\d{2}-\d{2})?\)', flags=re.I)
        self.aftermarket: Pattern[str] = re.compile(r'\(Aftermarket\)', flags=re.I)
        self.pirate: Pattern[str] = re.compile(r'\(Pirate\)', flags=re.I)
        self.unlicensed: Pattern[str] = re.compile(r'\(Unl\)', flags=re.I)
        self.promotional: Pattern[str] = re.compile(r'EPK|Press Kit|\(Promo\)', flags=re.I)
        self.covermount: Pattern[str] = re.compile(r'\(Covermount\)', flags=re.I)
        self.programs: Pattern[str] = re.compile(
            r'\((?:Test )?Program\)|(Check|Sample) Program', flags=re.I
        )
        self.manuals: Pattern[str] = re.compile(r'\(Manual\)', flags=re.I)
        self.multimedia: Pattern[str] = re.compile(r'\(Magazine\)', flags=re.I)
        self.video: Pattern[str] = re.compile(
            r'Game Boy Advance Video|'
            r'- (?:Preview|Movie) Trailer|'
            r'\((?:\w*\s)*Trailer(?:s|\sDisc)?(?:\s\w*)*\)|'
            r'\((?:E3.*)?Video\)',
            flags=re.I
        )

        # === EDITIONS ===
        self.not_for_resale: Pattern[str] = re.compile(r'\((?:Hibaihin|Not for Resale)\)', flags=re.I)
        self.oem: Pattern[str] = re.compile(r'\((?:\w-?\s*)*?OEM\)', flags=re.I)
        self.rerelease: Pattern[str] = re.compile(r'\(Rerelease\)', flags=re.I)

        # === DISC INFORMATION ===
        self.disc: Pattern[str] = re.compile(
            r'\(Dis[ck|que]?\s*\d+(?:\s*of\s*\d+)?\)',
            flags=re.I
        )
        self.side: Pattern[str] = re.compile(r'\(Side [AB](?:\d+)?\)', flags=re.I)

        # === ALTERNATE VERSIONS ===
        self.alt: Pattern[str] = re.compile(r'\(Alt.*?\)', flags=re.I)

        # === DATE PATTERNS ===
        self.dates: tuple[Pattern[str], ...] = (
            re.compile(r'\(\d{8}\)'),
            re.compile(r'\(\d{4}-\d{2}-\d{2}\)'),
            re.compile(r'\(\d{2}-\d{2}-\d{4}\)'),
            re.compile(r'\(\d{2}-\d{2}-\d{2}\)'),
            re.compile(r'\(\d{4}-\d{2}-\d{2}T\d{6}\)'),
            re.compile(r'\((\d{4}-\d{2})-xx\)'),
            re.compile(r'\(~?(\d{4})-xx-xx\)'),
            re.compile(
                r'\((January|February|March|April|May|June|July|August|September|October|November|December),\s?\d{4}\)',
                flags=re.I,
            ),
        )

    def __getitem__(self, key: str):
        """Allow dictionary-style access to patterns."""
        return getattr(self, key)
