# Coord

A desktop utility for tracking and copying screen coordinates.

## Features

- **Real-time cursor tracking** — displays current mouse coordinates updated in real time
- **Coordinate window** — opens a compact always-on-top window in the bottom-right corner showing live coordinates
- **Window coordinates** — shows the bounding rectangle of any open window, auto-copies to clipboard, disappears after 5 seconds
- **Image viewer** — opens an image and shows cursor coordinates within it, with copy support

## Requirements

- Windows
- Python 3.8+

## Installation

```bash
pip install -r  requirements.txt
```

## Hotkeys

| Key | Action |
|-----|--------|
| `v` | Open coordinate window |
| `m` | Return to main menu |
| `c` | Copy current coordinates |
| `w` | Get focused window coordinates |
| `i` | Open image viewer |

> All hotkeys work in both English and Russian keyboard layouts.

## Notes

- The coordinate window opens in the **bottom-right** corner of the screen
- The window info popup opens in the **top-right** corner and closes automatically after 5 seconds
- Window coordinates are copied to clipboard automatically when using `w`
- In the image viewer, press `c` to copy the current in-image coordinates