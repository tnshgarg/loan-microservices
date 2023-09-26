from ops.templates.repayments_reminder.components import get_table_html


def get_repayments_auto_deduction_template(pending_repayments_summary):
    company_name = pending_repayments_summary.get("company_name")
    total_due_amount = pending_repayments_summary.get("total_due_amount")
    due_date = pending_repayments_summary.get("due_date")
    summary_df = pending_repayments_summary.get("summary_df")

    employee_count = len(summary_df)
    table_html = get_table_html(summary_df)

    html_content = f'''
        <!DOCTYPE html>

        <html lang="en" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml">
        <head>
        <title></title>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
        <meta content="width=device-width, initial-scale=1.0" name="viewport"/><!--[if mso]><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch><o:AllowPNG/></o:OfficeDocumentSettings></xml><![endif]--><!--[if !mso]><!-->
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700;800;900" rel="stylesheet" type="text/css"/><!--<![endif]-->
        <style>
                * {{
                    box-sizing: border-box;
                }}

                body {{
                    margin: 0;
                    padding: 0;
                }}

                a[x-apple-data-detectors] {{
                    color: inherit !important;
                    text-decoration: inherit !important;
                }}

                #MessageViewBody a {{
                    color: inherit;
                    text-decoration: none;
                }}

                p {{
                    line-height: inherit
                }}

                .desktop_hide,
                .desktop_hide table {{
                    mso-hide: all;
                    display: none;
                    max-height: 0px;
                    overflow: hidden;
                }}

                .image_block img+div {{
                    display: none;
                }}

                @media (max-width:620px) {{
                    .social_block.desktop_hide .social-table {{
                        display: inline-block !important;
                    }}

                    .mobile_hide {{
                        display: none;
                    }}

                    .row-content {{
                        width: 100% !important;
                    }}

                    .stack .column {{
                        width: 100%;
                        display: block;
                    }}

                    .mobile_hide {{
                        min-height: 0;
                        max-height: 0;
                        max-width: 0;
                        overflow: hidden;
                        font-size: 0px;
                    }}

                    .desktop_hide,
                    .desktop_hide table {{
                        display: table !important;
                        max-height: none !important;
                    }}
                }}
            </style>
        </head>
        <body style="margin: 0; background-color: #f9f9f9; padding: 0; -webkit-text-size-adjust: none; text-size-adjust: none;">
        <table border="0" cellpadding="0" cellspacing="0" class="nl-container" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f9f9f9;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content stack" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; color: #000; width: 600px; margin: 0 auto;" width="600">
        <tbody>
        <tr>
        <td class="column column-1" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 10px; padding-top: 10px; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="100%">
        <table border="0" cellpadding="0" cellspacing="0" class="image_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tr>
        <td class="pad" style="padding-bottom:5px;padding-top:10px;width:100%;padding-right:0px;padding-left:0px;">
        <div align="center" class="alignment" style="line-height:10px"><img src="https://d22ss3ef1t9wna.cloudfront.net/email-assets/unipe_logo.png" style="display: block; height: auto; border: 0; max-width: 210px; width: 100%;" width="210"/></div>
        </td>
        </tr>
        </table>
        <table border="0" cellpadding="0" cellspacing="0" class="paragraph_block block-2" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad" style="padding-bottom:10px;padding-left:5px;padding-right:5px;padding-top:5px;">
        <div style="color:#101112;direction:ltr;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;font-size:13px;font-weight:400;letter-spacing:0px;line-height:120%;text-align:center;mso-line-height-alt:15.6px;">
        <p style="margin: 0;">Payroll backed consumer banking for Indian Workforce</p>
        </div>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-2" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f9f9f9;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content stack" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #fff; color: #000; width: 600px; margin: 0 auto;" width="600">
        <tbody>
        <tr>
        <td class="column column-1" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="100%">
        <table border="0" cellpadding="0" cellspacing="0" class="icons_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tr>
        <td class="pad" style="vertical-align: middle; color: #000000; font-family: inherit; font-size: 14px; font-weight: 400; text-align: center;">
        <table align="center" cellpadding="0" cellspacing="0" class="alignment" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
        <tr>
        <td style="vertical-align: middle; text-align: center; padding-top: 25px; padding-bottom: 25px; padding-left: 5px; padding-right: 5px;"><img align="center" class="icon" height="128" src="https://d22ss3ef1t9wna.cloudfront.net/email-assets/notification-bell-icon-3d-render-cute-cartoon-illustration-simple-yellow-bell-reminder-notice-concept-removebg-preview.png" style="display: block; height: auto; margin: 0 auto; border: 0;" width="145"/></td>
        </tr>
        </table>
        </td>
        </tr>
        </table>
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-2" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad" style="padding-bottom:10px;padding-left:30px;padding-right:30px;padding-top:10px;">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 18px; color: #555555; line-height: 1.5;">
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">Dear {company_name},</p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 18px;"> </p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">Greetings from Unipe!<br/><br/>A quick heads-up about the upcoming auto-deduction for the previous withdrawals availed by your employees. We believe in a seamless experience, and this communication is to ensure a hiccup-free repayment process.</p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 18px;"> </p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;"><strong>Key Details:</strong></p>
        <ul style="line-height: 1.5; mso-line-height-alt: 21px; font-size: 14px;">
        <li style="text-align: left;"><strong>Total Amount for Auto-deduction</strong>: ₹{total_due_amount}</li>
        <li style="text-align: left;"><strong>Count of employees</strong>: {employee_count}</li>
        <li style="text-align: left;"><strong>Due Date</strong>: {due_date}</li>
        </ul>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">This repayment amount will be auto-deducted from the respective employees' bank accounts via the e-mandate set up during their registration process. To ensure a seamless process, please:</p>
        <ul style="list-style-type: circle; line-height: 1.5; mso-line-height-alt: 21px; font-size: 14px;">
        <li style="text-align: left;">Make sure that employee salaries are disbursed before the due date.</li>
        <li style="text-align: left;">If there have been any changes in their banking details, kindly inform us at the earliest.</li>
        <li style="text-align: left;">Ensure all employees are aware of this upcoming auto-deduction, helping them plan their finances accordingly.</li>
        </ul>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;"><strong>Please Note:</strong></p>
        <ul style="list-style-type: square; line-height: 1.5; mso-line-height-alt: 21px; font-size: 14px;">
        <li style="text-align: left;">Failure to ensure adequate funds for the auto-collection on time will incur a penalty of ₹250 per employee per day or an added interest rate of 5% per month whichever is higher.</li>
        <li style="text-align: left;">Late payments can significantly harm a borrower's credit score, resulting in difficulty accessing credit.</li>
        <li style="text-align: left;">Late payments are reported to credit bureaus and will show up on the credit report of the borrower.</li>
        </ul>
        <p style="margin: 0; mso-line-height-alt: 21px;"><span style="font-size:14px;">For a detailed breakdown of the amounts per employee, please refer to the table below:</span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-3" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #fff; background-size: auto; width: 600px;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #e9f7f2; background-size: auto; border-bottom: 1px solid #cad7d0; border-left: 1px solid #cad7d0; border-radius: 15px 15px 0 0; border-right: 1px solid #cad7d0; border-top: 1px solid #cad7d0; color: #000; width: 540px; margin: 0 auto;" width="600">
        <tbody>
        <tr>
        <td class="column column-1" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: middle; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="16.666666666666668%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #555555; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:11px;"><strong>Employee ID</strong></span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        <td class="column column-2" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: middle; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="16.666666666666668%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #555555; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:11px;"><strong>Bank Account Number</strong></span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        <td class="column column-3" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: middle; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="16.666666666666668%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #555555; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:11px;"><strong>Loan Amount</strong></span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        <td class="column column-4" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: middle; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="16.666666666666668%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #555555; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:11px;"><strong>UTR Number</strong></span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        <td class="column column-5" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: middle; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="16.666666666666668%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #555555; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:11px;"><strong>Amount Credited Date</strong></span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        <td class="column column-6" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: middle; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="16.666666666666668%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #555555; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:11px;"><strong>Due Date</strong></span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        {table_html}
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-7" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f9f9f9;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content stack" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #fff; color: #000; width: 600px; margin: 0 auto;" width="600">
        <tbody>
        <tr>
        <td class="column column-1" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="100%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad" style="padding-bottom:10px;padding-left:30px;padding-right:30px;padding-top:30px;">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 18px; color: #555555; line-height: 1.5;">
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">The smooth facilitation of this repayment not only ensures trust but also showcases our joint commitment to employee welfare.</p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 18px;"> </p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">If you have any concerns or need any assistance regarding this process, feel free to reach out. We're here to help!</p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 18px;"> </p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">Thank you for your cooperation and understanding.</p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 18px;"> </p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">Warm regards,</p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 18px;"> </p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;">Customer Support Team</p>
        <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 21px;"><a href="https://www.unipe.money/" rel="noopener" style="text-decoration: underline; color: #7747ff;" target="_blank">Unipe.Money</a></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        <table border="0" cellpadding="10" cellspacing="0" class="divider_block block-2" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tr>
        <td class="pad">
        <div align="center" class="alignment">
        <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="20%">
        <tr>
        <td class="divider_inner" style="font-size: 1px; line-height: 1px; border-top: 1px solid #dddddd;"><span> </span></td>
        </tr>
        </table>
        </div>
        </td>
        </tr>
        </table>
        <table border="0" cellpadding="5" cellspacing="0" class="paragraph_block block-3" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="color:#101112;direction:ltr;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;font-size:10px;font-weight:400;letter-spacing:0px;line-height:120%;text-align:center;mso-line-height-alt:12px;">
        <p style="margin: 0;">Disclaimer: This email is confidential and intended for the recipient specified in the message only.</p>
        </div>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-8" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f9f9f9;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content stack" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #051365; color: #000; width: 600px; margin: 0 auto;" width="600">
        <tbody>
        <tr>
        <td class="column column-1" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 10px; vertical-align: bottom; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="33.333333333333336%">
        <table border="0" cellpadding="0" cellspacing="0" class="button_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tr>
        <td class="pad" style="padding-bottom:10px;padding-top:10px;text-align:center;">
        <div align="center" class="alignment"><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="mailto:support@unipe.money?subject=Query%20Regarding%20Repayments" style="height:34px;width:131px;v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#FFFFFF" fill="false"><w:anchorlock/><v:textbox inset="0px,0px,0px,0px"><center style="color:#ffffff; font-family:'Trebuchet MS', Tahoma, sans-serif; font-size:11px"><![endif]--><a href="mailto:support@unipe.money?subject=Query%20Regarding%20Repayments" style="text-decoration:none;display:inline-block;color:#ffffff;background-color:transparent;border-radius:4px;width:auto;border-top:1px solid #FFFFFF;font-weight:400;border-right:1px solid #FFFFFF;border-bottom:1px solid #FFFFFF;border-left:1px solid #FFFFFF;padding-top:5px;padding-bottom:5px;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;font-size:11px;text-align:center;mso-border-alt:none;word-break:keep-all;" target="_blank"><span style="padding-left:30px;padding-right:30px;font-size:11px;display:inline-block;letter-spacing:normal;"><span style="word-break: break-word; line-height: 22px;">Get in touch</span></span></a><!--[if mso]></center></v:textbox></v:roundrect><![endif]--></div>
        </td>
        </tr>
        </table>
        </td>
        <td class="column column-2" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-top: 5px; vertical-align: bottom; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="33.333333333333336%">
        <table border="0" cellpadding="0" cellspacing="0" class="icons_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tr>
        <td class="pad" style="vertical-align: middle; color: #000000; font-family: inherit; font-size: 14px; font-weight: 400; text-align: center;">
        <table align="center" cellpadding="0" cellspacing="0" class="alignment" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
        <tr>
        <td style="vertical-align: middle; text-align: center; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px;"><img align="center" class="icon" height="16" src="https://d22ss3ef1t9wna.cloudfront.net/email-assets/pin.png" style="display: block; height: auto; margin: 0 auto; border: 0;" width="13"/></td>
        </tr>
        </table>
        </td>
        </tr>
        </table>
        <table border="0" cellpadding="5" cellspacing="0" class="text_block block-2" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #ffffff; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:10px;">Address: No.32, Hesaragatta Main Road, Kumbarahalli, Bengaluru, Karnataka, 560090</span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        </td>
        <td class="column column-3" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 10px; vertical-align: bottom; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="33.333333333333336%">
        <table border="0" cellpadding="0" cellspacing="0" class="button_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tr>
        <td class="pad" style="padding-bottom:10px;padding-top:10px;text-align:center;">
        <div align="center" class="alignment"><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="https://app.unipe.money/" style="height:34px;width:149px;v-text-anchor:middle;" arcsize="12%" strokeweight="0.75pt" strokecolor="#FFFFFF" fill="false"><w:anchorlock/><v:textbox inset="0px,0px,0px,0px"><center style="color:#ffffff; font-family:'Trebuchet MS', Tahoma, sans-serif; font-size:11px"><![endif]--><a href="https://app.unipe.money/" style="text-decoration:none;display:inline-block;color:#ffffff;background-color:transparent;border-radius:4px;width:auto;border-top:1px solid #FFFFFF;font-weight:400;border-right:1px solid #FFFFFF;border-bottom:1px solid #FFFFFF;border-left:1px solid #FFFFFF;padding-top:5px;padding-bottom:5px;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;font-size:11px;text-align:center;mso-border-alt:none;word-break:keep-all;" target="_blank"><span style="padding-left:30px;padding-right:30px;font-size:11px;display:inline-block;letter-spacing:normal;"><span style="word-break: break-word; line-height: 22px;">Open Web App</span></span></a><!--[if mso]></center></v:textbox></v:roundrect><![endif]--></div>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-9" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f9f9f9;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content stack" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #051365; color: #000; width: 600px; margin: 0 auto;" width="600">
        <tbody>
        <tr>
        <td class="column column-1" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="100%">
        <table border="0" cellpadding="0" cellspacing="0" class="text_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad" style="padding-bottom:5px;padding-left:10px;padding-right:10px;padding-top:5px;">
        <div style="font-family: 'Trebuchet MS', Tahoma, sans-serif">
        <div class="" style="font-size: 12px; font-family: 'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #ffffff; line-height: 1.2;">
        <p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;"><span style="font-size:12px;">Follow us on</span></p>
        </div>
        </div>
        </td>
        </tr>
        </table>
        <table border="0" cellpadding="5" cellspacing="0" class="social_block block-2" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">
        <tr>
        <td class="pad">
        <div align="center" class="alignment">
        <table border="0" cellpadding="0" cellspacing="0" class="social-table" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; display: inline-block;" width="168px">
        <tr>
        <td style="padding:0 5px 0 5px;"><a href="https://www.facebook.com/unipe.money/" target="_blank"><img alt="Facebook" height="32" src="https://d22ss3ef1t9wna.cloudfront.net/email-assets/facebook2x.png" style="display: block; height: auto; border: 0;" title="facebook" width="32"/></a></td>
        <td style="padding:0 5px 0 5px;"><a href="https://www.instagram.com/unipe.money/" target="_blank"><img alt="Instagram" height="32" src="https://d22ss3ef1t9wna.cloudfront.net/email-assets/instagram2x.png" style="display: block; height: auto; border: 0;" title="instagram" width="32"/></a></td>
        <td style="padding:0 5px 0 5px;"><a href="https://www.linkedin.com/company/unipe-technology-inc/" target="_blank"><img alt="Linkedin" height="32" src="https://d22ss3ef1t9wna.cloudfront.net/email-assets/linkedin2x.png" style="display: block; height: auto; border: 0;" title="linkedin" width="32"/></a></td>
        <td style="padding:0 5px 0 5px;"><a href="https://www.youtube.com/@unipe8468" target="_blank"><img alt="YouTube" height="32" src="https://d22ss3ef1t9wna.cloudfront.net/email-assets/youtube2x.png" style="display: block; height: auto; border: 0;" title="YouTube" width="32"/></a></td>
        </tr>
        </table>
        </div>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row row-10" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f9f9f9;" width="100%">
        <tbody>
        <tr>
        <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" class="row-content stack" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #020b44; color: #000; width: 600px; margin: 0 auto;" width="600">
        <tbody>
        <tr>
        <td class="column column-1" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; padding-bottom: 5px; padding-top: 5px; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;" width="100%">
        <table border="0" cellpadding="5" cellspacing="0" class="paragraph_block block-1" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;" width="100%">
        <tr>
        <td class="pad">
        <div style="color:#ffffff;direction:ltr;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;font-size:11px;font-weight:400;letter-spacing:0px;line-height:120%;text-align:center;mso-line-height-alt:13.2px;">
        <p style="margin: 0;">© 2023 by Unipe Technology Inc</p>
        </div>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table><!-- End -->
        </body>
        </html>

    '''

    return html_content
