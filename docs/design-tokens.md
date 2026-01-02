# Design Tokens — Colors & Typography

This document centralizes the project's color palette and font choices so pages remain visually consistent. Use the CSS variables defined in `static/css/dashboard.css` (the `:root` block) when styling components.

- File reference: `static/css/dashboard.css`

## Color tokens
- `--text`: #111111 — Primary text color
- `--bg`: #f3f4f6 — App background
- `--card-bg`: #ffffff — Card / panel background
- `--muted`: #9ca3af — Muted text / secondary labels
- `--accent`: #f7e7d0 — Accent / active backgrounds
- `--border`: #cfcfcf — General borders (darker for improved contrast)
- `--topbar-border`: #E5E5E6 — Topbar bottom border
- `--focus`: #D9BD7D — Focus / input highlight (used for search input hover/focus)
- `--stroke`: #F2F2F2 — Subtle strokes (icon background border)

### Usage examples
Use tokens in CSS:

```css
button {
  background: var(--accent);
  color: var(--text);
  border: 1px solid var(--border);
}

.search input:focus {
  border-color: var(--focus);
}
```

## Typography
- `--font-stack`: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial

Usage:

```css
html, body {
  font-family: var(--font-stack);
  color: var(--text);
}
```

## Notes
- Prefer tokens over raw hex values for colors. If a new color is needed, add it to the `:root` tokens and document it here with intended usage.
- Keep token names semantic (e.g., `--focus`, `--muted`) so intent is clear across the codebase.


