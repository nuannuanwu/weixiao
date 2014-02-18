# -*- coding: utf-8 -*-
from django.db import transaction
from userena import signals as userena_signals
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import Teacher,Group,Student,School,Department,Position,Access,\
                Role,WebSite,DocumentCategory,DocumentReceiver,Communicate,StarFigure,WebSiteAccess,\
                SupplyCategory,Provider,Supply,GroupTeacher,MaterialReceiver,DiskCategory,MaterialApproval,DocumentApproval
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from manage.forms import TeacherForm
from django.core.context_processors import csrf
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import xlrd
import random
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from kinger import settings
from django.db.models import Q
from userena.models import UserenaSignup
try:
    import simplejson as json
except ImportError:
    import json
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8') 

SITE_INFO = Site.objects.get_current()

try:
    batch_import_user = User.objects.get(username="batch_import_j6l4g9")
except:
    batch_import_user = User.objects.create_user("batch_import_j6l4g9", None, 123456)
            

def set_class_teacher(group,data):
    GroupTeacher.objects.filter(group=group,type_id=1).delete()
    if group.headteacher_id:
        obj, created = GroupTeacher.objects.get_or_create(group=group,teacher_id=group.headteacher_id,type_id=1)
    if not data:
        return ''
    for d in data:
        obj, created = GroupTeacher.objects.get_or_create(group=group,teacher_id=d,type_id=1)

def set_guide_teacher(group,data):
    GroupTeacher.objects.filter(group=group,type_id=2).delete()
    if not data:
        return ''
    for d in data:
        obj, created = GroupTeacher.objects.get_or_create(group=group,teacher_id=d,type_id=2)


def create_user(username=None, email=None, password=123456,batch=False):
        """
        Creates and saves a User with the given username, email and password.
        """
        prefix = 'u'
        latest = User.objects.latest('id')
        if not username:
            username = "%s%d" % (prefix, latest.id + 1)
            if batch:
                username += '_'+str(random.randint(1,999))
            else:
                if User.objects.filter(username = username).count():
                    username += str(random.randint(1,999))
        user = User(username=username)
        user.is_active = True
        user.password = batch_import_user.password
        user.save()
        return user
    
    
def create_teacher(form, request, school=None,batch=False):
    """
    * *form:* 老师的 *form*
    * *request:* 当次访问的 ``request``对象
    * *school:* 角色所在学校
    """
    try:
        password = form.cleaned_data['password']
    except:
        password = 123456
    try:
        username = form.cleaned_data['username']
    except:
        username = None
    try:
        school_id = request.POST['school']
        school = get_object_or_404(School,pk=school_id)
    except:
        school = school if school else None
#     raise
    if batch:
        user = create_user(username=username,password=password,batch=batch)
    else:
        user = School.userObjects.create_user(username=username,password=password)
    
    user.first_name = user.username
    user.save()
    
    f = StarFigure()
    f.user = user
    f.save()
    
    teacher = Teacher()
    teacher.user = user
    teacher.creator = request.user
    try:
        name = request.POST['realname']
    except:
        name = ''
    if name:
        teacher.name = name
    else:
        teacher.name = user.first_name or user.username
    teacher.school = school or get_schools(user)[0]
    teacher.save()
    set_teacher_default_access(teacher)
    return teacher

def create_student(form, request, school=None,group_id=None,name='',batch=False):
    """
    * *form:* 学生的 *form*
    * *request:* 当次访问的 ``request``对象
    * *school:* 角色所在学校
    """
    student = None
    try:
        password = form.cleaned_data['password']
    except:
        password = 123456
  
    try:
        username = form.cleaned_data['username']
    except:
        username = None
            
    if not school:
        try:
            school_id = request.POST['school']
            school = get_object_or_404(School,pk=school_id)
        except:
            school = None
    if batch:
        user = create_user(username=username,password=password,batch=batch)
    else:
        user = School.userObjects.create_user(username=username,password=password)
    user.first_name = user.username
    user.save()
    
    f = StarFigure()
    f.user = user
    f.save()
    
    student = Student()
    student.user = user
    student.creator = request.user
    
    if name:
        student.name = name
    else:
        realname = request.POST.get('realname','')
        if realname:
            student.name = realname
        else:
            student.name = user.first_name or user.username
    student.school = school if school else get_schools(user)
    if group_id:
        student.group_id = group_id
    student.save()
    return student

