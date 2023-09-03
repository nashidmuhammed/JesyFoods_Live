$(document).ready(function(){
    $('#sale_drop').click(function(){
        $('.drop').toggle(300);
        $('.side_nav').addClass("active");
    });
    $('#cparty').click(function(){
        $('.cdrop').toggle(300);
        $('.side_nav').addClass("active");
    });
    $('.plus_btn').click(function(){
        $('#plus_btn_more').toggle(750);
    });
    // $('.home_content').click(function() {
    //     $('.side_nav').removeClass('active');
    //     $('.drop').hide()
    //     $('.cdrop').hide()
    //     console.log('home cont www')
    // });
    $('#btn_plus').click(function() {
        $(this).find('i').toggleClass('fas fa-plus fas fa-minus');
    });
    $('#btn_bar-2, #btn_bar, .black, .side_nav ul li .fa-search').click(function() {
        $('.side_nav').toggleClass('active');
    });
    
    });

// let btn = document.querySelector("#btn_bar");
// let btn2 = document.querySelector("#btn_bar-2");
// let search_btn = document.querySelector(".fa-search");
// let home_content = document.querySelector(".home_content");
// let black = document.querySelector(".black");
// let drop = document.querySelector(".drop");
// let cdrop = document.querySelector(".cdrop");

// btn.onclick = function() {
//     side_nav.classList.toggle("active")
//     drop.style.display = "none"
//     cdrop.style.display = "none"
// }
// btn2.onclick = function() {
//     console.log('btn 2 worked'+side_nav)
//     side_nav.classList.add("active")
//     drop.style.display = "none"
//     cdrop.style.display = "none"
//     console.log('btn 2 last')
// }
// search_btn.onclick = function() {
//     side_nav.classList.toggle("active")
//     drop.style.display = "none"
//     cdrop.style.display = "none"
// }
// home_content.onclick = function() {
//     side_nav.classList.remove("active")
//     drop.style.display = "none"
//     cdrop.style.display = "none"
// }
// black.onclick = function() {
//     side_nav.classList.remove("active")
//     drop.style.display = "none"
//     cdrop.style.display = "none"
// }







$(document).ready(function(){
    $(".prof .icon_wrap").click(function(){
        $(this).parent().toggleClass("active");
        $(".notification").removeClass("active");
    })
    $(".notification .icon_wrap").click(function(){
        $(this).parent().toggleClass("active");
        $(".prof").removeClass("active");
    })
})

window.addEventListener('mouseup', function(event){
var notification = document.getElementById('.notification');
if (event.target != prof && event.target.parentNode != notification){
    $(".notification").removeClass("active");
}
var prof = document.getElementById('.prof');
if (event.target != prof && event.target.parentNode != prof){
    $(".prof").removeClass("active");
}
});

/*Input-label */
document.querySelectorAll(".text-input").forEach((element) => {
    element.addEventListener("blur", (event) => {
        if (event.target.value != "") {
            event.target.nextElementSibling.classList.add("filled");
        }else {
            event.target.nextElementSibling.classList.remove("filled");
        }
    });
});

