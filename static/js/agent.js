const WRITE_MIN_DELAY = 10
const WRITE_DELAY_RANGE = 120

const WELCOME_MESSAGE = 'To begin finding your property I\'ll first need to ask you a few questions...'

const beginButton = document.querySelector('button.entry-buttons_begin')
const homeButton = document.querySelector('button.home')
const entryButtons = document.querySelector('.entry-buttons')
const promptResponseBox = document.querySelector('.prompt-response')
const promptForm = document.querySelector('.prompt-response form')
const userPromptMessage = promptForm.querySelector('textarea')
const cursorEffect = document.querySelector('.decorative-cursor')
const history = document.querySelector('.history')

const questionPrompts = {
	step: 0,
	questions: [
		{
			message: 'What are you\'re transport priorities? What connections would you need and how would you be looking to get around?',
			variableKey: 'transport',
			value: null,
		},
		{
			message: 'What size of a property would you be looking for? How many bedrooms and bathrooms? Any other must-haves?',
			variableKey: 'size',
			value: null,
		},
		{
			message: 'How would you describe the community and local scene in your perfect world?',
			variableKey: 'community',
			value: null,
		},
		{
			message: 'Are there any amenities or local features that you\'d need near by?',
			variableKey: 'amenities',
			value: null,
		},
	],
}

let acceptUserResponse = true;
let finishButtonsActive = false;

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

const handleSubmitResponse = async (container) => {
	writeMessage('Great! Let me have a look and see what I can find...', true)
	const response = await fetch(
		'/recommender',
		{
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(
					questionPrompts.questions.reduce(
					(accumulator, question) => {
						accumulator[question.variableKey] = question.value
						return accumulator
					},
					{
						transport: null,
						community: null,
						size: null,
						amenities: null,
					}
				)
			)
		},
	)
	const llmAnswer = await response.json()
	console.log(llmAnswer)
	writeMessage(llmAnswer.response, true, () => 0 + Math.random() * 10)
	container.remove()
	finishButtonsActive = false
}

const handleStartAgain = (container) => {
	questionPrompts.questions.forEach((question) => question.value = '')
	questionPrompts.step = 0
	acceptUserResponse = true
	writeMessage('No problem! Lets start again...', true)
	setTimeout(() => writeMessage(
		questionPrompts.questions[questionPrompts.step].message,
		true
	), 2000)
	container.remove()
	finishButtonsActive = false
}

const createFinishedButtons = () => {
	write('Thanks for that, are you happy with these answers of would you like to start over?', true)

	const container = document.createElement('div')
	const acceptButton = document.createElement('button')
	const startAgainButton = document.createElement('button')
	
	finishButtonsActive = true

	acceptButton.textContent = 'Begin Search'
	startAgainButton.textContent = 'Start Over'

	acceptButton.onclick = () => handleSubmitResponse(container)
	startAgainButton.onclick = () => handleStartAgain(container)

	acceptButton.style.marginLeft = '20px'
	acceptButton.classList.add('contained')

	container.appendChild(startAgainButton)
	container.appendChild(acceptButton)
	history.appendChild(container)
	promptResponseBox.scrollTop = promptResponseBox.scrollHeight
}

const handleUserResponse = () => {
	if (userPromptMessage.value === '') {
		return
	}

	if (acceptUserResponse) {
		questionPrompts.questions[questionPrompts.step].value = userPromptMessage.value
		writeMessage(userPromptMessage.value)
		userPromptMessage.value = ''
	}

	if (questionPrompts.step + 1 >= questionPrompts.questions.length) {
		if (!finishButtonsActive) {
			acceptUserResponse = false
			createFinishedButtons()
		}
	} else {
		setTimeout(() =>
			nextQuestion(userPromptMessage.value),
			1000,
		)
	}
}

const bindEventListeners = () => {
	beginButton.onclick = toggleExpanded
	homeButton.onclick = toggleExpanded
	promptForm.onsubmit = (e) => e.preventDefault()
	promptResponseBox.querySelector('button[type=submit]').onclick = handleUserResponse
	userPromptMessage.addEventListener('keypress', (e) => {
		if (e.key === 'Enter') {
			e.preventDefault()
			handleUserResponse()
		}
	})
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
