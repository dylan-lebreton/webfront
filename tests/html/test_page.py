from webfront.html.attributes import Lang, Dir
from webfront.html.elements import HTML
from webfront.html.page import Page

def test_page_renders_doctype_plus_html():
    html = HTML(lang=Lang("en"), dir_=Dir("ltr"), children=[])
    page = Page(html)
    assert page.render() == '<!DOCTYPE html><html lang="en" dir="ltr"></html>'
