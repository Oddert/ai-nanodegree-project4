const WRITE_MIN_DELAY = 10
const WRITE_DELAY_RANGE = 120

const write = (target, text) => {
    let partial = ''
    const writePartial = (idx) => {
        partial += text[idx]
        target.textContent = partial
        if (partial.length < text.length) {
            setTimeout(() => 
                writePartial(idx + 1),
                WRITE_MIN_DELAY + Math.random() * WRITE_DELAY_RANGE,
            )
        }
    }
    writePartial(0)
}

const toggleExpanded = () => {
    const target = document.querySelector('main')
    target.classList.toggle('expanded')
}

const bindEventListeners = () => {
    console.log('????')
    const beginButton = document.querySelector('.entry-buttons_begin')
    console.log(beginButton)
    beginButton.onclick = toggleExpanded
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
