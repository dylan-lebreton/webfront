import pytest
from webfront.html.attributes import Lang, Dir

def test_lang_normalizes_tag():
    assert Lang("fr-ca").render() == 'lang="fr-CA"'

def test_lang_allows_empty_string():
    assert Lang("").render() == 'lang=""'

def test_lang_rejects_invalid():
    with pytest.raises(ValueError):
        Lang("english")

def test_dir_renders():
    assert Dir("rtl").render() == 'dir="rtl"'
