# Cedilla Input Diagnosis

## Symptom

Typing dead acute followed by `c` produces `ć` in VS Code, browsers, and
several other applications, while some GTK text editors produce `ç`.

## Evidence

- The active GNOME keyboard source is `us+intl`.
- `~/.XCompose` still maps `<dead_acute> <c>` and `<dead_acute> <C>` to `ç`
  and `Ç`.
- `XCOMPOSEFILE` is declared in `~/.config/environment.d/xcompose.conf`.
- The graphical session receives `XCOMPOSEFILE`, but does not define
  `GTK_IM_MODULE`.
- User-local Firefox and Discord launchers explicitly override
  `GTK_IM_MODULE` with `xim`.
- VS Code 1.141.1 uses Electron 43.7.7 and runs through native Wayland.
- The running VS Code process does not contain `XCOMPOSEFILE`,
  `GTK_IM_MODULE`, or `XMODIFIERS` in its environment.
- The Portuguese Compose table already maps dead acute followed by `c` to
  `ç`; the custom Compose rule duplicates that locale behavior.

## Cause

Applications use inconsistent input paths. Native Wayland/Electron and the
per-application XIM overrides do not consume the custom XCompose rule in this
session. They fall back to the `us+intl` XKB composition, where dead acute
followed by `c` maps to `ć`. Applications using the GTK simple input context
consume the Compose mapping and produce `ç`.

## Safe Verification

An isolated VS Code window through X11 with the GTK simple input context was
tested with:

```bash
GTK_IM_MODULE=simple XCOMPOSEFILE="$HOME/.XCompose" \
    code --ozone-platform=x11 --user-data-dir /tmp/code-compose-test
```

This test produced `ç`. The earlier XIM test produced a standalone acute
accent followed by `c`, showing that XIM did not process the Compose sequence
in this environment. A complete fix belongs in the graphical session input
configuration, followed by removal of conflicting per-application XIM
overrides; it should not be implemented only in the VS Code launcher.

## Applied Fix

- Added `GTK_IM_MODULE=simple` to
  `~/.config/environment.d/xcompose.conf`.
- Kept `XCOMPOSEFILE=/home/daniel/.XCompose` in the same global session
  configuration.
- Replaced Firefox and Discord launcher overrides from `xim` to `simple`.
- Updated the current systemd user and D-Bus activation environments.
- Rebuilt the user desktop-entry database.

Already running applications retain their original environment and must be
fully restarted. A logout and login ensures that every new graphical process
inherits the persisted configuration.
