"""Build the Tableau workbook for the Insurance Claims dashboard.

Run from the repository root with:
    .\\.venv\\Scripts\\python.exe tableau\\build_workbook.py

The output is a Tableau 2020.1-compatible TWB that connects to the two CSV
exports in data/processed. Tableau Desktop can open the workbook directly.
"""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = Path(__file__).with_name("insurance_claims_dashboard.twb")

PORTFOLIO_DS = "federated.insurance_portfolio"
CLAIMS_DS = "federated.insurance_claims"

# Human-readable Tableau captions. Internal field names remain stable so that
# the CSV mapping and calculated-field formulas are not affected.
DISPLAY_LABELS = {
    "ClaimNb": "Claim Count",
    "VehGas": "Fuel Type",
    "TotalClaimAmount": "Total Claim Cost",
    "AverageClaimAmount": "Average Claim Amount",
    "MaxClaimAmount": "Maximum Claim Amount",
    "DriverAgeGroup": "Driver Age Group",
    "VehicleAgeGroup": "Vehicle Age Group",
    "VehiclePowerGroup": "Vehicle Power Group",
    "BonusMalusGroup": "Bonus–Malus Group",
    "ClaimAmount": "Claim Amount",
    "ClaimAmountRank": "Claim Cost Rank",
    "CumulativeClaimCost": "Cumulative Claim Cost",
    "CumulativeClaimCostPct": "Cumulative Claim Cost Share",
    "CumulativeClaimPct": "Cumulative Claim Share",
    "IsExtremeClaim": "Extreme Claim Flag",
}

PORTFOLIO_FIELDS = [
    ("IDpol", "string", "dimension", "nominal", None),
    ("Exposure", "real", "measure", "quantitative", "n#,##0.0"),
    ("ClaimNb", "integer", "measure", "quantitative", "n#,##0"),
    ("VehPower", "integer", "dimension", "ordinal", None),
    ("VehAge", "integer", "measure", "quantitative", "n#,##0"),
    ("DrivAge", "integer", "measure", "quantitative", "n#,##0"),
    ("BonusMalus", "integer", "measure", "quantitative", "n#,##0"),
    ("VehBrand", "string", "dimension", "nominal", None),
    ("VehGas", "string", "dimension", "nominal", None),
    ("Area", "string", "dimension", "nominal", None),
    ("Density", "integer", "measure", "quantitative", "n#,##0"),
    ("Region", "string", "dimension", "nominal", None),
    ("TotalClaimAmount", "real", "measure", "quantitative", 'c"€"#,##0;("€"#,##0)'),
    ("SeverityClaimCount", "integer", "measure", "quantitative", "n#,##0"),
    ("AverageClaimAmount", "real", "measure", "quantitative", 'c"€"#,##0;("€"#,##0)'),
    ("MaxClaimAmount", "real", "measure", "quantitative", 'c"€"#,##0;("€"#,##0)'),
    ("DriverAgeGroup", "string", "dimension", "nominal", None),
    ("VehicleAgeGroup", "string", "dimension", "nominal", None),
    ("VehiclePowerGroup", "string", "dimension", "nominal", None),
    ("BonusMalusGroup", "string", "dimension", "nominal", None),
]

PORTFOLIO_CALCULATIONS = [
    ("Policy Count", "integer", "1", "n#,##0"),
    ("Claim Frequency", "real", "SUM([ClaimNb]) / SUM([Exposure])", "n0.0000"),
    (
        "Average Severity",
        "real",
        "IF SUM([SeverityClaimCount]) = 0 THEN NULL ELSE SUM([TotalClaimAmount]) / SUM([SeverityClaimCount]) END",
        'c"€"#,##0;("€"#,##0)',
    ),
]

CLAIMS_FIELDS = [
    ("ClaimRowID", "integer", "dimension", "ordinal", None),
    ("IDpol", "string", "dimension", "nominal", None),
    ("ClaimAmount", "real", "measure", "quantitative", 'c"€"#,##0;("€"#,##0)'),
    ("ClaimAmountRank", "integer", "dimension", "ordinal", None),
    ("CumulativeClaimCost", "real", "measure", "quantitative", 'c"€"#,##0;("€"#,##0)'),
    ("CumulativeClaimCostPct", "real", "measure", "quantitative", "p0.0%"),
    ("CumulativeClaimPct", "real", "measure", "quantitative", "p0.0%"),
    ("IsExtremeClaim", "boolean", "dimension", "nominal", None),
    ("Region", "string", "dimension", "nominal", None),
    ("DrivAge", "integer", "measure", "quantitative", "n#,##0"),
    ("VehAge", "integer", "measure", "quantitative", "n#,##0"),
    ("VehPower", "integer", "dimension", "ordinal", None),
    ("BonusMalus", "integer", "measure", "quantitative", "n#,##0"),
    ("VehBrand", "string", "dimension", "nominal", None),
    ("VehGas", "string", "dimension", "nominal", None),
    ("Area", "string", "dimension", "nominal", None),
    ("DriverAgeGroup", "string", "dimension", "nominal", None),
    ("VehicleAgeGroup", "string", "dimension", "nominal", None),
    ("VehiclePowerGroup", "string", "dimension", "nominal", None),
    ("BonusMalusGroup", "string", "dimension", "nominal", None),
]


