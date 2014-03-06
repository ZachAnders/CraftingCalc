function select_tab(tab_id) {
	for (var i=0; i < 3; i++) {
		$("#tab_" + i).removeClass("active");
		$("#pane_" + i).addClass("hidden");
	}
	$("#tab_" + tab_id).addClass("active");
	$("#pane_" + tab_id).removeClass("hidden");
}
