from userena.utils import generate_sha1
from easy_thumbnails.fields import ThumbnailerImageField
import md5

def upload_to_mugshot(instance, filename):
    """
    Uploads a mugshot for a user to the ``USERENA_MUGSHOT_PATH`` and saving it
    under unique hash for the image. This is for privacy reasons so others
    can't just browse through the mugshot directory.

    """
    extension = filename.split('.')[-1].lower()
    salt, hash = generate_sha1(instance.id)
    return '%(path)s/%(hash)s.%(extension)s' % {
            'path': instance.__class__.__name__.lower(),
            'hash': hash[:22],
            'extension': extension
            }

class ThumbnailerImageFields(ThumbnailerImageField):
   
    def pre_save(self, model_instance, add):
        "check if samefile exist in storage,if exist user the old file else add a new one"
        from kinger.models import ImageWithMd5
        try:
            file_obj = getattr(model_instance,self.name).file
            md5_code = md5.new(file_obj.read()).hexdigest()
        except:
            md5_code = None
        file = ''
        if md5_code:
            try:
                file = ImageWithMd5.objects.filter(md5=md5_code).exclude(src='')[0].src
            except:
                file = super(ThumbnailerImageFields, self).pre_save(model_instance, add)
                m = ImageWithMd5()
                m.md5 = md5_code
                m.src = file.name
                m.save()
        return file
    
