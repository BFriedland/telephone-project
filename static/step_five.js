$(function () {
  $('#submit-text').on('click', function () {
    if ($('#prompt-entry').val() === "") {
      alert("You have to type something in the entry box");
    }
    else {
      data = {'prompt': $('#prompt-entry').val()};
      $.post('/final', data)
      .fail(function () {
        alert("Error");
        window.open('/', '_self');
      })
      .done(function (response) {
        window.open('/show_games', '_self');
      });
    }
  });
});
