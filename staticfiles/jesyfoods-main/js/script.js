/*load*/
console.log("ready")

AOS.init();

const hamburger = document.querySelector('.header .nav-bar .nav-list .hamburger');
const mob_menu = document.querySelector('.header .nav-bar .nav-list ul');
const menu_item = document.querySelectorAll('.header .nav-bar .nav-list ul li a');
const header = document.querySelector('#header');

hamburger.addEventListener('click',()=>{
    hamburger.classList.toggle('active');
    mob_menu.classList.toggle('active');
});



/*
document.addEventListener('scroll',()=>{
    var scroll_position = window.scrollY;
    if(scroll_position > 100){
        header.style.backgroundColor = '#fff';
        $("#header").css("box-shadow", "0 .125rem .25rem rgba(0, 0, 0, 0.350)");
    }else{
        header.style.backgroundColor = 'transparent'
        $("#header").css("box-shadow", "none");
    }
});
*/
menu_item.forEach(item=>{
    item.addEventListener('click',()=> {
        hamburger.classList.toggle('active');
        mob_menu.classList.toggle('active');
    });
});

$(".caro").owlCarousel({
    margin: 20,
    loop: true,
    autoplay: true,
    autoplayTimeout: 2000,
    autoplayHoverPause: true,
    responsive: {
      0:{
        items:1,
        nav: false
      },
      600:{
        items:2,
        nav: false
      },
      1000:{
        items:3,
        nav: false
      }
    }
  });

  
  $("#submit-form").submit((e)=>{
    e.preventDefault()
    $("#cont .btn-std").hide()   
    $(".subload").show()
    $("#submit-form").submit()
    // $.ajax({
    //     url:"https://script.google.com/macros/s/AKfycbw_WDn6uhFAlZ1IcJRM844fn8P644_5rpKQdNyFoYXNA_TvDVzOPHxoQg/exec",
    //     data:$("#submit-form").serialize(),
    //     method:"post",
    //     success:function (response){
    //       $(".contact .btn-std").show()   
    //       $(".subload").hide()
    //       $("#success_alert").modal()
    //     },
    //     error:function (err){
    //       $(".contact .btn-std").show()   
    //       $(".subload").hide()
    //       $("#error_alert").modal()

    //     }
    // })
  })

 $(document).ready(function(){
  $("#cont .close").click(function(){
    window.location.reload()
  })
  $("#cont .clos").click(function(){
    window.location.reload()
  })
 })

//Tasty Hub

//Add Input Box
$(document).ready(function() {
	var max_fields      = 10; //maximum input boxes allowed
	var wrapper   		= $(".input_fields_wrap"); //Fields wrapper
	var add_button      = $(".add_field_button"); //Add button ID
	var wrapper_steps   		= $(".input_fields_wrap_steps"); //Fields wrapper
	var add_button_steps      = $(".add_field_button_steps"); //Add button ID
	
	var x = 1; //initlal text box count
	$(add_button).click(function(e){ //on add input button click
		e.preventDefault();
		if(x < max_fields){ //max input box allowed
			x++; //text box increment
			$(wrapper).append('<div class="input-group mb-3"><input type="text" class="form-control"placeholder="Incrediants" aria-label="Incrediants" aria-describedby="basic-addon2"><div class="input-group-append"><button class="remove_field btn btn-outline-danger" type="button"><i class="fa fa-minus-circle" aria-hidden="true"></i></button></div></div>'); //add input box
		}
	});

  var y = 1; //initlal text box count
	$(add_button_steps).click(function(e){ //on add input button click
		e.preventDefault();
		if(y < max_fields){ //max input box allowed
			y++; //text box increment
			$(wrapper_steps).append('<div class="input-group mb-3"><input type="text" class="form-control"placeholder="Steps" aria-label="Incrediants" aria-describedby="basic-addon2"><div class="input-group-append"><button class="remove_field btn btn-outline-danger" type="button"><i class="fa fa-minus-circle" aria-hidden="true"></i></button></div></div>'); //add input box
		}
	});
	
	$(wrapper).on("click",".remove_field", function(e){ //user click on remove text
		e.preventDefault(); $(this).parent('div').parent('div').remove(); x--;
	})
  $(wrapper_steps).on("click",".remove_field", function(e){ //user click on remove text
		e.preventDefault(); $(this).parent('div').parent('div').remove(); x--;
	})
});


/*Scroll Recipie */
function isScrolledIntoView(elm) {
  var docViewTop = $(window).scrollTop();
  var docViewBottom = docViewTop + $(window).height();

  var elmTop = $(elm).offset().top;
  var elmBottom = elmTop + $(elm).height();

  return ((elmBottom <= docViewBottom) && (elmTop >= docViewTop));
}
$(window).scroll(function(){
  if (isScrolledIntoView('#follow') === true) {
      $('.sub_top').addClass('hide')
  }
  else if (isScrolledIntoView('#footer') === true) {
    $('.sub_top').addClass('hide')
}
  else  {
    $('.sub_top').removeClass('hide')
  }
});

//End Input box

//admin



  console.log("end")