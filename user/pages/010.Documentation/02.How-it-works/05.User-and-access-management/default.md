---
title: "User and Access Management"
slug: "user-management"
---
! This CMS includes a robust system for user management and restricting content access. Everything is controlled using simple `YAML` files.

### Access Control

The key to securing pages is the `access` YAML block in the header of every `default.md` file. It allows you to define who can view the page.

#### Common Examples:

**1. Require Any Login:**
This is the most frequent case. Anyone who is logged in can access the page, regardless of their role.
```yaml
access:
    <other>.login: true
```

**2. Require Administrator Rights:**
Only users who have the `admin.login: true` permission set in their profile can access the page.
```yaml
access:
    admin.login: true
```

**3. Access Only for a Specific User:**
You can also create entirely custom rules. If you want to restrict access only to the user `zden2k`, you first define a unique right in their file `user/accounts/zden2k.yaml`:
```yaml
# File: user/accounts/zden2k.yaml
access:
  admin:
    login: true
  zden2k:
    login: true # Unique right
```
And then you require this specific permission on the page:
```yaml
# File: default.md of the given page
access:
    zden2k.login: true
```

---
### Visibility in Menu vs. Access

!!!! It is important to distinguish between visibility and access!

**`visible: false`** This `YAML` key **only hides the item from the main menu**. The page still physically exists and is accessible to anyone who knows its direct URL (and meets the `access` rules). This is suitable for pages that should only be available via a link.

**`access:`** This block **truly secures the content**. Even if someone guesses the URL, the system will not allow them to view the page if they do not meet the defined rules (and will redirect them to `/login`).

#### Improved Process for Logged-In Users (Switch Account)

If you are logged in and the system denies you access, you will not see a generic error message. Instead, you will be **redirected back to `/login`** with a clear message that your **current account does not have permission**.

At the same time, a "Switch Account" button will be displayed. After clicking, you will be logged out, but the system **remembers the original page**. After logging in with a different, authorized account, you will be automatically redirected to the originally requested URL, which significantly improves user comfort.

---
### How to Create a New User

! Adding a new user is easy thanks to the prepared interactive script. **Never attempt to create files with passwords manually!**

**1. Run the script in the terminal:**
Navigate to the CMS root directory and run the following command:
```bash
./utils/add_new_user.py
```

**2. Follow the instructions:**
The script will gradually ask you for:
*   Username (no spaces or diacritics).
*   Full name (e.g., John Doe).
*   Password (will be entered hidden).
*   Email address.
*   Whether the user should have administrator rights.

**3. Done!**
The script will automatically create a correctly formatted file in the `user/accounts/` directory, for example, `johndoe.yaml`. The password will be securely stored as a **bcrypt hash**.

---
**[Back to "How It Works" overview](/doku/how-it-works)** | **[Back to the absolute start of the demo](/doku)**
