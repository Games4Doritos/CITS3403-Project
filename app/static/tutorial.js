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

const groundSprites = ["rock1", "rock2", "toxicSpill"];
const groundDimensions = [{"w":50,"h":30}, {"w":40,"h":46}, {"w":50,"h":15}];

const skySprites = ["drone", "lightningCloud"];
const skyDimensions = [{"w":40, "h":30}, {"w":50, "h":30}]

class tutorialPlayer {
    static{
        this.baseY = tutorialPlayerCanvas.height / 2;
    }

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
        this.jumpCount = 0;
        this.jumping = false;
    }
    draw(context){
        context.drawImage(this.sprite, this.x, this.y, 50, 55);
    }
    update(context){
        if (this.jumping){
            
            //velocity will start at -13, decelerate to 0, then accelerate to 13 (standard parabolic jump)
            //total jump height = 0.5 * (13) *(13+1) = 78
            //has been adjusted using deltatime to follow the function f(t) = -1/2 * t^2 + 13t - 6.5 (matches above behaviour)
            const now = performance.now();
            const t = (now - this.jumpTime) / 20;
            if (t >= 25.5){
                this.jumping = false;
                this.y = tutorialPlayer.baseY;
                return;
            }
            this.y = tutorialPlayer.baseY - (-0.5 * t * t + 13 * t - 6.5);  
        }
        this.draw(context);
    }
    jump(){
        if (!this.jumping){
            this.jumping = true;
            this.jumpTime = performance.now();
            this.jumpCount++;
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
    constructor( yState){
        if (yState === "sky"){
            this.y = tutorialCanvas.height/2 - 100;
        }
        else if (yState === "ground"){
            this.y = tutorialCanvas.height/2;
        }
        this.x = tutorialCanvas.width + 50;
        this.sprite = new Image();
        this.sprite.src = `/static/assets/drone.png`;
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
const groundImage = new Image();
groundImage.src = "/static/assets/ground.png";
const backImage = new Image();
backImage.src = "/static/assets/backGround.png";

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
            tutorialObstacles.push(new tutorialObstacle("ground"));
        } else {
            tutorialObstacles.push(new tutorialObstacle("sky"));
        }
        objCount++;
    }
    else if (objCount < 5 && Math.random() < 0.1 && tutorialObstacles[tutorialObstacles.length-1].x < tutorialCanvas.width - tutorialObstacle.spacing){
        if (Math.random() < 0.5){
            tutorialObstacles.push(new tutorialObstacle("ground"));
        } else {
            tutorialObstacles.push(new tutorialObstacle("sky"));
        }
        objCount++;
    }

    // Update obstacles and player
    tutorialCtx.drawImage(backImage, 0,20, tutorialCanvas.width, 160)
    tutorialObstacles.forEach(obs => obs.update(tutorialCtx));
    curTutorialPlayer.update(tutorialPlayerCtx);

    tutorialAnimationID = requestAnimationFrame(tutorialFrame);
}

window.addEventListener('keypress', (event) => {
    if (event.code === 'Space'){
        event.preventDefault();
        curTutorialPlayer.jump();
    }
});

tutorialAnimationID = requestAnimationFrame(tutorialFrame);