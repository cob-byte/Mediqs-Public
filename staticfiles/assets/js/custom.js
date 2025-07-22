(function ($) {
	
	"use strict";

	// Header Type = Fixed
  $(window).scroll(function () {
    var scroll = $(window).scrollTop();
    var box = $('.header-text').height();
    var header = $('header').height();

    if (scroll >= box - header) {
      $("header").addClass("background-header");
    } else {
      $("header").removeClass("background-header");
    }
  });


	$('.loop').owlCarousel({
      center: true,
      items:1,
      loop:true,
      autoplay: true,
      nav: true,
      margin:0,
      responsive:{ 
          1200:{
              items:5
          },
          992:{
              items:3
          },
          760:{
            items:2
        }
      }
  });

  // Acc
  $(document).on("click", ".naccs .menu div", function() {
    var numberIndex = $(this).index();

    if (!$(this).is("active")) {
        $(".naccs .menu div").removeClass("active");
        $(".naccs ul li").removeClass("active");

        $(this).addClass("active");
        $(".naccs ul").find("li:eq(" + numberIndex + ")").addClass("active");

        var listItemHeight = $(".naccs ul")
          .find("li:eq(" + numberIndex + ")")
          .innerHeight();
        $(".naccs ul").height(listItemHeight + "px");
      }
  });
	

	// Menu Dropdown Toggle
  if($('.menu-trigger').length){
    $(".menu-trigger").on('click', function() { 
      $(this).toggleClass('active');
      $('.header-area .nav').slideToggle(200);
    });
  }

  // Add a function to handle mobile scroll-to-section behavior
  function scrollToSectionMobile(hash) {
    var target = $(hash);
  
    if (target.length) {
      var navbarHeight = 80;
      var offset = target.offset().top - navbarHeight;
  
      $('html, body').stop().animate({
        scrollTop: offset
      }, 700, 'swing');
    }
  }

  function scrollToSection(hash) {
    var target = $(hash);
    
    if (target.length) {
      var navbarHeight = 80; // Replace 80 with the actual height of your fixed navbar
      var offset = target.offset().top - navbarHeight;
  
      $('html, body').stop().animate({
        scrollTop: offset
      }, 700, 'swing');
    }
  }  

  // Menu elevator animation
  $('.scroll-to-section a[href^="#"]').on('click', function(e) {
    e.preventDefault();
    $('.scroll-to-section a').removeClass('active');
    $(this).addClass('active');
    var target = this.hash;
    // Check if it's a mobile view (width < 991) and handle accordingly
    var width = $(window).width();
    if (width < 991) {
      scrollToSectionMobile(target);
    } else {
      scrollToSection(target);
    }
  });
  

  $(document).ready(function () {
      $(document).on("scroll", onScroll);
      
      //smoothscroll
      $('.scroll-to-section a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        $('.scroll-to-section a').removeClass('active');
        $(this).addClass('active');
        var target = this.hash;
        // Check if it's a mobile view (width < 991) and handle accordingly
        var width = $(window).width();
        if (width < 991) {
          scrollToSectionMobile(target);
        } else {
          scrollToSection(target);
        }
      });      
  });

  function onScroll(event) {
    var scrollPos = $(document).scrollTop();
    var headerHeight = $('header').height(); // Height of the fixed header
    var buffer = headerHeight + 200; // You can adjust the buffer value as needed
  
    $('.nav a').each(function() {
      var currLink = $(this);
      var hrefValue = currLink.attr("href");
  
      if (hrefValue && hrefValue.startsWith("#")) {
        var refElement = $(hrefValue);
        var refElementTop = refElement.offset().top - buffer;
        var refElementBottom = refElementTop + refElement.height();
  
        if (scrollPos >= refElementTop && scrollPos < refElementBottom) {
          $('.nav ul li a').removeClass("active");
          currLink.addClass("active");
        } else {
          currLink.removeClass("active");
        }
      }
    });
  }  

  // Acc
  $(document).on("click", ".naccs .menu div", function() {
    var numberIndex = $(this).index();

    if (!$(this).is("active")) {
        $(".naccs .menu div").removeClass("active");
        $(".naccs ul li").removeClass("active");

        $(this).addClass("active");
        $(".naccs ul").find("li:eq(" + numberIndex + ")").addClass("active");

        var listItemHeight = $(".naccs ul")
          .find("li:eq(" + numberIndex + ")")
          .innerHeight();
        $(".naccs ul").height(listItemHeight + "px");
      }
  });


	// Page loading animation
	 $(window).on('load', function() {

        $('#js-preloader').addClass('loaded');

    });
})(window.jQuery);