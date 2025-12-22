---
title: "Structure and Menu Item Types"
slug: "structure-and-menu"
---

## How is the menu generated?

!!! Directory Structure = Menu Structure
The left-hand menu navigation precisely corresponds to the file and directory structure in `user/pages/`. The system automatically traverses the directories and creates a hierarchy from them.

The following text tree shows how the section you are currently reading (`010.Documentation`) is structured.

```
010.Documentation/
├── 01.First-level/
│   ├── 01.Second-level-A/
│   │   ├── 01.Third-level/
│   │   │   └── default.md
│   │   └── default.md  <-- Page: "Second Level A"
│   ├── 02.Second-level-B/
│   │   ├── default.md  <-- Page: "Second Level B"
│   │   └── container-test/
│   │       └── default.md  <-- Page: "Container Tab Test"
│   └── default.md  <-- Page: "First Level"
├── 02.How-It-Works/
│   ├── 01.Page-Anatomy/
│   ├── 02.Structure-and-Menu/
│   │   └── default.md  <-- You are currently reading
...
└── default.md  <-- Section introduction page
```

There are two basic types of items you can create:

### 1. Page / Hub (Directory with `default.md`)

If a directory (e.g., `01.First-level`) contains a file named `default.md`, it becomes a **clickable link** in the menu.

*   **Example:** All clickable items in our demo (`First-level`, `Second-level-A`, etc.) are directories containing `default.md`.
*   **Usage:** Ideal for creating an introductory page for the given section, which can further link to subpages.

### 2. Container (Directory without `default.md`)

If a directory (in our demo, `Container-without-index`) **does not contain** a `default.md` file, it becomes a **non-clickable heading** in the menu.

*   **Example:** The `Container-without-index` item in the menu. You can hover over it, but you cannot click it.
*   **Usage:** Perfect for visually grouping several subpages under a common name.

!!!! **Important:** For advanced management of subpage display (e.g., multicolumn index, user visibility control), **create a Page / Hub** (type 1) and activate explicit container logic in the frontmatter. You can learn more in the **[Container Logic](/doku/how-it-works/container-logic)** section.

---
**[Back to "How It Works" overview](/doku/how-it-works)** | **[Back to the absolute start of the demo](/doku)**
