# -*-coding: utf8 -*-

import re

try:
    from PIL import Image, ImageChops, ImageFilter, ImageSequence
except ImportError:
    import Image
    import ImageChops
    import ImageFilter

from django.conf import settings as django_settings

try:
    from django.conf import BaseSettings
except ImportError:  # Django <= 1.2
    from django.conf import Settings as BaseSettings

from kinger.utils.storage import get_storage,get_thumbs_storage
import images2gif

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def get_thumbnail_image_name(filename, size='normal'):
    thumbnail_size = get_thumbnail_image_size(size)

    new_name = ''
    if thumbnail_size[0]:
        new_name += 'w'+ str(thumbnail_size[0])
    if thumbnail_size[1]:
        new_name += 'h'+ str(thumbnail_size[1])

    thumbnail_crop = get_thumbnail_image_crop(size)
    if thumbnail_crop:
        new_name += '.crop'

    extension = filename.split('.')[-1].lower()
    new_name = new_name+'.'+extension
    thumbnail_image_name = "thumbs/"+filename +'.'+ new_name
    return thumbnail_image_name

def get_thumbnail_image_size(size="normal"):
    thumbnail_aliases = django_settings.THUMBNAIL_ALIASES['']
    thumbnail_options = thumbnail_aliases[size]
    size = thumbnail_options['size']
    return size

# 定义 crop=true 则自动居中裁剪size 。不会等比例缩小
def get_thumbnail_image_crop(size="normal"):
    thumbnail_aliases = django_settings.THUMBNAIL_ALIASES['']
    thumbnail_options = thumbnail_aliases[size]
    crop = False
    try:
        if thumbnail_options['crop']:
            crop = thumbnail_options['crop']
    except Exception, e:
        pass
    return crop

def get_thumbnail_image_attr(filename):
    attr = {}
    print filename
    print "##############"
    storage = get_thumbs_storage()
    exists = storage.exists(filename)
    if exists:
        try:
            source_file = storage.open(filename)
            # 实例PIl对象
            im = Image.open(source_file.file)
            width,height = im.size
            attr = {'width':width,'height':height}
        except Exception, e:
            pass
    return attr


def get_thumbnail_image(filename, size='normal', autoSave = True):
    source_image_name = filename
    thumbnail_image_name = get_thumbnail_image_name(filename,size)
    thumbnail_size = get_thumbnail_image_size(size)
    thumbnail_crop = get_thumbnail_image_crop(size)
    # 检查缩略图是否存在 
    storage = get_storage()
    thumbs_storage = get_thumbs_storage()

    exists = thumbs_storage.exists(thumbnail_image_name)
    if exists:
        #print "storage exists file~~",thumbnail_image_name
        return thumbnail_image_name

    try:
        exists = storage.exists(source_image_name)
        if not exists:
            print "storage not exists source file >_< ",source_image_name
            return thumbnail_image_name
        source_file = storage.open(filename)
        # 实例PIl对象
        im = Image.open(source_file.file)

        format = Image.EXTENSION.get(thumbnail_image_name, 'PNG')
        if im.info.has_key("duration") and 0:
            # 动态gif图
            original_duration = im.info['duration']
            #frames = [frame.copy() for i, frame in enumerate(iter_frames(im))]    
            #frames = [scale_and_crop(frame, thumbnail_size) for i, frame in enumerate(iter_frames(im))]  
            frames = []
            for i, frame in enumerate(iter_frames(im)):
                frame = colorspace(frame)
                frame = autocrop(frame)
                frame = scale_and_crop(frame, thumbnail_size)
                frames.append(frame)
            #frames.reverse()
            i=0
            for frame in frames:
                i+=1
                #frame.thumbnail((72,72))
            output = StringIO()
            img_data = images2gif.writeGif(output, frames, duration=original_duration/1000.0, dither=0)
            thumbnail_file = thumbs_storage.save(thumbnail_image_name,img_data)
        else:
            im = colorspace(im)
            im = autocrop(im)
            im = scale_and_crop(im, thumbnail_size, thumbnail_crop)
            output = StringIO()
            im.save(output, format)

            is_transparent = is_transparent_image(im)
            if is_transparent:
                img_data = output.getvalue()
            else:
                img_data = im.tostring('jpeg', 'RGB')
            output.close()
            thumbnail_file = thumbs_storage.save(thumbnail_image_name,img_data)

    except Exception, e:
        raise
    return thumbnail_image_name


