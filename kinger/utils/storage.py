# -*- coding: utf-8 -*-




import hashlib,random
md5_constructor = hashlib.md5
md5_hmac = md5_constructor
sha_constructor = hashlib.sha1
sha_hmac = sha_constructor


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not salt:
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt+str(string)).hexdigest()

    return (salt, hash)

def hash_storage_filename(instance, filename):
    """
    Uploads a mugshot for a user to the ``USERENA_MUGSHOT_PATH`` and saving it
    under unique hash for the image. This is for privacy reasons so others
    can't just browse through the mugshot directory.

    """
    extension = filename.split('.')[-1].lower()
    salt, hash = generate_sha1(filename)
    return '%(path)s/%(hash)s.%(extension)s' % {
            'path': instance,
            'hash': hash[:32],
            'extension': extension
            }

from django.core.files.storage import get_storage_class, default_storage
def get_thumbs_storage():
    a = get_storage_class()(location='thumbs101')
    return a

def get_storage():
    return default_storage

    test = default_storage
    print type(test)
    try:
        import sae.storage
        from Feather.storage.sina import SaeStorage
        storage = SaeStorage()
    except Exception, e:
        storage = FileSystemStorage()

    return storage

def upload_to_storage(name,content):
    storage = get_storage()
    rs = storage.save(name, content)
    return rs