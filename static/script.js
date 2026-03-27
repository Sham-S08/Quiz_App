// ── Option Selection ─────────────────────────────────
document.querySelectorAll('.option-label').forEach((label, idx) => {
  const letters = ['A', 'B', 'C', 'D'];
  const bullet = label.querySelector('.option-bullet');
  if (bullet) bullet.textContent = letters[idx % 4] || idx + 1;

  label.addEventListener('click', () => {
    const name = label.querySelector('input[type="radio"]')?.name;
    if (!name) return;
    document.querySelectorAll(`input[name="${name}"]`).forEach(inp => {
      inp.closest('.option-label')?.classList.remove('selected');
    });
    label.classList.add('selected');
    label.querySelector('input[type="radio"]').checked = true;
  });
});

// ── Progress Bar ─────────────────────────────────────
(function () {
  const fill = document.getElementById('progress-fill');
  const label = document.getElementById('progress-label');
  const total = parseInt(document.getElementById('q-total')?.dataset.total || '0');
  const current = parseInt(document.getElementById('q-total')?.dataset.current || '0');

  if (fill && total > 0) {
    const pct = Math.round((current / total) * 100);
    setTimeout(() => { fill.style.width = pct + '%'; }, 100);
    if (label) label.textContent = current + ' / ' + total + ' questions';
  }
})();

// ── Timer ─────────────────────────────────────────────
(function () {
  const timerEl = document.getElementById('timer-value');
  const display = document.getElementById('timer-display');
  const pill    = document.getElementById('timer-pill');
  if (!timerEl || !display) return;

  const total = parseInt(timerEl.dataset.timer || '0');
  if (total <= 0) return;

  let timeLeft = total;

  const fmt = (s) => {
    if (s >= 60) {
      const m = Math.floor(s / 60);
      const sec = s % 60;
      return m + ':' + (sec < 10 ? '0' : '') + sec;
    }
    return s + 's';
  };

  display.textContent = fmt(timeLeft);

  const countdown = setInterval(() => {
    timeLeft--;
    display.textContent = fmt(timeLeft);

    if (timeLeft <= 10 && pill) {
      pill.classList.add('danger');
    }

    if (timeLeft <= 0) {
      clearInterval(countdown);
      document.getElementById('quiz-form')?.submit();
    }
  }, 1000);
})();

// ── Score bar animation (result page) ────────────────
(function () {
  const bar = document.getElementById('score-bar');
  if (!bar) return;
  const pct = parseInt(bar.dataset.pct || '0');
  setTimeout(() => { bar.style.width = pct + '%'; }, 200);
})();

// ── Admin: bundle questions before approve ────────────
function bundleQuestions(e) {
  e.preventDefault();
  const form  = e.target.closest('form');
  const total = parseInt(document.getElementById('gen-total')?.dataset.total || '0');
  const out   = [];

  for (let i = 1; i <= total; i++) {
    const q = {
      question: form[`q_${i}_question`]?.value || '',
      option1:  form[`q_${i}_option1`]?.value  || '',
      option2:  form[`q_${i}_option2`]?.value  || '',
      option3:  form[`q_${i}_option3`]?.value  || '',
      option4:  form[`q_${i}_option4`]?.value  || '',
      answer:   form[`q_${i}_answer`]?.value   || '',
    };
    if (q.question) out.push(q);
  }

  document.getElementById('questions-json').value = JSON.stringify(out);
  form.submit();
}

// ── Toggle password visibility (login) ───────────────
function toggleEye(id, btn) {
  const inp = document.getElementById(id);
  if (!inp) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    btn.textContent = '🙈';
  } else {
    inp.type = 'password';
    btn.textContent = '👁';
  }
}