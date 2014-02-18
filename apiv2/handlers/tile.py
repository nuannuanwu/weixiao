# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from apiv2.helpers import rc, DispatchMixin
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.comments import Comment
from kinger.models import Tile, TileTag, TileType, Group, NewTileCategory, Activity,TileToActivity,TileCreateTag,NewTileType
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from likeable.models import Like
from apiv2.helpers import query_range_filter

import apiv2.handlers.user
from apiv2.helpers import media_path,media_attr,code_to_video
import datetime
try:
    import simplejson as json
except ImportError:
    import json


class CategoryHandler(DispatchMixin, BaseHandler):
    
    model = NewTileCategory
    fields = ('new_category_id','name')
    allowed_methods = ("GET",)

    @classmethod
    def new_category_id(cls, model, request):
        """
        主键
        """
        return model.pk

    @classmethod
    def parent_name(cls, model, request):
        """
        父类名字
        """        
        return model.parent.name

    @DispatchMixin.get_required
    def parent_category(self, request):
        """
        获取父类

        ``GET`` `tiles/categorys <http://192.168.1.222:8080/v1/tiles/categorys>`_

        """       

        self.fields = ('new_category_id','name','sort')

        identity = request.GET.get('identity')
        is_tips = request.GET.get('is_tips', False)

        qs = NewTileCategory.objects.get_category(layer='parent', tips=is_tips, identity=identity)

        return query_range_filter(request.GET, qs, "categorys")

    @DispatchMixin.get_required
    def sub_category(self, request):
        """
        获取某个父类的子类

        ``GET`` `tiles/categorys/subcategory <http://192.168.1.222:8080/v1/tiles/categorys/subcategory>`_

        """
        self.fields = ('new_category_id','name','parent_id','parent_name','sort')

        is_tips = request.GET.get('is_tips', 1)
        parent_id = request.GET.get('parent_id')
        identity = request.GET.get('identity')

        try:
            if parent_id:
                # 特定父类的子类
                qs = NewTileCategory.objects.get_one_parent_sub(parent_id)
            else:
                # 某个类型的子类
                qs = NewTileCategory.objects.get_category(layer='sub', tips=is_tips, identity=identity)
            
            return query_range_filter(request.GET, qs, "categorys")

        except Exception, e:
            print e
            return rc.BAD_REQUEST    

        

class TileTagsHandler(BaseHandler):
    
    model = TileTag
    fields = ("tag_id", "name")
    allowed_methods = ("GET",)

    @classmethod
    def tag_id(cls, model, request):
        return model.id

    def read(self, request):
        '''
        获得瓦片标签列表

        ``GET`` `tiles/tags/ <http://192.168.1.222:8080/v1/tiles/tags>`_

        '''
        qs = TileTag.objects.all()
        return query_range_filter(request.GET, qs, "tags")


class TileTypesHandler(BaseHandler):
    model = TileType
    fields = ('type_id', 'name')
    allowed_methods = ("GET",)

    @classmethod
    def type_id(cls, model, request):
        return model.id

    def read(self, request):
        '''
        获取瓦片类型列表

        ``GET`` `tiles/types/ <http://192.168.1.222:8080/v1/tiles/types>`_

        '''
        qs = TileType.objects.all()
        return query_range_filter(request.GET, qs, "types")


