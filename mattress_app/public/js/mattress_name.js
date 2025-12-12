frappe.ui.form.on("Quotation Item", {
    custom_length: function(frm, cdt, cdn) {
        calculate_item(frm, cdt, cdn);
    },
    custom_width: function(frm, cdt, cdn) {
        calculate_item(frm, cdt, cdn);
    }
});

function calculate_item(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.custom_length || !row.custom_width) return;

    frappe.call({
        method: "mattress_app.api.matress_name.get_mattress_variant",
        args: {
            custom_length: row.custom_length,
            custom_width: row.custom_width,
        },
        callback: function(r) {
            if (!r.message) return;

            if (r.message.found) {
                frappe.model.set_value(cdt, cdn, "item_code", r.message.item_code);
                frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
                frappe.model.set_value(cdt, cdn, "custom_length", r.message.selected_length);
                frappe.model.set_value(cdt, cdn, "custom_width", r.message.selected_width);
                frappe.model.set_value(cdt, cdn, "custom_name", r.message.item_code);
            } else {
                frappe.msgprint(r.message.message);
            }
        }
    });
}
