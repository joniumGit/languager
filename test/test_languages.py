import pytest
from languager import get_language


def test_finland():
    lang = get_language('fi')
    assert get_language('fin') == lang
    assert lang.short == 'fi'
    assert lang.code == 'fin'
    assert lang.name == 'Finnish'
    assert lang.parent is None
    assert not lang.macro
    assert len(lang.macros) == 0


def test_china_macros():
    assert len(get_language('zho').macros) == 16
    assert len(get_language('zh').macros) == 16


def test_parent():
    assert 'nob' in get_language('nor').macros
    assert 'nor' in get_language('nob').parent
    assert get_language('nob').macro
    assert len(get_language('nob').macros) == 0


def test_reverse():
    assert get_language('Chinese') == get_language('zho')
    assert get_language('Finnish') == get_language('fi')


@pytest.mark.parametrize('lang', [
    'awdjopwpawiojdopawjoawjfpowafeoafhwafhawafpowajfaedwajddwad',
    'öö',
    'äää'
])
def test_not_found(lang):
    with pytest.raises(ValueError) as ex:
        get_language(lang)
    assert 'Not Found' in ex.value.args[0]


@pytest.mark.parametrize('lang', [
    'awdjopwpawiojdopawjoawjfpowafeoafhwafhawafpowajfaedwajddwad',
    'öö',
    'äää',
    None
])
def test_default(lang):
    lang = get_language(lang, default='az')
    assert lang == get_language('az')


@pytest.mark.parametrize('lang', [
    'awdjopwpawiojdopawjoawjfpowafeoafhwafhawafpowajfaedwajddwad',
    'öö',
    'äää'
])
def test_bad_default(lang):
    with pytest.raises(ValueError) as ex:
        get_language(lang, default=lang)
    assert 'Not Found' in ex.value.args[0]
    assert 'Not Found' in ex.value.__cause__.args[0]


def test_none_lang():
    with pytest.raises(ValueError) as ex:
        get_language(None)
    assert 'None' in ex.value.args[0]


def test_case():
    assert get_language('zHo') == get_language('Zh')
