---
title: "Image Embedding"
slug: "image-embedding"
---
## Images in Content

! You can easily embed images into your pages. Just upload them to the same directory as your `default.md` file.

### Basic Syntax
The basic syntax for displaying an image is:

```markdown
![Image Description](file-name.jpg)
```

### Resizing and Alignment
!! This CMS has a useful function for resizing and aligning images directly within the Markdown link. Simply append the parameter `?width=yyy`, where `yyy` is the desired width in pixels. You can also use `&align=left/right/center`.

**Example (normal image size):**
![Pacman](pacman.gif)

**Example (image size 200px, aligned left):**

<!-- You can define width, height, and align=left/right/center here -->
![Pacman](pacman02.gif?width=200&align=left)

Of course, you can also use a full path and the standard `<img>` tag with custom attributes:
<img alt="Gravit" src="/user/pages/010.Documentation/01.First-level/02.Second-level-B/container-tab/04.Images/linux.png" width="75" height="auto" class="align-right">

---
**[Back to the absolute start of the demo](/doku)**
