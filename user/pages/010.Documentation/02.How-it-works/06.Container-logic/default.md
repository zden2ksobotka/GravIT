---
title: "Container Logic and Multicolumn Index"
slug: "container-logic"
---

## Explicit Containers and Subpage Index

Originally, a container (non-clickable item) was created automatically if a directory lacked a `default.md` file. You can now create an **explicit container** using YAML frontmatter, which offers these advantages:

1.  It can have its own URL (`slug`).
2.  It can have its own `access` and `visible` rules.
3.  It **always** generates a subpage index and **ignores** any Markdown content in that `default.md` file.

### YAML Configuration

To activate and configure a container, use the following structure in the frontmatter:

```yaml
# Activates the explicit container logic
container: 
  enabled: true

  # Optional: Number of columns for index display
  columns: 3 

  # Optional: Display format.
  # Options: 'none', 'num' (numbered list), 'list', 'list2' (🔹 - default).
  format: "list2" 

  # Optional: Visibility logic for subpages
  show_all:
     # ONLY pages with 'visible: true' will be displayed for loggout users
     when_logout: false 
     
     # ALL pages (that are accessible) will be displayed for logged users
     when_login: true   
```

!!! **Important:** Even if you set `container: enabled: true`, the system still checks the **access rights** for subpages. If a user does not have access, the item will not be displayed in the index.

### The `show_all` Logic

This section provides granular control over displaying pages that have `visible: false` (i.e., they are hidden from the main menu):

*   **`when_logout: false`** (recommended): Logged-out users will not see any page with `visible: false` in the index.
*   **`when_login: true`** (recommended): Logged-in users (editors, administrators) will see **all** pages in the index, including those with `visible: false`, provided they have the rights to them. This is crucial for content management.

---
**[Back to "How It Works" overview](/doku/how-it-works)** | **[Back to the absolute start of the demo](/doku)**
