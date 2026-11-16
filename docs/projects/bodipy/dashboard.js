(() => {
  const $ = s => document.querySelector(s);
  const cards = [...document.querySelectorAll('.stage')];
  function filter() {
    let count = 0;
    const query = $('#query').value.trim().toLowerCase();
    cards.forEach(card => {
      card.hidden = !!(($('#element').value && card.dataset.element !== $('#element').value) ||
        ($('#phase').value && card.dataset.phase !== $('#phase').value) ||
        (query && !card.textContent.toLowerCase().includes(query)));
      if (!card.hidden) count++;
    });
    $('#count').textContent = `${count} / ${cards.length}개 단계`;
  }
  ['element','phase','query'].forEach(id => $('#'+id).addEventListener('input', filter));
  filter();
  const key = 'postdoc-bodipy-review-v1';
  const checks = [...document.querySelectorAll('[data-task]')];
  let state = {project:'bodipy',version:1,tasks:{},memo:''};
  function valid(s) {
    return s && s.project === 'bodipy' && s.version === 1 && typeof s.memo === 'string' &&
      s.tasks && typeof s.tasks === 'object' && !Array.isArray(s.tasks) &&
      Object.entries(s.tasks).every(([k,v]) => checks.some(c => c.dataset.task === k) && typeof v === 'boolean');
  }
  function count() { $('#task-count').textContent = `개인 검토 체크 ${checks.filter(c=>c.checked).length} / ${checks.length} · 게시된 과학적 판정과 별도`; }
  function apply() { checks.forEach(c => c.checked = !!state.tasks[c.dataset.task]); $('#memo').value = state.memo; count(); }
  function save() {
    state.updatedAt = new Date().toISOString();
    try { localStorage.setItem(key, JSON.stringify(state)); $('#storage-message').textContent = '이 브라우저에 저장됨'; }
    catch { $('#storage-message').textContent = '브라우저 저장을 사용할 수 없습니다. 작업 기록을 백업하세요.'; }
    count();
  }
  try { const saved=JSON.parse(localStorage.getItem(key)); if(valid(saved)) state=saved; }
  catch { $('#storage-message').textContent = '기존 기록을 읽지 못했습니다. 백업 JSON을 불러올 수 있습니다.'; }
  apply();
  checks.forEach(c => c.addEventListener('change', () => {state.tasks[c.dataset.task]=c.checked; save();}));
  $('#memo').addEventListener('input', () => { state.memo=$('#memo').value; save(); });
  $('#export').addEventListener('click', () => {
    const url=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)],{type:'application/json'}));
    const a=document.createElement('a'); a.href=url; a.download='bodipy-review-notes.json'; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  $('#import').addEventListener('change', async ev => {
    const file=ev.target.files[0]; if(!file)return;
    try { const next=JSON.parse(await file.text()); if(!valid(next))throw Error('BODIPY 작업 기록 형식이 맞지 않습니다.'); state=next; apply(); save(); }
    catch(err) { $('#storage-message').textContent=err.message; }
    ev.target.value='';
  });
})();
