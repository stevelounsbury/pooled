// global vars


window.onload = function(){

	$("#login-form a").click(function(){
		$(this).parent().parent().slideToggle();
		$("#signup-form").slideToggle();
	});
    
    	$("#signup-form a").click(function(){
		$(this).parent().parent().slideToggle();
		$("#login-form").slideToggle();
	});


};