def field(name: str) -> str:
    return f"[{name}]"


def caption(name: str) -> str:
    return DISPLAY_LABELS.get(name, name)


def direct_ref(datasource: str, name: str) -> str:
    """Return Tableau's direct field reference (used by dimensions and aggregate calculations)."""
    return f"[{datasource}].{field(name)}"


def instance_name(name: str, derivation: str, type_name: str) -> str:
    suffix = {"nominal": "nk", "ordinal": "ok", "quantitative": "qk"}[type_name]
    return f"[{derivation.lower()}:{name}:{suffix}]"


def instance(datasource: str, name: str, derivation: str, type_name: str) -> str:
    return f"[{datasource}].{instance_name(name, derivation, type_name)}"


def add_column(parent: ET.Element, name: str, datatype: str, role: str, type_name: str, fmt: str | None) -> None:
    attrs = {
        "caption": caption(name),
        "datatype": datatype,
        "name": field(name),
        "role": role,
        "type": type_name,
    }
    if datatype in {"integer", "real"}:
        attrs["aggregation"] = "Sum"
    if fmt:
        attrs["default-format"] = fmt
    ET.SubElement(parent, "column", attrs)


def add_datasource(workbook: ET.Element, datasource_caption: str, datasource: str, filename: str, fields, calculations=()) -> None:
    ds = ET.SubElement(workbook, "datasource", {"caption": datasource_caption, "inline": "true", "name": datasource, "version": "18.1"})
    connection = ET.SubElement(ds, "connection", {"class": "federated"})
    named_connections = ET.SubElement(connection, "named-connections")
    leaf_name = f"{datasource}.textscan"
    named = ET.SubElement(named_connections, "named-connection", {"name": leaf_name})
    ET.SubElement(
        named,
        "connection",
        {
            "auto-extract": "no",
            "character-set": "UTF-8",
            "class": "textscan",
            "directory": str(PROCESSED_DIR).replace("\\", "/"),
            "filename": filename,
            "force-character-set": "no",
            "force-header": "no",
            "force-separator": "no",
            "header": "yes",
            "separator": ",",
            "text-qualifier": '&quot;',
        },
    )
    relation = ET.SubElement(
        connection,
        "relation",
        {"connection": leaf_name, "name": f"{Path(filename).stem}#csv", "table": f"[{Path(filename).stem}#csv]", "type": "table"},
    )
    columns = ET.SubElement(relation, "columns", {"character-set": "UTF-8", "header": "yes", "locale": "en_US", "separator": ",", "text-qualifier": '&quot;'})
    for ordinal, (name, datatype, _role, _type_name, _fmt) in enumerate(fields):
        ET.SubElement(columns, "column", {"datatype": datatype, "name": name, "ordinal": str(ordinal)})
    ET.SubElement(connection, "refresh", {"increment-key": "", "incremental-updates": "false"})
    # Preserve the physical-to-local field mapping emitted by Tableau Desktop
    # for textscan connections. Without these records, Tableau 2020.1 can
    # read CSV metadata but does not bind worksheet fields such as Exposure.
    metadata_records = ET.SubElement(connection, "metadata-records")
    remote_types = {"integer": "20", "real": "5", "string": "129", "boolean": "11"}
    for ordinal, (name, datatype, _role, _type_name, _fmt) in enumerate(fields):
        record = ET.SubElement(metadata_records, "metadata-record", {"class": "column"})
        ET.SubElement(record, "remote-name").text = name
        ET.SubElement(record, "remote-type").text = remote_types[datatype]
        ET.SubElement(record, "local-name").text = field(name)
        ET.SubElement(record, "parent-name").text = f"[{Path(filename).stem}#csv]"
        ET.SubElement(record, "remote-alias").text = name
        ET.SubElement(record, "ordinal").text = str(ordinal)
        ET.SubElement(record, "local-type").text = datatype
        ET.SubElement(record, "aggregation").text = "Sum" if datatype in {"integer", "real"} else "Count"
        if datatype == "string":
            ET.SubElement(record, "scale").text = "1"
            ET.SubElement(record, "width").text = "1073741823"
        ET.SubElement(record, "contains-null").text = "true"
    ET.SubElement(ds, "aliases", {"enabled": "yes"})
    for name, datatype, role, type_name, fmt in fields:
        add_column(ds, name, datatype, role, type_name, fmt)
    for name, datatype, formula, fmt in calculations:
        calculation_column = ET.SubElement(
            ds,
            "column",
            {"caption": caption(name), "datatype": datatype, "default-format": fmt, "name": field(name), "role": "measure", "type": "quantitative"},
        )
        ET.SubElement(calculation_column, "calculation", {"class": "tableau", "formula": formula})


