const state = JSON.parse(localStorage.getItem('smartyState') || '{}');
state.points ??= 0; state.subjects ??= []; state.flashcards ??= []; state.events ??= []; state.history ??=[];
state.goalPoints ??= 200; state.style ??='Classic Buddy'; state.mode ??='Study';

const upgrades=[{name:'Neon Hero',cost:120},{name:'Cyber Friend',cost:250},{name:'Anime Mentor',cost:400}];
const slogans=['Tiny steps, giant glow-up 🚀','Brains loading... almost legendary 🧠','You + effort = unstoppable 🔥'];

const $ = id => document.getElementById(id);
const chatLog=$('chatLog');
function save(){localStorage.setItem('smartyState',JSON.stringify(state));render();}
function say(text,speak=true){chatLog.innerHTML += `<p><b>Smarty:</b> ${text}</p>`; chatLog.scrollTop=chatLog.scrollHeight; if(speak && 'speechSynthesis' in window){speechSynthesis.speak(new SpeechSynthesisUtterance(text));}}
function user(text){chatLog.innerHTML += `<p><b>You:</b> ${text}</p>`; chatLog.scrollTop=chatLog.scrollHeight;}

function askStartChat(){
  const today=new Date().toISOString().slice(0,10);
  const plans=state.events.filter(e=>e.date===today).map(e=>`${e.title} (${e.type})`).join(', ')||'Default study 90 min';
  say(`Hey friend! Today's plan: ${plans}. Want to add anything else?`);
  say('Quick check-in: energy level 1-5 and what topic feels hardest today?');
}

let timer={running:false,phase:'Study',left:30*60,totalLeft:90*60,int:null};
function resetTimer(){timer.left=(+$('studyMin').value)*60; timer.phase='Study'; timer.totalLeft=(+$('sessionMin').value)*60; drawTimer();}
function drawTimer(){const m=String(Math.floor(timer.left/60)).padStart(2,'0'); const s=String(timer.left%60).padStart(2,'0'); $('timerDisplay').textContent=`${m}:${s}`; $('timerPhase').textContent=`Phase: ${timer.phase}`;}
function motivational(){say(slogans[Math.floor(Math.random()*slogans.length)]);}
function tick(){
  if(!timer.running)return;
  timer.left--; timer.totalLeft--; drawTimer();
  if(timer.totalLeft%600===0) motivational();
  if(timer.left<=0){
    if(timer.phase==='Study'){
      const hard=state.subjects.some(s=>s.progress<40);
      if(hard && Math.random()>0.5){say('You are doing great! Taking an early 3-min break for focus reset.'); timer.left=3*60; timer.phase='Break';}
      else{timer.left=(+$('breakMin').value)*60; timer.phase='Break'; say('Break time 🌈 Stretch + water!');}
    } else {timer.left=(+$('studyMin').value)*60; timer.phase='Study'; say('Back in! Let\'s crush the next sprint ⚡');}
  }
  if(timer.totalLeft<=0){
    clearInterval(timer.int); timer.running=false;
    state.points += 40; state.history.unshift({date:new Date().toLocaleString(),note:'Completed full session',pts:+40});
    say('Session complete! +40 points. Proud of you 💖'); save();
  }
}

function addDefaultEvent(){
  const today = new Date();
  for(let i=0;i<14;i++){
    const d=new Date(today); d.setDate(today.getDate()+i);
    const key=d.toISOString().slice(0,10);
    if(!state.events.find(e=>e.date===key && e.title==='Default Study Session')) state.events.push({title:'Default Study Session (90m incl breaks)',date:key,type:'Study'});
  }
}

