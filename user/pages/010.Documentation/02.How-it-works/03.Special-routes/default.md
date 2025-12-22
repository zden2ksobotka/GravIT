---
title: "Special Routes (Not Just Pages)"
slug: "special-routes"
---

## Two Types of URL Addresses

Most of the content on this website is created by pages originating from files in the `user/pages/` directory. However, there is a second category of URL addresses that are defined directly in the application core.

### 1. Pages from Content
Their URL is derived from the directory structure and the `slug` in the file header. Everything you see in the menu and in our demo is an example.

### 2. Application Routes
These are fixed addresses that provide application functions. They are not tied to any file in `user/pages/` and may not be visible in the menu, yet they are fully functional.

**Main Examples:**

*   **[/login](/login):** Displays the login form. Try clicking!
*   **[/logout](/logout):** Logs you out after logging in.
*   **[/profile](/profile):** Displays your profile after logging in.
*   **`/search`:** This route is used for the search function and returns results (utilized by JavaScript).

These routes are crucial for the interactive features of the CMS.

---
**[Back to "How It Works" overview](/doku/how-it-works)** | **[Back to the absolute start of the demo](/doku)**