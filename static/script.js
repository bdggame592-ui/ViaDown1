document.addEventListener('DOMContentLoaded', () => {
    let selectedPlatform = null;
    const platforms = document.querySelectorAll('.platform');
    const downloadBtn = document.getElementById('download-btn');
    const urlInput = document.getElementById('url-input');
    const messageDiv = document.getElementById('message');
    const menuBtn = document.getElementById('menu-btn');
    const closeMenu = document.getElementById('close-menu');
    const menuContent = document.getElementById('menu-content');
    const overlay = document.getElementById('overlay');
    const menuItems = document.querySelectorAll('.menu-item');
    const menuSectionContent = document.getElementById('menu-section-content');
    
    let menuOpen = false;

    // Platform selection
    platforms.forEach(platform => {
        platform.addEventListener('click', () => {
            platforms.forEach(p => p.classList.remove('selected'));
            platform.classList.add('selected');
            selectedPlatform = platform.getAttribute('data-platform');
        });
    });

    // Download button
    downloadBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        if (!url) {
            showMessage('Please enter a video URL', 'error');
            return;
        }
        if (!selectedPlatform) {
            showMessage('Please select a platform', 'error');
            return;
        }

        showMessage('<i class="fas fa-spinner fa-spin"></i> Downloading...', 'loading');

        // Send request to Flask backend
        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `url=${encodeURIComponent(url)}&platform=${encodeURIComponent(selectedPlatform)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showMessage(`Download complete: <a href="/downloads/${encodeURIComponent(data.filename)}" download>${data.filename}</a>`, 'success');
            } else {
                showMessage('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showMessage('Error: ' + error, 'error');
        });
    });

    // Menu button click event
    menuBtn.addEventListener('click', () => {
        openMenu();
    });
    
    // Close menu button
    closeMenu.addEventListener('click', () => {
        closeMenuHandler();
    });
    
    // Overlay click to close menu
    overlay.addEventListener('click', () => {
        closeMenuHandler();
    });
    
    // Menu items click events
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const section = item.getAttribute('data-section');
            showContent(section);
            
            // Update active menu item
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
    
    // Function to open menu
    function openMenu() {
        menuContent.classList.add('open');
        overlay.classList.add('active');
        menuOpen = true;
        document.body.style.overflow = 'hidden';
        
        // Default to About section when opening menu
        showContent('about');
        menuItems.forEach(item => {
            if (item.getAttribute('data-section') === 'about') {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    // Function to close menu
    function closeMenuHandler() {
        menuContent.classList.remove('open');
        overlay.classList.remove('active');
        menuOpen = false;
        document.body.style.overflow = 'auto';
    }
    
    // Function to show message
    function showMessage(text, type) {
        messageDiv.innerHTML = text;
        messageDiv.className = 'message';
        if (type) {
            messageDiv.classList.add(type);
        }
    }
    
    // Function to show content
    function showContent(section) {
        if (section === 'how') {
            menuSectionContent.innerHTML = `
                <h3>How to Use</h3>
                <ol>
                    <li>Copy the URL of the video you want to download</li>
                    <li>Paste the URL in the input field</li>
                    <li>Select the platform where the video is from</li>
                    <li>Click the Download button</li>
                    <li>Wait for the download to complete</li>
                    <li>Your video will be saved to your device's download folder</li>
                </ol>
                <p><strong>Note:</strong> Downloading copyrighted content may violate terms of service.</p>
            `;
        }
        else if (section === 'help') {
            menuSectionContent.innerHTML = `
                <h3>Help & Support</h3>
                <p>If you're experiencing any issues with ViaDown, our support team is here to help you.</p>
                <p>Join our Telegram support group for quick help:</p>
                <a href="https://t.me/viadown_support" class="telegram-link" target="_blank">
                    <i class="fab fa-telegram"></i> Join ViaDown Support
                </a>
                <p>You can also email us at: <strong>support@viadown.com</strong></p>
            `;
        }
        else if (section === 'about') {
            menuSectionContent.innerHTML = `
                <h3>About ViaDown</h3>
                <p>ViaDown is a free and easy-to-use video downloader application that supports multiple platforms including YouTube, Facebook, Instagram, and TikTok.</p>
                <p>With ViaDown, you can download your favorite videos with just a few clicks and access them anytime from your device.</p>
                <p><strong>Version:</strong> 2.1.0</p>
                <p><strong>Release Date:</strong> January 2025</p>
            `;
        }
    }
    
    // Close menu when pressing Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && menuOpen) {
            closeMenuHandler();
        }
    });
});