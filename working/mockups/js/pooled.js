
$.ajaxSetup( { type: "POST" } );

var Pooled = {
	show_message : function(resp) {
		$("#message").html("<p>" + resp.message + "</p>").fadeIn("slow");
		if (resp.status == 0) 
		{ 
			$("#message p").addClass("error")
			$("#message").addClass("error").append("<p class='small'>Click to hide this message</p><div class='clear'></div>");
			$("#message").click(function(){$(this).fadeOut(1000);});
		}
		else
		{
			$("#message").fadeOut(3000);
		}
	},
	autocomplete : function(config) {
		var _helper = config.complete_helper || "#autocomplete";
		var _target = config.complete_target;
		var _id_target = config.id_target;
		var _params = {};
		var _url = config.url;
		var _min_length = config.min_length;
		var _after_select = config.after_select;
		
		$(_target).keyup(
			function () { 
				if (this.value.length > _min_length)
				{
					$.each(config.params, function(i,n){ 
						if (typeof(n)=="function") { 
							_params[i] = n(); 
						} else {
							_params[i] = n;
						}
					}); 
					var t = new Date();
					_params.time = t.getTime();
					$.getJSON(_url, _params,
						function(json){
							$(_helper).width($(_target).width());
							$(_helper).css( { left: $(_target).css("left"), top: parseInt($(_target).css("top")) + $(_target).height() + 10 + "px" } );
							$(_helper).empty().append("<ul>").hide();
							$.each(json, function(i, n) {
								$("<li>" + n.name + "</li>")
								.hover( function () { $(this).addClass("hover"); }, function () { $(this).removeClass("hover"); } ) 
								.click( function () {
									$(_target).attr("value", n.name);
									$(_id_target).attr("value", n.id);
									$(_helper).fadeOut("slow");
									if (typeof(_after_select) == "function") { _after_select(); }
								})
								.appendTo(_helper + " ul");
							});
							$(_helper).show();
						}
					);
				}
				else
				{
					$(_helper).empty().hide();
				}
			}
		);
		$(_target).focus( function() { $(_target).keyup(); } ); 
	}
};

// ucfirst modified from: 
// http://www.mediacollege.com/internet/javascript/text/case-capitalize.html 
function ucfirst(str)
{
	tmpStr = str.toLowerCase();
	stringLen = tmpStr.length;
	if (stringLen > 0)
	{
		for (i = 0; i < stringLen; i++)
		{
			if (i == 0)
			{
				tmpChar = tmpStr.substring(0,1).toUpperCase();
				postString = tmpStr.substring(1,stringLen);
				tmpStr = tmpChar + postString;
			}
			else
			{
				tmpChar = tmpStr.substring(i,i+1);
				if (tmpChar == " " && i < (stringLen-1))
				{
					tmpChar = tmpStr.substring(i+1,i+2).toUpperCase();
					preString = tmpStr.substring(0,i+1);
					postString = tmpStr.substring(i+2,stringLen);
					tmpStr = preString + tmpChar + postString;
				}
			}
		}
	}
	return tmpStr;
}
