async function loadData() {
    try {
        const response = await fetch(`/static/data/data.json?cache_bust=${new Date().getTime()}`);
        const data = await response.json();
        window.loadedData = data;

        generateSection('section-important', data.important_announcements, true, '/important', 'sort-important');
        generateSection('section-upcoming', data.upcoming_deadlines_events, true, '/upcoming', 'sort-upcoming');
        generateSection('section-milestones', data.milestones, true, '/milestones', 'sort-milestones');
    } catch (error) {
        console.error("Error loading data:", error);
    }
}

function generateSection(sectionId, items, showDate, link, sortSelectId) {
    const container = document.getElementById(sectionId);
    const sortSelect = document.getElementById(sortSelectId);

    const initialOrder = [...items];

    sortSelect.addEventListener('change', () => {
        if (sortSelect.value === "default") {
            items = [...initialOrder];
        } else {
            sortItems(items, sortSelect.value);
        }
        updateSectionItems(container, items, showDate, link);
    });

    updateSectionItems(container, items, showDate, link);
}

function updateSectionItems(container, items, showDate, link) {
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = '<p class="text-center text-muted fst-italic">No announcements</p>';
    } else {
        items.slice(0, 5).forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'd-flex flex-column align-items-center mb-2';

            if (showDate && item.date) {
                const dateSpan = document.createElement('span');
                dateSpan.className = 'fw-bold text-muted mb-1';
                dateSpan.textContent = item.date;
                itemDiv.appendChild(dateSpan);
            }

            const titleLink = document.createElement('a');
            titleLink.className = 'text-decoration-none text-center fw-bold';
            titleLink.href = item.link || '#';
            titleLink.target = '_blank';
            titleLink.textContent = item.title;
            itemDiv.appendChild(titleLink);

            container.appendChild(itemDiv);
        });

        if (items.length > 5) {
            const viewMoreButton = document.createElement('button');
            viewMoreButton.className = 'btn btn-outline-primary mt-2 view-more';
            viewMoreButton.textContent = 'View More';
            viewMoreButton.onclick = () => (window.location.href = link);
            container.appendChild(viewMoreButton);
        }
    }
}

function sortItems(items, sortOrder) {
    items.sort((a, b) => {
        const dateA = new Date(a.sorting_date);
        const dateB = new Date(b.sorting_date);
        return sortOrder === "nearest"
            ? dateA - dateB
            : dateB - dateA;
    });
}

function filterAnnouncements(query) {
    const sections = [
        { id: 'section-important', data: 'important_announcements', link: '/important' },
        { id: 'section-upcoming', data: 'upcoming_deadlines_events', link: '/upcoming' },
        { id: 'section-milestones', data: 'milestones', link: '/milestones' }
    ];

    sections.forEach(({ id, data, link }) => {
        const container = document.getElementById(id);
        const items = window.loadedData[data].filter(item =>
            item.title.toLowerCase().includes(query.toLowerCase())
        );

        updateSectionItems(container, items, true, link);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('logout-button').addEventListener('click', async () => {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/';
        } else {
            console.error('Logout failed');
        }
    });

    document.getElementById('logout-button-mobile').addEventListener('click', async () => {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/';
        } else {
            console.error('Logout failed');
        }
    });

    loadData();

    const hamburgerButton = document.getElementById('hamburger');
    const menuDropdown = document.getElementById('menuDropdown');

    hamburgerButton.addEventListener('click', () => {
        const isExpanded = hamburgerButton.getAttribute('aria-expanded') === 'true';
        hamburgerButton.setAttribute('aria-expanded', !isExpanded);

        menuDropdown.classList.toggle('show');
        menuDropdown.classList.toggle('collapse');
    });

    document.getElementById('search-button').addEventListener('click', () => {
        const query = document.getElementById('search-bar').value;
        filterAnnouncements(query);
    });

    document.getElementById('search-bar').addEventListener('input', () => {
        const query = document.getElementById('search-bar').value;
        filterAnnouncements(query);
    });
});