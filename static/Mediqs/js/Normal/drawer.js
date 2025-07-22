const drawerTransitioner = transitionHiddenElement({
    element: document.querySelector('.js-drawer'),
    visibleClass: 'is-open'
  });
  
  document.querySelector('.js-open-button').addEventListener('click', () => {
    drawerTransitioner.show()
    $('body').css('overflow', 'hidden'); // disable scrolling on body
  });
  
  document.querySelector('.js-close-button').addEventListener('click', () => {
    drawerTransitioner.hide()
    $('body').css('overflow', 'auto'); // enable scrolling on body
  });
  
  /** 
   * Library code
   * Using https://www.npmjs.com/package/@cloudfour/transition-hidden-element
   */
  
  function transitionHiddenElement({
    element,
    visibleClass,
    waitMode = 'transitionend',
    timeoutDuration,
    hideMode = 'hidden',
    displayValue = 'block'
  }) {
    if (waitMode === 'timeout' && typeof timeoutDuration !== 'number') {
      console.error(`
        When calling transitionHiddenElement with waitMode set to timeout,
        you must pass in a number for timeoutDuration.
      `);
  
      return;
    }
  
    // Don't wait for exit transitions if a user prefers reduced motion.
    // Ideally transitions will be disabled in CSS, which means we should not wait
    // before adding `hidden`.
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      waitMode = 'immediate';
    }
  
    /**
     * An event listener to add `hidden` after our animations complete.
     * This listener will remove itself after completing.
     */
    const listener = e => {
      // Confirm `transitionend` was called on  our `element` and didn't bubble
      // up from a child element.
      if (e.target === element) {
        applyHiddenAttributes();
  
        element.removeEventListener('transitionend', listener);
      }
    };
  
    const applyHiddenAttributes = () => {
      if(hideMode === 'display') {
        element.style.display = 'none';
      } else {
        element.setAttribute('hidden', true);
      }
    }
  
    const removeHiddenAttributes = () => {
      if(hideMode === 'display') {
        element.style.display = displayValue;
      } else {
        element.removeAttribute('hidden');
      }
    }
  
    return {
      /**
       * Show the element
       */
      show() {
        /**
         * This listener shouldn't be here but if someone spams the toggle
         * over and over really fast it can incorrectly stick around.
         * We remove it just to be safe.
         */
        element.removeEventListener('transitionend', listener);
  
        /**
         * Similarly, we'll clear the timeout in case it's still hanging around.
         */
        if (this.timeout) {
          clearTimeout(this.timeout);
        }
  
        removeHiddenAttributes();
  
        /**
         * Force a browser re-paint so the browser will realize the
         * element is no longer `hidden` and allow transitions.
         */
        const reflow = element.offsetHeight;
  
        element.classList.add(visibleClass);
      },
  
      /**
       * Hide the element
       */
      hide() {
        if (waitMode === 'transitionend') {
          element.addEventListener('transitionend', listener);
        } else if (waitMode === 'timeout') {
          this.timeout = setTimeout(() => {
            applyHiddenAttributes();
          }, timeoutDuration);
        } else {
          applyHiddenAttributes();
        }
  
        // Add this class to trigger our animation
        element.classList.remove(visibleClass);
      },
  
      /**
       * Toggle the element's visibility
       */
      toggle() {
        if (this.isHidden()) {
          this.show();
        } else {
          this.hide();
        }
      },
  
      /**
       * Tell whether the element is hidden or not.
       */
      isHidden() {
        /**
         * The hidden attribute does not require a value. Since an empty string is
         * falsy, but shows the presence of an attribute we compare to `null`
         */
        const hasHiddenAttribute = element.getAttribute('hidden') !== null;
  
        const isDisplayNone = element.style.display === 'none';
  
        const hasVisibleClass = [...element.classList].includes(visibleClass);
  
        return hasHiddenAttribute || isDisplayNone || !hasVisibleClass;
      },
  
      // A placeholder for our `timeout`
      timeout: null
    };
  }

var form_1 = document.querySelector(".form_1");
var form_2 = document.querySelector(".form_2");
var form_3 = document.querySelector(".form_3");
var form_4 = document.querySelector(".form_4");



var form_1_btns = document.querySelector(".form_1_btns");
var form_2_btns = document.querySelector(".form_2_btns");
var form_3_btns = document.querySelector(".form_3_btns");

var form_1_next_btn = document.querySelector(".form_1_btns .btn_next");
var form_2_back_btn = document.querySelector(".form_2_btns .btn_back");
var form_2_next_btn = document.querySelector(".form_2_btns .btn_next");
var form_3_back_btn = document.querySelector(".form_3_btns .btn_back");


var form_2_progessbar = document.querySelector(".form_2_progessbar");
var form_3_progessbar = document.querySelector(".form_3_progessbar");

var btn_done = document.querySelector(".btn_done");
var modal_wrapper = document.querySelector(".modal_wrapper");
var shadow = document.querySelector(".shadow");

