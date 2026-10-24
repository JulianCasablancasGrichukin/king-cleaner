document.querySelector('#go-back')?.addEventListener('click',()=>history.back());
const lines=document.querySelector('#operation-lines');
document.querySelector('#add-line')?.addEventListener('click',()=>{
  const copy=lines.firstElementChild.cloneNode(true);
  copy.querySelectorAll('input').forEach(input=>input.value='');
  lines.appendChild(copy);
});
lines?.addEventListener('click',event=>{
  if(event.target.closest('.remove-line')&&lines.children.length>1)event.target.closest('.operation-line').remove();
});
document.querySelectorAll('form[method="post"]').forEach(form=>form.addEventListener('submit',()=>{
  const button=form.querySelector('button:not([type="button"])');
  if(button){button.disabled=true;button.textContent='Guardando…';}
}));
window.addEventListener('pageshow',()=>document.querySelectorAll('button[disabled]').forEach(button=>{button.disabled=false;button.textContent='Confirmar';}));
