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

## Responsive breakpoints

The app uses consistent media-query breakpoints for iPad, small laptops, tablets, and phones. Use these same values when adding or changing responsive styles.

| Breakpoint | Target | Where used |
|------------|--------|------------|
| **1390px** | Small desktop / laptop | `dashboard.css`: topbar/content padding, search width, stats grid (4 cols), panels |
| **1190px** | iPad landscape / small laptop | `dashboard.css`: tighter padding, search 280px, page header wraps; `inventory.css`: table toolbar wraps, category dropdown 140px, card padding |
| **900px** | Narrow laptop / iPad | `dashboard.css`: content 12px 14px, search 240px; `inventory.css`: table actions/footer padding, search 180px, category 130px |
| **768px** | iPad portrait / tablet | `dashboard.css`: page header stacks (column), brand text hidden, search full width; `inventory.css`: request layout stacks, side panel full width, table toolbar/footer wrap, table wrapper 50vh |
| **640px** | Small tablet / large phone | `dashboard.css`: hamburger menu, sidebar as drawer, main margin-left 0 |
| **480px** | Phone | `dashboard.css`: stats 1 col; `inventory.css`: table column min-widths, category dropdown 120px, tighter padding |

### CSS files

- **`static/css/dashboard.css`**: App shell (topbar, sidebar, main content), page headers, stats grid, panels.
- **`static/css/inventory.css`**: Warehouse inventory, table actions, category filter, table wrapper, request layouts, side panel, grids.

### Usage

When adding new responsive styles, use the same `max-width` values so behavior stays consistent:

```css
@media (max-width: 1190px) {
  /* iPad / small laptop */
}
@media (max-width: 768px) {
  /* iPad portrait / tablet */
}
@media (max-width: 640px) {
  /* Sidebar becomes drawer */
}
@media (max-width: 480px) {
  /* Phone */
}
```

---

## Notes
- Prefer tokens over raw hex values for colors. If a new color is needed, add it to the `:root` tokens and document it here with intended usage.
- Keep token names semantic (e.g., `--focus`, `--muted`) so intent is clear across the codebase.


