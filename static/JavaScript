// variaveis globais
let nav = 0
let clicked = null
let events = localStorage.getItem('events') ? JSON.parse(localStorage.getItem('events')) : []

const newEvent = document.getElementById('newEventModal')
const deleteCalendarEventModal = document.getElementById('deleteCalendarEventModal')
const backDrop = document.getElementById('modalBackDrop')
const eventTitleInput = document.getElementById('eventTitleInput')
const calendar = document.getElementById('calendar')
const weekdays = ['domingo','segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado']
const fileInput = document.getElementById('receiptFile');

/* Calendar */
// Creating the calendar
function load (){ 
  const date = new Date() 
  
  //mudar titulo do mês:
  if(nav !== 0){
    date.setMonth(new Date().getMonth() + nav) 
  }
  
  const day = date.getDate()
  const month = date.getMonth()
  const year = date.getFullYear()
  const daysMonth = new Date (year, month + 1 , 0).getDate()
  const firstDayMonth = new Date (year, month, 1)
  const dateString = firstDayMonth.toLocaleDateString('pt-br', {
    weekday: 'long',
    year:    'numeric',
    month:   'numeric',
    day:     'numeric',
  })
  
  const paddinDays = weekdays.indexOf(dateString.split(', ') [0])
  
  //mostrar mês e ano:
  document.getElementById('monthDisplay').innerText = `${date.toLocaleDateString('pt-br',{month: 'long'})}, ${year}`

  calendar.innerHTML =''

  // criando uma div com os dias:
  for (let i = 1; i <= paddinDays + daysMonth; i++) {
    const dayS = document.createElement('div')
    dayS.classList.add('day')

    const dayString = `${month + 1}/${i - paddinDays}/${year}`

    //condicional para criar os dias de um mês:
    if (i > paddinDays) {
      dayS.innerText = i - paddinDays
      
      const eventDay = events.find(event=>event.date === dayString)
      
      if(i - paddinDays === day && nav === 0){
        dayS.id = 'currentDay'
      }

      if(eventDay){
        const eventDiv = document.createElement('div')
        eventDiv.classList.add('event')
        eventDiv.innerText = eventDay.title
        dayS.appendChild(eventDiv)
      }

      dayS.addEventListener('click', ()=> openCalendarModal(dayString))

    } else {
      dayS.classList.add('padding')
    }
    
    calendar.appendChild(dayS)
  }
}

/* Cria evento ou exibe o evento ja criado na data selecionada */
function openCalendarModal(date){
  clicked = date
  const eventDay = events.find((event)=>event.date === clicked)
 
  if (eventDay){
   document.getElementById('eventText').innerText = eventDay.title
   deleteCalendarEventModal.style.display = 'flex'
  } else {
    newEvent.style.display = 'flex'
  }

  backDrop.style.display = 'flex'
}

function closeCalendarModal(){
  eventTitleInput.classList.remove('error')
  newEvent.style.display = 'none'
  backDrop.style.display = 'none'
  deleteCalendarEventModal.style.display = 'none'

  eventTitleInput.value = ''
  clicked = null
  load()
}

function saveCalendarEvent(){
  if(eventTitleInput.value){
    eventTitleInput.classList.remove('error')

    events.push({
      date: clicked,
      title: eventTitleInput.value
    })

    localStorage.setItem('events', JSON.stringify(events))
    closeCalendarModal()
  }else{
    eventTitleInput.classList.add('error')
  }
}

function deleteCalendarEvent(){
  events = events.filter(event => event.date !== clicked)
  localStorage.setItem('events', JSON.stringify(events))
  closeCalendarModal()
}

// botões
function buttons (){
  document.getElementById('backButton').addEventListener('click', ()=>{
    nav--
    load()
  })
  document.getElementById('nextButton').addEventListener('click',()=>{
    nav++
    load()
  })
  document.getElementById('saveButton').addEventListener('click',()=> saveCalendarEvent())
  document.getElementById('cancelButton').addEventListener('click',()=>closeCalendarModal())
  document.getElementById('deleteButton').addEventListener('click', ()=>deleteCalendarEvent())
  document.getElementById('closeButton').addEventListener('click', ()=>closeCalendarModal())
}

// Fechar modal upload e calendario
window.onclick = function(event) {
  if (event.target === newEvent || event.target === deleteCalendarEventModal) {
    closeCalendarModal()
  }
  if(event.target === document.getElementById('modalUpload')){
    closeUploadModal()
  }
}

buttons()
load()

/* Modal upload comprovante */
function openUploadModal() {
  document.getElementById('modalUpload').style.display = 'flex';
}
// Close upload modal
function closeUploadModal() {
  document.getElementById('modalUpload').style.display = 'none';
}

/* Carrossel */
function scrollCarousel(direction) {
  const carousel = document.getElementById('carrossel');
  const scrollAmount = 1200;

  carousel.scrollBy({
    left: direction * scrollAmount,
    behavior: 'smooth'
  });
}
