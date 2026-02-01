/* ===============================================
   HEALTHCONNECT - JAVASCRIPT
   ===============================================
   This file contains all functionality and interactivity
   for the HealthConnect Symptoms Portal application.
   
   Main Features:
   - Symptom search functionality
   - Backend API integration
   - Dynamic result display
   - Common symptom tag handling
   =============================================== */

/**
 * DOMContentLoaded Event Listener
 * ===============================================
 * This event fires when the HTML document has been
 * completely parsed and loaded, before images load.
 * It's the perfect place to initialize JavaScript
 * since we know all DOM elements are available.
 * =============================================== */
document.addEventListener('DOMContentLoaded', function() {
    
    /**
     * ELEMENT REFERENCES
     * ===============================================
     * Get references to key DOM elements that we'll
     * interact with throughout this script.
     * ===============================================
     */
    
    /* Text input field where users type their symptoms */
    const searchInput = document.getElementById('symptom-input');
    
    /* Search button that triggers the symptom lookup */
    const searchBtn = document.getElementById('search-btn');
    
    /* All common symptom tag buttons (for quick selection) */
    const symptomTags = document.querySelectorAll('.symptom-tag');
    
    /* Container that holds and displays the results */
    const resultContainer = document.getElementById('result-container');
    
    /* Div where search results are displayed */
    const resultsList = document.getElementById('results-list');

    /**
     * ASYNC FUNCTION: fetchSymptoms(symptoms)
     * ===============================================
     * Sends the user's symptom query to the backend API
     * and handles the response. Uses async/await for
     * cleaner asynchronous code handling.
     * 
     * Parameters:
     * - symptoms (string): The symptom or condition
     *                       user entered/selected
     * 
     * Flow:
     * 1. Hide results container (they may be outdated)
     * 2. Show "Searching..." message to user
     * 3. Send POST request to backend with symptoms
     * 4. Handle successful response with displayResults()
     * 5. Show error message if something goes wrong
     * 6. Finally, show the results container
     * ===============================================
     */
    async function fetchSymptoms(symptoms) {
        // Hide the results container while we fetch new data
        resultContainer.classList.add('hidden');
        
        // Show loading message to indicate processing
        resultsList.innerHTML = '<div class="text-center text-gray-500">Searching...</div>';
        
        try {
            /**
             * Send POST request to the backend API
             * The backend endpoint should be running on localhost:8000
             */
            const response = await fetch('http://127.0.0.1:8000/check-symptoms', {
                // HTTP method: POST (sending data to server)
                method: 'POST',
                
                // Headers tell server we're sending JSON data
                headers: {
                    'Content-Type': 'application/json',
                },
                
                // Body contains the symptom data in JSON format
                body: JSON.stringify({ symptoms: symptoms }),
            });

            /**
             * Check if the response was successful
             * response.ok is true for status codes 200-299
             * If not ok, throw an error to be caught
             */
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            /**
             * Parse the JSON response from server
             * Expected format:
             * {
             *   "diagnosis": "condition name",
             *   "confidence": 0.85,
             *   "recommendation": "suggested next steps"
             * }
             */
            const data = await response.json();
            
            // Send the parsed data to display function
            displayResults(data);
            
        } catch (error) {
            /**
             * Catch any errors that occurred:
             * - Network errors (no connection to server)
             * - Invalid JSON response
             * - HTTP errors
             */
            console.error("Error fetching data:", error);
            
            // Display error message to user
            resultsList.innerHTML = '<div class="bg-red-100 text-red-700 p-4 rounded-lg">An error occurred. Please try again later.</div>';
        } finally {
            /**
             * Finally block runs whether try succeeded or failed
             * Always show the results container after request completes
             */
            resultContainer.classList.remove('hidden');
        }
    }

    /**
     * FUNCTION: displayResults(data)
     * ===============================================
     * Takes the API response data and displays it
     * in a formatted, user-friendly way on the page.
     * 
     * Parameters:
     * - data (object): Response from backend containing:
     *     - diagnosis: the condition name
     *     - confidence: probability (0-1)
     *     - recommendation: suggested action
     * 
     * This function:
     * 1. Creates diagnosis alert box with confidence %
     * 2. Creates recommendations box with next steps
     * 3. Injects HTML into the results-list div
     * ===============================================
     */
    function displayResults(data) {
        // Replace the entire results HTML with formatted data
        resultsList.innerHTML = `
            <!-- Diagnosis Information Box -->
            <div class="bg-blue-100 border border-blue-400 text-blue-800 px-4 py-3 rounded-md mb-4">
                <!-- Show the AI's diagnosis for the symptoms -->
                <p class="font-bold">Possible Diagnosis: ${data.diagnosis}</p>
                <!-- Show confidence as percentage (0-100%) -->
                <p class="text-sm">Confidence: ${Math.round(data.confidence * 100)}%</p>
            </div>
            
            <!-- Recommendations Information Box -->
            <div class="bg-green-100 border border-green-400 text-green-800 px-4 py-3 rounded-md">
                <!-- Header for next steps -->
                <p class="font-bold">Next Steps:</p>
                <!-- Show the recommended action/treatment -->
                <p>${data.recommendation}</p>
            </div>
        `;
    }

    /**
     * EVENT LISTENER: Search Button Click
     * ===============================================
     * When user clicks the "Search" button, get the
     * value from the input field and send it to API.
     * Only searches if input is not empty.
     * ===============================================
     */
    searchBtn.addEventListener('click', () => {
        // Get text from input and remove extra whitespace
        const symptoms = searchInput.value.trim();
        
        // Only search if user typed something
        if (symptoms) {
            fetchSymptoms(symptoms);
        }
    });

    /**
     * EVENT LISTENERS: Common Symptom Tags
     * ===============================================
     * Add click handlers to all symptom tag buttons.
     * When a tag is clicked:
     * 1. Get the symptom text from button
     * 2. Put it in the search input field
     * 3. Immediately fetch results (auto-search)
     * 
     * This provides a quick way for users to search
     * common symptoms without typing.
     * ===============================================
     */
    symptomTags.forEach(tag => {
        tag.addEventListener('click', () => {
            // Get the text content from the clicked tag button
            const symptoms = tag.textContent;
            
            // Place the symptom text into the search input
            searchInput.value = symptoms;
            
            // Immediately search for this symptom
            fetchSymptoms(symptoms);
        });
    });
});

