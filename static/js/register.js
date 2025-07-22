var currentTab = 0; // Current tab is set to be the first tab (0)
showTab(currentTab); // Display the current tab

function showTab(n) {
  // This function will display the specified tab of the form ...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";

  if (n == 0) {
    document.getElementById("submitBtn").style.display = "none";
    document.getElementById("prevBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
  }
  
  if (n == (x.length - 1)) {
    document.getElementById("nextBtn").style.display = "none";
    document.getElementById("submitBtn").style.display = "inline";
  } else {
    document.getElementById("nextBtn").style.display = "inline";
    document.getElementById("submitBtn").style.display = "none";
  }
  // ... and run a function that displays the correct step indicator:
  fixStepIndicator(n)
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  // if you have reached the end of the form... :
  if (currentTab >= x.length) {
    //...the form gets submitted:
    document.getElementById("regForm").submit();
    return false;
  }
  // Otherwise, display the correct tab:
  showTab(currentTab);
}

function validateForm() {
    var x, y, i, valid = true;
    x = document.getElementsByClassName("tab");
    y = x[currentTab].getElementsByTagName("input");
    
    for (i = 0; i < y.length; i++) {
      var name = y[i].getAttribute("name");
  
      if (y[i].value == "") {
        y[i].className += " invalid";
        if(name == "dob"){
            $(y[i]).popover({content: "Please input your date of birth", placement: "right"});
            $(y[i]).popover('show');
            valid = false;
        }
        else if(name == "phone_number")
        {
            $(y[i]).popover({content: "Please input your phone number", placement: "right"});
            $(y[i]).popover('show');
            valid = false;
        }
        else{
            $(y[i]).popover({content: "Please input your " + name, placement: "right"});
            $(y[i]).popover('show');
            valid = false;
        }
      }
      else if (name == "age" && !validateAge(y[i].value)) {
        y[i].className += " invalid";
        $(y[i]).popover({content: "Invalid age", placement: "right"});
        $(y[i]).popover('show');
        valid = false;
      }
      else if (name == "dob" && !validateDob(y[i].value)) {
        y[i].className += " invalid";
        $(y[i]).popover({content: "Invalid date of birth, format should be DD-MM-YYYY", placement: "right"});
        $(y[i]).popover('show');
        valid = false;
      }
      else if (name == "dob" && isFutureDate(y[i].value)) {
        y[i].className += " invalid";
        $(y[i]).popover({content: "Date of birth cannot be in the future", placement: "right"});
        $(y[i]).popover('show');
        valid = false;
      }
      else if (name == "gender" && !validateGender(y[i].value)) {
        y[i].className += " invalid";
        $(y[i]).popover({content: "Please select a gender", placement: "right"});
        $(y[i]).popover('show');
        valid = false;
      }
      else if (name == "phone_number" && !validatePhoneNumber(y[i].value)) {
        y[i].className += " invalid";
        $(y[i]).popover({content: "Invalid phone number. It must starts with either \"0\" or \"+63\", followed by a 10 digit number", placement: "right"});
        $(y[i]).popover('show');
        valid = false;
      }
      else {
        y[i].className = y[i].className.replace(" invalid", "");
        $(y[i]).popover('dispose');
      }
    }
  
    if (valid) {
      document.getElementsByClassName("step")[currentTab].className += " finish";
    }
    return valid;
  }
  
  function isFutureDate(dateString) {
    var today = new Date();
    var inputDate = new Date(dateString);
    return inputDate > today;
  }

  function validateAge(age) {
    var ageNum = parseInt(age);
    return Number.isInteger(ageNum) && ageNum >= 0;
  }  

  function validateDob(dob) {
    var dobRegex = /^\d{4}-\d{2}-\d{2}$/;
    return dobRegex.test(dob);
  }
  
  function validateGender(gender) {
    var validGenders = ["Male", "Female"];
    return validGenders.includes(gender);
  }
  
  function validatePhoneNumber(number) {
    // Philippine phone number can be +63 or 0 followed by the 10 digit number
    var phoneRegex = /^(0|\+63)[0-9]{10}$/;
    return phoneRegex.test(number);
  }

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i, x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class to the current step:
  x[n].className += " active";
}