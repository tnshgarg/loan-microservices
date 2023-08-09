import json


class HTMLBlocksService:

    @staticmethod
    def get_code_block(title, code_text):
        return f"""
        <div style="background-color:lightgray;">
            <p style="background-color:MidnightBlue;color:white;padding-left: 0.5em">{title}</p>
            <code>
                <pre>{code_text}</pre>
            </code>
        </div>
        """

    def get_button(title, link, background_color):
        return f"""
        <div style="display: grid;justify-content: center;width:10vw;margin:0 auto ">
            <br>
            <a href={link} style="background-color: {background_color};color: white;padding: 1em 1.5em;text-decoration: none;text-transform: uppercase;text-align:center">
                {title}
            </a>
        </div>
        """

    @staticmethod
    def insert_preformatted_text(text):
        return f"""
        <pre>
            {text}
        </pre>
        """

    @staticmethod
    def compile_html_blocks(items, buttons=[]):
        blocks = []

        for (title, doc) in items:
            blocks.append(
                HTMLBlocksService.get_code_block(
                    title, json.dumps(doc, default=str, indent=2))
            )
        for (title, link, background_color) in buttons:
            blocks.append(HTMLBlocksService.get_button(
                title, link, background_color))

        return blocks
