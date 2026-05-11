/*
  tutorial.js
  Mini interactive demo for the landing page.
  Mirrors the actual game - fixed player position, jump to avoid obstacles.
  No score, no game over - just feel the controls.
*/

const tutorialCanvas = document.getElementById('tutorialCanvas');
const tutorialCtx = tutorialCanvas.getContext('2d');

tutorialCanvas.width = tutorialCanvas.clientWidth;
tutorialCanvas.height = tutorialCanvas.clientHeight;

let bonusMultiplier = 0;

class TutorialPlayer {
    constructor(){
        this.x = tutorialCanvas.width * 0.1;
        this.y = tutorialCanvas.height * 0.65 - 60;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/technoChicken.png";
        this.jumpMemory = -1;
        this.jumpCount = 0;
    }
    draw(context){
        context.drawImage(this.sprite, this.x, this.y, 40, 60);
    }
    update(context){
        // Jump physics (exact same as main game)
        if (this.jumpMemory > -1){
            this.y -= (this.jumpMemory - 13);
            this.jumpMemory--;
        }
        else{
            bonusMultiplier = 0;
        }

        // Keep player above ground
        const groundY = tutorialCanvas.height * 0.65 - 60;
        if (this.y > groundY){
            this.y = groundY;
            this.jumpMemory = -1;
        }

        this.draw(context);
    }
    jump(){
        if (this.jumpMemory == -1){
            bonusMultiplier = 0.5;
            this.jumpCount++;
            this.jumpMemory = 26;
        }
    }
}

class TutorialObstacle {
    constructor(yState){
        this.x = tutorialCanvas.width + 50;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/random.png";
        this.alive = true;
        this.lastTime = performance.now();

        if (yState === "sky"){
            this.y = tutorialCanvas.height * 0.65 - 110;
        } else {
            this.y = tutorialCanvas.height * 0.65 - 50;
        }
    }
    draw(context){
        context.drawImage(this.sprite, this.x, this.y, 50, 50);
    }
    update(context){
        const now = performance.now();
        const deltaTime = (now - this.lastTime) * 0.06;
        this.lastTime = now;

        // Slower speed than main game so it's easier for tutorial
        this.x -= (tutorialCanvas.width + 100) * 0.004 * deltaTime;

        if (this.x < -50){
            this.alive = false;
        }

        this.draw(context);
    }
}

// Input handling
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space'){
        tutorialPlayer.jump();
        e.preventDefault();
    }
});

const tutorialPlayer = new TutorialPlayer();
let tutorialObstacles = [];
let lastObstacleTime = performance.now();

function drawGround(){
    const groundY = tutorialCanvas.height * 0.65;
    tutorialCtx.shadowColor = '#8E4DE4';
    tutorialCtx.shadowBlur = 15;
    tutorialCtx.fillStyle = '#5D05EA';
    tutorialCtx.fillRect(0, groundY, tutorialCanvas.width, 10);
    tutorialCtx.shadowBlur = 0;
}

function drawControls(){
    tutorialCtx.font = 'bold 16px Arial';
    tutorialCtx.fillStyle = 'rgba(142, 77, 228, 0.8)';
    tutorialCtx.textAlign = 'center';
    tutorialCtx.fillText('SPACE to jump', tutorialCanvas.width * 0.5, tutorialCanvas.height * 0.65 + 40);
}

function spawnObstacle(){
    const now = performance.now();
    // Spawn a new obstacle every 3 seconds
    if (now - lastObstacleTime > 3000){
        const yState = Math.random() < 0.5 ? "ground" : "sky";
        tutorialObstacles.push(new TutorialObstacle(yState));
        lastObstacleTime = now;
    }
}

function tutorialFrame(){
    tutorialCanvas.width = tutorialCanvas.clientWidth;
    tutorialCanvas.height = tutorialCanvas.clientHeight;

    tutorialCtx.clearRect(0, 0, tutorialCanvas.width, tutorialCanvas.height);

    drawGround();

    // Spawn and update obstacles
    spawnObstacle();
    tutorialObstacles = tutorialObstacles.filter(obs => obs.alive);
    tutorialObstacles.forEach(obs => obs.update(tutorialCtx));

    // Update player
    tutorialPlayer.update(tutorialCtx);

    drawControls();

    requestAnimationFrame(tutorialFrame);
}

tutorialFrame();