/**
 * NOTES ON BACKEND INTEGRATION
 * ===============================================
 * 
 * Backend API Endpoint:
 * - URL: http://127.0.0.1:8000/check-symptoms
 * - Method: POST
 * 
 * Expected Request Format:
 * {
 *   "symptoms": "user's symptom description"
 * }
 * 
 * Expected Response Format:
 * {
 *   "diagnosis": "name of condition",
 *   "confidence": 0.85,
 *   "recommendation": "suggested next steps"
 * }
 * 
 * Error Handling:
 * - If backend is not running, user sees error message
 * - If symptoms are not recognized, backend should
 *   return a default response
 * - Network timeouts should be handled gracefully
 * 
 * To start the backend server:
 * python -m uvicorn main:app --reload
 * (assuming you have a FastAPI application)
 * 
 * =============================================== */

/**
 * BROWSER COMPATIBILITY
 * ===============================================
 * 
 * This code uses modern JavaScript features:
 * - async/await (IE 11 not supported)
 * - fetch API (IE 11 not supported)
 * - arrow functions (IE 11 not supported)
 * 
 * For IE 11 support, use:
 * - Babel transpiler to convert to ES5
 * - Promise polyfill for async/await
 * - Fetch polyfill for XMLHttpRequest
 * 
 * Target browsers: Chrome, Firefox, Safari, Edge
 * (all modern versions from 2020+)
 * 
 * =============================================== */

/* ===============================================
   INIT: 3D TILT + GLARE BEHAVIOR
   ===============================================
   Attaches pointer event handlers to card elements on
   the page and updates transform + CSS variables to
   create a realistic tilt and moving glare. Smoothly
   resets on pointer leave.
   =============================================== */
