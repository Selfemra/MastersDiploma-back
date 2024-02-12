// admin_fetch.js

document.addEventListener('DOMContentLoaded', async function () {
    // Function to fetch JSON data from the server
    async function fetchData(endpoint) {
        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching data:', error);
            return null;
        }
    }

    /*async function handleVaultSelection() {
        const region = document.getElementById('region').value;
        const city = document.getElementById('city').value;
        const street = document.getElementById('street').value;
        const vault = document.getElementById('vault').value;
    
        // Call fetchPeople function and use the result as needed
        const people = await fetchPeople(region, city, street, vault);
        
        // Implement your logic to display or update the people list
        console.log('Fetched people:', people);
    }*/

    // Function to populate a <select> element with options
    function populateSelect(selectId, options) {
        const select = document.getElementById(selectId);

        // Clear existing options
        select.innerHTML = '';

        // Add new options based on the fetched data
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }

    // Event listeners to fetch cities, streets, and vaults based on user selections
    document.getElementById('region').addEventListener('change', async function () {
        const selectedRegion = this.value;
        const citiesEndpoint = `/admin/cities/${encodeURIComponent(selectedRegion)}`;
        const citiesData = await fetchData(citiesEndpoint);

        if (citiesData) {
            populateSelect('city', citiesData.cities);
            document.getElementById('city').disabled = false;
        }
    });

    document.getElementById('city').addEventListener('change', async function () {
        const selectedRegion = document.getElementById('region').value;
        const selectedCity = this.value;
        const streetsEndpoint = `/admin/streets/${encodeURIComponent(selectedRegion)}/${encodeURIComponent(selectedCity)}`;
        const streetsData = await fetchData(streetsEndpoint);

        if (streetsData) {
            populateSelect('street', streetsData.streets);
            document.getElementById('street').disabled = false;
        }
    });

    document.getElementById('street').addEventListener('change', async function () {
        const selectedRegion = document.getElementById('region').value;
        const selectedCity = document.getElementById('city').value;
        const selectedStreet = this.value;
        const vaultsEndpoint = `/admin/vaults/${encodeURIComponent(selectedRegion)}/${encodeURIComponent(selectedCity)}/${encodeURIComponent(selectedStreet)}`;
        const vaultsData = await fetchData(vaultsEndpoint);

        if (vaultsData) {
            populateSelect('vault', vaultsData.vaults);
            document.getElementById('vault').disabled = false;
        }
    });

    // Call the fetchRegions function when the page loads
    const regionsEndpoint = '/admin/regions';
    const regionsData = await fetchData(regionsEndpoint);

    if (regionsData) {
        populateSelect('region', regionsData.regions);
    }
});
