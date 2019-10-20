/*
 * Initial the bootstrap-toc in posts.
 *
 * © 2019 Cotes Chung
 * MIT Licensed
 */

$(function() {
  var navSelector = "#toc"
  Toc.init({
    $nav: $(navSelector),
    $scope: $("h2,h3")
  });
  $("body").scrollspy({
    target: navSelector
  });

  // Hide ToC title if there is no head
  if ($("#toc-wrap>nav#toc>ul>li").length == 0) {
    $("#toc-wrap>h3").addClass("hidden");
  }

});