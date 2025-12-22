---
title: "Page Anatomy"
slug: "page-anatomy"
---

## What constitutes a page?

! Every page in this CMS consists of two main parts:

1.  **Header (YAML Frontmatter):** A block of text at the very beginning of the `default.md` file, enclosed by `---`. It contains key metadata that controls the page's behavior.
2.  **Content (Markdown):** The actual text of the page, which you write below the header. Markdown is a lightweight markup language used for styling plain text and subsequently converting it into formatted HTML text suitable for publication.

<p style="line-height: normal;">
Unlike many WYSIWYG editors, Markdown does not generate unnecessary HTML clutter. Common online editors often insert formatting using nested &lt;span&gt; tags with inline styles. During subsequent edits, this code "bloats", is difficult to clean up, and becomes messy. Markdown, conversely, keeps the source text clean and generates the final HTML precisely and consistently.
</p>

### Key Items in the Header:

Here is an example of a page's `YAML` header:
```yaml
---
title: "Author signature and date"
slug: "author-signature"
author: 
    name: "Zden2k"
date: "2024-10-28"
access:
    admin.login: true
    zden2k.login: true
---
```

#### `title`
**The title, or heading of the page.** This is the text that appears as the main heading on the page and as the name in the menu and browser tab. It may contain diacritics and spaces.

#### `slug`
**The identifier in the URL.** This is a unique, simplified name used in the browser address. It **should not** contain spaces or diacritics. Thanks to the `slug`, you can have a clean and short URL (`.../how-it-works/page-anatomy`), even if the file is stored in a deep and complex structure. It is also the key for manual linking.

### Other Useful Properties

#### `author` and `date`
If the **Author** plugin is active, you can display a signature below the page using these two keys.

*   `author.name`: The name of the author to be displayed.
*   `date`: The publication date.

#### `access`
This section controls the access rights to the page. You can define very specific rules.

*   `admin.login: true`: Requires the logged-in user to also have **administrator rights**.
*   `zden2k.login: true`: You can also create entirely custom rules for specific users. If the user `user` has this permission defined in their profile, they can access the page. (NOTE: Changed example user to 'user' for generic English context, original Czech example was specific).
*   `<other>.login: true`: It requires the <other> user to be **logged in in any way** to view the page content. If not, they will be redirected to `/login`.

#### `visible`
This key determines whether the page will be visible in the main navigation.

* `visible: false`: The page will **not appear** in the menu but will still be accessible via a direct link (if the user meets the `access` rules).
* If the key is missing or is `visible: true`, the page will be visible in the menu.

---
**[Back to "How It Works" overview](/doku/how-it-works)** | **[Back to the absolute start of the demo](/doku)**
