const backCanvas = document.getElementById('backCanvas');
const obstacleCanvas = document.getElementById('gameCanvas');
const playerCanvas = document.getElementById('playerCanvas');
const obstacleCtx = gameCanvas.getContext('2d');
const playerCtx = playerCanvas.getContext('2d');
const backCtx = backCanvas.getContext('2d');

obstacleCanvas.width = gameCanvas.clientWidth;
obstacleCanvas.height = gameCanvas.clientHeight;
playerCanvas.width = playerCanvas.clientWidth;
playerCanvas.height = playerCanvas.clientHeight;
backCanvas.width = backCanvas.clientWidth;
backCanvas.height = backCanvas.clientHeight;

const groundSprites = ["rock1", "rock2", "toxicSpill"];
const groundDimensions = [{"w":50,"h":30}, {"w":40,"h":46}, {"w":50,"h":15}];

const skySprites = ["drone", "lightningCloud"];
const skyDimensions = [{"w":40, "h":30}, {"w":50, "h":30}]

class player{
    // dimensions of player are currently 50 x 55
    static {
        this.baseY = playerCanvas.height/2;
    }
    x;
    y;
    sprite;
    jumpMemory;
    lastTime;
    jumpCount;
    constructor(){
        this.x = playerCanvas.width*0.1;
        this.y = player.baseY;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/technoChicken.png";
        //Dimensions of sprite: 40x60
        this.jumping= false;
        this.jumpTime;
        this.jumpCount = 0;
        this.sprite.onload = () => {
            playerCtx.drawImage(this.sprite,this.x - 50,this.y,50,55)
        }
    }
    initialAnim(context){
        let startX = this.x - 50;
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
            x = startX + t * 0.001 * 100
            playerCtx.clearRect(0, 0, playerCanvas.width, playerCanvas.height);
            playerCtx.drawImage(this.sprite,x,this.y,50,55);
            
            animID = requestAnimationFrame(initialFrame);

        }
        animID = requestAnimationFrame(initialFrame);
        
    }
    draw(context){
        context.drawImage(this.sprite,this.x,this.y,50,55);
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
                this.y = player.baseY;
                return;
            }
            this.y = player.baseY - (-0.5 * t * t + 13 * t - 6.5);
            
        }
        else{
            bonusMultiplier = 0;
        }
        this.draw(context);
    }
    jump(){
        if (!this.jumping){
            this.jumping = true;
            this.jumpTime = performance.now();
            bonusMultiplier = 0.5
            this.jumpCount++;
        }
    }
}

