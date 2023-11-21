import pandas as pd


def get_table_cell_html(index, value):
    table_cell_html = f'''
        <td class="column column-{index+1}" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-left: 5px; padding-right: 5px; padding-top: 5px; vertical-align: middle; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="16.666666666666668%">
        <table border="0" cellpadding="5" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #555555; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 16.8px;"><span style="font-size:11px;">{value}</span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
    '''

    return table_cell_html


def get_table_html(summary_df: pd.DataFrame):
    table_rows = []
    for i in range(len(summary_df)):
        row_cells = []
        for j in range(len(summary_df.iloc[i])):
            table_cell_html = get_table_cell_html(j, summary_df.iloc[i, j])
            row_cells.append(table_cell_html)
        row_cells_html = '\n'.join(row_cells)

        border_bottom_dynamic_value = "0"
        border_radius_dynamic_value = ""
        if i == len(summary_df)-1:
            border_bottom_dynamic_value = "1px"
            border_radius_dynamic_value = "0 15px 15px"

        table_row_html = f'''
                <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-{i+4}" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #fff; width: 600px;" width="100%">
                <tbody>
                <tr>
                <td>
                <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #fff; border-bottom: {border_bottom_dynamic_value} solid #cad7d0; border-left: 1px solid #cad7d0; border-radius: 0 {border_radius_dynamic_value}; border-right: 1px solid #cad7d0; border-top: 0 solid #cad7d0; color: #000; width: 540px; margin: 0 auto;" width="600">
                <tbody>
                <tr>
                {row_cells_html}
                </tr>
                </tbody>
                </table>
                </td>
                </tr>
                </tbody>
                </table>
        '''
        table_rows.append(table_row_html)

    table_html = '\n'.join(table_rows)

    return table_html
