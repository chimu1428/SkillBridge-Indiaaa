document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('.alert').forEach(a=>setTimeout(()=>{if(window.bootstrap) bootstrap.Alert.getOrCreateInstance(a).close()},4500));document.querySelectorAll('form').forEach(f=>f.addEventListener('submit',()=>{const b=f.querySelector('button[type="submit"],button:not(.btn-close)');if(b&&b.textContent.toLowerCase().includes('submit')){b.disabled=true;b.innerHTML='<span class="spinner-border spinner-border-sm me-2"></span>Processing...'}}));});


// MahaSkill global feedback toasts
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.toast').forEach(function(el){
    try { new bootstrap.Toast(el, {delay:4500, autohide:true}).show(); } catch(e) {}
  });
});