class TileHandler(BaseHandler):
    model = Tile
    fields = ('id', 'title', 'image','new_category', 'image_large','image_middle', 'user', 'description', 'content', 'url', 'n_likers', 'n_comments', 'ctime', 'liked','comments',
        'new_type', ('tags', ()))
    allowed_methods = ("GET")

    @classmethod
    def ctime(cls, model, request):
        """
        增加了定期发布时间，故而，替换原先的ctime
        """
        return model.pub_time
    
    @classmethod
    def content(cls, model, request):
        """
        增加了定期发布时间，故而，替换原先的ctime
        """
        return code_to_video(model.content)

    @classmethod
    def user(cls, model, request):
        """
        增加了瓦片发布者creator
        """
        return model.creator    

    @classmethod
    def new_category(cls, model, request):
        try:
            return model.new_category
        except ObjectDoesNotExist:
            return {}
    
    @classmethod
    def new_type(cls, model, request):
        try:
            return model.new_type
        except ObjectDoesNotExist:
            return {}

    @classmethod
    def liked(cls, model, request):
        try:
            model.likes.get(user=request.user)
            return True
        except ObjectDoesNotExist:
            return False

    @classmethod
    def image(cls, model, request):
        try:
            if int(model.type_id) > 2:
                model.img = 'tile/tile_bg.png'
            img = model.img
            url = media_path(img,"normal")
            
            attr = media_attr(img,"normal");
            data = {}
            if url:
                data.update({'url':url})
            if attr:
                data.update({'width':attr['width'],'height':attr['height']}) 
            return data
        except Exception, e:
            print e
            return ""

    @classmethod
    def image_middle(cls, model, request):
        try:
            if int(model.type_id) > 2:
                model.img = 'tile/tile_bg.png'
            img = model.img
            url = media_path(img,"big")
            
            attr = media_attr(img,"big");
            data = {}
            if url:
                data.update({'url':url})
            if attr:
                data.update({'width':attr['width'],'height':attr['height']}) 
            return data
        except Exception, e:
            print e
            return ""
    
    @classmethod
    def image_large(cls, model, request):
        try:
            if int(model.type_id) > 2:
                model.img = 'tile/tile_bg.png'
            img = model.img
            url = media_path(img,"large")
            return url
        except Exception, e:
            print e
            return ""

    @classmethod
    def comments(cls, model, request, limit = 3):
        if model.n_comments > 0:
            return Comment.objects.for_model(model) \
                .filter(is_public=True).filter(is_removed=False) \
                .order_by("-submit_date")[0:limit]
        else:
            data = []
            return data

    def read(self, request):
        """
        获得所有内容(教师使用)

        ``GET`` `tiles/ <http://192.168.1.222:8080/v1/tiles>`_

        :param uid:
            用户 id. 用于查询与某用户相关的瓦片

        :param class_id:
            班级 id, 查询用户所在班级相关的瓦片


        获得某条内容的详细信息

        ``GET`` `tiles/show/ <http://192.168.1.222:8080/v1/tiles/show>`_

        :param id:
            某个瓦片的 id
        """
    
        params = request.GET
        tile_id = params.get("id")
        user_id = params.get("uid")
        class_id = params.get("class_id")


        if tile_id:
            try:
                tile = Tile.objects.get(pk=tile_id)
                tile.api_count += 1
                tile.save()
                
                pro = request.user.get_profile()
                pro.last_access = datetime.datetime.now()
                pro.save()
                return tile
            except Tile.DoesNotExist:
                return rc.NOT_HERE

        if not user_id and not class_id:
            #return rc.BAD_REQUEST
            return rc.bad_request( "user_id or class_id is requierd")

        q = Q(user__pk=user_id) if user_id else Q(group__pk=class_id)
        queryset = Tile.objects.filter(q).order_by("-ctime","-id")
        return query_range_filter(params, queryset, "tiles")

    # dispatch thought POST
    def create(self, request, method="post"):
        func = getattr(self, method.lower())
        if not func and not callable(func):
            return rc.FORBIDDEN
        return func(request)


