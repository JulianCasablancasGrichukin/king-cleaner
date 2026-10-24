document.querySelector('#go-back')?.addEventListener('click',()=>history.back());
const lines=document.querySelector('#operation-lines');
function updateSources(){
  if(!lines) return;
  const selected=[...lines.querySelectorAll('select[name="source"]')].map(select=>select.value).filter(Boolean);
  lines.querySelectorAll('.production-line').forEach(line=>{
    const select=line.querySelector('select');
    const option=select.selectedOptions[0];
    const amount=line.querySelector('input[name="amount"]');
    const unit=option?.dataset.unit;
    line.querySelector('.source-unit').textContent=unit ? `(${unit.toLowerCase()})` : '';
    line.querySelector('.source-info').textContent=unit ? `Disponible: ${option.dataset.available} ${unit.toLowerCase()}` : '';
    amount.step=unit==='UNIDADES' ? '1' : '0.01';
    amount.min=unit==='UNIDADES' ? '1' : '0.01';
    if(unit) amount.max=option.dataset.available; else amount.removeAttribute('max');
    select.setCustomValidity(select.value&&selected.filter(value=>value===select.value).length>1 ? 'No repitas un lote; suma su consumo en una fila.' : '');
  });
  const add=document.querySelector('#add-line');
  if(add) add.disabled=lines.children.length>=100;
}
document.querySelector('#add-line')?.addEventListener('click',()=>{
  if(lines.children.length>=100) return;
  const copy=lines.firstElementChild.cloneNode(true);
  copy.querySelectorAll('input').forEach(input=>input.value='');
  copy.querySelectorAll('select[name="source"]').forEach(select=>select.value='');
  lines.appendChild(copy);
  updateSources();
});
lines?.addEventListener('click',event=>{
  if(event.target.closest('.remove-line')&&lines.children.length>1){event.target.closest('.operation-line').remove();updateSources();}
});
lines?.addEventListener('change',updateSources);
updateSources();
const wizard=document.querySelector('#production-wizard');
if(wizard){
  const panels=[...wizard.querySelectorAll('[data-step]')];
  function showStep(step){
    panels.forEach(panel=>panel.hidden=Number(panel.dataset.step)!==step);
    wizard.querySelectorAll('[data-progress]').forEach(item=>{
      const active=Number(item.dataset.progress)===step;
      item.classList.toggle('current',active);
      if(active) item.setAttribute('aria-current','step'); else item.removeAttribute('aria-current');
    });
  }
  wizard.querySelectorAll('[data-next-step],[data-prev-step]').forEach(button=>button.hidden=false);
  wizard.querySelector('[data-next-step]').addEventListener('click',()=>{
    const inputs=[...panels[0].querySelectorAll('input,select')];
    if(inputs.every(input=>input.reportValidity())){showStep(2);panels[1].scrollIntoView({block:'start'});}
  });
  wizard.querySelector('[data-prev-step]').addEventListener('click',()=>{showStep(1);panels[0].scrollIntoView({block:'start'});});
  wizard.addEventListener('invalid',event=>{
    const panel=event.target.closest('[data-step]');
    if(panel) showStep(Number(panel.dataset.step));
  },true);
  showStep(Number(wizard.dataset.startStep));
}
document.querySelectorAll('form[method="post"]').forEach(form=>form.addEventListener('submit',event=>{
  if(event.defaultPrevented) return;
  const button=event.submitter;
  // Preserve the selected action when disabling submit buttons for duplicate protection.
  if(button?.name){const action=document.createElement('input');action.type='hidden';action.name=button.name;action.value=button.value;action.dataset.submitAction='true';form.appendChild(action);}
  form.querySelectorAll('button:not([type="button"])').forEach(submit=>{submit.dataset.originalLabel=submit.textContent;submit.disabled=true;});
  if(button) button.textContent='Procesando…';
}));
window.addEventListener('pageshow',()=>{
  document.querySelectorAll('button[data-original-label]').forEach(button=>{button.disabled=false;button.textContent=button.dataset.originalLabel;delete button.dataset.originalLabel;});
  document.querySelectorAll('input[data-submit-action]').forEach(input=>input.remove());
  updateSources();
});
