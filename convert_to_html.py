import markdown

with open('informe.md', 'r', encoding='utf-8') as f:
    md_text = f.read()

html_body = markdown.markdown(md_text, extensions=['fenced_code', 'nl2br'])

css = """
@page {
    size: A4;
    margin: 2cm 2cm 2.2cm 2cm;
}
body {
    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #222;
    margin: 0;
    padding: 0;
}
h1 {
    color: #5c2d11;
    font-size: 19pt;
    border-bottom: 2px solid #5c2d11;
    padding-bottom: 8px;
    margin-top: 0;
}
h2 {
    color: #78350f;
    font-size: 14pt;
    border-bottom: 1px solid #d97706;
    padding-bottom: 4px;
    margin-top: 22pt;
    page-break-after: avoid;
}
h3 {
    color: #92400e;
    font-size: 12pt;
    margin-top: 14pt;
    page-break-after: avoid;
}
p, ul, ol {
    margin-bottom: 9pt;
}
li {
    margin-bottom: 3pt;
}
code {
    font-family: 'Consolas', 'Courier New', monospace;
    background-color: #f3f4f6;
    padding: 2px 4px;
    border-radius: 4px;
    font-size: 9pt;
    color: #991b1b;
}
pre {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 10px 14px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 8.5pt;
    line-height: 1.4;
    page-break-inside: avoid;
    margin: 10pt 0;
}
pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
    font-size: inherit;
}
blockquote {
    border-left: 4px solid #d97706;
    padding-left: 12px;
    color: #4b5563;
    margin: 10pt 0;
    font-style: italic;
}
hr {
    border: 0;
    border-top: 1px solid #e5e7eb;
    margin: 18pt 0;
}
strong {
    color: #111827;
}
"""

html_full = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Informe Actividad 5 - Programación IV</title>
<style>
{css}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

with open('informe.html', 'w', encoding='utf-8') as f:
    f.write(html_full)

print("informe.html generado correctamente")