def school_agency(sid): 
    
    departements = Department.objects.filter(school_id=sid)
    positions = Position.objects.filter(school_id=sid)
    
    departement_list = []
    for d in departements:
        departement_list.append({'id':d.id,'name':d.name})
    position_list = []
    for p in positions:
        position_list.append({'id':p.id,'name':p.name})
            
    data = {'departments':departement_list,'positions':position_list}

    return HttpResponse(json.dumps(data))

def get_school_teacher(sid): 
    try:
        school = School.objects.get(pk=sid)
        teachers = school.teacher_set.all()
    except:
        teachers = []
    
    teacher_list = []
    for t in teachers:
        teacher_list.append({'id':t.id,'name':t.name})
            
    data = {'teachers':teacher_list}

    return HttpResponse(json.dumps(data))

def is_school_admin(user):
    try:
        admins = [u for u in user.teacher.school.admins.all()]
        if user in admins:
            return True
    except:
        pass
    return False

def school_class(request): 
    sid = request.GET.get("sid", "")
    ty = request.GET.get("ty", "")
    if ty:
        is_admin = True
    else:
        is_admin = is_school_admin(request.user)
    
    if is_admin:
        groups = Group.objects.filter(school_id=sid).exclude(type=3)
    else:
        group_pks = [g.group_id for g in GroupTeacher.objects.filter(teacher=request.user.teacher)]
        groups = Group.objects.filter(pk__in=group_pks)
    group_list = []
    for g in groups:
        group_list.append({'id':g.id,'name':g.name})

    return HttpResponse(json.dumps(group_list))

def get_school_realtes(request):
    sid = request.GET.get('school_id')
    try:
        school = School.objects.get(id=sid)
    except:
        data = {'status':0}
        return HttpResponse(json.dumps(data))
    providers = Provider.objects.filter(school=school)
    provider_list = []
    for p in providers:
        provider_list.append({'id': p.id ,'name': p.name})
    supplies = Supply.objects.filter(school=school,parent_id=0,is_show=True)
    supply_list = []
    for s in supplies:
        try:
            cname = s.category.name
        except:
            cname = ""
        supply_list.append({'id':s.id,'name':s.name,'cid':s.category_id,'cname':cname})
    categorys = supply_category_group(school)
    
    cats = SupplyCategory.objects.filter(school=school)
    category_group = []
    parent_cats = cats.filter(parent_id=0)
    for p in parent_cats:
        sub_cats = [{"sid":sc.id,"sname":sc.name} for sc in cats.filter(parent=p)]
        category_group.append({"pid":p.id,"pname":p.name,"member":sub_cats}) 
    data = {'providers':provider_list,'supplies':supply_list,'categorys':category_group,'status':1} 
    return HttpResponse(json.dumps(data))

def school_provider(sid): 
    providers = Provider.objects.filter(school_id=sid)
    provide_list = []
    for p in providers:
        provide_list.append({'id':p.id,'name':p.name})
    return HttpResponse(json.dumps(provide_list))

def pre_username():
    prefix = 'u'
    latest = User.objects.latest('id')
    username = "%s%d" % (prefix, latest.id + 1)
    if User.objects.filter(username = username).count():
        username += '_'+str(random.randint(1,999))
    password = 123456
    data = {'username':username,'password':password}
    return HttpResponse(json.dumps(data))

def username_info(username):
    try:
        user = User.objects.get(username=username)
        teacher = user.teacher
        is_teacher = True
    except:
        is_teacher = False
    data = {'is_teacher':is_teacher}
    return HttpResponse(json.dumps(data))

