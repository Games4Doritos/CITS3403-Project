const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
canvas.width = canvas.clientWidth;
canvas.height = canvas.clientHeight;


class player{
    constructor(){
        this.y = canvas.height/2;
        this.dy = 0;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/play.png";
        this.jumpMemory = 0;
    }
    draw(context){
        context.drawImage(this.sprite,canvas.width/2,this.y,50,50);
    }
    update(context){
        if (this.jumpMemory >0){
            //velocity will start at -15, decelerate to 0, then accelerate to 15 (standard parabolic jump)
            this.y -= this.jumpMemory - 15
            this.jumpMemory--;
            if (this.jumpMemory === 0){
                this.y += 15;
            }
        }
        
        this.draw(context);
    }
    jump(){
        if (this.jumpMemory == 0){
            this.jumpMemory = 30; 
        }
    }
}

class obstacle{
    static {
        this.lifetime = 1/128;
    }
    constructor(type, yState){
        if (yState === "sky"){
            this.y = canvas.height/2 - 100;
        }
        else if (yState === "ground"){
            this.y = canvas.height/2;
        }
        this.x = canvas.width + 50;
        this.sprite = new Image();
        this.sprite.src = "/static/assets/random.png";
        this.alive = true;
    }
    draw(context){
        context.drawImage(this.sprite,this.x,this.y,50,50);
    }
    update(context){
        if (this.x < -50){
            this.alive = false;
        }
        this.x -= (canvas.width + 100)*obstacle.lifetime;
        this.draw(context);
    }

}

curPlayer = new player();
let objCount = 0;
const obstacles = [];

let runStart = performance.now();
let lastTime = performance.now();

function frame(){
    const now = performance.now();
    const deltaTime = now - lastTime;
    const runDuration = now - runStart;
    lastTime = now;

    
    let count = 0;
    if (runDuration < 180000){
            obstacle.lifetime = 1/128 + runDuration * 0.0000001;
        }

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
            obstacles.push(new obstacle("gay", "ground"));
        }
        else{
            obstacles.push(new obstacle("gay", "sky"));
        }
        objCount++;
    }
    else if (objCount < 5 && Math.random() < 0.1 && obstacles[obstacles.length-1].x < canvas.width -200){
        
        
        if (Math.random() < 0.5){
            obstacles.push(new obstacle("gay", "ground"));
        }
        else{
            obstacles.push(new obstacle("gay", "sky"));
        }
        objCount++;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;

    
    curPlayer.update(ctx);
    obstacles.forEach(obs =>{
        obs.update(ctx);
    });
    requestAnimationFrame(frame);

}
curPlayer.draw(ctx);
frame();
window.addEventListener('keypress', (event) => {
    if (event.code === 'Space') {
        curPlayer.jump();
    }

});