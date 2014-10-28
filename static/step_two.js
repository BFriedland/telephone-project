var drawingCanvas = new fabric.Canvas('drawing', {
  isDrawingMode: true
});

drawingCanvas.setHeight(320);
drawingCanvas.setWidth(320);

fabric.Object.prototype.transparentCorners = false;

drawingCanvas.freeDrawingBrush.width = 30;

$('.color-selectors').on('click', 'li', function () {
  drawingCanvas.freeDrawingBrush.color = $(this).css('background-color');
  $(this).siblings().removeClass('selected');
  $(this).addClass('selected');
});

$('.size-selectors').on('click', '.sizer', function () {
  drawingCanvas.freeDrawingBrush.width = Number($(this).children().first()
                                                 .css('height').slice(0, -2));
  $('.sizer .selector').removeClass('selected');
  $(this).children().first().addClass('selected');
});

$('#clear').on('click', function () {
  drawingCanvas.clear();
});

$('#upload').on('click', function () {
  picJSON = drawingCanvas.toJSON();
  $.ajax({
    type: 'POST',
    url: '/step_three',
    data: JSON.stringify(picJSON),
    contentType: "application/json; charset=utf-8",
    dataType: "json"});
});
