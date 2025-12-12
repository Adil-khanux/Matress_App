import frappe

def get_attribute_values(custom_name, attribute_name):
    """Return sorted numeric values for Length / Width attributes of a given template item."""
    rows = frappe.db.sql("""
        SELECT CAST(attribute_value AS DECIMAL(10,2)) AS val
        FROM `tabItem Variant Attribute`
        WHERE parent = %s
          AND attribute = %s
        ORDER BY val
    """, (template_item, attribute_name), as_dict=True)

    return [float(r.val) for r in rows]


def pick_standard_value(custom, standards):
    """
    Mattress rule:
      - diff <= 0.5 → pick lower
      - diff > 0.5  → pick next higher
    """
    if not standards:
        return custom  # fallback if no standard exists

    standards = sorted(standards)

    # Below minimum
    if custom <= standards[0]:
        return standards[0]

    # Above maximum
    if custom >= standards[-1]:
        return standards[-1]

    # Find nearest standard
    for i in range(len(standards) - 1):
        low = standards[i]
        high = standards[i + 1]
        if low <= custom <= high:
            diff = custom - low
            return low if diff <= 0.5 else high

    return standards[-1]


def find_variant_item(custom_name, selected_length, selected_width):
    variant = frappe.db.sql("""
        SELECT item.name, item.item_name
        FROM `tabItem` item
        JOIN `tabItem Variant Attribute` attr1
            ON attr1.parent = item.name
            AND attr1.attribute = 'Length'
            AND CAST(attr1.attribute_value AS DECIMAL(10,2)) = %s
        JOIN `tabItem Variant Attribute` attr2
            ON attr2.parent = item.name
            AND attr2.attribute = 'Width'
            AND CAST(attr2.attribute_value AS DECIMAL(10,2)) = %s
        WHERE item.variant_of = %s
        LIMIT 1
    """, (selected_length, selected_width, template_item), as_dict=True)

    return variant[0] if variant else None


@frappe.whitelist()
def get_mattress_variant(custom_name, custom_length, custom_width):
    """
    Returns the nearest standard variant for the given custom_length and custom_width
    of a specific template_item.
    """
    custom_length = float(custom_length)
    custom_width = float(custom_width)

    # Step 1: get standard lengths and widths for the template item
    standard_lengths = get_attribute_values(custom_name, "Length")
    standard_widths = get_attribute_values(custom_name, "Width")

    # Step 2: pick nearest standard values
    selected_length = pick_standard_value(custom_length, standard_lengths)
    selected_width = pick_standard_value(custom_width, standard_widths)

    # Step 3: find matching variant
    variant = find_variant_item(custom_name, selected_length, selected_width)

    return {
    "selected_length": selected_length,
    "selected_width": selected_width,
    "item_code": variant["name"] if variant else None,
    "item_name": variant["item_name"] if variant else None,
    "found": True if variant else False,
    "message": "No matching variant found" if not variant else ""
}

