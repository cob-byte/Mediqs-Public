/*
Author       : Dreamguys
Template Name: Doccure - Bootstrap Template
Version      : 1.0
*/

(function($) {
    "use strict";
	
	// Pricing Options Show
	
	$('#pricing_select input[name="rating_option"]').on('click', function() {
		if ($(this).val() == 'price_free') {
			$('#custom_price_cont').hide();
		}
		if ($(this).val() == 'custom_price') {
			$('#custom_price_cont').show();
		}
		else {
		}
	});
	
	// Education Add More
	
    $(".education-info").on('click','.trash', function () {
		$(this).closest('.education-cont').remove();
		return false;
    });

    $(".add-education").on('click', function () {
		
		var educationcontent = '<div class="row form-row education-cont">' +
			'<div class="col-12 col-md-10 col-lg-11">' +
				'<div class="row form-row">' +
					'<div class="col-12 col-md-6 col-lg-4">' +
						'<div class="form-group">' +
							'<label>Degree</label>' +
							'<input type="text" class="form-control">' +
						'</div>' +
					'</div>' +
					'<div class="col-12 col-md-6 col-lg-4">' +
						'<div class="form-group">' +
							'<label>College/Institute</label>' +
							'<input type="text" class="form-control">' +
						'</div>' +
					'</div>' +
					'<div class="col-12 col-md-6 col-lg-4">' +
						'<div class="form-group">' +
							'<label>Year of Completion</label>' +
							'<input type="text" class="form-control">' +
						'</div>' +
					'</div>' +
				'</div>' +
			'</div>' +
			'<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
		'</div>';
		
        $(".education-info").append(educationcontent);
        return false;
    });
	
	// Experience Add More
	
    $(".experience-info").on('click','.trash', function () {
		$(this).closest('.experience-cont').remove();
		return false;
    });

    $(".add-experience").on('click', function () {
		
		var experiencecontent = '<div class="row form-row experience-cont">' +
			'<div class="col-12 col-md-10 col-lg-11">' +
				'<div class="row form-row">' +
					'<div class="col-12 col-md-6 col-lg-4">' +
						'<div class="form-group">' +
							'<label>Hospital Name</label>' +
							'<input type="text" class="form-control">' +
						'</div>' +
					'</div>' +
					'<div class="col-12 col-md-6 col-lg-4">' +
						'<div class="form-group">' +
							'<label>From</label>' +
							'<input type="text" class="form-control">' +
						'</div>' +
					'</div>' +
					'<div class="col-12 col-md-6 col-lg-4">' +
						'<div class="form-group">' +
							'<label>To</label>' +
							'<input type="text" class="form-control">' +
						'</div>' +
					'</div>' +
					'<div class="col-12 col-md-6 col-lg-4">' +
						'<div class="form-group">' +
							'<label>Designation</label>' +
							'<input type="text" class="form-control">' +
						'</div>' +
					'</div>' +
				'</div>' +
			'</div>' +
			'<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
		'</div>';
		
        $(".experience-info").append(experiencecontent);
        return false;
    });
	
	// service Add More
	
    // $(".service-info").on('click','.trash', function () {
	// 	$(this).closest('.service-cont').remove();
	// 	return false;
    // });

    // $(".add-service").on('click', function () {

    //     var servicecontent = '<div class="row form-row service-cont">' +
	// 		'<div class="col-12 col-md-5">' +
	// 			'<div class="form-group">' +
	// 				'<label>Add More Services</label>' +
	// 				'<input type="text" class="form-control">' +
	// 			'</div>' +
	// 		'</div>' +
	// 		'<div class="col-12 col-md-5">' +
	// 			'<div class="form-group">' +
	// 				'<label>Year</label>' +
	// 				'<input type="text" class="form-control">' +
	// 			'</div>' +
	// 		'</div>' +
	// 		'<div class="col-12 col-md-2">' +
	// 			'<label class="d-md-block d-sm-none d-none">&nbsp;</label>' +
	// 			'<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
	// 		'</div>' +
	// 	'</div>';
		
    //     $(".service-info").append(servicecontent);
    //     return false;
    // });

	
	// Deapartments Add More
	
    $(".department-info").on('click','.trash', function () {
		$(this).closest('.department-cont').remove();
		return false;
    });

    $(".add-department").on('click', function () {

        var departmentcontent = '<div class="row form-row department-cont">' +
			'<div class="col-12 col-md-10 col-lg-5">' +
				'<div class="form-group">' +

					'<label>Add New Departments</label>' +

					'<input type="text" name="department" class="form-control">' +
				'</div>' +
			'</div>' +
			'<div class="col-12 col-md-2 col-lg-2">' +
				'<label class="d-md-block d-sm-none d-none">&nbsp;</label>' +
				'<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
			'</div>' +
		'</div>';
		
        $(".department-info").append(departmentcontent);
        return false;
    });

	// Service Add More
	
    //$(".service-info").on('click','.trash', function () {
	//	$(this).closest('.service-cont').remove();
	//	return false;
    //});

   // $(".add-service").on('click', function () {

     //   var servicecontent = '<div class="row form-row service-cont">' +
	//		'<div class="col-12 col-md-10 col-lg-5">' +
	//			'<div class="form-group">' +
//
	//				'<label>Add New Services</label>' +
//
//					'<input type="text" name="service" class="form-control">' +
//				'</div>' +
//			'</div>' +
//			'<div class="col-12 col-md-2 col-lg-2">' +
//				'<label class="d-md-block d-sm-none d-none">&nbsp;</label>' +
//				'<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
//			'</div>' +
//		'</div>';
//		
//        $(".service-info").append(servicecontent);
 //       return false;
 //   });

 $(".service-info").on('click','.trash', function () {
    $(this).closest('.service-cont').remove();
    return false;
});

$(".add-service").on('click', function () {

	var serviceContent = '<tr class="form-row service-cont" style="display:block; width:100%;">' +
    '<td class="form-row" style="padding: 0; margin-left: -10px;">' +
    '<div class="col-12 d-flex align-items-center">' +
    '<div class="col-10 pr-0">' +
    '<div class="form-group"style="margin-bottom:22px">' +
    '<label>Add New Services</label>' +
    '<input type="text" name="service" class="form-control"style="width: 93%;">' +
    '</div>' +
    '</div>' +
    '<div class="col-2" style="margin-left:-20px;margin-top:20px">' +
    '<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
    '</div>' +
    '</div>' +
    '</td>' +
    '</tr>';

    $(".service-info").append(serviceContent);
    return false;
});


	// Specialization Add More
	
    $(".specialization-info").on('click','.trash', function () {
		$(this).closest('.specialization-cont').remove();
		return false;
    });

    $(".add-specialization").on('click', function () {

        var specializationcontent = '<div class="row form-row specialization-cont">' +
			'<div class="col-12 col-md-10 col-lg-5">' +
				'<div class="form-group">' +

					'<label>Add New Specializations</label>' +

					'<input type="text" name="specialization" class="form-control">' +
				'</div>' +
			'</div>' +
			'<div class="col-12 col-md-2 col-lg-2">' +
				'<label class="d-md-block d-sm-none d-none">&nbsp;</label>' +
				'<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
			'</div>' +
		'</div>';
		
        $(".specialization-info").append(specializationcontent);
        return false;
    });

	//Operation hour add more
	//var currentDayIndex = 0;

	//$(".operation-hours-info").on('click', '.trash', function () {
	//	$(this).closest('.form-row').remove();
	//	currentDayIndex--;
	//	return false;
	//});

	//$(".add-operation-hour").on('click', function () {
	//	var days = ["TUE", "WED", "THU", "FRI"];
	//	var daysCompelte = ["Tuesday", "Wednesday", "Thursday", "Friday"];
	//	var currentDay = days[currentDayIndex];
	//	var currentDayComplete = daysCompelte[currentDayIndex];

	//	if (currentDayIndex === 3) {
	//		$(this).remove();
	//	}

	//	var operationHourContent = '<tr class="form-row">' +
	//		'<td class="form-row">' +
	//		'<div class="row">' +
	//		'<div class="col-12 col-md-4">' +
	//		'<div class="form-group">' +
	//		'<label>Day</label>' +
	//		'<select class="form-control" name="day" id="day">' +
	//		'<option value="' + currentDay + '">' + currentDayComplete + '</option>' +
	//		'</select>' +
	//		'</div>' +
	//		'</div>' +
	//		'<div class="col-12 col-md-4">' +
	//		'<div class="form-group">' +
	//		'<label>Start Time</label>' +
	//		'<input type="time" class="form-control" name="start_time" id="start_time">' +
	//		'</div>' +
	//		'</div>' +
	//		'<div class="col-12 col-md-4">' +
	//		'<div class="form-group">' +
	//		'<label>End Time</label>' +
	//		'<input type="time" class="form-control" name="end_time" id="end_time">' +
	//		'</div>' +
	//		'</div>' +
	//		'</div>' +
	//		'<div class="col-12 col-md-2 col-lg-2">' +
	//		'<label class="d-md-block d-sm-none d-none">&nbsp;</label>' +
	//		'<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
	//		'</div>' +
	//		'</td>' +
	//		'</tr>';

	//	$(".operation-hours-info").append(operationHourContent);

	//	currentDayIndex++;

	//	if (currentDayIndex === 4) {
	//		$(".add-operation-hour").remove();
	//	}

	//	return false;
	//});

	// Operation hour add more
	// Initialize currentDayIndex and daysAdded
	var currentDayIndex = 0;
	var daysAdded = [];

	// List of all days
	var days = ["MON", "TUE", "WED", "THU", "FRI"];
	var daysComplete = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

	// List of days already added
	var daysAdded = $(".operation-hours-info select[name='day']").map(function() {
		return $(this).val();
	}).get();

	if (daysAdded.length === days.length) {
		$(".add-operation-hour").remove();
	}

	$(".operation-hours-info").on('click', '.trash', function () {
		var removedDay = $(this).closest('tr').find("select[name='day']").val();
		daysAdded = daysAdded.filter(function(day) {
			return day !== removedDay;
		});
		$(this).closest('tr').remove();
		return false;
	});

	$(".add-operation-hour").on('click', function () {
		var nextDayIndex = days.findIndex(function(day) {
			return !daysAdded.includes(day);
		});

		if (nextDayIndex === -1) {
			$(this).remove();
			return false;
		}

		var nextDay = days[nextDayIndex];
		var nextDayComplete = daysComplete[nextDayIndex];

		var operationHourContent = '<tr class="form-row">' +
		'<td class="form-row" style="padding: 0; margin-left: 8px;">' +
		'<div class="row">' +
		'<div class="col-12 col-md-4" style="margin-right: 0; margin-bottom: 0;">' +
		'<div class="form-group">' +
		'<label>Day</label>' +
		'<select class="form-control" name="day" id="day">' +
		'<option value="' + nextDay + '">' + nextDayComplete + '</option>' +
		'</select>' +
		'</div>' +
		'</div>' +
		'<div class="col-12 col-md-3" style="margin-right: 0; margin-bottom: 0;">' +
		'<div class="form-group">' +
		'<label>Start Time</label>' +
		'<input type="time" class="form-control" name="start_time" id="start_time">' +
		'</div>' +
		'</div>' +
		'<div class="col-12 col-md-3" style="margin-right: 0; margin-bottom: 0;">' +
		'<div class="form-group">' +
		'<label>End Time</label>' +
		'<input type="time" class="form-control" name="end_time" id="end_time">' +
		'</div>' +
		'</div>' +
		'<div class="col-12 col-md-2 col-lg-2" style="padding-top: 0.5rem; margin-right: 0;margin-top:35px">' +
		'<a href="javascript:void(0);" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
		'</div>' +
		'</div>' +
		'</td>' +
		'</tr>';

		$(".operation-hours-info").append(operationHourContent);

		daysAdded.push(nextDay);

		if (daysAdded.length === days.length) {
			$(".add-operation-hour").remove();
		}

		return false;
	});


	// Registration Add More
	
    $(".registrations-info").on('click','.trash', function () {
		$(this).closest('.reg-cont').remove();
		return false;
    });

    $(".add-reg").on('click', function () {

        var regcontent = '<div class="row form-row reg-cont">' +
			'<div class="col-12 col-md-5">' +
				'<div class="form-group">' +
					'<label>Registrations</label>' +
					'<input type="text" class="form-control">' +
				'</div>' +
			'</div>' +
			'<div class="col-12 col-md-5">' +
				'<div class="form-group">' +
					'<label>Year</label>' +
					'<input type="text" class="form-control">' +
				'</div>' +
			'</div>' +
			'<div class="col-12 col-md-2">' +
				'<label class="d-md-block d-sm-none d-none">&nbsp;</label>' +
				'<a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a>' +
			'</div>' +
		'</div>';
		
        $(".registrations-info").append(regcontent);
        return false;
    });
	
})(jQuery);