def add_dependencies(parent: ET.Element, datasource: str, fields, calculations=(), used=()) -> None:
    dependencies = ET.SubElement(parent, "datasource-dependencies", {"datasource": datasource})
    field_lookup = {name: (datatype, role, type_name, fmt) for name, datatype, role, type_name, fmt in fields}
    calculation_lookup = {name: (datatype, formula, fmt) for name, datatype, formula, fmt in calculations}
    for name in used:
        if name in field_lookup:
            datatype, role, type_name, fmt = field_lookup[name]
            add_column(dependencies, name, datatype, role, type_name, fmt)
        elif name in calculation_lookup:
            datatype, formula, fmt = calculation_lookup[name]
            column = ET.SubElement(
                dependencies,
                "column",
                {"caption": caption(name), "datatype": datatype, "default-format": fmt, "name": field(name), "role": "measure", "type": "quantitative"},
            )
            ET.SubElement(column, "calculation", {"class": "tableau", "formula": formula})
    for name, derivation in used.items() if isinstance(used, dict) else []:
        if name in field_lookup:
            datatype, role, type_name, _fmt = field_lookup[name]
        else:
            datatype, _formula, _fmt = calculation_lookup[name]
            type_name = "quantitative"
        ET.SubElement(
            dependencies,
            "column-instance",
            {"column": field(name), "derivation": derivation, "name": instance_name(name, derivation, type_name), "pivot": "key", "type": type_name},
        )


def add_worksheet(
    workbook: ET.Element,
    name: str,
    datasource: str,
    fields,
    calculations,
    rows: str,
    cols: str,
    mark: str,
    encodings,
    title: str,
    used: dict[str, str],
    filters=(),
    tooltip_lines=(),
    show_mark_labels: bool = False,
) -> None:
    worksheet = ET.SubElement(workbook, "worksheet", {"name": name})
    layout = ET.SubElement(worksheet, "layout-options")
    title_node = ET.SubElement(layout, "title")
    formatted = ET.SubElement(title_node, "formatted-text")
    ET.SubElement(formatted, "run", {"bold": "true", "fontcolor": "#254C65", "fontname": "Arial", "fontsize": "11"}).text = title
    table = ET.SubElement(worksheet, "table")
    view = ET.SubElement(table, "view")
    datasources = ET.SubElement(view, "datasources")
    ET.SubElement(datasources, "datasource", {"caption": "Insurance Portfolio" if datasource == PORTFOLIO_DS else "Insurance Claims", "name": datasource})
    add_dependencies(view, datasource, fields, calculations, used)
    for filter_column, min_value, max_value in filters:
        filter_node = ET.SubElement(view, "filter", {"class": "quantitative", "column": instance(datasource, filter_column, "None", "ordinal"), "included-values": "in-range"})
        ET.SubElement(filter_node, "min").text = str(min_value)
        ET.SubElement(filter_node, "max").text = str(max_value)
    ET.SubElement(view, "aggregation", {"value": "true"})
    style = ET.SubElement(table, "style")
    ET.SubElement(ET.SubElement(style, "style-rule", {"element": "worksheet"}), "format", {"attr": "font-family", "value": "Arial"})
    if show_mark_labels:
        label_style = ET.SubElement(style, "style-rule", {"element": "mark"})
        ET.SubElement(label_style, "format", {"attr": "mark-labels-show", "value": "true"})
    panes = ET.SubElement(table, "panes")
    pane = ET.SubElement(panes, "pane")
    pane_view = ET.SubElement(pane, "view")
    ET.SubElement(pane_view, "breakdown", {"value": "auto"})
    ET.SubElement(pane, "mark", {"class": mark})
    encoding_node = ET.SubElement(pane, "encodings")
    for encoding, column in encodings:
        # Tableau's TWB schema names the Marks-card Detail shelf "lod".
        # "detail" is a UI label, not a valid XML encoding element.
        encoding_element = "lod" if encoding == "detail" else encoding
        ET.SubElement(encoding_node, encoding_element, {"column": column})
    # Tableau 2020.1 permits a custom tooltip within the pane (not directly
    # under worksheet) and does not accept a show-buttons attribute here.
    if tooltip_lines:
        customized_tooltip = ET.SubElement(pane, "customized-tooltip")
        formatted_tooltip = ET.SubElement(customized_tooltip, "formatted-text")
        for line in tooltip_lines:
            ET.SubElement(formatted_tooltip, "run").text = f"{line}\n"
    ET.SubElement(table, "rows").text = rows
    ET.SubElement(table, "cols").text = cols


def add_text_zone(parent: ET.Element, zone_id: int, x: int, y: int, w: int, h: int, text: str, size: int = 10) -> None:
    zone = ET.SubElement(parent, "zone", {"fixed-size": str(h), "h": str(h), "id": str(zone_id), "is-fixed": "true", "type": "text", "w": str(w), "x": str(x), "y": str(y)})
    formatted = ET.SubElement(zone, "formatted-text")
    ET.SubElement(formatted, "run", {"fontcolor": "#404040", "fontname": "Arial", "fontsize": str(size)}).text = text


def add_sheet_zone(parent: ET.Element, zone_id: int, sheet: str, x: int, y: int, w: int, h: int) -> None:
    ET.SubElement(parent, "zone", {"h": str(h), "id": str(zone_id), "name": sheet, "show-title": "true", "w": str(w), "x": str(x), "y": str(y)})


