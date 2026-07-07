(function() {
  const API = 'data/profile.json';
  let data = null;

  function esc(s) {
    if (s == null) return '';
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function loadData() {
    return fetch(API)
      .then(r => r.json())
      .then(d => { data = d; return d; })
      .catch(err => {
        console.error('Load failed:', err);
        document.getElementById('content').innerHTML = '<p class="loading">Error loading data.</p>';
      });
  }

  function renderAbout() {
    if (!data) return;
    document.getElementById('content').innerHTML = `
      <p>${esc(data.profile.bio)}</p>

      <p><strong>Research:</strong> ${esc(data.profile.research)}</p>
      <p><strong>Leadership & Impact:</strong> ${esc(data.profile.impact)}</p>
      <p>
        ${data.profile.links.map(l => `<a href="${esc(l.url)}" target="_blank">${esc(l.label)}</a>`).join(' | ')}
      </p>

      <h2>Research & Technology Leadership</h2>
      ${data.researchLeadership.map(r => `
        <h3>${esc(r.area)}</h3>
        <p>${esc(r.desc)}</p>
      `).join('')}

      <h2>Education</h2>
      <ul>
        ${data.education.map(e => `
          <li><strong>${esc(e.years)}</strong>: ${esc(e.degree)}, ${esc(e.institution)}<br><em>${esc(e.field)}</em></li>
        `).join('')}
      </ul>
    `;
  }

  function renderPublications() {
    if (!data) return;
    document.getElementById('content').innerHTML = `
      <h2>Selected Publications</h2>
      <ul class="pub-list">
        ${data.publications.map(p => `
          <li class="pub-item">
            <div class="pub-title">${esc(p.title)}</div>
            <div class="pub-venue">${esc(p.venue || 'Preprint')}${p.year ? ', ' + esc(p.year) : ''}</div>
            ${p.note ? `<div class="pub-note">${esc(p.note)}</div>` : ''}
          </li>
        `).join('')}
      </ul>

      <h2>Selected Patents</h2>
      <ul class="pub-list">
        ${data.patents.map(p => `
          <li class="pub-item">
            <div class="pub-title">${esc(p.title)}</div>
            <div class="pub-venue">${esc(p.id)}${p.note ? ' — ' + esc(p.note) : ''}</div>
          </li>
        `).join('')}
      </ul>
    `;
  }

  function renderExperience() {
    if (!data) return;
    document.getElementById('content').innerHTML = `
      <h2>Work Experience</h2>
      <ul class="exp-list">
        ${data.experience.map(e => `
          <li class="exp-item">
            <div class="exp-org">${esc(e.org)} (${esc(e.years)})</div>
            <div class="exp-role">${esc(e.role)}</div>
          </li>
        `).join('')}
      </ul>

      <h2>Professional Leadership</h2>
      <ul class="exp-list">
        ${data.leadership.map(l => `
          <li class="exp-item">
            <div class="exp-org">${esc(l.role)}</div>
            <div class="exp-role">${esc(l.years)}</div>
          </li>
        `).join('')}
      </ul>

      <h2>Key National Projects (Past 5 Years)</h2>
      <ul class="exp-list">
        ${data.nationalProjects.map(p => `
          <li class="exp-item">
            <div class="exp-org">${esc(p.title)} (${esc(p.years)})</div>
            <div class="exp-role">${esc(p.role)}${p.note ? ' — ' + esc(p.note) : ''}</div>
          </li>
        `).join('')}
      </ul>

      <h2>Key Enterprise & Commercial Projects (Past 3 Years)</h2>
      <ul class="exp-list">
        ${data.enterpriseProjects.map(p => `
          <li class="exp-item">
            <div class="exp-org">${esc(p.title)} (${esc(p.years)})</div>
            <div class="exp-role">${esc(p.role)}</div>
          </li>
        `).join('')}
      </ul>
    `;
  }

  function renderAwards() {
    if (!data) return;
    document.getElementById('content').innerHTML = `
      <h2>Selected Honors and Awards</h2>
      <ul class="award-list">
        ${data.awards.map(a => `
          <li class="award-item">
            ${a.year ? '<span class="award-year">' + esc(a.year) + ':</span> ' : ''}
            ${esc(a.title)}
            ${a.note ? ' — <em>' + esc(a.note) + '</em>' : ''}
          </li>
        `).join('')}
      </ul>
    `;
  }

  function init() {
    const page = document.body.dataset.page;
    loadData().then(() => {
      if (page === 'about') renderAbout();
      else if (page === 'publications') renderPublications();
      else if (page === 'experience') renderExperience();
      else if (page === 'awards') renderAwards();
      document.getElementById('nav-' + page).classList.add('active');
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
