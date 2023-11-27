import uuid
from typing import Dict, List

from robot.api import logger

HTML_TEMPLATE = """
<div style="overflow:auto"><style type="text/css">
table#{table_id} {{
    border-collapse:collapse;
    border: 2px ridge black;
    text-align: left;    
}}
table#{table_id} th {{
    border: 1px solid grey;
    border-collapse:collapse;
    white-space: nowrap;
    font-weight: bold;
    font-size: 0.9em;
    background: #ddd;
    padding: 0.1em 0.3em;
}}
table#{table_id} td {{
    border: 1px solid #ddd;
    padding: 0.3em;
    font-size: 0.9em;
    white-space: nowrap;
}}
table#{table_id} tr:hover {{
    background:lightblue;
}}
</style>
"""


def generate_table_id() -> str:
    return f"table_{str(uuid.uuid4()).split('-')[-1]}"


def table_to_html(results: List[Dict]) -> str:
    if not results:
        return ""
    table_id = generate_table_id()
    html_table = HTML_TEMPLATE.format(table_id=table_id)
    headers = "".join(f"<th>{column}</th>" for column in results[0])
    html_table += f'<table id="{table_id}"><caption>Query results</caption><thead><tr>{headers}</tr></thead><tbody>'
    for row in results:
        log_row = "".join(f"<td>{value}</td>" for value in row.values())
        html_table += f"<tr>{log_row}</tr>"
    html_table += "</tbody></table></div>"
    return html_table


def log_results_as_html_table(results: List[Dict]) -> None:
    log_table = table_to_html(results)
    if log_table:
        logger.info(log_table, html=True)
