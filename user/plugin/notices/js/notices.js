document.addEventListener('DOMContentLoaded', function() {
    // Find all closable notice boxes
    const notices = document.querySelectorAll('.notice.closable');

    notices.forEach(function(notice) {
        // Create the close button
        const closeBtn = document.createElement('span');
        closeBtn.className = 'notice-closebtn';
        closeBtn.innerHTML = '&times;';

        // Prepend the close button to the notice div
        notice.insertBefore(closeBtn, notice.firstChild);

        // Add click event to the close button
        closeBtn.onclick = function() {
            const div = this.parentElement;
            div.style.opacity = "0";
            setTimeout(function() { 
                div.style.display = "none"; 
            }, 600);
        }
    });
});
