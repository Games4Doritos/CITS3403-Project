const gameCanvas = document.getElementById('gameCanvas');
const playerCanvas = document.getElementById('playerCanvas');
const gameCtx = gameCanvas.getContext('2d');
const playerCtx = playerCanvas.getContext('2d');

gameCanvas.width = gameCanvas.clientWidth;
gameCanvas.height = gameCanvas.clientHeight;
playerCanvas.width = playerCanvas.clientWidth;
playerCanvas.height = playerCanvas.clientHeight;

class player{
    x;
    y;
    sprite;
    jumpMemory;
    lastTime;
    jumpCount;
    constructor(){
        this.x = playerCanvas.width*0.1;
        this.y = playerCanvas.height/2;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/technoChicken.png";
        //Dimensions of sprite: 40x60
        this.jumpMemory = -1;
        this.lastTime = performance.now();
        this.jumpCount = 0;
        this.sprite.onload = () => {
            playerCtx.drawImage(this.sprite,this.x - 40,this.y,40,60)
        }
    }
    initialAnim(context){
        let startX = this.x - 40;
        let x = startX;
        let runStart = performance.now();
        let lastTime = runStart;
        let animID;

        const initialFrame = () => {
            
            const now = performance.now();
        
            if (now-runStart >= 500){
                cancelAnimationFrame(animID);
                start();
                return;
            }
            lastTime = now;
            const t = now-runStart;

            //x = startX + (t < 250 ? t * t * 0.000192: (t) * (t) * 0.000192);
            x = startX + t * 0.001 * 80
            playerCtx.clearRect(0, 0, playerCanvas.width, playerCanvas.height);
            playerCtx.drawImage(this.sprite,x,this.y,40,60);
            
            animID = requestAnimationFrame(initialFrame);

        }
        animID = requestAnimationFrame(initialFrame);
        
    }
    draw(context){
        context.drawImage(this.sprite,this.x,this.y,40,60);
    }
    update(context){

        if (this.jumpMemory >-1){
            //velocity will start at -13, decelerate to 0, then accelerate to 13 (standard parabolic jump)
            //total jump height = 0.5 * (13) *(13+1) = 78
            this.y -= (this.jumpMemory - 13) ;
            this.jumpMemory--;
            
        }
        else{
            bonusMultiplier = 0;
        }
        
        this.draw(context);
    }
    jump(){
        if (this.jumpMemory == -1){
            bonusMultiplier = 0.5
            this.jumpCount++;
            this.jumpMemory = 26; 
        }
    }
}

class obstacle{
    y;
    x;
    sprite;
    alive;
    lastTime;
    static {
        this.speed = 1/128;
        this.spacing = 200;
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
        this.sprite.src = `/static/assets/${type}.png`;
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
        this.x -= (gameCanvas.width + 100)*obstacle.speed *deltaTime;
        this.draw(context);
    }

}

curPlayer = new player();
let objCount = 0;
const obstacles = [];
let animationID;
let running = true;

let runStart;
let lastTime;
let pausedTime = 0.00;
let finalRunDuration;

let dead = false;
const gameUI = document.getElementById("gameUI");
const end = document.getElementById("end");
const pauseScreen = document.getElementById("pauseScreen")

let score = 0;
let baseMultiplier = 1;
let bonusMultiplier = 0;

const scoreElement = document.getElementById("score");
const multiplierElement = document.getElementById("multiplier");