def iter_frames(im):
    try:
        i= 0
        while 1:
            im.seek(i)
            imframe = im.copy()
            if i == 0: 
                palette = imframe.getpalette()
            else:
                imframe.putpalette(palette)
            yield imframe
            i += 1
    except EOFError:
        pass


def is_transparent_image(image):
    """
    Check to see if an image is transparent.
    """
    if not isinstance(image, Image.Image):
        # Can only deal with PIL images, fall back to the assumption that that
        # it's not transparent.
        return False
    return (image.mode in ('RGBA', 'LA') or
            (image.mode == 'P' and 'transparency' in image.info))


def _compare_entropy(start_slice, end_slice, slice, difference):
    """
    Calculate the entropy of two slices (from the start and end of an axis),
    returning a tuple containing the amount that should be added to the start
    and removed from the end of the axis.

    """
    start_entropy = utils.image_entropy(start_slice)
    end_entropy = utils.image_entropy(end_slice)
    if end_entropy and abs(start_entropy / end_entropy - 1) < 0.01:
        # Less than 1% difference, remove from both sides.
        if difference >= slice * 2:
            return slice, slice
        half_slice = slice // 2
        return half_slice, slice - half_slice
    if start_entropy > end_entropy:
        return 0, slice
    else:
        return slice, 0


def colorspace(im, bw=False, replace_alpha=False, **kwargs):
    """
    Convert images to the correct color space.

    A passive option (i.e. always processed) of this method is that all images
    (unless grayscale) are converted to RGB colorspace.

    This processor should be listed before :func:`scale_and_crop` so palette is
    changed before the image is resized.

    bw
        Make the thumbnail grayscale (not really just black & white).

    replace_alpha
        Replace any transparency layer with a solid color. For example,
        ``replace_alpha='#fff'`` would replace the transparency layer with
        white.

    """
    is_transparent = is_transparent_image(im)
    if bw:
        if im.mode in ('L', 'LA'):
            return im
        if is_transparent:
            return im.convert('LA')
        else:
            return im.convert('L')

    if im.mode in ('L', 'RGB'):
        return im

    if is_transparent:
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        if not replace_alpha:
            return im
        base = Image.new('RGBA', im.size, replace_alpha)
        base.paste(im)
        im = base
        return im

    return im.convert('RGB')


def autocrop(im, autocrop=False, **kwargs):
    """
    Remove any unnecessary whitespace from the edges of the source image.

    This processor should be listed before :func:`scale_and_crop` so the
    whitespace is removed from the source image before it is resized.

    autocrop
        Activates the autocrop method for this image.

    """
    if autocrop:
        bw = im.convert('1')
        bw = bw.filter(ImageFilter.MedianFilter)
        # White background.
        bg = Image.new('1', im.size, 255)
        diff = ImageChops.difference(bw, bg)
        bbox = diff.getbbox()
        if bbox:
            im = im.crop(bbox)
    return im


