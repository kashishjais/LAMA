function loadTheImage(image) {
  
  const canvas = this.canvas;
  fabric.Image.fromURL(image, function(img) {
    // add background image
    canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas), {
       scaleX: canvas.width / img.width,
       scaleY: canvas.height / img.height
    });
 });
}

function converterDataURItoBlob(dataURI) {
  let byteString;
  let mimeString;
  let ia;

  if (dataURI.split(',')[0].indexOf('base64') >= 0) {
    byteString = atob(dataURI.split(',')[1]);
  } else {
    byteString = encodeURI(dataURI.split(',')[1]);
  }
  // separate out the mime component
  mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

  // write the bytes of the string to a typed array
  ia = new Uint8Array(byteString.length);
  for (var i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  return new Blob([ia], {type:mimeString});
}

function generateMask(image) {
  // remove background image
  canvas.setBackgroundImage(null, canvas.renderAll.bind(canvas));
  var dataURL = canvas.toDataURL();
  document.getElementById("img").src = dataURL;
  console.log(image);
  loadTheImage(image)
}

function saveAs(blob, fileName){
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = fileName;
  a.click();
}

var canvas = new fabric.Canvas("draw", {
	isDrawingMode: true,
  freeDrawingCursor: 'none'
});

var cursor = new fabric.StaticCanvas("cursor");

canvas.freeDrawingBrush.width = 20;
canvas.freeDrawingBrush.color = '#000000';

var cursorOpacity = .5;
var mousecursor = new fabric.Circle({ 
  left: -100, 
  top: -100, 
  radius: canvas.freeDrawingBrush.width / 2, 
  fill: "rgba(255,0,0," + cursorOpacity + ")", 
  stroke: "black",
  originX: 'center', 
  originY: 'center'
});

cursor.add(mousecursor);

canvas.on('mouse:move', function (evt) {
	var mouse = this.getPointer(evt.e);  
  mousecursor
  	.set({
      top: mouse.y,
      left: mouse.x
    })
    .setCoords()
	  .canvas.renderAll();
});

canvas.on('mouse:out', function () {
  // put circle off screen
  
  mousecursor
  	.set({
      top: -100,
      left: -100
    })
    .setCoords()
    .canvas.renderAll();
});

//while brush size is changed
document.getElementById("size").oninput = function () {
	var size = this.value;
  mousecursor
  	.center()
  	.set({
      radius: size/2
  	})
    .setCoords()
    .canvas.renderAll();
};

//after brush size has been changed
document.getElementById("size").onchange = function () {
	var size = this.value;
  canvas.freeDrawingBrush.width = size;
  mousecursor
  	.set({
      left: mousecursor.originalState.left,
      top: mousecursor.originalState.top,
      radius: size/2
  	})
    .setCoords()
    .canvas.renderAll();
};

//change mousecursor opacity
document.getElementById("opacity").onchange = function () {
	cursorOpacity = this.value;
  var fill = mousecursor.fill.split(",");
  fill[fill.length-1] = cursorOpacity + ")";
  mousecursor.fill = fill.join(",");
}

//change drawing color
document.getElementById("color").onchange = function () {
	canvas.freeDrawingBrush.color = this.value;  
  var bigint = parseInt(this.value.replace("#", ""), 16);
  var r = (bigint >> 16) & 255;
  var g = (bigint >> 8) & 255;
  var b = bigint & 255;  
  mousecursor.fill = "rgba(" + [r,g,b,cursorOpacity].join(",") + ")";
};

//switch drawing mode
document.getElementById("mode").onchange = function () {
	canvas.isDrawingMode = this.checked;
  
  if (!this.checked) {
  	cursor.remove(mousecursor);
  }
  else {
  	canvas.deactivateAll().renderAll();
  	cursor.add(mousecursor);
  }
}

document.querySelector("#btngen").addEventListener("click", ()=> {
  generateMask(document.querySelector("#btngen").dataset.img)
});


document.querySelector("#btnsave").addEventListener("click", ()=> {
  // save image from #img to local storage
  var dataURL = document.getElementById("img").src;
  var blob = converterDataURItoBlob(dataURL);
  var fileName = "mask.png";
  saveAs(blob, fileName);
});

document.querySelector("#btnclear").addEventListener("click", ()=> {
  // clear image from #img
  document.getElementById("img").src = "";
  canvas.setBackgroundImage(null, canvas.renderAll.bind(canvas));
  loadTheImage(document.querySelector("#btnclear").dataset.img)
});
