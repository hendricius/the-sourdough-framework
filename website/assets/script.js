document.addEventListener('DOMContentLoaded', function() {
  var menuItems = document.querySelector('.menu-items');
  menuItems.addEventListener('click', function(event) {
    if (event.target.tagName === 'SPAN') {
      var checkboxes = document.querySelectorAll('#toggle-menu');
      checkboxes.forEach(function(checkbox) {
        checkbox.checked = false;
      });
    }
  });
});
