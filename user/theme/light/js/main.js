document.addEventListener("DOMContentLoaded", function() {
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebarClose = document.getElementById("sidebar-close");
  const sidebar = document.getElementById("sidebar");
  const sidebarOverlay = document.getElementById("sidebar-overlay");
  const searchToggle = document.getElementById('search-toggle');
  const searchToggleSidebar = document.getElementById('search-toggle-sidebar');
  const pageContentDiv = document.getElementById('page-content');
  const searchContainer = document.getElementById('search-container');
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const pageBreadcrumbs = document.getElementById('page-breadcrumbs');

  let searchConfig = { minLength: 3 };

  async function fetchSearchConfig() {
    try {
      const response = await fetch('/search/config');
      if (!response.ok) throw new Error('Failed to fetch search config');
      const config = await response.json();
      searchConfig.minLength = config.min_length || 3;
      if (searchInput) {
        searchInput.placeholder = `Enter at least ${searchConfig.minLength} characters (regex supported)`;
      }
    } catch (error) {
      console.error('Error fetching search config:', error);
    }
  }
  fetchSearchConfig();

  function toggleSidebar() {
    sidebar.classList.toggle('is-active');
    sidebarOverlay.classList.toggle('is-active');
  }

  if (sidebarToggle && sidebar && sidebarClose && sidebarOverlay) {
    sidebarToggle.addEventListener("click", toggleSidebar);
    sidebarClose.addEventListener("click", toggleSidebar);
    sidebarOverlay.addEventListener("click", toggleSidebar);
  }

  searchContainer.style.display = 'none';

  function openSearch() {
    // First, always close the sidebar if it's open. This is the primary action
    // when this function is called from the sidebar itself.
    if (sidebar && sidebar.classList.contains('is-active')) {
      toggleSidebar();
    }

    // Now, if search is already open, we don't need to do anything else.
    if (searchContainer.style.display === 'block') return;

    if (pageBreadcrumbs) pageBreadcrumbs.style.display = 'none';
    
    if (!document.getElementById('search-breadcrumbs')) {
      const searchNav = document.createElement('nav');
      searchNav.id = 'search-breadcrumbs';
      searchNav.className = 'breadcrumbs';
      searchNav.innerHTML = `<ol><li><a href="/">Domu</a></li><li class="active"><a href="#" aria-current="page">Search</a></li></ol>`;
      searchContainer.parentNode.insertBefore(searchNav, searchContainer);
    }

    pageContentDiv.style.display = 'none';
    searchContainer.style.display = 'block';
    searchInput.focus();
    performSearch(''); // Immediately fetch and display the tree
  }

  function closeSearch() {
    if (searchContainer.style.display === 'none') return; // Already closed

    const searchBreadcrumbs = document.getElementById('search-breadcrumbs');
    if (searchBreadcrumbs) searchBreadcrumbs.remove();
    if (pageBreadcrumbs) pageBreadcrumbs.style.display = '';

    searchContainer.style.display = 'none';
    pageContentDiv.style.display = 'block';
    searchInput.value = '';
    searchResults.innerHTML = '';
  }

  function handleSearchToggle(e) {
    e.preventDefault();
    if (searchContainer.style.display === 'none') {
      openSearch();
    } else {
      closeSearch();
    }
  }

  if (searchToggle) {
    searchToggle.addEventListener('click', handleSearchToggle);
  }
  if (searchToggleSidebar) {
    searchToggleSidebar.addEventListener('click', openSearch); // Always open from sidebar
  }

  let searchTimeout;
  if (searchInput) {
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value;
        searchTimeout = setTimeout(() => performSearch(query), 300);
    });
  }

  function performSearch(query) {
      fetch('/search?q=' + encodeURIComponent(query))
          .then(response => {
              if (!response.ok) throw new Error('Network response was not ok');
              return response.text();
          })
          .then(data => {
              searchResults.innerHTML = data;
          })
          .catch(error => {
              console.error("Search failed:", error);
              searchResults.innerHTML = '<p style="color: red;">Search failed. Please try again.</p>';
          });
  }

  window.onscroll = function() {
    const header = document.querySelector(".full-width-header");
    const contentWrapper = document.querySelector(".main-content-wrapper");
    if (header && contentWrapper) {
      if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
        header.classList.add('scrolled');
        contentWrapper.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
        contentWrapper.classList.remove('scrolled');
      }
    }

  };
});