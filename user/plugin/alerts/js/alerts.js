document.addEventListener('DOMContentLoaded', function() {
    // Find all closable alert boxes
    const alerts = document.querySelectorAll('.alert.closable');

    alerts.forEach(function(alert) {
        // Create the close button
        const closeBtn = document.createElement('span');
        closeBtn.className = 'closebtn';
        closeBtn.innerHTML = '&times;';

        // Prepend the close button to the alert div
        alert.insertBefore(closeBtn, alert.firstChild);

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