function render(){
  $('points').textContent=state.points; $('goalPoints').value=state.goalPoints; $('styleCurrent').textContent=`Current style: ${state.style}`;
  $('goalStatus').textContent=`Goal: ${state.goalPoints} points (${Math.max(state.goalPoints-state.points,0)} to go)`;
  $('subjects').innerHTML=state.subjects.map((s,i)=>`<li>${s.name}: ${s.progress}% <button onclick="updateSub(${i})">Update</button></li>`).join('');
  $('flashcards').innerHTML=state.flashcards.map(fc=>`<li><b>${fc.front}</b> → ${fc.back}</li>`).join('');
  $('events').innerHTML=state.events.sort((a,b)=>a.date.localeCompare(b.date)).map(e=>`<li class="${e.type.toLowerCase()}">${e.date} - ${e.title} (${e.type})</li>`).join('');
  $('history').innerHTML=state.history.map(h=>`<li>${h.date}: ${h.note} (${h.pts>0?'+':''}${h.pts} pts)</li>`).join('');
  $('store').innerHTML=upgrades.map(u=>`<button onclick="buyUpgrade('${u.name}',${u.cost})">${u.name} (${u.cost})</button>`).join('');
}
window.updateSub=(i)=>{const val=+prompt('Progress % now?'); if(!Number.isNaN(val)){state.subjects[i].progress=Math.min(100,Math.max(0,val)); save();}}
window.buyUpgrade=(name,cost)=>{if(state.points>=cost){state.points-=cost; state.style=name; say(`Style upgraded to ${name}! Looking awesome 😎`); save();}else say('Not enough points yet — keep going!');}

$('sendBtn').onclick=()=>{const txt=$('chatInput').value.trim(); if(!txt)return; user(txt); $('chatInput').value='';
  if(/explain/i.test(txt)) say('Got it! I can explain in a quick and fun way. Tell me the exact topic.');
  else if(/check answer/i.test(txt)) say('Sure! Paste your answer and the correct one, and I will compare it quickly.');
  else say('Love that! Next mini-question: what is one key idea from your syllabus in 1 sentence?');
};
$('micBtn').onclick=()=>{if(!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)){say('Speech recognition not supported in this browser.'); return;} const SR=window.SpeechRecognition||window.webkitSpeechRecognition;const rec=new SR();rec.onresult=e=>{$('chatInput').value=e.results[0][0].transcript;};rec.start();};
$('startTimer').onclick=()=>{if(timer.running)return; timer.running=true; if(!timer.int) timer.int=setInterval(tick,1000); say('Session started! Quick update: what is today\'s goal?');};
$('pauseTimer').onclick=()=>{timer.running=false; say('Paused. Want a quick recap quiz while paused?');};
$('endEarly').onclick=()=>{timer.running=false; state.points=Math.max(0,state.points-20); state.history.unshift({date:new Date().toLocaleString(),note:'Ended early',pts:-20}); say('Session ended early, -20 points. No stress — restart when ready 💪'); save();};
$('addSubject').onclick=()=>{const n=$('subjectName').value.trim(); if(n){state.subjects.push({name:n,progress:0}); $('subjectName').value=''; save();}};
$('addCard').onclick=()=>{const f=$('fcFront').value.trim(),b=$('fcBack').value.trim(); if(f&&b){state.flashcards.push({front:f,back:b}); $('fcFront').value=''; $('fcBack').value=''; save();}};
$('addEvent').onclick=()=>{const t=$('eventTitle').value.trim(); const d=$('eventDate').value; const ty=$('eventType').value; if(t&&d){state.events.push({title:t,date:d,type:ty}); save();}};
$('saveGoal').onclick=()=>{state.goalPoints=+$('goalPoints').value||200; save();};
$('studyMode').onclick=()=>{state.mode='Study'; say('Study mode on: flashcards + revision + short explanations only when asked.'); save();};
$('homeworkMode').onclick=()=>{state.mode='Homework'; say('Homework mode on: upload image, ask questions, and I will keep you on time.'); save();};
$('homeworkImage').onchange=e=>{const file=e.target.files[0]; if(file){$('preview').src=URL.createObjectURL(file); say('Image received! Ask your question about it.');}};

addDefaultEvent(); resetTimer(); render(); askStartChat();
