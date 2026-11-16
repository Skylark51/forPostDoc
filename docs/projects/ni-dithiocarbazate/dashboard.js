(() => {
  const rows=[...document.querySelectorAll('tbody tr')];
  const status=r=>r.cells[2]?.textContent.trim();
  const done=rows.filter(r=>status(r)==='완료').length;
  const running=rows.filter(r=>status(r)==='진행중').length;
  const queued=rows.filter(r=>status(r)==='대기').length;
  document.getElementById('ni-metrics').innerHTML=[['정상 종료',done,'계산 종료 기준'],['실행 중',running,'서버 확인 시점'],['대기',queued,'선행 계산 이후 순차 실행'],['종료율',(100*done/rows.length).toFixed(1)+'%','전체 '+rows.length+'개 계산']].map(([title,n,note])=>`<div class="metric"><span>${title}</span><strong>${n}</strong><span>${note}</span></div>`).join('');
  const bar=document.getElementById('ni-progress');bar.value=done;bar.max=rows.length;
  document.getElementById('ni-rate').textContent=`${done} / ${rows.length}개 정상 종료 · 계산 종료와 연구 검증 완료는 별도`;
  const blocks=[];
  document.querySelectorAll('main>.scroll').forEach((section,i)=>{
    const rs=[...section.querySelectorAll('tbody tr')];
    const n=rs.filter(r=>status(r)==='완료').length;
    const run=rs.filter(r=>status(r)==='진행중').length;
    const title=section.previousElementSibling;
    title.id='stage-'+i;
    blocks.push(`<tr><td><a href="#stage-${i}">${title.textContent}</a></td><td>${n} / ${rs.length}</td><td>${run}</td><td>${rs.length-n-run}</td></tr>`);
    section.classList.add('panel');
  });
  document.getElementById('ni-stages').innerHTML=blocks.join('');
  rows.forEach(r=>{const cell=r.cells[2],s=cell.textContent;cell.textContent='';const badge=document.createElement('span');badge.className='badge '+(s==='완료'?'ok':s==='진행중'?'run':'');badge.textContent=s;cell.append(badge);});
  document.getElementById('ni-filter').addEventListener('change',ev=>{rows.forEach(r=>r.hidden=!!ev.target.value && status(r)!==ev.target.value);});
})();