def checked_domain(value,site_id):
    try:
        int(value)
        data = {'status':'n'}
        return HttpResponse(json.dumps(data))
    except:
        pass

    domain = WebSite.objects.filter(type=0,domain=value)
    if site_id:
        domain = domain.exclude(id=site_id)
    if domain.count():
        status = 'n'
    else:
        status = 'y'
    if status == 'y':
        info = "恭喜！您输入的域名可以使用。"
    else:
        info = "抱歉，输入的域名不可用。"
    data = {'status':status,'info':info}
    return HttpResponse(json.dumps(data))

def is_teacher(user):
    """是否为老师用户"""
    try:
        d = isinstance(user.teacher,Teacher)
        if d:
            return True
        else:
            return False
    except Exception:
        return False

def is_student(user):
    """是否为家长用户"""
    try:
        d = isinstance(user.student,Student)
        if d:
            return True
        else:
            return False
    except Exception:
        return False

def get_name(user):
    """
    获取老师或学生的姓名
    """
    if not user:
        return ''
    if is_teacher(user):
        return user.teacher.name
    if is_student(user):
        return user.student.name
    try:
        return user.profile.realname
    except:
        return ''
      
def agency_access_list():
    access_list = [a for a in Access.objects.filter(level=0).exclude(parent_id=0)]
    return access_list

def school_access_list():
    access_list = [a for a in Access.objects.filter(level=1).exclude(parent_id=0)]
    return access_list
    
def roles_access_list(roles):
    access_list = []
    for r in roles:
        for a in r.accesses.all():
            if not a in access_list:
                access_list.append(a)
    return access_list

def set_schools_admin(schools,user,roles):
    agency_accesses = agency_access_list()
    school_accesses = school_access_list()
    roles_accesses = roles_access_list(roles)
    
    is_agency_admin = [c for c in roles_accesses if c not in agency_accesses]
    if is_agency_admin:
        for s in schools.filter(type=2):
            s.admins.add(user)
            
    is_school_admin = [c for c in roles_accesses if c not in school_accesses]
    if is_school_admin:
        for s in schools.filter(type=1):
            s.admins.add(user)
        
def user_access_list(user):
    try:
        roles = user.roles.all()
    except:
        roles = []
    return roles_access_list(roles)
        
def get_site(request):
    domain = request.META['HTTP_HOST'] or request.get_host()
    print domain,'ddddddddddddddddd'
    domain_parts = domain.split('.')
#    if len(domain_parts) == 4 and (domain_parts[1] == 'testwebsite' or domain_parts[1] == 'website'):
    if len(domain_parts) == 3 and (domain_parts[1] == 'jytn365' or domain_parts[1] == 'local'):
        domain__code = domain_parts[0]
        try:
            site_id = int(domain__code)
            site = WebSite.objects.filter(id=site_id,status=1)[0]
            return site
        except:
            pass
            
        try:
            site = WebSite.objects.filter(domain=domain__code)[0]
            return site
        except:
            pass
            
    q = Q(domain=domain,status=1)
    try:
        site = WebSite.objects.filter(q)[0]
    except:
        site = None
    return site 

def get_schools(user):
    schools = []
    school = user.teacher.school
    if school.is_delete:
        return schools
    if not school.parent_id:
        schools.append(school)
        schools = schools + [s for s in School.objects.filter(parent=school,is_delete=False)]
    else:
        schools.append(school)
    return schools

def get_school_with_workgroup(user):
    school = user.teacher.school
    if not school.parent_id:
        return get_schools(user)
    else:
        schools = []
        schools.append(school)
        com_schools = [c.school for c in Communicate.objects.filter(parent=school.parent)]
        if school in com_schools:
            com_schools.remove(school)
            for s in com_schools:
                schools.append(s)
        return schools
        

def get_user_name(user):       
    if is_teacher(user):
        return user.teacher.name
    if is_student(user):
        return user.student.name
    return user.profile.realname

