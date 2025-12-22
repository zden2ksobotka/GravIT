---
title: Home
slug: home
# The first page in the order is always the default page, and if we don't want it in the menu, we set it to non-visible.
# This applies even though it will always be shown as the first page on the domain."
visible: False
---

# GravIT!:rainbow:

! <p>GravIT! This **Simple CMS** is built on the philosophy of **"simplicity"**. Unlike heavy content management systems, almost everything that would reduce speed or add unnecessary complexity has been omitted.
**Content, configuration, and users** are all defined in a simple schema of text files using Markdown and YAML **flat-file** principle. This guarantees lightning-fast response and maximum transparency.</p>

## In-Memory Power: Speed Above Gold :rocket:
The CMS utilizes modern **Python and FastAPI**, one of the fastest asynchronous frameworks available today. Upon startup, the complete content is loaded into **memory (RAM)**. The CMS's programming languages are **Python**, **Twig** and **SCSS**, with only the necessary amount of **JavaScript**: 

![Gravit](gravit_code_light.png?width=300&align=center)

<br>
Pages are then served from the **in-memory cache** with a response time that is many times faster than database queries. Thanks to **multi-threading** support, the application can effectively utilize multiple CPU cores.

## Modular Approach: Write What You Need
GravIT! is not for everyone. It is designed for those who appreciate **freedom and simplicity**. If you find a specific feature missing, it is by design-the CMS is intended as a minimalist core that you can easily extend yourself using **purposeful plugins or your own code**.

🔸   **Versioning and Backup:** Content management is as simple as a `git commit`. The entire website is just one directory that can be easily versioned and backed up.<br>
🔸   **No Admin Panel:** The system avoids a complex GUI, thereby reducing maintenance, security risks, and dependency on outdated libraries.<br>


### Key Features
🔸   **Architecture:** Python 3 and FastAPI for lightning-fast asynchronous operation.<br>
🔸   **Content:** Integrated Markdown with YAML for metadata and configuration.<br>
🔸   **Navigation:** Automatic, multi-level structure of bookmarks.<br>
🔸   **Search:** Fast search with regular expression support.<br>
🔸   **Security:** Support for multiple users and granular access control to content.<br>
🔸   **Aesthetics:** Responsive design and support for modern styles (SCSS, Emojis :100:{.emoji-size--ultra_small}).<br>
🔸   **Code:** Syntax highlighting with modern themes.<br>
🔸   **Extensions:** A rich library of purposeful plugins that do not modify the core application.<br>

