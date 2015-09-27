"use strict"

var newCanvas = $('<canvas/>',{'class':'radHuh'})

$('#x').append(newCanvas)

console.log(newCanvas.width())

var ctx = $(newCanvas)[0].getContext('2d');

var area = {
    init: function(canvas) {
        this.width = canvas.width();
        this.height = canvas.height();
        this.canvas = $(canvas)[0];
        this.canvas.setAttribute('width', this.width);
        this.canvas.setAttribute('height', this.height);
        
        console.log(canvas)
        console.log(this.width + "  -- " + this.height)
    },
    newball: function() {
        return new Ball(this)
    },
    clear: function() {
        this.canvas.getContext('2d').clearRect(0,0,this.width, this.height);
    }
}

area.init(newCanvas)
//var ball = area.newball();

function Ball(area) {
    if (window === this)
        return new Ball(area);
    this.init(area);
    return this;
}
Ball.prototype = {
    init: function(area) {
        this.width = Math.floor(area.width / 24 ); 
        this.height = Math.floor(area.height / 24 );
        this.areaWidth = area.width;
        this.areaHeight = area.height;
        this.r = 10;
        this.x = this.findlegalXY(area.width-this.r)
        this.y = this.findlegalXY(area.height-this.r)
        this.moveX = Math.floor(Math.random() * this.r)
        this.moveY = Math.floor(Math.random() * this.r)
        this.ctx = area.canvas.getContext('2d')
    },

    findlegalXY(w) {
        var lx = Math.floor(Math.random()*w);
        while(lx < this.r)
            lx = Math.floor(Math.random()*w);
        return lx
    },

    move() {
        if (this.x + this.r > this.areaWidth ||
            this.x - this.r < 0) 
            this.moveX = (-this.moveX);
        if (this.y + this.r > this.areaHeight ||
            this.y - this.r < 0) 
            this.moveY = (-this.moveY);

        this.x += this.moveX
        this.y += this.moveY
    },
    
    draw() {
        this.ctx.beginPath();
        this.ctx.arc(this.x, this.y, this.r, 0, 2 * Math.PI);
        this.ctx.fillStyle = 'green';
        this.ctx.fill();
        this.ctx.lineWidth = 1;
        this.ctx.strokeStyle = '#003300';
        this.ctx.stroke();
    }
}

var b = area.newball();
b.draw();

setInterval(function() {
    area.clear();
    b.move();
    b.draw()
}, 30)







