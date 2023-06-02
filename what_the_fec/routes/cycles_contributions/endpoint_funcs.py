from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection, text

from what_the_fec.routes.helpers import intersection_render_table

TABLE_NAME = "cycles_contributions"


def get_all_func(conn: Connection, request: Request, templates: Jinja2Templates):
    entity_1_table_name = "cycles"
    entity_1_attribute = "year"
    entity_1_column = f"{entity_1_attribute} (from \"{entity_1_table_name}\")"
    
    entity_2_table_name = "contributions"
    entity_2_attribute = "sub_id"
    entity_2_column = f"{entity_2_attribute} (from \"{entity_2_table_name}\")"

    query = f"""
        SELECT 
            `{entity_1_table_name}`.{entity_1_attribute} as `{entity_1_column}`,
            `{entity_2_table_name}`.{entity_2_attribute} as `{entity_2_column}`
        FROM `{TABLE_NAME}`
            INNER JOIN `{entity_1_table_name}` 
                ON `{TABLE_NAME}`.{entity_1_table_name}_year = `{entity_1_table_name}`.year
            INNER JOIN `{entity_2_table_name}` 
                ON `{TABLE_NAME}`.{entity_2_table_name}_id = `{entity_2_table_name}`.id
    """

    entity_1_query = f"""
        SELECT * from cycles
    """

    entity_2_query = f"""
        SELECT 
            `contributions`.id,
            transaction_pgi,
            image_num,
            transaction_dt,
            transaction_amt,
            trans_id,
            file_num,
            memo_cd,
            memo_text,
            sub_id,
            `committees`.name as committee,
            `report_types`.name as report_type,
            `transaction_types`.name as transaction_type,
            `amendment_indicators`.name as amendment_indicator,
            `contributor_types`.name as contributor_type
        FROM `contributions`
            INNER JOIN `committees` 
                ON `contributions`.committees_id = `committees`.id
            INNER JOIN `report_types` 
                ON `contributions`.report_types_id = `report_types`.id
            INNER JOIN `transaction_types` 
                ON `contributions`.transaction_types_id = `transaction_types`.id
            INNER JOIN `amendment_indicators` 
                ON `contributions`.amendment_indicators_id = `amendment_indicators`.id
            INNER JOIN `contributor_types` 
                ON `contributions`.contributor_types_id = `contributor_types`.id;
    """

    entity_1_dropdown_selections_query = f"SELECT * FROM `{entity_1_table_name}`"
    entity_2_dropdown_selections_query = f"SELECT {entity_2_attribute} FROM `{entity_2_table_name}`"

    entity_1_dropdown_selections = conn.execute(text(entity_1_dropdown_selections_query)).mappings().all()
    entity_2_dropdown_selections = conn.execute(text(entity_2_dropdown_selections_query)).mappings().all()

    dropdown_items_for_add = {
        entity_1_column: {
            "data": entity_1_dropdown_selections,
            "relevant_column_name": f"{entity_1_attribute}",
        },
        entity_2_column: {
            "data": entity_2_dropdown_selections,
            "relevant_column_name": f"{entity_2_attribute}",
        },
    }

    return intersection_render_table(
        conn=conn,
        query=query,
        request=request,
        table_name=TABLE_NAME,
        templates=templates,
        entity_1_table_name=entity_1_table_name,
        entity_1_query=entity_1_query,
        entity_2_table_name=entity_2_table_name,
        entity_2_query=entity_2_query,
        dropdown_keys=dropdown_items_for_add.keys(),
        dropdown_items_for_add = dropdown_items_for_add
    )