class obstacle{
    y;
    x;
    sprite;
    alive;
    lastTime;
    w;
    h;
    static {
        this.speed = 1/128;
        this.spacing = 200;
    }
    constructor(yState){
        this.sprite = new Image();
        if (yState === "sky"){
            
            let choice = Math.floor(Math.random()*1.9);
            this.sprite.src = `/static/assets/${skySprites[choice]}.png`;
            this.w = skyDimensions[choice].w;
            this.h = skyDimensions[choice].h;
            this.y = obstacleCanvas.height/2 - 100 +  (55-this.h);
        }
        else if (yState === "ground"){
            let choice = Math.floor(Math.random()*2.9);
            this.sprite.src = `/static/assets/${groundSprites[choice]}.png`;
            this.w = groundDimensions[choice].w;
            this.h = groundDimensions[choice].h;
            this.y = obstacleCanvas.height/2 + (55-this.h);
        }
        this.x = obstacleCanvas.width + this.w;
        this.alive = true;
        this.lastTime = performance.now();
    }
    draw(context){
        context.drawImage(this.sprite,this.x,this.y,this.w,this.h);
    }
    update(context){
        if (this.x < -this.w){
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
        this.x -= (obstacleCanvas.width + 100)*obstacle.speed *deltaTime;
        this.draw(context);
    }

}

let curPlayer = new player();
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
const pauseScreen = document.getElementById("pauseScreen");
const startScreen = document.getElementById("startScreen");
const retry = document.getElementById("retry");

let score = 0;
let baseMultiplier = 1;
let bonusMultiplier = 0;

const scoreElement = document.getElementById("score");
const multiplierElement = document.getElementById("multiplier");

// draws the background and ground
const groundImage = new Image();
groundImage.src = "/static/assets/ground.png";
groundImage.onload = () => {
    backCtx.drawImage(groundImage, 0, player.baseY + 30, obstacleCanvas.width, 80);
}
const backImage = new Image();
backImage.src = "/static/assets/backGround.png";
backImage.onload = () => {
    backCtx.drawImage(backImage, 0, 10, obstacleCanvas.width, 160);
}


function frame(){
    let count = 0;
    obstacleCanvas.width = obstacleCanvas.clientWidth;
    obstacleCanvas.height = obstacleCanvas.clientHeight;
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
            obstacles.push(new obstacle("ground"));
        }
        else{
            obstacles.push(new obstacle("sky"));
        }
        objCount++;
    }
    else if (objCount < 5 && Math.random() < 0.1 && obstacles[obstacles.length-1].x < obstacleCanvas.width - obstacle.spacing){
        if (Math.random() < 0.5){
            obstacles.push(new obstacle("ground"));
        }
        else{
            obstacles.push(new obstacle("sky"));
        }
        objCount++;
    }
    if (dead){
        return;
    }
    obstacleCtx.clearRect(0, 0, obstacleCanvas.width, player.baseY);
    playerCtx.clearRect(0, 0, playerCanvas.width, playerCanvas.height);

    const now = performance.now();
    const deltaTime = now - lastTime;
    const runDuration = now - runStart - pausedTime;

    // convert baseMultiplier to seconds and divide by 20 (increases every 20 seconds)
    // baseMultiplier maxes out at 5 - takes 800 seconds (~13 minutes) to reach
    baseMultiplier = Number(Math.round(1 + 0.1 * Math.min(Math.floor(runDuration * 0.00005),40) + 'e' + 1) + 'e-' + 1);
    // add baseMultiplier and bonusMultiplier together, then add bonus and debuff is active (done safely and rounded to avoid precision errors)
    let multiplier = Number(Math.round(baseMultiplier + bonusMultiplier - sabotageDebuff + dailyFriendBonus + 'e' + 1) + 'e-' + 1);
    // Make sure multiplier never goes below 0.1
    if (multiplier < 0.1) multiplier = 0.1;    
    multiplierElement.textContent = `${multiplier}`;
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
        obs.update(obstacleCtx);
    });
    
    obstacles.forEach(obs => {
        centeredPlayerX = curPlayer.x + 0.5*50;
        centeredPlayerY = curPlayer.y + 0.5*55;
        centeredObsX = obs.x + 0.5 *obs.w;
        centeredObsY = obs.y + 0.5 *obs.h;

        if (Math.abs(centeredPlayerX - centeredObsX) < 0.5*50 + 0.5*obs.w - 2 && Math.abs(centeredPlayerY - centeredObsY) <  0.5*55 + 0.5*obs.h -2){
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

    retry.style.display = "flex";
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
    curPlayer.initialAnim(playerCtx);
    
}

function jumpHandle(event){
    if ((event.type === 'mousedown' || event.key === ' ' || event.key === 'Spacebar') && running){
        curPlayer.jump();
    }

}

function start(){
    runStart = performance.now();
    lastTime = runStart;
    animationID = requestAnimationFrame(frame);
    running = true;
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

function restart(){
    for  (let i =0; i< objCount;i++){
        obstacles.pop()
    }
    objCount = 0;
    running = false;

    pausedTime = 0.00;
    finalRunDuration = 0.00;
    dead = false;

    score = 0;
    baseMultiplier = 1;
    bonusMultiplier = 0;
    sabotageDebuff = 0;

    backCtx.clearRect(0,0, backCanvas.width, backCanvas.height);
    playerCtx.clearRect(0,0, playerCanvas.width, playerCanvas.height);
    obstacleCtx.clearRect(0,0, obstacleCanvas.width, obstacleCanvas.height);

    backCtx.drawImage(groundImage, 0, player.baseY + 30, obstacleCanvas.width, 80);
    backCtx.drawImage(backImage, 0, 10, obstacleCanvas.width, 160);

    const finalTime = document.getElementById("finalTime");
    const totalJumps = document.getElementById("totalJumps");
    const totalScore = document.getElementById("totalScore");
    const newCurrency = document.getElementById("newCurrency");
    finalTime.style.display = "none";
    totalJumps.style.display = "none";
    totalScore.style.display = "none";
    newCurrency.style.display = "none";
    document.getElementById("failMessage").style.display = "none";
    document.getElementById("successMessage").style.display = "none";

    gameUI.style.display = "none";
    end.style.display= "none";
    startScreen.style.display = "flex";
    multiplierElement.textContent = "1";
    scoreElement.textContent = "0";
    document.getElementById("pauseButton").style.display = "block";
    curPlayer = new player();
    retry.style.display = "none";
}