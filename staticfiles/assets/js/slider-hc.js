$('.owl-carousel').owlCarousel({
    loop:false,
  stagePadding: 20,
    margin:20,
    nav:true,
    navText : ['<span class="icon left" style="font-size: 55px; margin-right: 7px;">‹</span>','<span class="icon right" style="font-size: 55px; margin-left: 7px;">›</span>'],
    responsive:{
        0:{
            items:1
        },
        640:{
            items:1
        },
      960:{
            items:2
        },
        1200:{
            items:2
        }
    }
})