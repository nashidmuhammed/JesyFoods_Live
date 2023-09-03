// var hamburger = document.querySelector(".hamburger");
var side_bar = document.querySelector("#side_bar");
var bd = document.querySelector(".black_close");
// hamburger.addEventListener("click", function(){
// document.querySelector("body").classList.toggle("active");
// })

side_bar.addEventListener("click", function(){
    document.querySelector("body").classList.toggle("active");
    document.querySelector(".black_close").classList.toggle("active");
    })

bd.addEventListener("click", function(){
    document.querySelector("body").classList.add("active");
    document.querySelector(".black_close").classList.toggle("active");
    })