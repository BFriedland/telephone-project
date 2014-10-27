var drawingCanvas = new fabric.Canvas('drawing', {
  isDrawingMode: true
});

var displayCanvas = new fabric.StaticCanvas('oldpic');

fabric.Object.prototype.transparentCorners = false;

drawingCanvas.freeDrawingBrush.width = 30;

$('.color-selectors').on('click', 'li', function () {
  drawingCanvas.freeDrawingBrush.color = $(this).css('background-color');
  $(this).siblings().removeClass('selected');
  $(this).addClass('selected');
});

$('.size-selectors').on('click', 'li', function () {
  drawingCanvas.freeDrawingBrush.width = Number($(this).css('height').slice(0, -2));
  $(this).siblings().removeClass('selected');
  $(this).addClass('selected');
});

$('#clear').on('click', function () {
  drawingCanvas.clear();
});

$('#submit-text').on('click', function () {
  $('.drawing-prompt').text($('#textbox').val());
});

$('#upload').on('click', function () {
  picJSON = drawingCanvas.toJSON();
  $.ajax({
    type: 'POST',
    url: '/new-drawing',
    data: JSON.stringify(picJSON),
    contentType: "application/json; charset=utf-8",
    dataType: "json"})
  .done(function (data) {
    drawingCanvas.clear();
    displayCanvas.loadFromJSON(data, displayCanvas.renderAll.bind(displayCanvas));
  });
});