function frame(){
    let count = 0;
    gameCanvas.width = gameCanvas.clientWidth;
    gameCanvas.height = gameCanvas.clientHeight;
    playerCanvas.width = playerCanvas.clientWidth;
    playerCanvas.height = playerCanvas.clientHeight;

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
            obstacles.push(new obstacle("random", "ground"));
        }
        else{
            obstacles.push(new obstacle("random", "sky"));
        }
        objCount++;
    }
    else if (objCount < 5 && Math.random() < 0.1 && obstacles[obstacles.length-1].x < gameCanvas.width - obstacle.spacing){
        if (Math.random() < 0.5){
            obstacles.push(new obstacle("random", "ground"));
        }
        else{
            obstacles.push(new obstacle("random", "sky"));
        }
        objCount++;
    }
    if (dead){
        return;
    }
    gameCtx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    playerCtx.clearRect(0, 0, playerCanvas.width, playerCanvas.height);

    const now = performance.now();
    const deltaTime = now - lastTime;
    const runDuration = now - runStart - pausedTime;

    // convert baseMultiplier to seconds and divide by 20 (increases every 20 seconds)
    // baseMultiplier maxes out at 5 - takes 800 seconds (~13 minutes) to reach
    baseMultiplier = Number(Math.round(1 + 0.1 * Math.min(Math.floor(runDuration * 0.00005),40) + 'e' + 1) + 'e-' + 1);
    // add baseMultiplier and bonusMultiplier together (done safely and rounded to avoid precision errors)
    let multiplier = Number(Math.round(baseMultiplier + bonusMultiplier - sabotageDebuff + 'e' + 1) + 'e-' + 1);
    // Make sure multiplier never goes below 0.1
    if (multiplier < 0.1) multiplier = 0.1;    multiplierElement.textContent = `${multiplier}`;
    // score is 1/10 * frame time at each frame, multiplied by the multiplier
    score += (deltaTime * 0.1) * multiplier;
    scoreElement.textContent = `${Math.round(score)}`;
    lastTime = now;

    if (runDuration < 180000){
        /* All cumulative delta times will not sum exactly to runDuration (practicality),
           so max speed will be set to 0.0168125 and final min spacing will be set to 
           to prevent differing values across devices

           initial speed = 1/128
           max speed = initial speed + 180000 * 0.00000005 = 0.0078125 + 0.09 = 0.0168125

           initial min spacing = 200
           final min spacing = 200 + 180000 * 0.001 = 380

           initial 
        */
        obstacle.speed += deltaTime * 0.00000005;
        obstacle.spacing += deltaTime * 0.001;
    }
    else {
        obstacle.speed = 0.0168125;
        obstacle.spacing = 380;
    }
    curPlayer.update(playerCtx);
    obstacles.forEach(obs =>{
        obs.update(gameCtx);
    });
    
    obstacles.forEach(obs => {
        // Checks if colliding with an obstacle at every frame -> run ends if so
        if (Math.abs(curPlayer.x - obs.x) < 48 && Math.abs(curPlayer.y -obs.y) <  48){
            runEnd();
            return;
        }
    });
    if (running){
        animationID = requestAnimationFrame(frame);
    }
}

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const uploadResults = async (finalTime, totalJumps, totalScore, newCurrency) => {
    try{
        const response = await fetch("/play", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                finalTime: finalTime, 
                totalJumps: totalJumps,
                totalScore: totalScore, 
                newCurrency: newCurrency,
            }),
        });
        const data = await response.text();
        const failMessage = document.getElementById("failMessage");
        const successMessage = document.getElementById("successMessage");
        if (!end.style.display){
            return;
        }
        if (!response.ok){
            if (response.status === 400){
                failMessage.textContent = `Run Failed to Submit, are you sure it was valid?`;
            }
            else{
                failMessage.textContent = `Run Failed to Submit, Error Code: ${response.status}`;
            }
            successMessage.style.display = "none";
            failMessage.style.display="block";
        }
        else{
            failMessage.style.display="none";
            successMessage.style.display = "block";

        }
        
    }
    catch (error) {
        console.error('Error:', error);
    }
    

}

async function runEnd(){
    running = false;
    if (dead){
        return;
    }
    //rounds it to two decimal places in milliseconds
    finalRunDuration = Number(Math.round(performance.now() - runStart - pausedTime + 'e' + 2) + 'e-' + 2);
    //rounds to two decimal places in seconds
    cancelAnimationFrame(animationID); 
    dead = true;
    //get final stats
    const finalRunSeconds = Number(Math.round(finalRunDuration * 0.001 + 'e' + 2) + 'e-' + 2);
    const roundedScore = Math.round(score);
    const currency = Math.floor(roundedScore * 0.01);
    // currency will be 1/100 of the total score, rounded down

    const finalTime = document.getElementById("finalTime");
    const totalJumps = document.getElementById("totalJumps");
    const totalScore = document.getElementById("totalScore");
    const newCurrency = document.getElementById("newCurrency");
    //set final stats in appropriate elements
    finalTime.firstElementChild.textContent = `${finalRunSeconds} Seconds`;
    totalJumps.firstElementChild.textContent = `${curPlayer.jumpCount}`;
    totalScore.firstElementChild.textContent = `${roundedScore}`;
    newCurrency.firstElementChild.textContent = `${currency}`;
    
    //small animation
    document.getElementById("pauseButton").style.display = "none";
    end.style.display = "flex";
    await wait(1000);
    finalTime.style.display = "block";
    await wait(500);
    totalJumps.style.display = "block";
    await wait(500);
    totalScore.style.display = "block";
    await wait(500);
    newCurrency.style.display = "block";

    uploadResults(finalRunSeconds, curPlayer.jumpCount, roundedScore, currency);
}
function pauseButton(){
    if (dead){
        return;
        
    }
    if (running){
        lastTime = performance.now();
        cancelAnimationFrame(animationID);
        running = false;
        pauseScreen.style.display = "flex";
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
        pauseScreen.style.display = "none";
    }
}

function initialAnim(){
    document.getElementById("startScreen").style.display = "none";
    gameUI.style.display = "block";
    runStart = performance.now();
    lastTime = runStart;
    curPlayer.initialAnim(playerCtx);
    
}

function jumpHandle(event){
    if ((event.type === 'mousedown' || event.key === ' ' || event.key === 'Spacebar') && running){
        curPlayer.jump();
    }

}

function start(){
    animationID = requestAnimationFrame(frame);
    document.addEventListener('keydown', (event) => {
        jumpHandle(event);
    });
    playerCanvas.addEventListener('mousedown', (event) => {
        jumpHandle(event);
    });
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden'){
            if (running){
                pauseButton();
            }
        }
    });
}

