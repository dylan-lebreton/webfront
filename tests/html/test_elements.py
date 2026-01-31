from webfront.html.attributes import Lang, Dir
from webfront.html.elements import DocType, HTML

def test_doctype_renders():
    assert DocType().render() == "<!DOCTYPE html>"

def test_html_element_renders_with_attrs():
    el = HTML(lang=Lang("en"), dir_=Dir("ltr"), children=[])
    assert el.render() == '<html lang="en" dir="ltr"></html>'

def test_html_element_omits_missing_attrs():
    el = HTML(children=[])
    assert el.render() == "<html></html>"
