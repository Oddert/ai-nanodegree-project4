const WRITE_MIN_DELAY = 10
const WRITE_DELAY_RANGE = 120

const beginButton = document.querySelector('button.entry-buttons_begin')
const homeButton = document.querySelector('button.home')
const entryButtons = document.querySelector('.entry-buttons')
const promptResponseBox = document.querySelector('.prompt-response')
const promptForm = document.querySelector('.prompt-response form')
const cursorEffect = document.querySelector('.decorative-cursor')
const history = document.querySelector('.history')

const userSelectionAnswers = {
	transport: null,
	size: null,
	community: null,
	amenities: null,
}

const questionPrompts = [
	{
		message: 'what transport?',
		variableKey: 'transport',
	},
	{
		message: 'what size?',
		variableKey: 'size',
	},
	{
		message: 'what community?',
		variableKey: 'community',
	},
	{
		message: 'what amenities?',
		variableKey: 'amenities',
	},
]

const write = (
	target,
	text,
	speedFunc = () => WRITE_MIN_DELAY + Math.random() * WRITE_DELAY_RANGE,
) => {
    let partial = ''
    const writePartial = (idx) => {
        partial += text[idx]
        target.textContent = partial
        if (partial.length < text.length) {
            setTimeout(() => 
                writePartial(idx + 1),
				speedFunc(),
            )
        }
    }
    writePartial(0)
}

const toggleExpanded = () => {
    const target = document.querySelector('main')
	const wasExpanded = target.classList.contains('expanded')
	target.classList.toggle('expanded')
	if (wasExpanded) {
		entryButtons.classList.remove('hidden')
		cursorEffect.classList.remove('hidden')
		promptResponseBox.classList.add('hidden')
		homeButton.classList.add('hidden')
	} else {
		setTimeout(
			() => {
				entryButtons.classList.add('hidden')
				cursorEffect.classList.add('hidden')
				promptResponseBox.classList.remove('hidden')
				homeButton.classList.remove('hidden')
			},
			1000,
		)
	}
}

const writeMessage = (isSystem = false) => {
	const newMessage = document.createElement('p')
	newMessage.classList.add('message')
	history.appendChild(newMessage)
	promptResponseBox.scrollTop = promptResponseBox.scrollHeight
	if (isSystem) {
		newMessage.classList.add('system')
		write(
			newMessage,
			'sample text one two three',
			() => 10 + Math.random() * 10,
		)
	} else {
		newMessage.classList.add('user')
		newMessage.textContent = 'sample text one two three'
	}
}

const bindEventListeners = () => {
	beginButton.onclick = toggleExpanded
	homeButton.onclick = toggleExpanded
	promptForm.onsubmit = (e) => e.preventDefault()
	promptResponseBox.querySelector('button[type=submit]').onclick = () =>
		writeMessage(Math.floor(Math.random() * 2))
}

const beingLandingTitleAnimation = () => {
    const title = document.querySelector('.title-section .title')
    const titleText = title.textContent
    title.textContent = ''
    write(title, titleText)
}

const onLoad = () => {
    beingLandingTitleAnimation()
    bindEventListeners()
}

document.addEventListener('DOMContentLoaded', onLoad)
