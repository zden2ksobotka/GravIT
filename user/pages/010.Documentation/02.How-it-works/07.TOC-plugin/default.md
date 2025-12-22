---
title: TOC Plugin (Table of Contents)
slug: toc-plugin
---

# TOC (Table of Contents)

! The **TOC** plugin is used for automatic content generation (Table of Contents) from page headings and for navigation. It is designed to be fully **automatic** and requires minimal intervention.

## Enabling and Disabling

| Option | Description | Default behavior (without configuration) |
| :--- | :--- | :--- |
| `toc: true` | Enables content generation. The plugin automatically inserts the TOC before the first H1 heading. | **Disabled** (if no H2, H3, H4 headings are defined) |
| `toc: false` | Explicitly disables content generation even if there are headings on the page. | |

## Advanced Configuration (In YAML Frontmatter)

The plugin allows detailed configuration of the TOC's display and behavior. All options are defined under the `toc` key in the page's frontmatter.

### Configuration Example

```yaml
---
title: Page with Advanced TOC
toc:
    enabled: true
    baselevel: 2
    headinglevel: 5
---
```

### Options Overview

| Option | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `enabled` | bool | `false` | Main switch. Set to `true` to enable TOC generation. |
| `baselevel` | int | `None` | Sets the **minimum** heading level to be included in the TOC (e.g., `2` for H2). |
| `headinglevel` | int | `None` | Sets the **maximum** heading level to be included in the TOC (e.g., `4` for H4). |

## Controlling Heading Levels

The plugin works with a range of headings defined by `baselevel` and `headinglevel`.

*   `baselevel` (bottom range) is typically `2` (for `<h2>`).
*   `headinglevel` (top range) is typically `4` (for `<h4>`).

If neither `baselevel` nor `headinglevel` is defined, the plugin uses its internal default settings.

### Example Heading that will be included (H2-H5)
```yaml
toc:
    baselevel: 2
    headinglevel: 5
```

```markdown
## This heading will be included
### This one too will be included
##### And this one as well
###### But this one will NOT be included (because it is H6)
```

> [!TIP|=] TIP: For consistent output and maximum control, always explicitly define `baselevel` and `headinglevel`.

---
**[Back to "How It Works" overview](/doku/how-it-works)** | **[Back to the absolute start of the demo](/doku)**
