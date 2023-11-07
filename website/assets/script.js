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

  // Add permalinks to headers
  var heads = document.querySelectorAll('.sectionHead');
  heads.forEach(function (head) {
    let permalink = document.createElement("a");
    permalink.href = '#' + head.id;
    permalink.classList.add('permalink');
    permalink.append('🔗');
    head.append(permalink);
  });
});
