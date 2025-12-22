/*
 * user/plugin/blog/js/blog.js
 * Fallback script for the search toggle on dynamic pages (like blog index).
 * This logic ensures that the search toggle event listener is registered,
 * regardless of whether the main theme script successfully registers it.
 *
 * NOTE: This script is a necessary fallback because the global main.js listener
 * fails to attach correctly on the blog index route. We safely remove the
 * existing listener (by cloning the element) and attach our own implementation
 * that duplicates the required logic (openSearch/closeSearch) from main.js.
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchToggle = document.getElementById('search-toggle');
    const pageContent = document.getElementById('page-content');
    const searchContainer = document.getElementById('search-container');
    const searchInput = document.getElementById('search-input');
    
    if (searchToggle && pageContent && searchContainer) {
        // 1. Safely remove existing event listeners by cloning and replacing the element
        const newSearchToggle = searchToggle.cloneNode(true);
        searchToggle.parentNode.replaceChild(newSearchToggle, searchToggle);

        // 2. Attach our custom toggle logic
        newSearchToggle.addEventListener('click', function(event) {
            event.preventDefault();

            // Check if the search is currently active
            const isSearchActive = searchContainer.style.display !== 'none' && searchContainer.style.display !== '';

            if (isSearchActive) {
                // If active, run closeSearch logic (restoring original state)
                searchContainer.style.display = 'none';
                pageContent.style.display = 'block';

                // Reverting breadcrumbs (logic duplicated from main.js closeSearch)
                const searchBreadcrumbs = document.getElementById('search-breadcrumbs');
                if (searchBreadcrumbs) searchBreadcrumbs.remove();
                const pageBreadcrumbs = document.getElementById('page-breadcrumbs');
                if (pageBreadcrumbs) pageBreadcrumbs.style.display = ''; // Restore display style

                if (searchInput) {
                    searchInput.value = '';
                    const searchResults = document.getElementById('search-results');
                    if (searchResults) searchResults.innerHTML = '';
                }

            } else {
                // If inactive, run openSearch logic
                
                // Closing sidebar is primary action (logic duplicated from main.js openSearch)
                const sidebar = document.getElementById('sidebar');
                if (sidebar && sidebar.classList.contains('is-active')) {
                    const sidebarOverlay = document.getElementById("sidebar-overlay");
                    sidebar.classList.toggle('is-active');
                    if (sidebarOverlay) sidebarOverlay.classList.toggle('is-active');
                }

                // Hiding/showing elements
                const pageBreadcrumbs = document.getElementById('page-breadcrumbs');
                if (pageBreadcrumbs) pageBreadcrumbs.style.display = 'none';
                
                // Creating search breadcrumbs
                if (!document.getElementById('search-breadcrumbs')) {
                    const searchNav = document.createElement('nav');
                    searchNav.id = 'search-breadcrumbs';
                    searchNav.className = 'breadcrumbs';
                    searchNav.innerHTML = `<ol><li><a href="/">Domu</a></li><li class="active"><a href="#" aria-current="page">Search</a></li></ol>`;
                    searchContainer.parentNode.insertBefore(searchNav, searchContainer);
                }

                // Show search container
                pageContent.style.display = 'none';
                searchContainer.style.display = 'block';
                if (searchInput) searchInput.focus();
                
                // Initial search to display the page tree (logic duplicated from main.js openSearch)
                function performSearch(query) {
                    fetch('/search?q=' + encodeURIComponent(query))
                        .then(response => {
                            if (!response.ok) throw new Error('Network response was not ok');
                            return response.text();
                        })
                        .then(data => {
                            const searchResults = document.getElementById('search-results');
                            if (searchResults) searchResults.innerHTML = data;
                        })
                        .catch(error => {
                            console.error("Search failed:", error);
                            const searchResults = document.getElementById('search-results');
                            if (searchResults) searchResults.innerHTML = '<p style="color: red;">Search failed. Please try again.</p>';
                        });
                }
                performSearch(''); // Immediately fetch and display the tree
            }
        });
    }
});