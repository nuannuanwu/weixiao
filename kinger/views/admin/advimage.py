# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from kinger.models import TinymceImage,TemporaryFiles
from kinger.helpers import media_path
from kinger.settings import FILE_PATH,STATIC_ROOT,FILE_URL
from django.contrib.sites.models import Site
from celery.task.http import URL
from django.core.urlresolvers import reverse
from oss_extra.storage import AliyunStorage
import os
try:
    import simplejson as json
except ImportError:
    import json
import Image
import StringIO
    
SITE_INFO = Site.objects.get_current()


@csrf_exempt
def upload_image(request):  

    if request.method == 'POST':  
        if "upload_file" in request.FILES:  
            f = request.FILES["upload_file"]
            
            tiny = TinymceImage() 
            try:
                 tiny.img = f
                 tiny.save()
                 return HttpResponse(tiny.img.url)
            except:
                pass
            name = "/richimage/"+f.name
            
            path = default_storage.save(name,f)
            url = default_storage.url(path)
            return HttpResponse(url)
    return HttpResponse(u"上传失败！")

@csrf_exempt
def upload_tile_image(request):  
    if request.method == 'POST' and "img" in request.FILES:  
        f = request.FILES["img"]
        chunks = int(request.POST.get('chunks'))
#        if chunks == 1:
#            print f,'fffffffffffffffffffff'
#            print f.name,'nnnnnnnnnnnnnnnnnn'
#            print f.read(),'rrrrrrrrrrrrrrrrrrrrrr'
#            pic = TinymceImage() 
#            try:
#                 pic.img = f
#                 pic.save()
#                 url = media_path(pic.img,size = "start_normal")
#                 data = json.dumps({'status':1,'desc':"ok","pic":url,"pid":pic.id})
#                 return HttpResponse(data)
#            except:
##                pass
#        else:
        chunk = int(request.POST.get('chunk'))
        file_id = request.POST.get('file_id')
        name = request.POST.get('name')
        
        file_path = FILE_PATH + '/temp/' + str(file_id)
        print file_path,'ppppppppppppppppppppp'
        fp = open(file_path,"a+b")
        fp.write(f.read())
        fp.close()
#            fr = open(file_path,"rb")
#            print fr.read(),'rrrrrrrrrrrrrrrrrrrrrrrrrrrr---------------------------------------------'
#            fr.close()
        
        if chunk + 1  == chunks:
#                filename = 'tinymceimage/' + str(file_id) + '.' +  name.split('.')[-1].lower()
#                print filename,'fffffffffffffffffffffffffff'
#                fr = open(file_path,"rb")
#                content = fr.read()
#                fr.close()
#                try:
#                    if os.path.isfile(file_path):
#                        print 222222222222222222222222222
#                        os.remove(file_path)
#                except:
#                    pass
            
#                print 'http://' + SITE_INFO.domain + reverse('cron_make_large_img')
#                try:
#                URL('http://' + SITE_INFO.domain + reverse('cron_make_large_img')).post_async(filename=filename,file_path=file_path)
#                except:
#                    pass
#                AliyunStorage(). _put_file(filename, content)
#                print 1111111111111111111111111111111
            
#                pic = TinymceImage()
#                pic.img = filename
#                pic.save()
#                url = media_path(pic.img,size = "start_normal")
            extension = name.split('.')[-1].lower()
            file_img = FILE_PATH + '/tile/' + str(file_id) + '.' + extension
            img_url = FILE_URL + 'tile/' + str(file_id) + '.' + extension
            fr = open(file_path,"rb")
            content = fr.read()
            fr.close()
            
#                img = open(file_img,"wb")
#                img.write(content)
#                img.close()
            thumbnail_string(file_img,content,size=(80, 80))
            
            temp = TemporaryFiles()
            temp.fileid = str(file_id)
            temp.path = file_img
            temp.save()
            
            data = json.dumps({'status':1,'desc':"ok","pic":img_url,"pid":'','file_path':file_path,'extension':extension})
            return HttpResponse(data)
#                except:
#                    pass
        else:
            return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
    data = json.dumps({'status':0,'desc':"error"})
    return HttpResponse(data)


def thumbnail_string(name,buf, size=(80, 80)):
    f = StringIO.StringIO(buf)
    image = Image.open(f)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    try:
        image = image.resize(size, Image.ANTIALIAS)
    except:
        pass
    o = StringIO.StringIO()
    image.save(o, "JPEG")
    image.save(name)
    

