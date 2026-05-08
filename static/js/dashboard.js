// dashboard.js
document.addEventListener('DOMContentLoaded', function() {
  const dashboardEvents = JSON.parse(document.getElementById('eventos-data').textContent);
  const eventMap = {};
  dashboardEvents.forEach(([titulo, fecha, descripcion]) => {
    const day = Number(fecha.split('/')[0]);
    if (!eventMap[day]) {
      eventMap[day] = [];
    }
    eventMap[day].push({ titulo, fecha, descripcion });
  });

  const selectedDateHeading = document.getElementById('selectedDateHeading');
  const selectedEventList = document.getElementById('selectedEventList');
  const dayButtons = document.querySelectorAll('.calendar-day');

  dayButtons.forEach(button => {
    const day = Number(button.dataset.day);
    const dayEvents = eventMap[day] || [];
    if (dayEvents.length > 0) {
      button.classList.add('has-event');
      if (!button.querySelector('.calendar-dot')) {
        const dot = document.createElement('span');
        dot.className = 'calendar-dot';
        dot.textContent = dayEvents.length;
        button.appendChild(dot);
      }
    }
  });

  function renderSelectedDay(day) {
    const events = eventMap[day] || [];
    if (events.length === 0) {
      selectedDateHeading.textContent = `No hay eventos el día ${day}`;
      selectedEventList.innerHTML = '<p class="no-event">Este día no tiene eventos programados.</p>';
      return;
    }

    selectedDateHeading.textContent = `Eventos para el día ${day}`;
    selectedEventList.innerHTML = events.map(event => `
      <div class="event-list-item">
        <strong>${event.fecha} – ${event.titulo}</strong>
        <p>${event.descripcion}</p>
      </div>
    `).join('');
  }

  dayButtons.forEach(button => {
    button.addEventListener('click', () => {
      dayButtons.forEach(btn => btn.classList.remove('selected'));
      button.classList.add('selected');
      renderSelectedDay(button.dataset.day);
    });
  });

  const firstEventDay = Object.keys(eventMap)[0];
  if (firstEventDay) {
    const initialButton = document.querySelector(`.calendar-day[data-day="${firstEventDay}"]`);
    if (initialButton) {
      initialButton.click();
    }
  }
});