def get_category_group(school):
    cats = DocumentCategory.objects.filter(school=school)
    category_group = []
    parent_cats = cats.filter(parent_id=0)
    for p in parent_cats:
        sub_cats = cats.filter(parent=p)
        category_group.append({"parent":p,"member":sub_cats})    
    return category_group

def disk_category_group(school,user=None):
    print school,'school----------------------'
    if user:
        cats = DiskCategory.objects.filter(school=school,user=user,type=0)
    else:
        type = 1 if school.parent_id > 0 else 2
        print type,'type-----------------------'
        cats = DiskCategory.objects.filter(school=school,type=type)
    category_group = []
    parent_cats = cats.filter(parent_id=0)
    for p in parent_cats:
        sub_cats = cats.filter(parent=p)
        category_group.append({"parent":p,"member":sub_cats})    
    return category_group

def supply_category_group(school):
    cats = SupplyCategory.objects.filter(school=school)
    category_group = []
    parent_cats = cats.filter(parent_id=0)
    for p in parent_cats:
        sub_cats = cats.filter(parent=p)
        category_group.append({"parent":p,"member":sub_cats})    
    return category_group

def mark_as_read(doc,user):
    try:
        docr = DocumentReceiver.objects.get(document=doc,user=user,is_send=True)
        docr.is_read = True
        docr.save()
    except:
        pass

def mark_supply_doc_as_read(doc,user):
    try:
        docr = MaterialReceiver.objects.get(document=doc,user=user,is_send=True)
        docr.is_read = True
        docr.save()
    except:
        pass
    
def ajax_validate_form(form):
    data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()]))
    return HttpResponse(data, mimetype='application/json')

def ajax_validate_error(form):
    if form.is_valid():
        status = True
    else:
        status = False
    data = json.dumps({'status':status})
    return HttpResponse(data, mimetype='application/json')

def ajax_validate_form_error_list(error_list):
    data = json.dumps(dict([(k, [unicode(e) for e in v]) for k,v in error_list]))
    return HttpResponse(data, mimetype='application/json')

