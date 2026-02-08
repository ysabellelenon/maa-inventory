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

## Button classes

These button classes provide consistent primary and secondary actions. `btn-gold`, `btn-green`, `btn-red`, and `btn-back` are defined in `maainventory/templates/maainventory/base.html` (available on every page); `btn-create` is in `static/css/inventory.css` (available on pages that load it).

| Class | Use for | Appearance | Defined in |
|-------|---------|------------|------------|
| **`btn-gold`** | Primary actions (e.g. Add Supplier, Back to Suppliers) | Gold background (`--focus`), white text | `base.html` |
| **`btn-green`** | Success/confirm actions (e.g. Approve, Add New Inventory Item) | Green background (#16a34a), white text | `base.html` |
| **`btn-red`** | Reject/danger actions (e.g. Reject request) | Red background (#EF4444), white text | `base.html` |
| **`btn-back`** | Secondary back/navigation links | Light gray background (#F9FAFB), dark text, bordered | `base.html` |
| **`btn-create`** | Add/Create/New actions in page headers (e.g. Add Item, New Request) | Gold background (#D9BD7D), pill shape, white text | `inventory.css` |

`btn-gold`, `btn-green`, `btn-red`, and `btn-back` share the same size: `padding: 8px 18px`, `font-size: 14px`, `gap: 8px`. `btn-create` uses `padding: 8px 12px`, `gap: 4px`, `border-radius: 999px` (pill shape). Icons inside should be 16×16px; use `<img>` or `<svg>` with `width="16" height="16"`.

### Usage examples

```html
<!-- Gold primary action -->
<a href="{% url 'add_supplier' %}" class="btn-gold">
  <img src="{% static 'icons/plus.svg' %}" alt="Add" />
  Add Supplier
</a>

<!-- Green confirm action -->
<button type="submit" class="btn-green">
  <img src="{% static 'icons/check.svg' %}" alt="" />
  Approve
</button>

<!-- Red reject/danger action -->
<button type="button" class="btn-red">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">...</svg>
  Reject
</button>

<!-- Gray back link -->
<a href="{% url 'requests' %}" class="btn-back">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">...</svg>
  Back to Requests
</a>

<!-- Pill-style create button (inventory.css) -->
<a href="{% url 'add_item' %}" class="btn-create">
  <img src="{% static 'icons/plus.svg' %}" alt="" />
  <span>Add Item</span>
</a>
```

**Notes:**
- Do not add inline styles or overrides for these buttons; keep styling consistent.
- `btn-gold` and `btn-green` expect `<img>` children; `btn-back` and `btn-red` support both `<img>` and `<svg>`.
- `btn-create` is in `inventory.css`, so it is available on pages that load that stylesheet (e.g. Warehouse Inventory, Branch Stock Requests, Purchase Orders).

---

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


