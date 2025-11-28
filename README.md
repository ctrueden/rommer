# Rommer: Wrangle your ROMs

Rommer is a tool for managing collections of binary ROM files.

## Installation

Make sure you have Python 3.6+ and SQLite3 available.

```
git clone git://github.com/ctrueden/rommer
cd rommer
python setup.py install
```

As usual with Python programs, you probably want to be inside a
[virtual environment](https://docs.python.org/3/tutorial/venv.html)
before installing—or else install for the current user only via:
```
python setup.py install --user --prefix=
```

## Usage

1. Import DATs to the Rommer database:
   ```
   rommer import /path/to/my/dat-files
   ```

2. Scan your ROMs to generate a report on what matches:
   ```
   rommer report /path/to/my/rom-files
   ```

Use `rommer -h` for a list of available commands.
For help with a specific command, use e.g. `rommer import -h`.

Rommer's database is stored at `~/.config/rommer/rommer.db` by default.
You can set the `ROMMER_CONFIG` environment variable to override it.

## Why Rommer

There are a lot of similar great tools available already! So why Rommer?

My personal requirements for this kind of tool are:

1. Command-line driven
2. Cross-platform
3. Free and open source
4. Simple to install and use

Let's see what else is available:

|      Tool       | Cross-platform | Open source | Command line |
|:---------------:|:--------------:|:-----------:|:------------:|
| [Clrmamepro][1] |       ❌       |     ❌      |      ❌      |
|  [Romcenter][2] |       ❌       |     ❌      |      ❌      |
|    [Romulus][3] |       ❌       |     ❌      |      ❌      |
|   [RomVault][4] |       ❌       |     ✅      |      ❌      |
| [SabreTools][5] |       ➖       |     ➖      |      ❌      |
|      [ROMba][6] |       ✅       |     ✅      |      ➖      |

[1]: https://mamedev.emulab.it/clrmamepro/ "Romcenter"
[2]: https://www.romcenter.com/ "Romcenter"
[3]: https://romulus.cc/ "Romulus"
[4]: https://github.com/RomVault/RVWorld "RomVault"
[5]: https://github.com/SabreTools/SabreTools "SabreTools"
[6]: https://github.com/uwedeportivo/romba "ROMba"

Of these, ROMba comes closest to meeting my needs. But:

- Installation is complex.
- It imposes a specific storage mechanism for managed ROMs.
- The "command line" functionality is actually a web shell.
- I don't want my ROM management tool running as a server.

So I wrote my own thing. Maybe it helps someone else too?