def get_content_type_by_filename(file_name):
    suffix = ""
    name = os.path.basename(file_name)
    suffix = name.split('.')[-1]

    #http://www.iangraham.org/books/html4ed/appb/mimetype.html
    map = {}
    map['html'] = 'text/html'
    map['htm'] = 'text/html'
    map['asc'] = 'text/plain'
    map['txt'] = 'text/plain'
    map['c'] = 'text/plain'
    map['c++'] = 'text/plain'
    map['cc'] = 'text/plain'
    map['cpp'] = 'text/plain'
    map['h'] = 'text/plain'
    map['rtx'] = 'text/richtext'
    map['rtf'] = 'text/rtf'
    map['sgml'] = 'text/sgml'
    map['sgm'] = 'text/sgml'
    map['tsv'] = 'text/tab-separated-values'
    map['wml'] = 'text/vnd.wap.wml'
    map['wmls'] = 'text/vnd.wap.wmlscript'
    map['etx'] = 'text/x-setext'
    map['xsl'] = 'text/xml'
    map['xml'] = 'text/xml'
    map['talk'] = 'text/x-speech'
    map['css'] = 'text/css'

    map['gif'] = 'image/gif'
    map['xbm'] = 'image/x-xbitmap'
    map['xpm'] = 'image/x-xpixmap'
    map['png'] = 'image/png'
    map['ief'] = 'image/ief'
    map['jpeg'] = 'image/jpeg'
    map['jpg'] = 'image/jpeg'
    map['jpe'] = 'image/jpeg'
    map['tiff'] = 'image/tiff'
    map['tif'] = 'image/tiff'
    map['rgb'] = 'image/x-rgb'
    map['g3f'] = 'image/g3fax'
    map['xwd'] = 'image/x-xwindowdump'
    map['pict'] = 'image/x-pict'
    map['ppm'] = 'image/x-portable-pixmap'
    map['pgm'] = 'image/x-portable-graymap'
    map['pbm'] = 'image/x-portable-bitmap'
    map['pnm'] = 'image/x-portable-anymap'
    map['bmp'] = 'image/bmp'
    map['ras'] = 'image/x-cmu-raster'
    map['pcd'] = 'image/x-photo-cd'
    map['wi'] = 'image/wavelet'
    map['dwg'] = 'image/vnd.dwg'
    map['dxf'] = 'image/vnd.dxf'
    map['svf'] = 'image/vnd.svf'
    map['cgm'] = 'image/cgm'
    map['djvu'] = 'image/vnd.djvu'
    map['djv'] = 'image/vnd.djvu'
    map['wbmp'] = 'image/vnd.wap.wbmp'

    map['ez'] = 'application/andrew-inset'
    map['cpt'] = 'application/mac-compactpro'
    map['doc'] = 'application/msword'
    map['msw'] = 'application/x-dox_ms_word'
    map['oda'] = 'application/oda'
    map['dms'] = 'application/octet-stream'
    map['lha'] = 'application/octet-stream'
    map['lzh'] = 'application/octet-stream'
    map['class'] = 'application/octet-stream'
    map['so'] = 'application/octet-stream'
    map['dll'] = 'application/octet-stream'
    map['pdf'] = 'application/pdf'
    map['ai'] = 'application/postscript'
    map['eps'] = 'application/postscript'
    map['ps'] = 'application/postscript'
    map['smi'] = 'application/smil'
    map['smil'] = 'application/smil'
    map['mif'] = 'application/vnd.mif'
    map['xls'] = 'application/vnd.ms-excel'
    map['xlc'] = 'application/vnd.ms-excel'
    map['xll'] = 'application/vnd.ms-excel'
    map['xlm'] = 'application/vnd.ms-excel'
    map['xlw'] = 'application/vnd.ms-excel'
    map['ppt'] = 'application/vnd.ms-powerpoint'
    map['ppz'] = 'application/vnd.ms-powerpoint'
    map['pps'] = 'application/vnd.ms-powerpoint'
    map['pot'] = 'application/vnd.ms-powerpoint'

    map['wbxml'] = 'application/vnd.wap.wbxml'
    map['wmlc'] = 'application/vnd.wap.wmlc'
    map['wmlsc'] = 'application/vnd.wap.wmlscriptc'
    map['vcd'] = 'application/x-cdlink'
    map['pgn'] = 'application/x-chess-pgn'
    map['dcr'] = 'application/x-director'
    map['dir'] = 'application/x-director'
    map['dxr'] = 'application/x-director'
    map['spl'] = 'application/x-futuresplash'

    map['gtar'] = 'application/x-gtar'
    map['tar'] = 'application/x-tar'
    map['ustar'] = 'application/x-ustar'
    map['bcpio'] = 'application/x-bcpio'
    map['cpio'] = 'application/x-cpio'
    map['shar'] = 'application/x-shar'
    map['zip'] = 'application/zip'
    map['hqx'] = 'application/mac-binhex40'
    map['sit'] = 'application/x-stuffit'
    map['sea'] = 'application/x-stuffit'
    map['bin'] = 'application/octet-stream'
    map['exe'] = 'application/octet-stream'
    map['src'] = 'application/x-wais-source'
    map['wsrc'] = 'application/x-wais-source'
    map['hdf'] = 'application/x-hdf'

    map['js'] = 'application/x-javascript'
    map['sh'] = 'application/x-sh'
    map['csh'] = 'application/x-csh'
    map['pl'] = 'application/x-perl'
    map['tcl'] = 'application/x-tcl'

    map['skp'] = 'application/x-koan'
    map['skd'] = 'application/x-koan'
    map['skt'] = 'application/x-koan'
    map['skm'] = 'application/x-koan'
    map['nc'] = 'application/x-netcdf'
    map['cdf'] = 'application/x-netcdf'
    map['swf'] = 'application/x-shockwave-flash'
    map['sv4cpio'] = 'application/x-sv4cpio'
    map['sv4crc']  = 'application/x-sv4crc'
    map['t'] = 'application/x-troff'
    map['tr'] = 'application/x-troff'
    map['roff'] = 'application/x-troff'
    map['man'] = 'application/x-troff-man'
    map['me'] = 'application/x-troff-me'
    map['ms'] = 'application/x-troff-ms'
    map['latex'] = 'application/x-latex'
    map['tex'] = 'application/x-tex'
    map['texinfo'] = 'application/x-texinfo'
    map['texi'] = 'application/x-texinfo'
    map['dvi'] = 'application/x-dvi'
    map['xhtml'] = 'application/xhtml+xml'
    map['xht'] = 'application/xhtml+xml'

    map['au'] = 'audio/basic'
    map['snd'] = 'audio/basic'
    map['aif'] = 'audio/x-aiff'
    map['aiff'] = 'audio/x-aiff'
    map['aifc'] = 'audio/x-aiff'
    map['wav'] = 'audio/x-wav'
    map['mpa'] = 'audio/x-mpeg'
    map['abs'] = 'audio/x-mpeg'
    map['mpega'] = 'audio/x-mpeg'
    map['mp2a'] = 'audio/x-mpeg2'
    map['mpa2'] = 'audio/x-mpeg2'
    map['mid'] = 'audio/midi'
    map['midi'] = 'audio/midi'
    map['kar'] = 'audio/midi'
    map['mp2'] = 'audio/mpeg'
    map['mp3'] = 'audio/mpeg'
    map['m3u'] = 'audio/x-mpegurl'
    map['ram'] = 'audio/x-pn-realaudio'
    map['rm'] = 'audio/x-pn-realaudio'
    map['rpm'] = 'audio/x-pn-realaudio-plugin'
    map['ra'] = 'audio/x-realaudio'

    map['pdb'] = 'chemical/x-pdb'
    map['xyz'] = 'chemical/x-xyz'
    map['igs'] = 'model/iges'
    map['iges'] = 'model/iges'
    map['msh'] = 'model/mesh'
    map['mesh'] = 'model/mesh'
    map['silo'] = 'model/mesh'

    map['wrl'] = 'model/vrml'
    map['vrml'] = 'model/vrml'
    map['vrw'] = 'x-world/x-vream'
    map['svr'] = 'x-world/x-svr'
    map['wvr'] = 'x-world/x-wvr'
    map['3dmf'] = 'x-world/x-3dmf'
    map['p3d'] = 'application/x-p3d'

    map['mpeg'] = 'video/mpeg'
    map['mpg'] = 'video/mpeg'
    map['mpe'] = 'video/mpeg'
    map['mpv2'] = 'video/mpeg2'
    map['mp2v'] = 'video/mpeg2'
    map['qt'] = 'video/quicktime'
    map['mov'] = 'video/quicktime'
    map['avi'] = 'video/x-msvideo'
    map['movie'] = 'video/x-sgi-movie'
    map['vdo'] = 'video/vdo'
    map['viv'] = 'video/viv'
    map['mxu'] = 'video/vnd.mpegurl'

    map['ice'] = 'x-conference/x-cooltalk'
    import mimetypes
    mimetypes.init()
    mime_type = ""
    try:
        mime_type = mimetypes.types_map["." + suffix]
    except Exception, e:
        if map.has_key(suffix):
            mime_type = map[suffix]
        else:
            mime_type = 'application/octet-stream'
    return mime_type

