function select_tab(tab_id) {
	for (var i=0; i < 3; i++) {
		$("#tab_" + i).removeClass("active");
		$("#pane_" + i).addClass("hidden");
	}
	$("#tab_" + tab_id).addClass("active");
	$("#pane_" + tab_id).removeClass("hidden");
	if (tab_id == 1) {
		add_gold_val(0);
		add_xp_val(0);
	}
}

function calc_onload(tab_num) {
	select_tab(tab_num);
}

function del_wright(wright_id) {
	$.post("del_wright", { "id" : wright_id }).done(function(data) {
		$("#wright_" + wright_id).remove();
	});
}

function add_gold(form) {
	val = $("#" + form).val();
	console.log(val);
	add_gold_val(val);
	return false;
}

function add_gold_val(val) {
	$.post("modify_resources", {"action":"add_gold", "value":val}).done(function(data) {
		$("#gold_value").text(data.value);
	}, "json");
}

function add_xp_val(val) {
	$.post("modify_resources", {"action":"add_exp", "value":val}).done(function(data) {
		$("#exp_value").text(data.value);
	}, "json");
}

function add_exp(form, divisor) {
	val = $("#" + form).val();
	val = Math.floor(val/divisor);
	add_xp_val(val);
	return false;

}

function add_job() {
	vals = $("#add_job_form").serialize()
	$.post("add_job", vals).done(function(data) {
		console.log(data);
		if (data.status == 0) {
			alert = $("#job_error_alert")
			alert.text(data.error);
			alert.removeClass("hidden");
		} else {
			location.reload();
		}
	}, "json");
	return false;
}

function del_job(job_id) {
	$.post("del_job", { "id" : job_id }).done(function(data) {
		$("#job_" + job_id).remove();
	});
}

function pass_time(val) {
	$.post("pass_time", { "value" : val}).done(function(data) {
		location.reload();
	});
}