def add_filter_zone(parent: ET.Element, zone_id: int, field_name: str, sheet_name: str, x: int, y: int, w: int) -> None:
    ET.SubElement(parent, "zone", {"h": "3500", "id": str(zone_id), "name": sheet_name, "param": direct_ref(PORTFOLIO_DS, field_name), "show-null-ctrls": "false", "type": "filter", "values": "relevant", "w": str(w), "x": str(x), "y": str(y)})


def add_dashboard(workbook: ET.Element, name: str, datasource_specs, zone_builder) -> None:
    dashboard = ET.SubElement(workbook, "dashboard", {"name": name})
    layout = ET.SubElement(dashboard, "layout-options")
    title = ET.SubElement(ET.SubElement(layout, "title"), "formatted-text")
    ET.SubElement(title, "run", {"bold": "true", "fontcolor": "#1F4E79", "fontname": "Arial", "fontsize": "16"}).text = name
    ET.SubElement(dashboard, "size", {"maxheight": "900", "maxwidth": "1400", "minheight": "900", "minwidth": "1400"})
    datasources = ET.SubElement(dashboard, "datasources")
    for datasource, fields in datasource_specs:
        ET.SubElement(
            datasources,
            "datasource",
            {"caption": "Insurance Portfolio" if datasource == PORTFOLIO_DS else "Insurance Claims", "name": datasource},
        )
        dashboard_dimensions = {
            field_name: "None"
            for field_name, _datatype, role, type_name, _fmt in fields
            if role == "dimension" and type_name in {"nominal", "ordinal"}
        }
        add_dependencies(dashboard, datasource, fields, (), dashboard_dimensions)
    zones = ET.SubElement(dashboard, "zones")
    root = ET.SubElement(zones, "zone", {"h": "100000", "id": "1", "type": "layout-basic", "w": "100000", "x": "0", "y": "0"})
    ET.SubElement(root, "zone", {"h": "5000", "id": "2", "type": "title", "w": "100000", "x": "0", "y": "0"})
    zone_builder(root)


def add_dashboard_action(
    actions: ET.Element,
    *,
    caption: str,
    name: str,
    dashboard: str,
    source_sheet: str,
    command: str,
    parameters: dict[str, str],
) -> None:
    """Add a Tableau dashboard action using Tableau's legacy action XML."""
    action = ET.SubElement(actions, "action", {"caption": caption, "name": name})
    ET.SubElement(action, "activation", {"auto-clear": "true", "type": "on-select"})
    ET.SubElement(action, "source", {"dashboard": dashboard, "type": "sheet", "worksheet": source_sheet})
    command_node = ET.SubElement(action, "command", {"command": command})
    for parameter_name, value in parameters.items():
        ET.SubElement(command_node, "param", {"name": parameter_name, "value": value})