def get_redirect_domain(request):
    domain_parts = request.get_host().split('.')
    if len(domain_parts) == 1:
        return 'localhost:8000'
    if domain_parts[-1] == 'test':
        return 'website.222.test'
    if domain_parts[-1] != 'dev':
        return 'localhost:8000'
    return 'weixiao178.com'

def get_parent_domain(request):
    domain_parts = request.get_host().split('.')
    try:
        length = len(domain_parts) - 1
        if length == 0:
            return 'http://localhost:8000'
        if domain_parts[-1] == 'test' and domain_parts[length-1] == '222':
            return 'http://website.222.test'
        if domain_parts[-1].split(':')[0] == 'dev':
            return 'http://localhost:8000'
        if domain_parts[length-1] == 'jytn365':
            return 'http://test.weixiao178.com'
        return 'http://weixiao178.com'
    except:
        return 'http://weixiao178.com'
    
#    if len(domain_parts) == 1:
#        return 'http://localhost:8000'
#    if domain_parts[-1] == 'test':
#        return 'http://website.222.test'
#    if domain_parts[-1] != 'dev':
#        return 'http://localhost:8000'
#    return 'http://weixiao178.com'

def get_parent_domain_string(request):
    domain_parts = request.get_host().split('.')
    try:
        length = len(domain_parts) - 1
        if domain_parts[-1] == 'local':
            return 'local.dev:8000'
        if domain_parts[-1] == 'test' and domain_parts[length-1] == '222':
            return 'website.222.test'
        if domain_parts[length-1] == 'jytn365':
            return 'jytn365.com'
        return 'jytn365.com'
    except:
        return 'jytn365.com'