def scale_and_crop(im, size, crop=False, upscale=False, **kwargs):
    """
    Handle scaling and cropping the source image.

    Images can be scaled / cropped against a single dimension by using zero
    as the placeholder in the size. For example, ``size=(100, 0)`` will cause
    the image to be resized to 100 pixels wide, keeping the aspect ratio of
    the source image.

    crop
        Crop the source image height or width to exactly match the requested
        thumbnail size (the default is to proportionally resize the source
        image to fit within the requested thumbnail size).

        By default, the image is centered before being cropped. To crop from
        the edges, pass a comma separated string containing the ``x`` and ``y``
        percentage offsets (negative values go from the right/bottom). Some
        examples follow:

        * ``crop="0,0"`` will crop from the left and top edges.

        * ``crop="-10,-0"`` will crop from the right edge (with a 10% offset)
          and the bottom edge.

        * ``crop=",0"`` will keep the default behavior for the x axis
          (horizontally centering the image) and crop from the top edge.

        The image can also be "smart cropped" by using ``crop="smart"``. The
        image is incrementally cropped down to the requested size by removing
        slices from edges with the least entropy.

        Finally, you can use ``crop="scale"`` to simply scale the image so that
        at least one dimension fits within the size dimensions given (you may
        want to use the upscale option too).

    upscale
        Allow upscaling of the source image during scaling.

    """
    source_x, source_y = [float(v) for v in im.size]
    target_x, target_y = [float(v) for v in size]

    if crop or not target_x or not target_y:
        scale = max(target_x / source_x, target_y / source_y)
    else:
        scale = min(target_x / source_x, target_y / source_y)

    # Handle one-dimensional targets.
    if not target_x:
        target_x = source_x * scale
    elif not target_y:
        target_y = source_y * scale

    if scale < 1.0 or (scale > 1.0 and upscale):
        # Resize the image to the target size boundary. Round the scaled
        # boundary sizes to avoid floating point errors.
        im = im.resize((int(round(source_x * scale)),
                        int(round(source_y * scale))),
                       resample=Image.ANTIALIAS)

    if crop:
        # Use integer values now.
        source_x, source_y = im.size
        # Difference between new image size and requested size.
        diff_x = int(source_x - min(source_x, target_x))
        diff_y = int(source_y - min(source_y, target_y))
        if diff_x or diff_y:
            # Center cropping (default).
            halfdiff_x, halfdiff_y = diff_x // 2, diff_y // 2
            box = [halfdiff_x, halfdiff_y,
                   min(source_x, int(target_x) + halfdiff_x),
                   min(source_y, int(target_y) + halfdiff_y)]
            # See if an edge cropping argument was provided.
            edge_crop = (isinstance(crop, basestring) and
                         re.match(r'(?:(-?)(\d+))?,(?:(-?)(\d+))?$', crop))
            if edge_crop and filter(None, edge_crop.groups()):
                x_right, x_crop, y_bottom, y_crop = edge_crop.groups()
                if x_crop:
                    offset = min(int(target_x) * int(x_crop) // 100, diff_x)
                    if x_right:
                        box[0] = diff_x - offset
                        box[2] = source_x - offset
                    else:
                        box[0] = offset
                        box[2] = source_x - (diff_x - offset)
                if y_crop:
                    offset = min(int(target_y) * int(y_crop) // 100, diff_y)
                    if y_bottom:
                        box[1] = diff_y - offset
                        box[3] = source_y - offset
                    else:
                        box[1] = offset
                        box[3] = source_y - (diff_y - offset)
            # See if the image should be "smart cropped".
            elif crop == 'smart':
                left = top = 0
                right, bottom = source_x, source_y
                while diff_x:
                    slice = min(diff_x, max(diff_x // 5, 10))
                    start = im.crop((left, 0, left + slice, source_y))
                    end = im.crop((right - slice, 0, right, source_y))
                    add, remove = _compare_entropy(start, end, slice, diff_x)
                    left += add
                    right -= remove
                    diff_x = diff_x - add - remove
                while diff_y:
                    slice = min(diff_y, max(diff_y // 5, 10))
                    start = im.crop((0, top, source_x, top + slice))
                    end = im.crop((0, bottom - slice, source_x, bottom))
                    add, remove = _compare_entropy(start, end, slice, diff_y)
                    top += add
                    bottom -= remove
                    diff_y = diff_y - add - remove
                box = (left, top, right, bottom)
            # Finally, crop the image!
            if crop != 'scale':
                im = im.crop(box)
    return im