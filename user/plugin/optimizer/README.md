# Optimizer Plugin

This plugin is designed to significantly improve the loading speed of the website for returning visitors by implementing a **Service Worker**.

## How it Works

The primary function of this plugin is to dynamically generate a `service-worker.js` file every time the application starts. This approach ensures the list of cached assets is always up-to-date with the current theme and active plugins.

Here is the process:

1.  **Dynamic Generation:** On application startup, the plugin scans the active theme and all loaded plugins to compile a comprehensive list of their CSS and JavaScript assets.
2.  **Template Injection:** It reads a template file (`service-worker.js.tpl`) and injects this dynamically generated list of assets into it.
3.  **File Creation:** The final, populated JavaScript code is written to `service-worker.js` within the plugin's directory.
4.  **Client-Side Registration:** The plugin includes a small JavaScript file (`js/optimizer.js`) on the main page, which is responsible for registering the generated `service-worker.js` in the user's browser.

Once registered, the Service Worker intercepts network requests and serves the cached assets directly from the user's local cache, avoiding unnecessary network requests and dramatically speeding up page loads on subsequent visits.

## Server Requirements (Nginx)

For the Service Worker to function correctly, a specific configuration is required in Nginx. The Service Worker file is located in a subdirectory (`/user/plugin/optimizer/`), but it needs to control the entire site (`/`). To allow this, you must add the following `location` block to your Nginx server configuration:

```nginx
# Allow the Service Worker to control the entire site
location = /user/plugin/optimizer/service-worker.js {
    add_header 'Service-Worker-Allowed' '/';
    add_header 'Cache-Control' 'no-cache, no-store, must-revalidate';
}
```