def set_website_visit(user,site):
#    try:
    acc = WebSiteAccess()
    acc.user = user
    acc.website = site
    acc.save()
#    except:
#        pass
    return None

def is_agency_user(user):
    try:
        school = user.teacher.school
        if school.parent_id == 0:
            return True
    except:
        pass
    return False

def user_manage_school(user,school_id=0):
    schools = get_schools(user)
    school_pks = [s.id for s in schools]
    if is_agency_user(user) and school_id != 0:
        school = get_object_or_404(School,id=school_id,id__in=school_pks)
    else:
        school = schools[0]
    return school

def get_agency_teacher_by_group(group):
    schools = []
    school = group.school
    if school.is_delete:
        return []
    if school.parent_id == 0:
        schools.append(school)
        schools = schools + [s for s in School.objects.filter(parent=school,is_delete=False)]
    else:
        agency = school.parent
        schools.append(agency)
        schools = schools + [s for s in School.objects.filter(parent=agency,is_delete=False)]
    
    teachers = [t for t in Teacher.objects.filter(school__in=schools,is_authorize=True)]
    return teachers

def set_teacher_default_access(teacher):
    try:
        role,create = Role.objects.get_or_create(name='内置角色',type=1,school=teacher.school)
        teacher.user.roles.add(role)
        return True
    except:
        pass
    return False

def school_inner_role(school):
    try:
        code_list = ['manage_message_list','manage_send_message','manage_message_record',\
                     'manage_document','manage_shcedule','manage_supply_document','manage_disk']
        access_list = [a for a in Access.objects.filter(code__in=code_list)]
        
        role,create = Role.objects.get_or_create(name='内置角色',type=1,school=school)
        if not role.description:
            role.description = '系统内置角色，用来初始化职员权限,不可删除及更名'
        role.save()
        role.accesses = access_list
        if role.id and create:
            return True
    except:
        pass
    return False

def get_domain_redirct(request):
    domain = request.get_host()
    print domain,'domain--------------------'
    domain_list = ['www.weixiao178.com','www.test.weixiao178.com','website.222.test','localhost:8000']
    if domain in domain_list:
        return None
    try:
        site = WebSite.objects.get(type=1,domain=domain,status=1)
        return site
    except:
        pass
    return None

def unread_count(request):
    """
    获取某个用户的各种消息未读数
    """
    user = request.user
    messages_count = MessageRecipient.objects.count_unread_messages_for(request.user)
    document_count = MaterialReceiver.objects.filter(is_send=True,user=request.user,is_read=False).count()
    approve_count = MaterialApproval.objects.filter(approvaler=request.user,status=0).count()
    docs = DocumentReceiver.objects.filter(is_send=True,user=request.user,is_read=False).count()
    apps = DocumentApproval.objects.filter(approvaler=request.user,status=0).count()
    ctx = {"messages": messages_count,"docouments":document_count,"approves":approve_count,"docs":docs,"apps":apps}
    return ctx
    
        