def validate_workbook(workbook: ET.Element) -> None:
    worksheet_names = {worksheet.get("name") for worksheet in workbook.findall("worksheets/worksheet")}
    dashboard_names = {dashboard.get("name") for dashboard in workbook.findall("dashboards/dashboard")}
    allowed_encodings = {"color", "size", "text", "shape", "wedge-size", "lod", "geometry", "image", "tooltip", "path"}
    aggregate_calculations = {
        name for name, _datatype, formula, _fmt in PORTFOLIO_CALCULATIONS if "SUM(" in formula
    }

    for worksheet in workbook.findall("worksheets/worksheet"):
        table = worksheet.find("table")
        view = table.find("view")
        dependency_instances = {}
        dependency_columns = {}
        for dependencies in view.findall("datasource-dependencies"):
            datasource = dependencies.get("datasource")
            dependency_instances[datasource] = {
                column_instance.get("name") for column_instance in dependencies.findall("column-instance")
            }
            dependency_columns[datasource] = {
                column.get("name") for column in dependencies.findall("column")
            }

        references = []
        for shelf_name in ("rows", "cols"):
            shelf = table.find(shelf_name)
            if shelf is not None and shelf.text:
                references.append(shelf.text)
        references.extend(
            encoding.get("column")
            for encoding in table.findall("panes/pane/encodings/*")
            if encoding.get("column")
        )
        references.extend(
            filter_node.get("column")
            for filter_node in view.findall("filter")
            if filter_node.get("column")
        )

        for reference in references:
            matching_datasource = next(
                (datasource for datasource in dependency_instances if reference.startswith(f"[{datasource}].")),
                None,
            )
            if matching_datasource is None:
                raise ValueError(f"Unqualified or unknown worksheet field reference in {worksheet.get('name')}: {reference}")
            local_reference = reference.split("].", 1)[1]
            if local_reference not in dependency_instances[matching_datasource] and local_reference not in dependency_columns[matching_datasource]:
                raise ValueError(f"Missing worksheet field dependency in {worksheet.get('name')}: {local_reference}")
            if local_reference in {field(name) for name, *_rest in PORTFOLIO_FIELDS if _rest[2] == "nominal"}:
                continue
            if local_reference in {field(name) for name in aggregate_calculations}:
                continue
            if ":nk]" in local_reference and not local_reference.startswith("[attribute:"):
                raise ValueError(f"Nominal field must use a direct reference in {worksheet.get('name')}: {reference}")

        encoding_tags = {encoding.tag for encoding in table.findall("panes/pane/encodings/*")}
        invalid_encodings = encoding_tags - allowed_encodings
        if invalid_encodings:
            raise ValueError(f"Invalid Tableau encodings in {worksheet.get('name')}: {sorted(invalid_encodings)}")

        has_shelf = any(
            table.find(shelf_name) is not None and table.find(shelf_name).text
            for shelf_name in ("rows", "cols")
        )
        if not has_shelf and not encoding_tags:
            raise ValueError(f"Worksheet has no configured view: {worksheet.get('name')}")

    for dashboard in workbook.findall("dashboards/dashboard"):
        dashboard_instances = {}
        dashboard_columns = {}
        for dependencies in dashboard.findall("datasource-dependencies"):
            datasource = dependencies.get("datasource")
            dashboard_instances[datasource] = {
                column_instance.get("name") for column_instance in dependencies.findall("column-instance")
            }
            dashboard_columns[datasource] = {
                column.get("name") for column in dependencies.findall("column")
            }

        for zone in dashboard.findall("zones/zone/zone"):
            zone_sheet = zone.get("name")
            zone_type = zone.get("type")
            if zone_sheet and zone_type not in {"filter", "color"} and zone_sheet not in worksheet_names:
                raise ValueError(f"Dashboard zone references an unknown worksheet: {zone_sheet}")
            if zone_type == "filter":
                if zone_sheet not in worksheet_names:
                    raise ValueError(f"Dashboard filter references an unknown worksheet: {zone_sheet}")
                reference = zone.get("param", "")
                matching_datasource = next(
                    (datasource for datasource in dashboard_instances if reference.startswith(f"[{datasource}].")),
                    None,
                )
                if matching_datasource is None:
                    raise ValueError(f"Unqualified or unknown dashboard filter reference: {reference}")
                local_reference = reference.split("].", 1)[1]
                if local_reference not in dashboard_instances[matching_datasource] and local_reference not in dashboard_columns[matching_datasource]:
                    raise ValueError(f"Missing dashboard filter dependency: {local_reference}")
                if ":nk]" in local_reference:
                    raise ValueError(f"Dashboard filter must use a direct nominal-field reference: {reference}")

    expected_action_commands = {
        "[Action_Filter_Selected_Region]": "tsc:tsl-filter",
        "[Action_Highlight_Driver_Age]": "tsc:brush",
    }
    actions = workbook.find("actions")
    if actions is None:
        raise ValueError("Workbook has no dashboard actions")
    configured_actions = {action.get("name"): action for action in actions.findall("action")}
    if set(configured_actions) != set(expected_action_commands):
        raise ValueError("Workbook dashboard actions do not match the expected UX configuration")
    for action_name, expected_command in expected_action_commands.items():
        action = configured_actions[action_name]
        source = action.find("source")
        command = action.find("command")
        if source is None or source.get("worksheet") not in worksheet_names:
            raise ValueError(f"Action {action_name} references an unknown source worksheet")
        if source.get("dashboard") not in dashboard_names:
            raise ValueError(f"Action {action_name} references an unknown source dashboard")
        if command is None or command.get("command") != expected_command:
            raise ValueError(f"Action {action_name} has an invalid Tableau command")
        parameters = {param.get("name"): param.get("value") for param in command.findall("param")}
        if parameters.get("target") not in dashboard_names:
            raise ValueError(f"Action {action_name} references an unknown target dashboard")

    for worksheet in workbook.findall("worksheets/worksheet"):
        tooltip = worksheet.find("table/panes/pane/customized-tooltip/formatted-text")
        if tooltip is None or not list(tooltip):
            raise ValueError(f"Worksheet {worksheet.get('name')} has no explanatory tooltip")