class TileActionHandler(TileHandler):
    """
    管理瓦片操作.
    """
    allowed_methods = ("POST")

    def post(self, request):
        """
        发布一条内容, 针对个人或者班级.

        ``POST`` `tiles/create/ <http://192.168.1.222:8080/v1/tiles/types>`_

        :param type_id:
            瓦片类型

        :param uid:
            发布者，默认为匿名用户(uid: -1)

        :param class_id:
            瓦片所属班级，是否属于班级的内容

        :param content:
            内容描述

        :param img:
            二进制图片信息.
        """
        params = request.POST
        type_id = params.get("type_id")
        uid = params.get("uid", -1)
        class_id = params.get("class_id")
        content = params.get("content", "")
        category_id = params.get("category_id",0)
        img = request.FILES.get('img')
        video = params.get("video", "")
        title = params.get("title", "")
        tag = params.get("tag", "")

        category_id = int(category_id)

        try:
            tile_type = NewTileType.objects.get(pk=type_id)
            if not title:
                title = tile_type.name
        except NewTileType.DoesNotExist:
            pass
            #return rc.NOT_HERE

        try:
            tile_category = NewTileCategory.objects.all_with_deleted().get(pk=category_id)
            if not title:
                title = tile_category.name
        except NewTileCategory.DoesNotExist:
            return rc.not_here("tile_category object is not exist")
            #return rc.NOT_HERE

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return rc.not_here("user object  is not exist")
            #return rc.NOT_HERE

        try:
            group = Group.objects.get(pk=class_id) if class_id else None
        except Group.DoesNotExist:
            group = None

        tile = Tile(creator=request.user, user=user, group=group)
        tile.title = title
        tile.new_type_id = type_id
        tile.description = content
        tile.img = img
        tile.video = video

        tile.new_category_id = category_id
        try:
            is_exist = Tile.objects.get(creator=request.user, user=user, group=group,\
                title = title,description = content,img = img,video = video,new_category_id = category_id)
            return None
        except:
            tile.save()
            if tag and tile.id:
                tile_tag = TileCreateTag()
                tile_tag.tag = tag
                tile_tag.tile = tile
                tile_tag.save()
            
        return tile if tile.id else None
    
    
    
    
    def modify(self, request):
        """
        修改一条内容, 针对个人或者班级.

        ``POST`` `tiles/modify/ <http://192.168.1.222:8080/v1/tiles/modify>`_

        :param id:
            瓦片id
            
        :param type_id:
            瓦片类型

        :param uid:
            发布者，默认为匿名用户(uid: -1)

        :param class_id:
            瓦片所属班级，是否属于班级的内容

        :param content:
            内容描述

        :param img:
            二进制图片信息.
        """
        params = request.POST
        id = params.get("id")
        type_id = params.get("type_id","")
        uid = params.get("uid", "")
        class_id = params.get("class_id","")
        content = params.get("content", "")
        category_id = params.get("category_id",type_id)
        img = request.FILES.get('img','')
        video = params.get("video", "")
        title = params.get("title", "")
        print id,'======='
        try:
            tile = Tile.objects.get(pk=id)
        except Tile.DoesNotExist:
            return rc.not_here("tile object is not exist")

        category_id = int(category_id)
        if category_id in (1,2,3):
            category_id = 17

        if type_id:
            try:
                tile_type = TileType.objects.get(pk=type_id)
            except TileType.DoesNotExist:
                return rc.not_here("tile_type object is not exist")
            tile.type_id = type_id
            #return rc.NOT_HERE
        if category_id:
            try:
                tile_category = TileCategory.objects.all_with_deleted().get(pk=category_id)
            except TileCategory.DoesNotExist:
                return rc.not_here("tile_category object is not exist")
            tile.category_id = category_id
            
        if uid:
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                return rc.not_here("user object  is not exist")
            tile.user = user

        if class_id:
            try:
                group = Group.objects.get(pk=class_id)
            except Group.DoesNotExist:
                return rc.not_here("group object  is not exist")
            tile.group = group
        
        if title:
            tile.title = title
        if content:
            tile.description = content
        if img:
            tile.img = img 
        if video:
            tile.video = video
        
        if tile.category_id == 9:
            #if not group:
                #return rc.not_here("group object is not exist for Activity")
            try:
                desc = json.loads(tile.description)
                act = desc['events']
            except:
                return rc.not_here("Activity description object must be json include key events")
            if not act:
                desc = ''
            else:
                i = 0
                for d in act:
                    if not d['content']:
                       i += 1 
                if i == len(act):
                    desc = ''
            if not desc:
                return rc.not_here("Activity description object can not be null")
            try:
                has_migration = TileToActivity.objects.get(tile=tile)
            except:
                has_migration = None
            if has_migration:
                active = has_migration.active
            else:
                active = Activity()
                
            active.user = tile.user
            active.creator = tile.creator
            active.group = tile.group
            active.start_time = tile.start_time
            active.microsecond = tile.microsecond
            active.description = json.dumps({"events":desc['events']})
            active.save()   
            
            if not has_migration:
                migration = TileToActivity()
                migration.tile = tile
                migration.active = active
                migration.save()  
            
        tile.save()
        return tile


    def delete(self, request):
        """
        删除一条内容

        ``POST`` `tiles/destroy/ <http://192.168.1.222:8080/v1/tiles/types>`_

        :param id:
            某条瓦片的 id
        """
        tile_id = request.POST.get("id")
        try:
            Tile.objects.get(pk=tile_id).delete()
        except Tile.DoesNotExist:
            return rc.NOT_HERE

        # when return rc.deleted, content would be empty
        # no matter what content you pass to it.
        return rc.accepted({"result": True})

    def upload_video(self, request):
        """
        上传视频
        """
        files = {'mugshot': request.FILES['video']}
#         rs = {"result": "http://pyflask-base.stor.sinaapp.com/video/iphone_firefly_green_720_half.mp4"}
        rs = {"result": "http://weixiao178.com/video/iphone_firefly_green_720_half.mp4"}
        # when return rc.deleted, content would be empty
        # no matter what content you pass to it.
        return rc.accepted(rs)

