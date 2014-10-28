$(function () {
  $('#submit-text').on('click', function () {
    data = {'prompt': $('#prompt-entry').val()};
    $.post('/step_two', data)
    .fail(function () {
      alert("Error");
      window.open('/', '_self');
    })
    .done(function (response) {
      response = JSON.parse(response);
      $('#content').html(response.html);
      $('.drawing-prompt').text(response.prompt);
      $.getScript('/static/step_two.js');
    });
  });
});
