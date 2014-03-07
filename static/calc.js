function select_tab(tab_id) {
	for (var i=0; i < 3; i++) {
		$("#tab_" + i).removeClass("active");
		$("#pane_" + i).addClass("hidden");
	}
	$("#tab_" + tab_id).addClass("active");
	$("#pane_" + tab_id).removeClass("hidden");
}

function calc_onload(tab_num) {
	select_tab(tab_num);
}

function del_wright(wright_id) {
	$.post("/rm_wright", { "wright_id" : wright_id }).done(function(data) {
		location.reload();
	});
}
