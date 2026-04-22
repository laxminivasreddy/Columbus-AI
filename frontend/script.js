// script.js - Complete modular JavaScript for all pages

// Base App Class (shared functionality)
class BaseApp {
    constructor() {
        this.initNavigation();
        this.initDarkMode();
        this.initScrollEffects();
    }

    initNavigation() {
        const mobileBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileBtn && mobileMenu) {
            mobileBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }
    }

    initDarkMode() {
        const toggle = document.getElementById('darkModeToggle');
        if (!toggle) return;

        const isDark = localStorage.getItem('darkMode') === 'true';
        if (isDark) {
            document.documentElement.classList.add('dark');
            document.getElementById('darkModeIcon').className = 'fas fa-sun text-xl text-yellow-300';
        } else {
            document.documentElement.classList.remove('dark');
            document.getElementById('darkModeIcon').className = 'fas fa-moon text-xl';
        }

        toggle.addEventListener('click', () => {
            const isDarkMode = document.documentElement.classList.contains('dark');
            if (isDarkMode) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('darkMode', 'false');
                document.getElementById('darkModeIcon').className = 'fas fa-moon text-xl';
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('darkMode', 'true');
                document.getElementById('darkModeIcon').className = 'fas fa-sun text-xl text-yellow-300';
            }
        });
    }

    initScrollEffects() {
        window.addEventListener('scroll', () => {
            const navbar = document.getElementById('navbar');
            if (window.scrollY > 100) {
                navbar?.classList.add('scrolled', 'shadow-lg');
            } else {
                navbar?.classList.remove('scrolled', 'shadow-lg');
            }
        });
    }
}

// 🌦️ Weather App
class WeatherApp extends BaseApp {
    constructor() {
        super();
        this.apiKey = 'f2e48371a7c9d1b6c3e3e0e9f8d7c6b5'; // Demo key - replace with your OpenWeatherMap key
        this.apiUrl = 'https://api.openweathermap.org/data/2.5';
        this.init();
    }

    init(page = 'weather') {
        this.form = document.getElementById('weatherForm');
        if (!this.form) return;
        this.cityInput = document.getElementById('cityInput');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.currentWeather = document.getElementById('currentWeather');
        this.forecastSection = document.getElementById('forecastSection');
        this.errorMessage = document.getElementById('errorMessage');

        this.form.addEventListener('submit', (e) => this.handleSearch(e));
        document.getElementById('tryAgainBtn')?.addEventListener('click', () => this.clearError());

        // Set default city
        this.cityInput.value = 'Tokyo';
    }

    async handleSearch(e) {
        e.preventDefault();
        const city = this.cityInput.value.trim();
        
        if (!city) {
            this.showError('Please enter a city name');
            return;
        }

        this.showLoading();
        try {
            const weatherData = await this.fetchWeather(city);
            this.displayWeather(weatherData);
            this.hideError();
        } catch (error) {
            this.showError('City not found. Please check spelling and try again.');
        } finally {
            this.hideLoading();
        }
    }

    async fetchWeather(city) {
        // Current weather
        const currentRes = await fetch(`${this.apiUrl}/weather?q=${city}&appid=${this.apiKey}&units=metric`);
        if (!currentRes.ok) throw new Error('City not found');
        const currentData = await currentRes.json();

        // 5-day forecast
        const forecastRes = await fetch(`${this.apiUrl}/forecast?q=${city}&appid=${this.apiKey}&units=metric`);
        const forecastData = await forecastRes.json();

        return { current: currentData, forecast: forecastData };
    }

    displayWeather(data) {
        const { current, forecast } = data;
        
        // Current weather
        document.getElementById('currentCity').textContent = `${current.name}, ${current.sys.country}`;
        document.getElementById('currentTemp').textContent = `${Math.round(current.main.temp)}°`;
        document.getElementById('currentCondition').textContent = current.weather[0].main;
        document.getElementById('humidity').textContent = `${current.main.humidity}%`;
        document.getElementById('windSpeed').textContent = `${current.wind.speed} m/s`;
        document.getElementById('visibility').textContent = `${(current.visibility / 1000).toFixed(1)} km`;
        document.getElementById('feelsLike').textContent = `${Math.round(current.main.feels_like)}°`;
        
        // Weather icon
        const iconCode = current.weather[0].icon;
        document.getElementById('currentWeatherIcon').className = this.getWeatherIcon(iconCode);

        // Show sections
        this.currentWeather.classList.remove('hidden');
        this.forecastSection.classList.remove('hidden');

        // Forecast
        this.displayForecast(forecast);
    }

