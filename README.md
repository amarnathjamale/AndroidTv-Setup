# AndroidTv-Setup

My setup for Android TV and Google TV boxes. It is built on
[CleanYourTV](https://github.com/Gathin23/cleanyourtv) by Gathin (MIT): the ads, telemetry and
preinstalled clutter are turned off over Wi-Fi or LAN, and a small Apple TV style launcher takes over the home screen. It needs no root, and nothing is uninstalled.

On top of CleanYourTV this repo adds:

- **The launcher in Marathi** (`launcher/app/src/main/res/values-mr/`): every label, menu and prompt, with
  Devanagari digits on the clock.
- **A Marathi calendar line** under the date, e.g. `आश्विन कृष्ण नवमी · शके १९४८`. It shows the tithi, paksha,
  amanta month (adhik months included) and Shaka year. The box computes it itself, with no network
  ([details](#the-marathi-calendar)).
- **The `marathi` theme** (`themes/marathi/`): a Sahyadri fort with its bastions and the bhagwa, drawn in
  code. There are four pictures, for dawn, dusk, a moonlit night and a Diwali night with akash kandils, and
  each shows at its time of day. During Diwali it also has a festive skin.
- **Remote app buttons on Home by scancode**, for firmware that never hands remote keys to accessibility
  helpers.
- **Per-device setups** in `setups/`: the debloat list, restore script and notes for each box I have
  set up.

![The marathi theme on a TV](themes/marathi/screenshot.jpg)

## Quick start

You need a computer on the same network as the TV, Python 3, and Docker or JDK 17 with Android SDK 34
for the launcher build.

1. **On the TV:**
   - Go to Settings > Device Preferences > About and press OK on **Build** seven times.
   - Go back to Developer options and turn on **USB debugging**, plus Network debugging if there is one.
2. **Tools:** `python3 -m venv tools/venv && tools/venv/bin/pip install -r tools/requirements.txt`, then
   `export TV_HOST=<tv ip>` and `tools/venv/bin/python -I tools/tv.py --probe`. Accept "Allow USB
   debugging?" on the TV.
3. **Back up**, then debloat with a list: one from `setups/`, one from upstream's `examples/`, or your own.
   Run `tools/disable.sh setups/skyworth-srt412/debloat.txt`. Undo it with `tools/restore.sh` and the same list.
4. **Launcher:** set your dock in `launcher/app/src/main/res/values/config.xml` (`dock_apps`). Then run
   `tools/docker-build.sh`, then `SKIP_BUILD=1 launcher/build-and-install.sh`.
5. **Theme:** `tools/theme.sh themes/marathi`. Remove it with `tools/theme.sh --reset`.
6. **Turn USB debugging off** when you are done. While it is on, port 5555 is a shell on the TV for anything on
   your network.

[PROMPT.md](PROMPT.md) is the full step-by-step procedure, written for a coding agent (Claude Code, Codex,
Gemini CLI) to follow on a real TV.

## The Marathi calendar

`launcher/app/src/main/java/com/gathin/tvhome/Panchang.java` follows the conventions of a Maharashtrian
panchang:

- **Tithi:** the one running at sunrise in Pune, so a day keeps one tithi wherever the TV is.
- **Month:** amanta (new moon to new moon). Each month is named by the sidereal sign the Sun is in at the new moon that starts
  it, with Lahiri ayanamsa. A month whose two new moons share a sign is adhik.
- **Year:** Shaka, which is the Gregorian year minus 78 from Gudi Padwa and minus 79 before it.

The Sun and Moon positions come from Jean Meeus' *Astronomical Algorithms*. Computed new moons match
published times to within about 2 minutes. The line follows the sunrise tithi, as printed calendars do, so
a festival kept by midday or afternoon can fall a day after it. Ganesh Chaturthi and Dussehra are examples.

It turns on when the launcher is in Marathi (`"locale": "mr"`) and `lunar_date` is on, which the `marathi`
theme does. In other languages, `lunar_date` keeps upstream's Chinese and Vietnamese lunar date.

## The `marathi` theme

| Key | Value |
|---|---|
| Wallpapers | `01-pahat` (dawn), `02-sandhyakal` (dusk), `03-ratra` and `04-diwali` (night), by `wallpaper_moods` |
| Language | `locale: mr`, 24-hour clock (`clock_format`), Marathi calendar line under the date |
| Diwali | `festival: diwali` until the date in `festival_until`; change it each year |

`themes/marathi/make_wallpapers.py` draws the pictures with Pillow and NumPy. They use no photos, artwork or
fonts, and are released under CC0. For the morning, evening and night moods to follow your sunrise and sunset, set
`latitude` and `longitude` in `config.xml`.

## What is where

| Path | What it is |
|---|---|
| `setups/` | One folder per box I have set up: debloat list, restore script, notes |
| `themes/marathi/` | The theme and its wallpaper script |
| `launcher/` | The launcher (package `com.gathin.tvhome`), with the Marathi strings and calendar |
| `tools/` | CleanYourTV's ADB client and scripts: `tv.py`, `disable.sh`, `restore.sh`, `check.py`, `theme.sh`, `docker-build.sh` |
| `addons/` | CleanYourTV's optional add-on apps, built and installed one at a time (weather, sleep timer and more) |
| `examples/` | CleanYourTV's tested debloat lists for more than 400 TV models |
| `docs/` | CleanYourTV's guides: [launcher](docs/launcher.md), [restore](docs/restore.md), [troubleshooting](docs/TROUBLESHOOTING.md) |

## Credits and licence

The base is [CleanYourTV](https://github.com/Gathin23/cleanyourtv), © 2026 Gathin, under the MIT licence
(see [LICENSE](LICENSE)); the tools, the launcher, the add-ons, the examples and the docs come from there.
The Marathi translation, the calendar, the `marathi` theme and `setups/` are my additions, under the same
licence. The theme's pictures are CC0.

`tests/` is upstream's test suite. The tests for upstream's README, its translations, the CI files and the press
counts fail here, because this repo replaces or drops those files. The tests for the code, the lists, the themes and the
locales pass. One theme test, `test_shipped_config_keys_are_read`, wrongly flags `clock_format`: `Config.java`
reads it through the `CLOCK_FORMAT_KEY` constant, which the test's pattern does not see.
