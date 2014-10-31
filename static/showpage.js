var load_game = function (id, image1Canvas, image2Canvas) {
  $.get('/game/' + id.toString())
  .fail(function () {
    alert("could not get game" + id.toString());
  })
  .done(function (game) {
    game = JSON.parse(game);
    $('#game_id').text(game.id);
    $('#prompt1').text(game.first_prompt);
    $('#prompt2').text(game.second_prompt);
    $('#prompt3').text(game.third_prompt);
    image1Canvas.loadFromJSON(game.first_image, image1Canvas.renderAll.bind(image1Canvas));
    image2Canvas.loadFromJSON(game.second_image, image2Canvas.renderAll.bind(image2Canvas));
  });
};


$(function () {
  var image1Canvas = new fabric.StaticCanvas('image1');
  var image2Canvas = new fabric.StaticCanvas('image2');
  image1Canvas.setHeight(320);
  image1Canvas.setWidth(320);
  image2Canvas.setHeight(320);
  image2Canvas.setWidth(320);

  current_index = 0;
  current_game = list_of_games[current_index];

  load_game(current_game, image1Canvas, image2Canvas);

  $('#next').on('click', function () {
    current_index = (current_index + 1) % list_of_games.length;
    current_game = list_of_games[current_index];
    load_game(current_game, image1Canvas, image2Canvas);
  });

  $('#previous').on('click', function () {
    current_index = (current_index - 1) % list_of_games.length;
    if (current_index < 0) {
      current_index += list_of_games.length;
    }
    console.log(current_index);
    current_game = list_of_games[current_index];
    load_game(current_game, image1Canvas, image2Canvas);
  });
});



