$(document).ready(function() {
    $('#fn-load').hide()
    
});
$(window).on("load",function(){
    $("#main-load").fadeOut("slow");
    //header.style.backgroundColor = 'transparent'
        $("#header").css("box-shadow", "none");
  });

 // Deletable clear icon
// $(document).ready(function() {
//     $('input.deletable').wrap('<span class="deleteicon"></span>').after($('<span>x</span>').click(function() {
//         $(this).prev('input').val('').trigger('change').focus();
//     }));
// });

