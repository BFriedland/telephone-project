$(function () {
  $('#submit-text').on('click', function () {
    data = {'prompt': $('#prompt-entry').val()};
    $.post('/new-prompt', data);
    window.open('/step_two', '_self');
  });
});
