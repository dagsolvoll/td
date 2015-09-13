function log(debug, str) {
    if (debug)
       console.log(str)
}

window.onload = function(e) {
    log(0, "onload")
    t = tetris("myCanvas", 192, 384)
    t.canvas.focus()
}

function tetris(id, w, h) {
    // About object is returned if there is no 'id' parameter
    var about = {
        Version: 0.1,
        Author: "Dag Solvoll",
        Created: "Fall 2015",
        Updated: "10 September 2015"
    };

    if (id) {
        // Avoid clobbering the window scope:
        // return a new _ object if we're in the wrong scope
        if (window === this) {
            return new tetris(id,w,h);
        }
        this.canvas = document.getElementById(id);
        this.canvas2 = document.getElementById(id + "2");

        this.ctx = this.canvas.getContext("2d");

        this.cyanbrick   = {size: 4, blocks: [0x0F00, 0x2222, 0x00F0, 0x4444], color: 'cyan'   };
        this.bluebrick   = {size: 3, blocks: [0x44C0, 0x8E00, 0x6440, 0x0E20], color: 'blue'   };
        this.orangebrick = {size: 3, blocks: [0x4460, 0x0E80, 0xC440, 0x2E00], color: 'orange' };
        this.yellowbrick = {size: 2, blocks: [0xCC00, 0xCC00, 0xCC00, 0xCC00], color: 'yellow' };
        this.greenbrick  = {size: 3, blocks: [0x06C0, 0x8C40, 0x6C00, 0x4620], color: 'green'  };
        this.purplebrick = {size: 3, blocks: [0x0E40, 0x4C40, 0x4E00, 0x4640], color: 'purple' };
        this.redbrick    = {size: 3, blocks: [0x0C60, 0x4C80, 0xC600, 0x2640], color: 'red'    };

        this.pieces = []

        this.brick = this.randombrick()
        this.nextbrick = this.randombrick()
        this.init(w,h)
        return this;
    } else {
        return about
    }
}