form_1_next_btn.addEventListener("click", function(){
  if ($('#uploaded_view').attr("data-uploaded") === "true") {
    form_1.style.display = "none";
    form_2.style.display = "block";

    form_1_btns.style.display = "none";
    form_2_btns.style.display = "flex";

    form_2_progessbar.classList.add("active");
  } else {
    alert("Please upload an image before proceeding.");
  }
});

form_2_back_btn.addEventListener("click", function(){
	form_1.style.display = "block";
	form_2.style.display = "none";

	form_1_btns.style.display = "flex";
	form_2_btns.style.display = "none";

	form_2_progessbar.classList.remove("active");
});

form_2_next_btn.addEventListener("click", function(){
  if ($('#uploaded_view_id_proof_front').attr("data-uploaded") === "true" && $('#uploaded_view_id_proof_back').attr("data-uploaded") === "true") {
    form_2.style.display = "none";
    form_3.style.display = "block";

    form_3_btns.style.display = "flex";
    form_2_btns.style.display = "none";

    form_3_progessbar.classList.add("active");
  } else {
    alert("Please upload an image of your ID before proceeding.");
  }
});

form_3_back_btn.addEventListener("click", function(){
	form_2.style.display = "block";
	form_3.style.display = "none";

	form_2_btns.style.display = "flex";
	form_3_btns.style.display = "none";

	form_3_progessbar.classList.remove("active");
});

btn_done.addEventListener("click", function(){
  if ($('#uploaded_view_selfie').attr("data-uploaded") === "true") {
    modal_wrapper.classList.add("active");
  } else {
    alert("Please upload an image before proceeding.");
  }
})

shadow.addEventListener("click", function(){
	modal_wrapper.classList.remove("active");
})

$(function() {
  $(".drop_box").each(function() {
    var btnUpload = $(this).find(".btn_upload > input[type='file']"),
        dropBox = $(this),
        fileRemove = $(this).parent().find(".file_remove");

    btnUpload.on("change", function(e) {
      if (e.target.files[0]) {
        handleFileUpload(e.target.files[0], dropBox, btnUpload);
      }
    }); 

    btnUpload.on('click', function(event) {
      event.stopPropagation();
    });
    

    dropBox.on("click", function(e) {
      e.stopPropagation();
      btnUpload.trigger('click');      
    });
    

    dropBox.on("dragover", function(e) {
      e.preventDefault();
      dropBox.addClass("dragover");
    });

    dropBox.on("dragleave", function(e) {
      dropBox.removeClass("dragover");
    });

    dropBox.on("drop", function(e) {
      e.preventDefault();
      dropBox.removeClass("dragover");
      var files = e.originalEvent.dataTransfer.files;
      btnUpload.prop("files", files);
      if (files[0]) {
        handleFileUpload(files[0], dropBox, btnUpload);
      }
    });

    fileRemove.on("click", function(e) {
      e.preventDefault();
      var parentContainer = $(this).parent();
      parentContainer.removeClass("show");
      parentContainer.find(".uploaded_image").remove();
      dropBox.find(".button_outer").removeClass("file_uploading");
      dropBox.find(".button_outer").removeClass("file_uploaded");
      dropBox.show();
      btnUpload.val("");
      
      // reset data-uploaded attribute
      var uploadedViewId = dropBox.parent().find(".uploaded_file_view").attr('id');
      $("#" + uploadedViewId).attr("data-uploaded", "false"); // Reset data-uploaded attribute
    });
  });
  
  function handleFileUpload(file, dropBox, btnUpload) {
    var ext = file.name.split(".").pop().toLowerCase();
    var uploadedViewId = dropBox.parent().find(".uploaded_file_view").attr('id'); // get the id of the .uploaded_file_view

    if ($.inArray(ext, ["gif", "png", "jpg", "jpeg"]) == -1) {
      dropBox.find(".error_msg").text("Not an Image...");
      $("#" + uploadedViewId).attr("data-uploaded", "false"); // Reset data-uploaded attribute
      btnUpload.val("");
    } else if (file.size > 2 * 1024 * 1024) { 
      dropBox.find(".error_msg").text("File size must be less than 2MB...");
      $("#" + uploadedViewId).attr("data-uploaded", "false"); // Reset data-uploaded attribute
      btnUpload.val("");
    } else {
      dropBox.find(".error_msg").text("");
      dropBox.find(".button_outer").addClass("file_uploading");
      setTimeout(function() {
        dropBox.find(".button_outer").addClass("file_uploaded");
        dropBox.hide();
      }, 3000);
      var uploadedFile = URL.createObjectURL(file);
      setTimeout(function() {
        $("#" + uploadedViewId).append('<div class="uploaded_image"><img src="' + uploadedFile + '" /></div>').addClass("show").attr("data-uploaded", "true"); // Update the data-uploaded attribute here
      }, 3500);      
    }
  }
});

  