class TileCategoryHandler(TileHandler):
    """ 负责瓦片数据查询 """

    allowed_methods = ("GET")

    def for_baby(self, request):
        '''
        获得小孩的所有内容(家长使用)

        ``GET`` `tiles/by_babys/ <http://192.168.1.222:8080/v1/tiles/by_babys>`_

        :param type_id:
            瓦片类型 id ，或者一组 id .类似于: 1,2,3,4

        :param category_id:
            瓦片分类 id ，或者一组 id .类似于: 1,2,3,4

        '''
        ids = request.GET.get("type_id", "")       

        qs = Tile.objects.get_tiles_baby(request.user).filter(new_category__is_tips=0).exclude(new_category__parent_id=1130).exclude(new_category_id=9)

        if ids:
            qs = qs.filter(type__pk__in=ids.split(","))

        try:
            category_ids = request.GET.get("category_id", "")   
            if category_ids:
                qs = qs.filter(category__pk__in=category_ids.split(","))
        except Exception, e:
            pass

        #qs = qs.filter(is_public=False)
        #return query_range_filter(request.GET, qs, "tiles")

        rs = query_range_filter(request.GET, qs, "tiles")
 
        self.cache_last_tile_id(rs,request.user)
        return rs


    def by_tags(self, request):
        '''
        获得小孩的所有内容(家长使用)

        ``GET`` `tiles/by_tags/ <http://192.168.1.222:8080/v1/tiles/by_tags>`_

        :param tag_id:
            瓦片标签 id ，或者一组 id .类似于: 1,2,3,4

        :param category_id:
            瓦片分类 id ，或者一组 id .类似于: 1,2,3,4

        '''

        ids = request.GET.get("tag_id", "")

        qs = Tile.objects.get_tiles_edu(request.user)
                
        if ids:
            qs = qs.filter(tags__pk__in=ids.split(","))
        
        try:
            category_ids = request.GET.get("category_id", "")   
            if category_ids:
                qs = qs.filter(category__pk__in=category_ids.split(","))
        except Exception, e:
            pass

        #return query_range_filter(request.GET, qs, "tiles")
        rs = query_range_filter(request.GET, qs, "tiles")
 
        self.cache_last_tile_id(rs,request.user)
        return rs

    def for_baby_with_promotion(self, request):
        '''
        ``by_babys`` + ``by_tags`` 接口的所有内容(家长使用)

        ``GET`` `tiles/by_babys_with_push/ <http://192.168.1.222:8080/v1/tiles/by_babys_with_push>`_

        '''

        qs = Tile.objects.get_tiles_all_login(request.user)

        try:
            category_ids = request.GET.get("category_id", "")   
            if category_ids:
                qs = qs.filter(category__pk__in=category_ids.split(","))
        except Exception, e:
            pass
            
        rs = query_range_filter(request.GET, qs, "tiles")
 
        self.cache_last_tile_id(rs,request.user)
        return rs

    def cache_last_tile_id(self,rs,user):
        try:
            pk =  rs['tiles'][0].id
            Tile.objects.set_user_last_tile(user=user,last_tile_id=pk)
        except Exception, e:
            pass

        return True
    # dispatch - thought GET
    def read(self, request, category=None):
        func = getattr(self, category)
        if not func and not callable(func):
            return rc.FORBIDDEN
        return func(request)


class TileLikeableHandler(TileHandler):
    """
    选择或者反选喜欢项.
    """
    allowed_methods = ("POST")

    def post(self, request):
        """
        喜欢某个瓦片(tile)

        ``POST`` `tiles/like/ <http://192.168.1.222:8080/v1/tiles/like>`_

        :param id:
            某个瓦片的 id

        """
        params = request.POST
        tid = params.get("id")
        is_tips = params.get("is_tips",None)
       
        try:
            tile = Tile.objects.get(pk=tid)
            ct = ContentType.objects.get_by_natural_key("kinger", "tile")
        except ContentType.DoesNotExist:
            tile = None
            return rc.NOT_HERE
        # generate a like by this user for the content object
        try:
            Like.objects.create(user=request.user, liked=tile)
        except IntegrityError:
            try:
                Like.objects.get(user=request.user, object_id=tid, content_type=ct).delete()
            except Like.DoesNotExist:
                return rc.NOT_HERE
        if tile and tile.id:
            try:
                n_likers = Like.objects.filter(content_type=ct,object_id=tid).count()
                tile.n_likers = n_likers
                tile.save()
            except:
                pass
        return tile
        

    def delete(self, request):
        """
        取消喜欢某个瓦片(tile)

        ``POST`` `tiles/like/ <http://192.168.1.222:8080/v1/tiles/like>`_

        :param id:
            某个瓦片的 id

        """

        params = request.POST
        tid = params.get("id")

        try:
            Like.objects.get(user=request.user, object_id=tid).delete()
        except Like.DoesNotExist:
            return rc.NOT_HERE

        return rc.accepted({"result": True})
    
    
class TileCtagHandler(TileHandler):
    """
    选择或者反选喜欢项.
    """
    allowed_methods = ("POST")

    def post(self, request):
        """
        喜欢某个瓦片(tile)

        ``POST`` `tiles/like/ <http://192.168.1.222:8080/v1/tiles/like>`_

        :param id:
            某个瓦片的 id

        """
        params = request.POST
        tag = params.get("tag",'')
        d = []
        try:
            t = eval(tag)
        except:
            return rc.not_here("please pass the correct parameters")
        for g in t:
            if g:
                num = TileCreateTag.objects.filter(tag=g).count()
                if num:
                    d.append({"tag":g,"exist": True})
                else:
                    d.append({"tag":g,"exist": False})   
        return rc.accepted(d)