function initTiltCards() {
    const selectors = '.symptom-card, .max-w-3xl.mx-auto.bg-white, .text-center.bg-white.p-6.rounded-xl.shadow-sm';
    const cards = document.querySelectorAll(selectors);

    cards.forEach(card => {
        // Avoid initializing twice
        if (card.dataset.tiltInit) return;
        card.dataset.tiltInit = '1';

        // Default CSS variables
        card.style.setProperty('--px', '50%');
        card.style.setProperty('--py', '50%');
        card.style.setProperty('--g', '0');

        let rect = null;

        function handleMove(e) {
            // Support both mouse and touch
            const clientX = e.clientX ?? (e.touches && e.touches[0] && e.touches[0].clientX);
            const clientY = e.clientY ?? (e.touches && e.touches[0] && e.touches[0].clientY);
            rect = rect || card.getBoundingClientRect();
            const x = (clientX - rect.left) / rect.width;
            const y = (clientY - rect.top) / rect.height;
            const clamp = v => Math.max(0, Math.min(1, v));
            const cx = clamp(x);
            const cy = clamp(y);

            // Calculate rotation in degrees (tilt toward cursor)
            const rotateY = (cx - 0.5) * 20; // horizontal tilt
            const rotateX = (0.5 - cy) * 20; // vertical tilt

            // Apply perspective and rotation
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.03)`;

            // Update glare position and intensity
            card.style.setProperty('--px', `${cx * 100}%`);
            card.style.setProperty('--py', `${cy * 100}%`);
            const dx = cx - 0.5;
            const dy = cy - 0.5;
            const dist = Math.sqrt(dx*dx + dy*dy);
            const g = Math.max(0, Math.min(1, 1 - dist * 1.5));
            card.style.setProperty('--g', g.toString());
        }

        function handleEnter() {
            rect = card.getBoundingClientRect();
            card.style.transition = 'transform 150ms cubic-bezier(.2,.9,.2,1), box-shadow 150ms';
            card.style.boxShadow = '0 20px 40px rgba(2,6,23,0.35)';
        }

        function handleLeave() {
            card.style.transition = 'transform 600ms cubic-bezier(.2,.9,.2,1), box-shadow 600ms';
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
            card.style.boxShadow = '';
            card.style.setProperty('--g', '0');
            rect = null;
        }

        card.addEventListener('mousemove', handleMove);
        card.addEventListener('touchmove', handleMove, {passive: true});
        card.addEventListener('mouseenter', handleEnter);
        card.addEventListener('mouseleave', handleLeave);
        card.addEventListener('touchstart', handleEnter, {passive: true});
        card.addEventListener('touchend', handleLeave, {passive: true});
    });
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTiltCards);
} else {
    initTiltCards();
}

// Fallback: ensure the frosted glass header styles persist (applies inline styles)
(function ensureFrostedHeader() {
    function applyHeaderStyles() {
        const nav = document.querySelector('nav.floating-header');
        if (!nav) return;
        // Inline-style fallback (highest priority) to keep the frosted glass
        nav.style.background = 'rgba(255,255,255,0.05)';
        nav.style.webkitBackdropFilter = 'blur(12px)';
        nav.style.backdropFilter = 'blur(12px)';
        nav.style.borderBottom = '1px solid rgba(255,255,255,0.10)';
        nav.style.boxShadow = '0 8px 24px rgba(2,6,23,0.5)';
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyHeaderStyles);
    } else {
        applyHeaderStyles();
    }
})();

/* Smooth scroll fallback for internal anchor links with header offset */
(function attachAnchorScrollHandler() {
    const navSelector = 'nav.floating-header';

    function getHeaderHeight() {
        const nav = document.querySelector(navSelector);
        return nav ? Math.ceil(nav.getBoundingClientRect().height) : 56;
    }

    function handleClick(e) {
        const anchor = e.target.closest('a');
        if (!anchor) return;
        const href = anchor.getAttribute('href');
        if (!href || !href.startsWith('#') || href === '#') return;
        const id = href.slice(1);
        const target = document.getElementById(id);
        if (!target) return; // let default behavior occur

        e.preventDefault();

        const headerHeight = getHeaderHeight();
        const targetTop = Math.round(target.getBoundingClientRect().top + window.scrollY - headerHeight - 8);
        window.scrollTo({ top: targetTop, behavior: 'smooth' });

        // update the URL hash without abrupt jump
        history.pushState(null, '', href);
    }

    document.addEventListener('click', handleClick);
})();

/* ===============================================
   PERIODIC HERO ANIMATION (every 10 seconds)
   ===============================================
   Re-triggers the hero slide & fade-in by toggling
   the `hero-animate` class. Respects the user's
   prefers-reduced-motion setting and avoids running
   when reduced motion is requested.
   =============================================== */
(function periodicHeroAnimation() {
    // Skip if user prefers reduced motion
    const prefersReduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduce) return;

    const HERO_SELECTOR = '.hero-gradient';
    const hero = document.querySelector(HERO_SELECTOR);
    if (!hero) return;

    const PLAY_INTERVAL_MS = 10000; // 10 seconds
    const REMOVE_AFTER_MS = 1200;   // slightly longer than longest animation

    function playOnce() {
        // ensure class is not present
        hero.classList.remove('hero-animate');
        // force reflow to ensure animation restarts
        void hero.offsetWidth;
        hero.classList.add('hero-animate');

        // remove after animation completes so it can be re-added later
        setTimeout(() => hero.classList.remove('hero-animate'), REMOVE_AFTER_MS);
    }

    // Initial play on load, with a small delay for layout
    window.setTimeout(playOnce, 220);

    // Re-play at interval
    const intervalId = setInterval(playOnce, PLAY_INTERVAL_MS);

    // Clean up if the page is unloaded
    window.addEventListener('beforeunload', () => clearInterval(intervalId));
})();