    displayForecast(forecastData) {
        const container = document.getElementById('forecastCards');
        container.innerHTML = '';

        // Get daily forecasts (every 8th item = 3 hours * 8 = 24 hours)
        const dailyForecasts = forecastData.list.filter((_, index) => index % 8 === 0).slice(0, 5);

        dailyForecasts.forEach((item, index) => {
            const date = new Date(item.dt * 1000);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            
            const card = document.createElement('div');
            card.className = 'forecast-card bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-xl border border-white/40 hover:shadow-2xl transition-all duration-300 text-center';
            card.innerHTML = `
                <div class="text-3xl mb-4">${dayName}</div>
                <i class="${this.getWeatherIcon(item.weather[0].icon)} weather-icon text-gray-500 mb-4 block mx-auto"></i>
                <div class="text-3xl font-bold text-gray-900 mb-2">${Math.round(item.main.temp)}°</div>
                <div class="text-lg text-gray-600">${item.weather[0].main}</div>
                <div class="text-sm text-gray-500 mt-2">${Math.round(item.main.temp_min)}° / ${Math.round(item.main.temp_max)}°</div>
            `;
            container.appendChild(card);
        });
    }

    getWeatherIcon(iconCode) {
        const iconMap = {
            '01d': 'fas fa-sun', '01n': 'fas fa-moon',
            '02d': 'fas fa-cloud-sun', '02n': 'fas fa-cloud-moon',
            '03d': 'fas fa-cloud', '03n': 'fas fa-cloud',
            '04d': 'fas fa-clouds', '04n': 'fas fa-clouds',
            '09d': 'fas fa-cloud-rain', '09n': 'fas fa-cloud-rain',
            '10d': 'fas fa-cloud-sun-rain', '10n': 'fas fa-cloud-moon-rain',
            '11d': 'fas fa-bolt', '11n': 'fas fa-bolt',
            '13d': 'fas fa-snowflake', '13n': 'fas fa-snowflake',
            '50d': 'fas fa-smog', '50n': 'fas fa-smog'
        };
        return iconMap[iconCode] || 'fas fa-cloud';
    }

    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
        document.getElementById('getWeatherBtn').disabled = true;
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
        document.getElementById('getWeatherBtn').disabled = false;
    }

    showError(message) {
        this.errorMessage.querySelector('p').textContent = message;
        this.errorMessage.classList.remove('hidden');
        this.currentWeather?.classList.add('hidden');
        this.forecastSection?.classList.add('hidden');
    }

    hideError() {
        this.errorMessage.classList.add('hidden');
    }

    clearError() {
        this.cityInput.value = '';
        this.hideError();
        this.currentWeather?.classList.add('hidden');
        this.forecastSection?.classList.add('hidden');
    }
}

// 🏨 Hotels App
class HotelsApp extends BaseApp {
    constructor() {
        super();
        this.hotelsData = this.generateHotelsData();
        this.init();
    }

    init(page = 'hotels') {
        this.form = document.getElementById('hotelSearchForm');
        if (!this.form) return; // ✅ IMPORTANT FIX
        this.hotelsGrid = document.getElementById('hotelsGrid');
        this.noResults = document.getElementById('noResults');

        this.form.addEventListener('submit', (e) => this.handleSearch(e));
        document.getElementById('clearFiltersBtn')?.addEventListener('click', () => this.resetSearch());

        // Set default dates
        this.setDefaultDates();
    }

    generateHotelsData() {
        return [
            {
                id: 1,
                name: "Park Hyatt Tokyo",
                location: "Shinjuku, Tokyo",
                price: 450,
                rating: 4.8,
                reviews: 2347,
                image: "https://images.unsplash.com/photo-1571896349840-0d711a87172e?w=800",
                amenities: ["Free WiFi", "Spa", "Pool", "Gym"],
                type: "Luxury"
            },
            {
                id: 2,
                name: "citizenM Tokyo Shibuya",
                location: "Shibuya, Tokyo",
                price: 189,
                rating: 4.6,
                reviews: 1567,
                image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                amenities: ["Free WiFi", "Bar", "Gym"],
                type: "Design"
            },
            {
                id: 3,
                name: "The Ritz Paris",
                location: "Place Vendôme, Paris",
                price: 1200,
                rating: 4.9,
                reviews: 892,
                image: "https://images.unsplash.com/photo-1578683015141-0acef5920d76?w=800",
                amenities: ["Spa", "Restaurant", "Concierge"],
                type: "Luxury"
            },
            {
                id: 4,
                name: "Hilton New York Times Square",
                location: "Midtown, New York",
                price: 320,
                rating: 4.4,
                reviews: 3456,
                image: "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                amenities: ["Pool", "Gym", "Restaurant"],
                type: "Business"
            },
            {
                id: 5,
                name: "Moxy London City",
                location: "Liverpool Street, London",
                price: 210,
                rating: 4.7,
                reviews: 1234,
                image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800",
                amenities: ["Bar", "Gym", "Free WiFi"],
                type: "Lifestyle"
            },
            {
                id: 6,
                name: "Atlantis The Palm",
                location: "Palm Jumeirah, Dubai",
                price: 850,
                rating: 4.9,
                reviews: 5678,
                image: "https://images.unsplash.com/photo-1571896349842-33c89424de2b?w=800",
                amenities: ["Waterpark", "Beach", "Aquarium"],
                type: "Resort"
            },
            // Add more hotels...
        ];
    }

