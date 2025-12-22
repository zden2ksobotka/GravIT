---
title: "Third Level - End"
slug: "third-level"
---

## You are at the end of Branch A.

! This is the deepest page in this branch. You can return using the menu above or the links at the top of the page (i.e., the `breadcrumb navigation`).

!! Notice that pages are created using a directory structure and display the content of `default.md` files, which contain the page content in `Markdown syntax`, and auxiliary page variables in `Yaml`.

The following text tree shows how the section you are currently reading (`010.Dokumentace`) is structured.

```
user/pages/010.Documentation/
├── 01.First-level/
│   ├── 01.Second-level-A/
│   │   ├── 01.Third-level/
│   │   │   └── default.md  <-- You are currently reading this page (Slug: third-level)
│   │   └── default.md      <-- Page: "Second Level A"
│   ├── 02.Second-level-B/
│   │   ├── default.md      <-- Page: "Second Level B"
│   │   └── container-test/
│   │       └── default.md  <-- Container page with an overview of subpages
│   └── default.md          <-- Page: "First Level"
├── 02.How-It-Works/
│   ├── 01.Page-Anatomy/
│   ... (other sub-sections with default.md)
│   └── default.md          <-- Page: "How It Works"
└── default.md              <-- Section introduction page (Slug: documentation)
```

### Want to see something else?
Manual links are not limited to the path forward. You can link anywhere.

**[Let's jump straight to the Branch B hub!](/doku/first-level/second-level-b)**

---
### You are at the end of the demo

If you have explored everything, you can easily return to the introduction page of this section.

**[Go to the start of the "Documentation" demo](/doku)**