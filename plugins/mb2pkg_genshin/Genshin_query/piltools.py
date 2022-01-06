

def paste_image(pt, im, x, y, w=-1, h=-1, with_mask=True):
    """

    :param pt: 原图片
    :param im: 要粘贴的图片
    :param x: x
    :param y: y
    :param w: 宽
    :param h: 高
    :param with_mask: mask
    """

    w = im.width if w == -1 else w
    h = im.height if h == -1 else h
    im = im.resize((w, h))

    pt.paste(im, (x, y, x + w, y + h), im.convert("RGBA") if with_mask else None)
