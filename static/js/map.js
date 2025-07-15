// ✅ Debounce utility to prevent rapid repeated function calls (e.g., marker drag, map click)
// this function does not get called to frequently (e.g. during dragging)
// Helps avoid overwhelming the server and improves performance
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// ✅ Wrap reverseGeocode in debounce with a 1000ms delay
const debounceReverseGeocode = debounce(reverseGeocode, 1000);

// ✅ Save marker location to localStorage so it persists across reloads
function saveLocation(lat, lng) {
    localStorage.setItem('savedLat', lat);
    localStorage.setItem('savedLng', lng);
}

// ✅ Load saved location if it exists
function loadSavedLocation() {
    const lat = localStorage.getItem('savedLat');
    const lng = localStorage.getItem('savedLng');
    if (lat && lng) {
        return { lat: parseFloat(lat), lng: parseFloat(lng) };
    }
    return null;
}

// ✅ Initialize the map and marker on page load
function initMap() {
    const saved = loadSavedLocation();

    function setupMap(lat, lng) {
        document.getElementById('lat').value = lat;
        document.getElementById('lng').value = lng;

        window.map = L.map('map').setView([lat, lng], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(window.map);

        window.marker = L.marker([lat, lng], { draggable: true }).addTo(window.map);

        // ✅ Drag marker to update coordinates and address
        window.marker.on('dragend', function () {
            const pos = window.marker.getLatLng();
            document.getElementById('lat').value = pos.lat;
            document.getElementById('lng').value = pos.lng;
            saveLocation(pos.lat, pos.lng); // ✅ Save dragged position
            debounceReverseGeocode(pos.lat, pos.lng);
        });

        // ✅ Click map to move marker and update coordinates/address
        window.map.on('click', function (e) {
            const lat = e.latlng.lat;
            const lng = e.latlng.lng;
            document.getElementById('lat').value = lat;
            document.getElementById('lng').value = lng;
            window.marker.setLatLng([lat, lng]);
            saveLocation(lat, lng); // ✅ Save clicked position
            debounceReverseGeocode(lat, lng);
        });

        debounceReverseGeocode(lat, lng); // ✅ Initial address lookup
    }

    if (saved) {
        setupMap(saved.lat, saved.lng); // ✅ Use saved position if available
    } else if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                setupMap(position.coords.latitude, position.coords.longitude);
            },
            function (error) {
                alert("Unable to retrieve your location. Error: " + error.message);
            }
        );
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

// ✅ Recenter map and marker to user’s current position
function getCurrentLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(function (position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        document.getElementById('lat').value = lat;
        document.getElementById('lng').value = lng;

        if (window.map && window.marker) {
            window.map.setView([lat, lng], 13);
            window.marker.setLatLng([lat, lng]);
            saveLocation(lat, lng); // ✅ Save reset location
            debounceReverseGeocode(lat, lng);
        }
    }, function (error) {
        alert("Unable to retrieve your location. Error: " + error.message);
    });
}

// ✅ Reverse geocode: get address from coordinates
function reverseGeocode(lat, lng) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;

    fetch(url, {
        headers: {
            'User-Agent': 'Game Sightings/1.0'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                document.getElementById('autocomplete').value = data.display_name;
            }
        })
        .catch(error => {
            console.error('Reverse geocoding failed:', error);
        });
}

// ✅ Forward geocode: user types an address, map jumps to that location
function forwardGeocode(address) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`;

    fetch(url, {
        headers: {
            'User-Agent': 'Game Sightings/1.0'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);

                document.getElementById('lat').value = lat;
                document.getElementById('lng').value = lon;

                if (window.map && window.marker) {
                    window.map.setView([lat, lon], 13);
                    window.marker.setLatLng([lat, lon]);
                    saveLocation(lat, lon); // ✅ Save user-entered address
                }
            } else {
                alert("Location not found.");
            }
        })
        .catch(error => {
            console.error('Forward geocoding failed:', error);
        });
}

// ✅ Listen for manual typing into the location field
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('autocomplete');
    if (input) {
        input.addEventListener('change', function () {
            const address = input.value.trim();
            if (address.length > 3) {
                forwardGeocode(address);
            }
        });
    }

    // ✅ Optional: hook up a "Reset Location" button (if one exists)
    const resetBtn = document.getElementById('reset-location');
    if (resetBtn) {
        resetBtn.addEventListener('click', getCurrentLocation);
    }
});

// ✅ Load the map on page load
window.onload = initMap;