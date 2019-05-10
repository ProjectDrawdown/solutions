import ui.color

def test_webcolor_to_rgb():
    assert ui.color.webcolor_to_rgb('goldenrod') == (218, 165, 32)
    assert ui.color.webcolor_to_rgb('blanchedalmond') == (255, 235, 205)
    assert ui.color.webcolor_to_rgb('Peru') == (205, 133, 63)
    assert ui.color.webcolor_to_rgb('RebeccaPurple') == (102, 51, 153)
    assert ui.color.webcolor_to_rgb('no_such_color') == (128, 128, 128)

def test_get_sector_color():
    assert ui.color.get_sector_color('Electricity Generation') == 'Peru'
    assert ui.color.get_sector_color('No Such Color') == 'Beige'
