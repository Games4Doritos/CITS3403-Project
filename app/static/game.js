const gameCanvas = document.getElementById('gameCanvas');
const playerCanvas = document.getElementById('playerCanvas');
const gameCtx = gameCanvas.getContext('2d');
const playerCtx = playerCanvas.getContext('2d');

gameCanvas.width = gameCanvas.clientWidth;
gameCanvas.height = gameCanvas.clientHeight;
playerCanvas.width = playerCanvas.clientWidth;
playerCanvas.height = playerCanvas.clientHeight;


class player{
    constructor(){
        this.y = playerCanvas.height/2;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/play.png";
        this.jumpMemory = -1;
        this.lastTime = performance.now();
        this.jumpCount = BigInt(0);
    }
    draw(context){
        context.drawImage(this.sprite,playerCanvas.width/2,this.y,50,50);
    }
    update(context){
        const now = performance.now();
        /*Calculation justification:
        Raw now-lastTime is in milliseconds hence * 0.001
        To converge towards 60fps since fps isn't always consistent, * 60 as 
        ideally the field will be updated 60 times per second
        */
        const deltaTime = (now - this.lastTime) * 0.06;
        this.lastTime = now;

        if (this.jumpMemory >-1){
            //velocity will start at -12, decelerate to 0, then accelerate to 12 (standard parabolic jump)
            this.y -= (this.jumpMemory - 12) ;
            this.jumpMemory--;
            
        }
        
        this.draw(context);
    }
    jump(){
        if (this.jumpMemory == -1){
            this.jumpCount++;
            this.jumpMemory = 24; 
        }
    }
}

class obstacle{
    static {
        this.lifetime = 1/128;
    }
    constructor(type, yState){
        if (yState === "sky"){
            this.y = gameCanvas.height/2 - 100;
        }
        else if (yState === "ground"){
            this.y = gameCanvas.height/2;
        }
        this.x = gameCanvas.width + 50;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/random.png";
        this.alive = true;
        this.lastTime = performance.now();
    }
    draw(context){
        context.drawImage(this.sprite,this.x,this.y,50,50);
    }
    update(context){
        if (this.x < -50){
            this.alive = false;
        }
        const now = performance.now();
        /*Calculation justification:
        Raw now-lastTime is in milliseconds hence * 0.001
        To converge towards 60fps since fps isn't always consistent, * 60 as 
        ideally the field will be updated 60 times per second
        */
        const deltaTime = (now - this.lastTime)*0.06;
        this.lastTime = now;
        this.x -= (gameCanvas.width + 100)*obstacle.lifetime *deltaTime;
        this.draw(context);
    }

}

curPlayer = new player();
let objCount = 0;
const obstacles = [];
let animationID;
let running = true;

let runStart = performance.now();
let lastTime = runStart;
let pausedTime = 0.00;
let finalRunDuration;

let dead = false;
const end = document.getElementById("end");

function frame(){
    let count = 0;
    gameCanvas.width = gameCanvas.clientWidth;
    gameCanvas.height = gameCanvas.clientHeight;

    obstacles.forEach(obs =>{
        if (!obs.alive){
            count++;
        }
    });
    for (let i =0;i<count;i++){
        obstacles.shift();
        objCount--;
    }
    if (objCount === 0){
        if (Math.random() < 0.5){
            obstacles.push(new obstacle("idk", "ground"));
        }
        else{
            obstacles.push(new obstacle("idk", "sky"));
        }
        objCount++;
    }
    else if (objCount < 5 && Math.random() < 0.1 && obstacles[obstacles.length-1].x < gameCanvas.width -200){
        
        
        if (Math.random() < 0.5){
            obstacles.push(new obstacle("idk", "ground"));
        }
        else{
            obstacles.push(new obstacle("idk", "sky"));
        }
        objCount++;
    }
    gameCtx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    playerCtx.clearRect(0, 0, playerCanvas.width, playerCanvas.height);

    const now = performance.now();
    const deltaTime = now - lastTime;
    const runDuration = now - runStart - pausedTime;
    console.log(1000/deltaTime);
    lastTime = now;

    if (runDuration < 180000){
        /* Can also do obstacle.lifetime = 1/128 + runDuration * 0.00000005
        as all deltaTimes will sum up to runDuration
        */
            obstacle.lifetime += deltaTime * 0.00000005;
    }
    curPlayer.update(playerCtx);
    obstacles.forEach(obs =>{
        obs.update(gameCtx);
    });
    if (running){
        animationID =requestAnimationFrame(frame);
    }
    

}
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function end(){
    if (dead){
        return;
    }
    //rounds it to two decimal places in milliseconds
    finalRunDuration = Number(Math.round(performance.now() - runStart + 'e' + 2) + 'e-' + 2);
    cancelAnimationFrame(animationID);
    dead = true;
    const finalTime = document.getElementById("finalTime");
    const totalJumps = document.getElementById("totalJumps");
    const totalScore = document.getElementById("totalScore");
    finalTime.textContent = `Final Time: ${(finalRunDuration*0.001).toFixed(2)} Seconds`;
    totalJumps.textContent = `Total Jumps: ${curPlayer.jumpCount}`;
    totalScore.textContent = `Total Score: ${1}`;
    end.style.display = "flex";
    await wait(1000);
    finalTime.style.display = "block";
    await wait(500);
    totalJumps.style.display = "block";
    await wait(500);
    totalScore.style.display = "block";
}
function pauseButton(){
    if (dead){
        return;
        
    }
    if (running){
        lastTime = performance.now();
        cancelAnimationFrame(animationID);
        running = false;
    }
    else {
        curPlayer.lastTime = performance.now();
        obstacles.forEach(obs => {
            obs.lastTime = performance.now();
        });
        pausedTime += performance.now() - lastTime;
        lastTime = performance.now();
        animationID = requestAnimationFrame(frame);
        running = true;
    }
}


animationID = requestAnimationFrame(frame);
window.addEventListener('keypress', (event) => {
    if (event.code === 'Space') {
        curPlayer.jump();
    }

});