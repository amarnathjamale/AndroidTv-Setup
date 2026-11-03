# Skyworth SRT412

An operator-branded Android TV box: Skyworth SRT412 (device `HP40A3`, Amlogic, armeabi-v7a, 2 GB RAM),
Android TV 12, build `STTC.220815.001.C4.0.12_20260618`, wired to the LAN. Set up on 2026-11-03.

| File | What it is |
|---|---|
| `debloat.txt` | The packages turned off (disabled for user 0, never uninstalled), with the reason for each. |
| `restore.sh` | Undoes the debloat, gives Home back to the stock launcher and removes the theme. |

Take a backup before you change anything: the package lists, `getprop`, all settings, the Home owner and
`wm size`/`density`. Keep it out of git, because the settings dumps carry device identifiers.
`tools/disable.sh` keeps its undo record in `~/.cleanyourtv/`, keyed by the list's path, so run
`restore.sh` from the same checkout you applied the list from.

## What changed on the box

- **Disabled:** the operator's TV app, Google Assistant (katniss), Google feedback, partnersetup,
  onetimeinitializer, tvrecommendations (sponsored rows), calendar sync, print spooler and TalkBack.
  The stock launcher `com.google.android.tvlauncher` is also disabled, because CleanYourTV is Home.
- **Kept:** Chromecast built-in, the Play Store and Play Services, and every `com.sdt.*` package
  (firmware OTA, remote OTA, front panel, the remote's driver).
- **Installed:**
  - The launcher from this repo. Its dock is CloudStream, SmartTube, SK Tech and Nuvio.
  - Nuvio TV, the armeabi-v7a APK from the github.com/NuvioMedia/NuvioTV releases. Sign in to sync addons and
    progress across devices.
  - The weather add-on (`addons/weather`).
- **Theme:** `themes/marathi`.

## The remote's operator-app button

The red button sends `KEY_F10` (scancode 68). `config.xml` maps it to CloudStream with
`app_keys` `scan:68:com.lagradost.cloudstream3.prerelease`, and that works **from the Home screen only**.

This firmware never passes remote keys to accessibility services. `InputKeyService` was bound with key
filtering on (`InputFilterEnabled: true`) and got no key event at all, not even OK. So the key helpers
CleanYourTV normally uses for system-wide buttons cannot work here. `MainActivity` handles `scan:`
entries itself, which is how the button works on Home.

## Notes

- **Wallpaper moods:** `latitude` and `longitude` in `config.xml` are left empty in the repo. Set them to
  your city for sunrise and sunset based moods; empty uses the launcher's default times.
- **No local JDK is needed:** `tools/docker-build.sh` builds the launcher and add-ons in Docker.
- **Turn USB debugging off** when you are done. While it is on, port 5555 gives any device on the LAN a
  shell on the box.