def main() -> None:
    for required in (PROCESSED_DIR / "tableau_portfolio.csv", PROCESSED_DIR / "tableau_claims.csv"):
        if not required.exists():
            raise FileNotFoundError(f"Required Tableau data source does not exist: {required}")

    ET.register_namespace("user", "http://www.tableausoftware.com/xml/user")
    workbook = ET.Element(
        "workbook",
        {"locale": "en_US", "source-build": "2020.1", "source-platform": "win", "version": "18.1"},
    )
    preferences = ET.SubElement(workbook, "preferences")
    ET.SubElement(preferences, "preference", {"name": "ui.shelf.height", "value": "26"})
    ET.SubElement(workbook, "style-theme", {"name": "smooth"})
    datasources = ET.SubElement(workbook, "datasources")
    add_datasource(datasources, "Insurance Portfolio", PORTFOLIO_DS, "tableau_portfolio.csv", PORTFOLIO_FIELDS, PORTFOLIO_CALCULATIONS)
    add_datasource(datasources, "Insurance Claims", CLAIMS_DS, "tableau_claims.csv", CLAIMS_FIELDS)

    # These actions make exploration intentional: one click on a region filters
    # the companion overview views, while a selected driver-age mark highlights
    # the matching row in the driver/vehicle matrix without hiding other marks.
    actions = ET.SubElement(workbook, "actions")
    add_dashboard_action(
        actions,
        caption="Filter overview by selected region",
        name="[Action_Filter_Selected_Region]",
        dashboard="Executive Portfolio Overview",
        source_sheet="Regional Claim Frequency",
        command="tsc:tsl-filter",
        parameters={
            "exclude": "Regional Claim Frequency",
            "special-fields": "all",
            "target": "Executive Portfolio Overview",
        },
    )
    add_dashboard_action(
        actions,
        caption="Highlight selected driver age group in matrix",
        name="[Action_Highlight_Driver_Age]",
        dashboard="Claims & Risk Segments",
        source_sheet="Driver Age Frequency Severity",
        command="tsc:brush",
        parameters={
            "exclude": "Driver Age Frequency Severity",
            "field-captions": "Driver Age Group",
            "target": "Claims & Risk Segments",
        },
    )

    worksheets = ET.SubElement(workbook, "worksheets")
    portfolio_measure_sheets = [
        ("KPI Policy Count", "Policy Count", "Policy Count", "Sum"),
        ("KPI Exposure", "Exposure", "Exposure", "Sum"),
        ("KPI Claim Count", "Claim Count", "ClaimNb", "Sum"),
        ("KPI Claim Frequency", "Claim Frequency", "Claim Frequency", "None"),
        ("KPI Total Claim Cost", "Total Claim Cost", "TotalClaimAmount", "Sum"),
        ("KPI Average Severity", "Average Severity", "Average Severity", "None"),
    ]
    for worksheet_name, title, measure, derivation in portfolio_measure_sheets:
        measure_type = "quantitative"
        measure_ref = direct_ref(PORTFOLIO_DS, measure) if measure in {"Claim Frequency", "Average Severity"} else instance(PORTFOLIO_DS, measure, derivation, measure_type)
        kpi_definition = {
            "Policy Count": "Number of distinct policies in the selected portfolio.",
            "Exposure": "Total observed policy time, measured in years.",
            "Claim Count": "Number of reported claims during the selected exposure.",
            "Claim Frequency": "Reported claims per exposure year: Claim Count / Exposure.",
            "Total Claim Cost": "Aggregate observed claim cost in euros.",
            "Average Severity": "Average observed cost per claim in euros.",
        }[title]
        add_worksheet(
            worksheets,
            worksheet_name,
            PORTFOLIO_DS,
            PORTFOLIO_FIELDS,
            PORTFOLIO_CALCULATIONS,
            "",
            "",
            "Text",
            [("text", measure_ref)],
            title,
            {measure: derivation},
            tooltip_lines=(f"{title}: <{measure_ref}>", kpi_definition),
            show_mark_labels=True,
        )

    region_ref = direct_ref(PORTFOLIO_DS, "Region")
    frequency_ref = direct_ref(PORTFOLIO_DS, "Claim Frequency")
    total_cost_ref = instance(PORTFOLIO_DS, "TotalClaimAmount", "Sum", "quantitative")
    driver_ref = direct_ref(PORTFOLIO_DS, "DriverAgeGroup")
    driver_tooltip_ref = instance(PORTFOLIO_DS, "DriverAgeGroup", "Attribute", "nominal")
    power_ref = direct_ref(PORTFOLIO_DS, "VehiclePowerGroup")
    exposure_ref = instance(PORTFOLIO_DS, "Exposure", "Sum", "quantitative")
    severity_ref = direct_ref(PORTFOLIO_DS, "Average Severity")
    add_worksheet(
        worksheets, "Regional Claim Frequency", PORTFOLIO_DS, PORTFOLIO_FIELDS, PORTFOLIO_CALCULATIONS, region_ref, frequency_ref, "Bar", [("color", region_ref), ("tooltip", total_cost_ref)], "Claim Frequency by Region", {"Region": "None", "Claim Frequency": "None", "TotalClaimAmount": "Sum"},
        tooltip_lines=(f"Region: <{region_ref}>", f"Claim Frequency: <{frequency_ref}>", f"Total Claim Cost: <{total_cost_ref}>", "Claim Frequency is reported claims per exposure year.", "Select a region to filter the companion overview views."),
    )
    add_worksheet(
        worksheets, "Regional Claim Cost", PORTFOLIO_DS, PORTFOLIO_FIELDS, PORTFOLIO_CALCULATIONS, region_ref, total_cost_ref, "Bar", [("color", region_ref), ("tooltip", frequency_ref)], "Total Claim Cost by Region", {"Region": "None", "TotalClaimAmount": "Sum", "Claim Frequency": "None"},
        tooltip_lines=(f"Region: <{region_ref}>", f"Total Claim Cost: <{total_cost_ref}>", f"Claim Frequency: <{frequency_ref}>", "Total Claim Cost is the aggregate observed cost in euros."),
    )
    add_worksheet(
        worksheets, "Driver Age Frequency Severity", PORTFOLIO_DS, PORTFOLIO_FIELDS, PORTFOLIO_CALCULATIONS, severity_ref, frequency_ref, "Circle", [("detail", driver_ref), ("color", driver_ref), ("size", exposure_ref), ("tooltip", driver_tooltip_ref)], "Driver Age: Frequency vs Severity", {"DriverAgeGroup": "Attribute", "Claim Frequency": "None", "Average Severity": "None", "Exposure": "Sum"},
        tooltip_lines=(f"Driver Age Group: <{driver_tooltip_ref}>", f"Claim Frequency: <{frequency_ref}>", f"Average Severity: <{severity_ref}>", f"Exposure: <{exposure_ref}>", "Marker area represents Exposure; select a mark to highlight its matrix row."),
    )
    add_worksheet(
        worksheets, "Vehicle Power Frequency", PORTFOLIO_DS, PORTFOLIO_FIELDS, PORTFOLIO_CALCULATIONS, power_ref, frequency_ref, "Bar", [("color", power_ref), ("tooltip", severity_ref)], "Vehicle Power Claim Frequency", {"VehiclePowerGroup": "None", "Claim Frequency": "None", "Average Severity": "None"},
        tooltip_lines=(f"Vehicle Power Group: <{power_ref}>", f"Claim Frequency: <{frequency_ref}>", f"Average Severity: <{severity_ref}>", "Claim Frequency is reported claims per exposure year."),
    )
    add_worksheet(
        worksheets, "Driver Vehicle Frequency Matrix", PORTFOLIO_DS, PORTFOLIO_FIELDS, PORTFOLIO_CALCULATIONS, driver_ref, power_ref, "Square", [("color", frequency_ref), ("text", frequency_ref), ("tooltip", exposure_ref)], "Driver Age and Vehicle Power Frequency", {"DriverAgeGroup": "None", "VehiclePowerGroup": "None", "Claim Frequency": "None", "Exposure": "Sum"},
        tooltip_lines=(f"Driver Age Group: <{driver_ref}>", f"Vehicle Power Group: <{power_ref}>", f"Claim Frequency: <{frequency_ref}>", f"Exposure: <{exposure_ref}>", "Use this matrix to compare claims per exposure year across paired segments."),
        show_mark_labels=True,
    )

    rank_ref = instance(CLAIMS_DS, "ClaimAmountRank", "None", "ordinal")
    amount_ref = instance(CLAIMS_DS, "ClaimAmount", "Sum", "quantitative")
    cumulative_pct_ref = instance(CLAIMS_DS, "CumulativeClaimCostPct", "Avg", "quantitative")
    cumulative_item_ref = instance(CLAIMS_DS, "CumulativeClaimPct", "Avg", "quantitative")
    claim_region_tooltip_ref = instance(CLAIMS_DS, "Region", "Attribute", "nominal")
    extreme_ref = direct_ref(CLAIMS_DS, "IsExtremeClaim")
    add_worksheet(
        worksheets, "Pareto Curve", CLAIMS_DS, CLAIMS_FIELDS, (), cumulative_pct_ref, cumulative_item_ref, "Line", [("path", rank_ref), ("tooltip", amount_ref)], "Cumulative Claim Cost (Pareto)", {"CumulativeClaimCostPct": "Avg", "CumulativeClaimPct": "Avg", "ClaimAmountRank": "None", "ClaimAmount": "Sum"},
        tooltip_lines=(f"Cumulative Claim Cost: <{cumulative_pct_ref}>", f"Cumulative Claim Share: <{cumulative_item_ref}>", f"Claim Amount: <{amount_ref}>", "Use the curve to see how quickly high-cost claims accumulate the total cost."),
    )
    add_worksheet(
        worksheets, "High Cost Claims", CLAIMS_DS, CLAIMS_FIELDS, (), rank_ref, amount_ref, "Bar", [("color", extreme_ref), ("tooltip", claim_region_tooltip_ref)], "Top 20 Claim Amounts", {"ClaimAmountRank": "None", "ClaimAmount": "Sum", "IsExtremeClaim": "None", "Region": "Attribute"}, filters=(("ClaimAmountRank", 1, 20),),
        tooltip_lines=(f"Claim Cost Rank: <{rank_ref}>", f"Claim Amount: <{amount_ref}>", f"Region: <{claim_region_tooltip_ref}>", "These are the 20 largest observed claim amounts; retain valid high-cost claims in reporting."),
    )
    add_worksheet(
        worksheets, "High Cost Segments", PORTFOLIO_DS, PORTFOLIO_FIELDS, PORTFOLIO_CALCULATIONS, power_ref, total_cost_ref, "Bar", [("color", power_ref), ("tooltip", frequency_ref)], "Total Claim Cost by Vehicle Power", {"VehiclePowerGroup": "None", "TotalClaimAmount": "Sum", "Claim Frequency": "None"},
        tooltip_lines=(f"Vehicle Power Group: <{power_ref}>", f"Total Claim Cost: <{total_cost_ref}>", f"Claim Frequency: <{frequency_ref}>", "Compare Total Claim Cost with Claim Frequency rather than cost alone."),
    )

    dashboards = ET.SubElement(workbook, "dashboards")

    def overview_zones(root: ET.Element) -> None:
        add_text_zone(
            root,
            3,
            0,
            5000,
            100000,
            3000,
            "Explore the selected portfolio with exposure-aware KPIs. Claim Frequency = Claim Count / Exposure (claims per exposure year); Total Claim Cost and Average Severity are shown in euros. Findings are descriptive associations, not causal conclusions.",
        )
        filters = ["Region", "VehGas", "DriverAgeGroup", "VehicleAgeGroup", "BonusMalusGroup"]
        for index, filter_name in enumerate(filters):
            add_filter_zone(root, 10 + index, filter_name, "Regional Claim Frequency", index * 20000, 8000, 20000)
        cards = ["KPI Policy Count", "KPI Exposure", "KPI Claim Count", "KPI Claim Frequency", "KPI Total Claim Cost", "KPI Average Severity"]
        for index, card in enumerate(cards):
            add_sheet_zone(root, 20 + index, card, index * 16666, 12000, 16666, 14000)
        add_sheet_zone(root, 30, "Regional Claim Frequency", 0, 26000, 50000, 74000)
        add_sheet_zone(root, 31, "Regional Claim Cost", 50000, 26000, 50000, 74000)

    def segments_zones(root: ET.Element) -> None:
        add_text_zone(
            root,
            33,
            0,
            5000,
            100000,
            3000,
            "Compare Claim Frequency (claims per exposure year) and Average Severity (euros per claim). Circle area represents Exposure; select a driver-age mark to highlight its row in the matrix.",
        )
        filters = ["Region", "VehGas", "DriverAgeGroup", "VehicleAgeGroup", "BonusMalusGroup"]
        for index, filter_name in enumerate(filters):
            add_filter_zone(root, 40 + index, filter_name, "Driver Age Frequency Severity", index * 20000, 8000, 20000)
        add_sheet_zone(root, 50, "Driver Age Frequency Severity", 0, 12000, 55000, 50000)
        add_sheet_zone(root, 51, "Regional Claim Frequency", 55000, 12000, 45000, 25000)
        add_sheet_zone(root, 52, "Vehicle Power Frequency", 55000, 37000, 45000, 25000)
        add_sheet_zone(root, 53, "Driver Vehicle Frequency Matrix", 0, 62000, 100000, 35000)
        add_text_zone(root, 54, 0, 97000, 100000, 3000, "Interpret segments using Claim Frequency, Average Severity, Exposure, and Claim Count together. The comparisons are descriptive, not causal.")

    def concentration_zones(root: ET.Element) -> None:
        add_text_zone(root, 55, 0, 5000, 100000, 3000, "Pareto views show cumulative shares of observed claim cost. Claim amounts and Total Claim Cost are shown in euros; use the tooltips to interpret each mark. High-cost claims require review, not automatic exclusion.")
        add_sheet_zone(root, 60, "Pareto Curve", 0, 8000, 58000, 56000)
        add_sheet_zone(root, 61, "High Cost Claims", 58000, 8000, 42000, 28000)
        add_sheet_zone(root, 62, "High Cost Segments", 58000, 36000, 42000, 28000)
        add_text_zone(root, 63, 0, 64000, 100000, 9000, "Recommendations\n1. Monitor Young (18-24) for Claim Frequency and Average Severity.\n2. Review Rhone-Alpes as a high-frequency, material-cost region.\n3. Review high-cost claims without excluding valid observations.", 11)
        add_text_zone(root, 64, 0, 73000, 100000, 3000, "Management attention: track top-1% claim-cost share, claims at or above the 99.5th percentile, and Average Severity.")

    add_dashboard(dashboards, "Executive Portfolio Overview", [(PORTFOLIO_DS, PORTFOLIO_FIELDS)], overview_zones)
    add_dashboard(dashboards, "Claims & Risk Segments", [(PORTFOLIO_DS, PORTFOLIO_FIELDS)], segments_zones)
    add_dashboard(
        dashboards,
        "Claim Cost Concentration",
        [(CLAIMS_DS, CLAIMS_FIELDS), (PORTFOLIO_DS, PORTFOLIO_FIELDS)],
        concentration_zones,
    )

    # Tableau 2020.1 expects an active workbook view. Each dashboard window
    # must declare its sheet viewpoints before the active node; an active node
    # by itself is schema-invalid, while omitting windows leaves no active view.
    dashboard_sheets = {
        "Executive Portfolio Overview": [
            "KPI Policy Count",
            "KPI Exposure",
            "KPI Claim Count",
            "KPI Claim Frequency",
            "KPI Total Claim Cost",
            "KPI Average Severity",
            "Regional Claim Frequency",
            "Regional Claim Cost",
        ],
        "Claims & Risk Segments": [
            "Driver Age Frequency Severity",
            "Regional Claim Frequency",
            "Vehicle Power Frequency",
            "Driver Vehicle Frequency Matrix",
        ],
        "Claim Cost Concentration": [
            "Pareto Curve",
            "High Cost Claims",
            "High Cost Segments",
        ],
    }
    windows = ET.SubElement(workbook, "windows", {"source-height": "32"})
    for dashboard_name, sheet_names in dashboard_sheets.items():
        window = ET.SubElement(windows, "window", {"class": "dashboard", "maximized": "true", "name": dashboard_name})
        viewpoints = ET.SubElement(window, "viewpoints")
        for sheet_name in sheet_names:
            ET.SubElement(viewpoints, "viewpoint", {"name": sheet_name})
        ET.SubElement(window, "active", {"id": "-1"})

    validate_workbook(workbook)
    ET.indent(workbook, space="  ")
    ET.ElementTree(workbook).write(OUTPUT_PATH, encoding="utf-8", xml_declaration=True)
    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
