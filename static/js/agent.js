const WRITE_MIN_DELAY = 10
const WRITE_DELAY_RANGE = 120

// TODO: complete this prompt
const WELCOME_MESSAGE = 'To begin finding your property please...'

const beginButton = document.querySelector('button.entry-buttons_begin')
const homeButton = document.querySelector('button.home')
const entryButtons = document.querySelector('.entry-buttons')
const promptResponseBox = document.querySelector('.prompt-response')
const promptForm = document.querySelector('.prompt-response form')
const cursorEffect = document.querySelector('.decorative-cursor')
const history = document.querySelector('.history')

const questionPrompts = {
	step: 0,
	questions: [
		{
			message: 'what transport?',
			variableKey: 'transport',
			value: null,
		},
		{
			message: 'what size?',
			variableKey: 'size',
			value: null,
		},
		{
			message: 'what community?',
			variableKey: 'community',
			value: null,
		},
		{
			message: 'what amenities?',
			variableKey: 'amenities',
			value: null,
		},
	],
}

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

const writeMessage = (text, isSystem = false) => {
	const newMessage = document.createElement('p')
	newMessage.classList.add('message')
	history.appendChild(newMessage)
	promptResponseBox.scrollTop = promptResponseBox.scrollHeight
	if (isSystem) {
		newMessage.classList.add('system')
		write(
			newMessage,
			text,
			() => 0 + Math.random() * 40,
		)
	} else {
		newMessage.classList.add('user')
		newMessage.textContent = text
	}
}

const nextQuestion = () => {
	questionPrompts.step++
	const question = questionPrompts.questions[questionPrompts.step]
	writeMessage(question.message, true)
}

const handleUserResponse = () => {
	const userPromptMessage = promptForm.querySelector('textarea')
	questionPrompts.questions[questionPrompts.step].value = userPromptMessage.value
	writeMessage(userPromptMessage.value)
	setTimeout(() =>
		nextQuestion(userPromptMessage.value),
		1000,
	)
	userPromptMessage.value = ''
}

const bindEventListeners = () => {
	beginButton.onclick = toggleExpanded
	homeButton.onclick = toggleExpanded
	promptForm.onsubmit = (e) => e.preventDefault()
	promptResponseBox.querySelector('button[type=submit]').onclick = handleUserResponse
}

const beingLandingTitleAnimation = () => {
    const title = document.querySelector('.title-section .title')
    const titleText = title.textContent
    title.textContent = ''
    write(title, titleText)
}

const conversationStart = () => {
	setTimeout(() => writeMessage(WELCOME_MESSAGE, true), 3000)
	setTimeout(() => writeMessage(
		questionPrompts.questions[questionPrompts.step].message, true),
		5000,
	)
}

const onLoad = () => {
    beingLandingTitleAnimation()
    bindEventListeners()
	conversationStart()
}

document.addEventListener('DOMContentLoaded', onLoad)