    handleSearch(e) {
        e.preventDefault();
        const location = document.getElementById('hotelLocation').value;
        const checkin = document.getElementById('checkinDate').value;
        const checkout = document.getElementById('checkoutDate').value;
        const guests = document.getElementById('guests').value;

        if (!location) {
            alert('Please select a destination');
            return;
        }

        // Filter hotels by location
        const filteredHotels = this.hotelsData.filter(hotel => 
            hotel.location.toLowerCase().includes(location.toLowerCase())
        );

        if (filteredHotels.length === 0) {
            this.hotelsGrid.classList.add('hidden');
            this.noResults.classList.remove('hidden');
            document.getElementById('resultsCount').textContent = '0 hotels found';
        } else {
            this.displayHotels(filteredHotels);
            this.hotelsGrid.classList.remove('hidden');
            this.noResults.classList.add('hidden');
            document.getElementById('resultsCount').textContent = `${filteredHotels.length} hotels found`;
        }
    }

    displayHotels(hotels) {
        const container = document.getElementById('hotelsGrid');
        container.innerHTML = '';

        hotels.forEach(hotel => {
            const card = this.createHotelCard(hotel);
            container.appendChild(card);
        });
    }

    createHotelCard(hotel) {
        const card = document.createElement('div');
        card.className = 'hotel-card bg-white rounded-3xl shadow-xl overflow-hidden hover:shadow-2xl group cursor-pointer border border-gray-100';
        
        card.innerHTML = `
            <div class="relative h-64 overflow-hidden">
                <img src="${hotel.image}" alt="${hotel.name}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
                <div class="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-gray-800">
                    ${hotel.type}
                </div>
            </div>
            <div class="p-8">
                <h3 class="text-2xl font-bold text-gray-900 mb-2 leading-tight">${hotel.name}</h3>
                <p class="text-lg text-gray-600 mb-4">${hotel.location}</p>
                
                <div class="flex items-center mb-6">
                    <div class="flex rating-stars mr-3">
                        ${[...Array(5)].map((_, i) => `<i class="fas fa-star ${i < Math.floor(hotel.rating) ? 'text-yellow-400' : 'text-gray-300'}"></i>`).join('')}
                    </div>
                    <span class="text-lg font-semibold text-gray-700">${hotel.rating}</span>
                    <span class="text-sm text-gray-500 ml-2">(${hotel.reviews.toLocaleString()})</span>
                </div>
                
                <div class="flex items-center justify-between">
                    <div>
                        <div class="text-3xl font-bold text-accent mb-1">$${hotel.price}</div>
                        <div class="text-sm text-gray-500">per night</div>
                    </div>
                    <button class="bg-gradient-to-r from-accent to-blue-500 text-white font-bold py-3 px-8 rounded-2xl hover:shadow-lg hover:scale-105 transition-all duration-300 shadow-md">
                        Book Now
                    </button>
                </div>
            </div>
        `;

        // Book button
        card.querySelector('button').addEventListener('click', (e) => {
            e.stopPropagation();
            alert(`Booking ${hotel.name}...\n\nComing soon! Great choice! 😊`);
        });

        return card;
    }

    setDefaultDates() {
        const today = new Date();
        const checkin = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000); // +7 days
        const checkout = new Date(today.getTime() + 10 * 24 * 60 * 60 * 1000); // +10 days
        
        document.getElementById('checkinDate').value = checkin.toISOString().split('T')[0];
        document.getElementById('checkoutDate').value = checkout.toISOString().split('T')[0];
    }

    resetSearch() {
        this.form.reset();
        this.setDefaultDates();
        this.hotelsGrid.classList.add('hidden');
        this.noResults.classList.add('hidden');
    }
}

// 🏠 Main Page App (existing)
class MainApp {
    constructor() {
        this.init();
    }

    init() {
        // Your existing main page logic here
        // ... (keep your existing MainApp code)
    }
}


// Page initialization
document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.id;

    // Disabled static class initializations as real backend APIs are now in place natively in the HTML files.
    // if (page === 'weatherPage') {
    //     new WeatherApp();
    // } 
    // else if (page === 'hotelsPage') {
    //     new HotelsApp();
    // } 
    
    if (page === 'homePage') {
        new MainApp();
    }
});
