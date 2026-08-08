const links=[...document.querySelectorAll('.nav-link[href^="#"]')];
const sections=[...document.querySelectorAll('section[id]')];

function updateActive(){
  const y=window.scrollY+110;
  let current='overview';
  for(const section of sections){if(section.offsetTop<=y) current=section.id;}
  links.forEach(link=>link.classList.toggle('active',link.getAttribute('href')===`#${current}`));
}

window.addEventListener('scroll',updateActive,{passive:true});
updateActive();

document.querySelectorAll('button').forEach(button=>{
  button.addEventListener('click',()=>{
    if(button.disabled)return;
    button.animate([{transform:'scale(.97)'},{transform:'scale(1)'}],{duration:130,easing:'ease-out'});
  });
});
