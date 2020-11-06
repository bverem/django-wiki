$(document).ready(function() {
  $('.wiki-article .thumbnail').each(function() {
    caption = $(this).children('.caption').html();

    // Instead of colorbox, let's grab our modal
    $(this).children('a').on('click', function(e){
      e.preventDefault();
      asset_id = $(this).attr('data-id');
      getFileModal(asset_id);
    })
  });
});

function getFileModal(asset_id){
  $.ajax({
    type: "GET",
    url: window.location.href.split('/').splice(0,3).join('/') + '/files/get-file-data/',
    data: {"asset_id": asset_id, "return_type": "modal"},
    success: function(response) {
      $('#file-modal-container').html(response);
      $('#file-modal').modal();
    }
  });
  return false;
}