tetris.prototype = {

    init: function(w, h) {

        this.ix = 0
        this.iy = 0
        this.timer = null
        this.width = w
        this.height = h
        this.block_size = 16
        this.num_x = w / this.block_size
        this.num_y = h / this.block_size
        this.board = []
        this.figidx = 0
        this.READY = 0
        this.START = 1
        this.STOP = 2
        this.ENDED = 3
        this.state = this.READY

        this.canvas.addEventListener("mousedown", function(event) {
            this.toggleMouse()
        }.bind(this), false)
        this.canvas.addEventListener("keydown", function(event) {
            this.keydown(event.which || event.keyCode)
        }.bind(this), false)

        this.toggleMouse(this.START)
    },

    randombrick: function() {
        if (this.pieces.length == 0) {
            this.pieces = [
                this.cyanbrick, this.bluebrick, this.orangebrick, this.yellowbrick, this.greenbrick, this.purplebrick, this.redbrick,
                this.cyanbrick, this.bluebrick, this.orangebrick, this.yellowbrick, this.greenbrick, this.purplebrick, this.redbrick,
                this.cyanbrick, this.bluebrick, this.orangebrick, this.yellowbrick, this.greenbrick, this.purplebrick, this.redbrick,
                this.cyanbrick, this.bluebrick, this.orangebrick, this.yellowbrick, this.greenbrick, this.purplebrick, this.redbrick]
        }
        var type = this.pieces.splice((this.pieces.length-1)*Math.random(0, this.pieces.length-1), 1)[0]; // remove a single piece
        return type
//        return this.pieces[Math.round((this.pieces.length-1)*Math.random(0, this.pieces.length-1))];
    },

    draw: function() {
        this.ctx.clearRect(0,0,this.width,this.height);
        this.drawlines()
        this.drawbrick(this.ix, this.iy)
        if (this.state != this.ENDED) {
            log(0, this.ix + " - " + this.iy + " - " + (this.outside(this.ix, this.iy)))
            this.iy += 1 
            if (this.outside(this.ix, this.iy)) {
                var br = this.brickcoord(this.ix, this.iy-1)
                for (var i = 0; i < br.length; i++) {
                    if (!this.board[br[i][1]])
                        this.board[br[i][1]] = []
                    this.board[br[i][1]][br[i][0]] = this.brick.color
                }
                this.ix = 3
                this.iy = 0
                this.brick = this.nextbrick
                this.nextbrick = this.randombrick()
            }
            this.drawboard()
            this.drawnextbrick()
        } else {
            this.drawboard()
            this.drawnextbrick()        
            this.toggleMouse()    
        }
    },

    drawnextbrick: function() {
        ctx = this.canvas2.getContext("2d")
        ctx.clearRect(0,0,64,64)
        var i = 0
        for (bit = 0x8000; bit > 0; bit = bit >> 1, i++) {
            row = Math.floor(i / 4)
            col = i - (row*4)
            if (this.nextbrick.blocks[this.figidx] & bit) {
                this.drawbox(ctx, this.nextbrick.color, col, row)
            }
        }
    },

    drawlines: function() {
        this.ctx.strokeStyle = "#cccccc"
        for (var i = 0; i < this.num_x; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i*this.block_size,0);
            this.ctx.lineTo(i*this.block_size,this.num_y*this.block_size);
            this.ctx.stroke();
        }
        for (var i = 0; i < this.num_y; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, i*this.block_size);
            this.ctx.lineTo(this.num_y*this.block_size, i*this.block_size);
            this.ctx.stroke();
        }
    },

    drawbox: function(ctx, color, x,y) {
        var bs = this.block_size
        ctx.fillStyle = color;
        ctx.fillRect (x*bs, y*bs, bs, bs);
    },

    drawboard: function(x, y){
        var bs = this.block_size
        var ended = []

        for (var i = 0; i < this.board.length; i++) {
            if (this.board[i]) {
                var all = 0
                for (var j= 0; j < this.board[i].length; j++) {
                    if (this.board[i][j]) {
                        all += 1
                        this.ctx.fillStyle = this.board[i][j]
                        this.ctx.fillRect (j*bs, i*bs, bs, bs);
                        if (!ended[j])
                            ended[j] = 1
                        else
                            ended[j] = ended[j] + 1
                    }
                }
                if (all == this.num_x) {
                    var nb = []
                    for (var xi = 0; xi < this.board.length; xi++) {
                        if (xi < i)
                            nb[xi+1] = this.board[xi]
                        else if (xi > i) 
                            nb[xi] = this.board[xi]
                    }
                    this.board = nb
                }
            }
        }

        for (var i = 0; i < ended.length; i++) {
            if (ended[i] == this.num_y) {
                this.state = this.ENDED
                this.toggleMouse()
            }
        }
    },

    outside: function(x, y) {
        var bc = this.brickcoord(x,y)
        log(0, bc)
        for (var i = 0; i < bc.length; i++) {
            var xx = bc[i][0]
            var xy = bc[i][1]
            log(0, "O(" + i + "): " + xx + ", " + xy + " :: " + this.ix + " - " + this.iy )
            if (xy < 0 || xy >= this.num_y || xx < 0 || xx >= this.num_x) {
                return true
            }
            if (this.board[xy] && this.board[xy][xx]) {
                return true
            }
        }

        return false
    },

    brickcoord: function(x,y) {
        var bc = []
        var idx = 0
        var i = 0
        for (var bit = 0x8000; bit > 0; bit = bit >> 1, i++) {
            var row = Math.floor(i / 4)
            var col = i - (row*4)
            if (this.brick.blocks[this.figidx] & bit) {
                bc[idx++] = [col + x, row + y]
            }
        }
        return bc
    },

    drawbrick: function(x, y){
        i = 0
        b = []
        for (bit = 0x8000; bit > 0; bit = bit >> 1, i++) {
            row = Math.floor(i / 4)
            col = i - (row*4)
            if (this.brick.blocks[this.figidx] & bit) {
                if (this.board[y+row] && this.board[y+row][x+col]) {
                    this.state = this.ENDED
                    log(1, "Hit")
                    b = []
                    break
                } else {
                    b[b.length] = [x+col, y+row]
                }
            }
        }
        if (b.length > 0) {
            b.forEach (function(a) {this.drawbox(this.ctx, this.brick.color, a[0], a[1])}.bind(this))
        }
    }, 

    rotate: function (forward) {        
        if (forward) {
            this.oldfigidx = this.figidx
            this.figidx = (this.figidx + 1) % 4
        } else {
            this.figidx = this.oldfigidx
        }
        log(0, this.figidx)
    },

    toggleMouse: function () {
        if (this.state == this.ENDED) {
            if (this.timer) {
                clearInterval(this.timer) 
                this.timer = null           
            }
        } else {
            if (this.timer) {
                clearInterval(this.timer) 
                this.timer = null           
            } else {
                this.timer = setInterval(this.draw.bind(this), 300)
            }
        }
    }, 

    keydown: function(key) {
            if (key === 38) { // Up is enterd
                this.rotate(1)
                if (this.outside(this.ix, this.iy))
                    this.rotate(0)
            } else if (key == 40) {// Down
                this.iy += 1
                if (this.outside(this.ix, this.iy))
                    this.iy -= 1
            } else if (key == 39) {// Right
                this.ix += 1
                if (this.outside(this.ix, this.iy))
                    this.ix -= 1
            } else if (key == 37) {// Left
                this.ix -= 1
                if (this.outside(this.ix, this.iy))
                    this.ix += 1
            } else if (key == 32) {
                for (i = this.iy; i < this.num_y; i++) {
                    this.iy += 1
                    if (this.outside(this.ix, this.iy))
                        break;
                }   
                this.iy -= 1
            }
            log(1, "Key= " + key)
    }

};
