/*
  tutorial.js
  Mini interactive demo for the landing page.
  Directly adapted from game.js - same physics and obstacle logic.
  No score, no game over, no pause - just feel the controls.
*/

const tutorialCanvas = document.getElementById('tutorialCanvas');
const tutorialPlayerCanvas = document.getElementById('tutorialPlayerCanvas');
const tutorialCtx = tutorialCanvas.getContext('2d');
const tutorialPlayerCtx = tutorialPlayerCanvas.getContext('2d');

tutorialCanvas.width = tutorialCanvas.clientWidth;
tutorialCanvas.height = tutorialCanvas.clientHeight;
tutorialPlayerCanvas.width = tutorialPlayerCanvas.clientWidth;
tutorialPlayerCanvas.height = tutorialPlayerCanvas.clientHeight;

class tutorialPlayer {
    x;
    y;
    sprite;
    jumpMemory;
    lastTime;
    jumpCount;
    constructor(){
        this.x = tutorialPlayerCanvas.width * 0.1;
        this.y = tutorialPlayerCanvas.height / 2;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/technoChicken.png";
        this.jumpMemory = -1;
        this.lastTime = performance.now();
        this.jumpCount = 0;
    }
    draw(context){
        context.drawImage(this.sprite, this.x, this.y, 40, 60);
    }
    update(context){
        if (this.jumpMemory > -1){
            this.y -= (this.jumpMemory - 13);
            this.jumpMemory--;
        }
        this.draw(context);
    }
    jump(){
        if (this.jumpMemory == -1){
            this.jumpCount++;
            this.jumpMemory = 26;
        }
    }
}

class tutorialObstacle {
    y;
    x;
    sprite;
    alive;
    lastTime;
    static {
        // Same speed as main game
        this.speed = 1/128;
        this.spacing = 300;
    }
    constructor(type, yState){
        if (yState === "sky"){
            this.y = tutorialCanvas.height/2 - 100;
        }
        else if (yState === "ground"){
            this.y = tutorialCanvas.height/2;
        }
        this.x = tutorialCanvas.width + 50;
        this.sprite = new Image();
        this.sprite.src = `/static/assets/${type}.png`;
        this.alive = true;
        this.lastTime = performance.now();
    }
    draw(context){
        context.drawImage(this.sprite, this.x, this.y, 50, 50);
    }
    update(context){
        if (this.x < -50){
            this.alive = false;
        }
        const now = performance.now();
        const deltaTime = (now - this.lastTime) * 0.06;
        this.lastTime = now;
        this.x -= (tutorialCanvas.width + 100) * tutorialObstacle.speed * deltaTime;
        this.draw(context);
    }
}

const curTutorialPlayer = new tutorialPlayer();
let objCount = 0;
const tutorialObstacles = [];
let tutorialAnimationID;

function drawControls(){
    tutorialCtx.font = 'bold 16px Arial';
    tutorialCtx.fillStyle = 'rgba(142, 77, 228, 0.8)';
    tutorialCtx.textAlign = 'center';
    tutorialCtx.fillText('SPACE to jump', tutorialCanvas.width * 0.5, tutorialCanvas.height * 0.85);
}

function tutorialFrame(){
    tutorialCanvas.width = tutorialCanvas.clientWidth;
    tutorialCanvas.height = tutorialCanvas.clientHeight;
    tutorialPlayerCanvas.width = tutorialPlayerCanvas.clientWidth;
    tutorialPlayerCanvas.height = tutorialPlayerCanvas.clientHeight;

    // Clear both canvases
    tutorialCtx.clearRect(0, 0, tutorialCanvas.width, tutorialCanvas.height);
    tutorialPlayerCtx.clearRect(0, 0, tutorialPlayerCanvas.width, tutorialPlayerCanvas.height);

    // Obstacle management
    let count = 0;
    tutorialObstacles.forEach(obs => {
        if (!obs.alive) count++;
    });
    for (let i = 0; i < count; i++){
        tutorialObstacles.shift();
        objCount--;
    }
    if (objCount === 0){
        if (Math.random() < 0.5){
            tutorialObstacles.push(new tutorialObstacle("random", "ground"));
        } else {
            tutorialObstacles.push(new tutorialObstacle("random", "sky"));
        }
        objCount++;
    }
    else if (objCount < 5 && Math.random() < 0.1 && tutorialObstacles[tutorialObstacles.length-1].x < tutorialCanvas.width - tutorialObstacle.spacing){
        if (Math.random() < 0.5){
            tutorialObstacles.push(new tutorialObstacle("random", "ground"));
        } else {
            tutorialObstacles.push(new tutorialObstacle("random", "sky"));
        }
        objCount++;
    }

    // Update obstacles and player
    tutorialObstacles.forEach(obs => obs.update(tutorialCtx));
    curTutorialPlayer.update(tutorialPlayerCtx);

    // Draw controls hint
    drawControls();

    tutorialAnimationID = requestAnimationFrame(tutorialFrame);
}

window.addEventListener('keypress', (event) => {
    if (event.code === 'Space'){
        curTutorialPlayer.jump();
    }
});

tutorialAnimationID = requestAnimationFrame(tutorialFrame);