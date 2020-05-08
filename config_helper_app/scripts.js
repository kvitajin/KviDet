const imageLoader = document.getElementById('imageLoader');
const canvas = document.getElementById('imageCanvas');
const ctx = canvas.getContext('2d');
const vectorListEl = document.getElementById('vectorList');

let lastMouseClickPosition = {
    x: 0,
    y: 0
}

let vectors = [];

imageLoader.addEventListener('change', handleImage, false);

canvas.addEventListener('mousedown', e => {
    lastMouseClickPosition = getMousePos(canvas, e);
})

canvas.addEventListener('mouseup', e => {
    const currentMousePosition = getMousePos(canvas, e);
    const newVector = {
        id: vectors.length + 1,
        x: currentMousePosition.x - lastMouseClickPosition.x,
        y: currentMousePosition.y - lastMouseClickPosition.y
    };

    if (newVector.x === 0 && newVector.y === 0) {
        return;
    }

    ctx.beginPath();
    ctx.strokeStyle = 'red';
    canvas_arrow(ctx, lastMouseClickPosition.x, lastMouseClickPosition.y, currentMousePosition.x, currentMousePosition.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.fillStyle = 'orange';
    ctx.font = "24px serif";
    ctx.fillText(newVector.id, currentMousePosition.x + 10, currentMousePosition.y);

    vectors.push(newVector);
    const vectorItem = document.createElement('li');
    vectorItem.innerText = `x: ${newVector.x}, y: ${newVector.y}`;
    vectorListEl.appendChild(vectorItem);
});

function handleImage(e) {
    const reader = new FileReader();
    vectors = []
    vectorListEl.innerHTML = '';

    reader.onload = function (event) {
        const img = new Image();
        img.onload = function () {
            canvas.width = img.width;
            canvas.height = img.height;
            const boundingRect = ctx.canvas.getBoundingClientRect();
            ctx.scale(canvas.width / boundingRect.width, canvas.height / boundingRect.height);
            ctx.drawImage(img, 0, 0);
        }
        img.src = event.target.result;
    }
    reader.readAsDataURL(e.target.files[0]);
}

function canvas_arrow(context, fromx, fromy, tox, toy) {
    const headlen = 10; // length of head in pixels
    const dx = tox - fromx;
    const dy = toy - fromy;
    const angle = Math.atan2(dy, dx);
    context.moveTo(fromx, fromy);
    context.lineTo(tox, toy);
    context.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
    context.moveTo(tox, toy);
    context.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
}

function getMousePos(canvas, evt) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}
