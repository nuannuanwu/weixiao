# -*- coding: utf-8 -*-
import os.path
######################
# MEZZANINE SETTINGS #
######################
print os.path.dirname(__file__)
APP_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.dirname(APP_DIR))
print APP_DIR,PROJECT_DIR

GRAPPELLI_ADMIN_TITLE = u'生命教育 - - 后台管理系统'
# The following settings are already defined in mezzanine.conf.defaults
# with default values, but are common enough to be put here, commented
# out, for convenient overriding.

# Controls the ordering and grouping of the admin menu.
#
# ADMIN_MENU_ORDER = (
#	 ("Content", ("pages.Page", "blog.BlogPost",
#		"generic.ThreadedComment", ("Media Library", "fb_browse"),)),
#	 ("Site", ("sites.Site", "redirects.Redirect", "conf.Setting")),
#	 ("Users", ("auth.User", "auth.Group",)),
# )

# A three item sequence, each containing a sequence of template tags
# used to render the admin dashboard.
#
# DASHBOARD_TAGS = (
#	 ("blog_tags.quick_blog", "mezzanine_tags.app_list"),
#	 ("comment_tags.recent_comments",),
#	 ("mezzanine_tags.recent_actions",),
# )

# A sequence of fields that will be injected into Mezzanine's (or any
# library's) models. Each item in the sequence is a four item sequence.
# The first two items are the dotted path to the model and its field
# name to be added, and the dotted path to the field class to use for
# the field. The third and fourth items are a sequence of positional
# args and a dictionary of keyword args, to use when creating the
# field instance. When specifying the field class, the path
# ``django.models.db.`` can be omitted for regular Django model fields.
#
# EXTRA_MODEL_FIELDS = (
#	 (
#		 # Dotted path to field.
#		 "mezzanine.blog.models.BlogPost.image",
#		 # Dotted path to field class.
#		 "somelib.fields.ImageField",
#		 # Positional args for field class.
#		 ("Image",),
#		 # Keyword args for field class.
#		 {"blank": True, "upload_to": "blog"},
#	 ),
#	 # Example of adding a field to *all* of Mezzanine's content types:
#	 (
#		 "mezzanine.pages.models.Page.another_field",
#		 "IntegerField", # 'django.db.models.' is implied if path is omitted.
#		 ("Another name",),
#		 {"blank": True, "default": 1},
#	 ),
# )

# Setting to turn on featured images for blog posts. Defaults to False.
#
# BLOG_USE_FEATURED_IMAGE = True

# If ``True``, users will be automatically redirected to HTTPS
# for the URLs specified by the ``SSL_FORCE_URL_PREFIXES`` setting.
#
# SSL_ENABLED = True

# Host name that the site should always be accessed via that matches
# the SSL certificate.
#
# SSL_FORCE_HOST = "www.example.com"

# Sequence of URL prefixes that will be forced to run over
# SSL when ``SSL_ENABLED`` is ``True``. i.e.
# ('/admin', '/example') would force all URLs beginning with
# /admin or /example to run over SSL. Defaults to:
#
# SSL_FORCE_URL_PREFIXES = ("/admin", "/account")

SITE_TITLE = 'kinger'

########################
# MAIN DJANGO SETTINGS #
########################

# People who get code error notifications.
# In the format (('Full Name', 'email@example.com'),
#				('Full Name', 'anotheremail@example.com'))
ADMINS = (
	# ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# If you set this to True, Django will use timezone-aware datetimes.
#时区设置
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#设置django界面语言
LANGUAGE_CODE = 'zh-cn'

LANGUAGES = (
	('zh_CN', 'Chinese Simplified'),
	#('zh', 'Chinese Traditional'),
	('en', 'English'),
)

# A boolean that turns on/off debug mode. When set to ``True``, stack traces
# are displayed for error pages. Should always be set to ``False`` in
# production. Best set to ``True`` in local_settings.py
DEBUG = False

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True



# Make this unique, and don't share it with anybody.
SECRET_KEY = "96f8815f-b23c-4128-b097-8a4118d2cb3fb981fa87-b81b-4744-b413-819f7fde181f43353c7c-a2b6-435d-b673-8145bc9a31f5"

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = ("127.0.0.1",)

# List of callables that know how to import templates from various sources.
#TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
#        'django.template.loaders.filesystem.Loader',
#        'django.template.loaders.app_directories.Loader',
#    )),
#)
TEMPLATE_LOADERS = (
	"django.template.loaders.filesystem.Loader",
	"django.template.loaders.app_directories.Loader",
)

AUTHENTICATION_BACKENDS = (
	'userena.backends.UserenaAuthenticationBackend',
	'guardian.backends.ObjectPermissionBackend',
	'django.contrib.auth.backends.ModelBackend',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	"django.contrib.staticfiles.finders.FileSystemFinder",
	"django.contrib.staticfiles.finders.AppDirectoriesFinder",
#	'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


#############
# DATABASES #
#############

try:
	import sae.const
except:
	pass
from os import environ

#根据环境定义数据库连接参数
islocalhost = not environ.get("APP_NAME","")

if islocalhost:
	mysql_name = 'kinger'
	mysql_user = 'root'
	mysql_pass = '111111'
	mysql_host = '192.168.1.222'
	mysql_port = '3306'
	mysql_host_s = '192.168.1.222'
	DEBUG = True
else:#sae上
	mysql_name = sae.const.MYSQL_DB
	mysql_user = sae.const.MYSQL_USER
	mysql_pass = sae.const.MYSQL_PASS
	mysql_host = sae.const.MYSQL_HOST
	mysql_port = sae.const.MYSQL_PORT
	mysql_host_s = sae.const.MYSQL_HOST_S
	DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
	"default": {
		# Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
		"ENGINE": "django.db.backends.mysql",
		# DB name or path to database file if using sqlite3.
		"NAME": mysql_name,
		# Not used with sqlite3.
		"USER": mysql_user,
		# Not used with sqlite3.
		"PASSWORD": mysql_pass,
		# Set to empty string for localhost. Not used with sqlite3.
		"HOST": mysql_host,
		# Set to empty string for default. Not used with sqlite3.
		"PORT": mysql_port,
	},
	"master": {
		# Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
		"ENGINE": "django.db.backends.mysql",
		# DB name or path to database file if using sqlite3.
		"NAME": mysql_name,
		# Not used with sqlite3.
		"USER": mysql_user,
		# Not used with sqlite3.
		"PASSWORD": mysql_pass,
		# Set to empty string for localhost. Not used with sqlite3.
		"HOST": mysql_host,
		# Set to empty string for default. Not used with sqlite3.
		"PORT": mysql_port,
	},
	"slave": {
		# Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
		"ENGINE": "django.db.backends.mysql",
		# DB name or path to database file if using sqlite3.
		"NAME": mysql_name,
		# Not used with sqlite3.
		"USER": mysql_user,
		# Not used with sqlite3.
		"PASSWORD": mysql_pass,
		# Set to empty string for localhost. Not used with sqlite3.
		"HOST": mysql_host_s,
		# Set to empty string for default. Not used with sqlite3.
		"PORT": mysql_port,
	}		
}
class DataBaseRouter(object):
	"""
	A router to control all database operations.
	"""
	def db_for_read(self, model,  *args, **kwargs):
		"""
		Attempts to read.
		"""
		return "slave"

	def db_for_write(self, model,  *args, **kwargs):
		"""
		Attempts to write .
		"""
		return "master"
	   
	def allow_relation(self, obj1, obj2, **hints):
		"Allow any relation between two objects in the db pool"
		db_list = ('master','slave')
		if obj1._state.db in db_list and obj2._state.db in db_list:
			return True
		return None

	def allow_syncdb(self, db, model):
		"Explicitly put all models on all databases."
		return True
	   
	   
DATABASE_ROUTERS = [DataBaseRouter()]
#########
# PATHS #
#########

import os

# Full filesystem path to the project.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Name of the directory for the project.
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIRNAME

MEDIA_ROOT = os.path.join(PROJECT_DIR, '_media')
MEDIA_URL = '/_media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, '_static')
STATIC_URL = '/_static/'


FILE_PATH = os.path.join(PROJECT_ROOT, 'file')
FILE_URL = '/site_file/'

PROFILE_LOG_BASE = os.path.join(PROJECT_ROOT, 'profile_log')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"

# Package/module name to import the root urlpatterns from for the project.
ROOT_URLCONF = "%s.urls" % PROJECT_DIRNAME

# Put strings here, like "/home/html/django_templates"
# or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)


################
# APPLICATIONS #
################

INSTALLED_APPS = [
	'grappelli',
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.redirects",
	"django.contrib.sessions",
	"django.contrib.sites",
	"django.contrib.sitemaps",
	"django.contrib.staticfiles",

	'django.contrib.comments',
	'django.contrib.markup',
	'django.contrib.humanize',

	"backend",
	"sae_extra",
	"oss",
	"oss_extra",
#	"debug_toolbar",
	# 主程序
	'kinger',
	'manage',
	# 专家问答
	'aq',
	# 客服问答
	'waiter',
	#oa办公系统
	'oa',
	#oa物资管理
	'oa.supply',
	# 短信相关
	'sms',
	# 分页功能
	'pagination',
	# 用户扩展信息
	'kinger.profiles',
	#成长书
	'kinger.growth',
	'bootstrap',
	# 前台用户注册登录功能 + 附加message
	'userena', 'guardian', 'easy_thumbnails', 'userena.contrib.umessages',
	# 相册功能
	#'photologue', 'tagging',
	# 喜欢功能
	'likeable',
	# 评分系统
	#'djangoratings',
	# 数据库维护
	#'south',
	# oauth2 底层包
	'oauth2app', 'uni_form',
	# oauth2 基本接口,供外部调用
	'kinger.apps.oauth2',
	# api 数据接口
	'api',
	'apiv2',
	# api 客户端，调试使用
	'kinger.apps.client',
	'storages',
	# 'piston'
	'bootstrapform',
	'captcha',
	# 提醒机制
	'notifications',
#     'djcelery',
]

try:
	import sae.const
except:
	INSTALLED_APPS.append('djcelery')
# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
	# 可以在模板使用 user 和 perms
	"django.contrib.auth.context_processors.auth",
	"django.contrib.messages.context_processors.messages",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.static",
	"django.core.context_processors.media",
	"django.core.context_processors.request",

	# 配置全局变量
	"kinger.context_processors.ctx_config",
)

# 在 kinger.context_processors.ctx_config 会读取以下配置
CTX_CONFIG = {
	'KINGER_TITLE':u'微校',
	'KINGER_TAGLINE':u'成长',
	'KINGER_SUB_TITLE':u'童年',
	'STUDENT_PAGE_SIZE': 50,
	'KINGER_PAGE_SIZE': 6,
	'KINGER_DEFAULT_AVATAR':'img/avatar_128.png',
	'KINGER_DEFAULT_GROUP_IMG':'img/group_128.png',
	'DEFAULT_AVATAR':'img/avatar_64.png',
	'DEFAULT_AVATAR_LARGE':'img/avatar_128.png',
}

# List of middleware classes to use. Order is important; in the request phase,
# these middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE_CLASSES = (
	#缓存
	#'django.middleware.cache.UpdateCacheMiddleware',#必须在中间件清单的第一条

	"django.middleware.common.CommonMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.redirects.middleware.RedirectFallbackMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	# gzip
	'django.middleware.gzip.GZipMiddleware',
	'pagination.middleware.PaginationMiddleware',

#	'debug_toolbar.middleware.DebugToolbarMiddleware',
	'oa.middleware.SubdomainMiddleware',

	#'django.middleware.cache.FetchFromCacheMiddleware',#必须在中间件清单的最后一条
)

# Store these package names here as they may change in the future since
# at the moment we are using custom forks of them.
PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"


AUTHENTICATION_BACKENDS = (
	'userena.backends.UserenaAuthenticationBackend',
	'guardian.backends.ObjectPermissionBackend',
	'django.contrib.auth.backends.ModelBackend',
)

################
# oauth2	   #
################
OAUTH2_ACCESS_TOKEN_EXPIRATION = 3600*24*30


################
# easy_thumbnails#
################

THUMBNAIL_ALIASES = {
	'': {
		'mini': {'size': (48, 48), 'crop': True},
		'small': {'size': (64, 64), 'crop': True},
		'normal': {'size': (192, 0), 'crop': True},
		'big': {'size': (384, 0), 'crop': True},
		"large": {'size':(650,0)},
		"avatar": {'size':(64,64)},
		"avatar_normal": {'size':(128,128)},
		"avatar_large": {'size':(192, 192)},
		'album_big': {'size': (350, 225), 'crop': True},
		'album_normal': {'size': (200, 100), 'crop': True},
		'album_small': {'size': (100, 100), 'crop': True},
		'album_tiny': {'size': (52, 52), 'crop': True},
		'album_large': {'size': (566, 0), 'crop': True},
		'album_standard': {'size': (300, 300), 'crop': True},
		'start_normal': {'size': (146, 146), 'crop': True},
		'video_topic': {'size': (120, 90), 'crop': True},
		'site_logo': {'size': (120, 80), 'crop': True},
		'axis_normal':{'size': (210, 210), 'crop': True},
		'edu_normal':{'size': (230, 0), 'crop': True},
		'theme_normal':{'size': (100, 70), 'crop': True},
		'theme_big':{'size': (450, 275), 'crop': True},    
        'theme_large':{'size': (470, 295), 'crop': True},
		'recommend':{'size': (230, 270), 'crop': True},
		'small_list': {'size': (100, 0), 'crop': True},

		'img_large': {'size': (620, 0), 'crop': True},
		'img_middle': {'size': (230, 0), 'crop': True},
		'img_small': {'size': (100, 0), 'crop': True},
		'img_axis': {'size': (210, 210), 'crop': True},
	},
}


################
# userena #
################
# Userena settings
LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'
AUTH_PROFILE_MODULE = 'profiles.Profile'

USERENA_DISABLE_PROFILE_LIST = True
USERENA_MUGSHOT_SIZE = 140
USERENA_REDIRECT_ON_SIGNOUT = '/'
USERENA_SIGNIN_REDIRECT_URL = '/'

# Guardian
ANONYMOUS_USER_ID = -1



#EMAIL_BACKEND = 'sae_extra.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# email config
EMAIL_HOST='smtp.sina.com'
EMAIL_PORT=25
EMAIL_HOST_USER='yii4sae@sina.com'
EMAIL_HOST_PASSWORD='123456'
EMAIL_USE_TLS = False
#SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
#CACHE_BACKEND = 'locmem:///'
#CACHE_BACKEND = 'file:///var/tmp/django_cache'

CACHEMACHINE_DEPEND_SILENC = True

#仿缓存（供开发时使用）
#CACHE_BACKEND = 'dummy:///'

CACHE_COUNT_TIMEOUT = 3600
THUMBNAIL_SUBDIR = "thumbs"
THUMBNAIL_EXTENSION = "png"

try:
	if not islocalhost:
		THUMBNAIL_DEFAULT_STORAGE = 'sae_extra.storage.SaeStorage'
		DEFAULT_FILE_STORAGE =  'sae_extra.storage.SaeStorage'

		CACHES = {
			'default': {
				'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
				'LOCATION': '127.0.0.1:11211',
				'TIMEOUT': 3600*24*30
			},
			'database': {
				'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
				'LOCATION': 'django_cache',
				'TIMEOUT': 3600*24*30
			}	

		}
		
		OSS_ACCESS_KEY_ID = 'buRMMbpMqqOgp7ai'
		OSS_SECRET_ACCESS_KEY = 'FT8DBVVMYG9UXg2DL3qEoZa3ytmoIT'
		OSS_HOST = 'oss.aliyuncs.com'
		OSS_HOST_INTER = 'oss-internal.aliyuncs.com'
		OSS_BUCKET = 'base01'
except:
	pass


try:
	import sae.const
except:
	import djcelery
	djcelery.setup_loader()
	BROKER_URL = "amqp://guest:guest@localhost:5672//"
	TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
    
   
#########################
# OPTIONAL APPLICATIONS #
#########################

# These will be added to ``INSTALLED_APPS``, only if available.
OPTIONAL_APPS = (
	"django_extensions",
	"compressor",
	PACKAGE_NAME_FILEBROWSER,
	PACKAGE_NAME_GRAPPELLI,
)

# debug 功能
DEBUG_TOOLBAR_PANELS = (
	'debug_toolbar.panels.version.VersionDebugPanel',
	'debug_toolbar.panels.timer.TimerDebugPanel',
	'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
	'debug_toolbar.panels.headers.HeaderDebugPanel',
	'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
	'debug_toolbar.panels.template.TemplateDebugPanel',
	'debug_toolbar.panels.sql.SQLDebugPanel',
	'debug_toolbar.panels.signals.SignalDebugPanel',
	'debug_toolbar.panels.logger.LoggingPanel',
)

INTERNAL_IPS = ('127.0.0.1','183.15.162.124','192.168.1.110')
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False,'HIDE_DJANGO_SQL': False,}

#############
# piston
############
PISTON_IGNORE_DUPE_MODELS = True
# PISTON_DISPLAY_ERRORS = True


##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
try:
	from local_settings import *
except ImportError:
	pass

try:
	from crontab_settings import *
except ImportError:
	pass

try:
	from sae_test_settings import *
except ImportError:
	pass

SEND_ACCOUNT_TIMEDELTA = 300
CHANGE_USERNAME_TIMEDELTA = 2592000
####################
# DYNAMIC SETTINGS #
####################
NOTIFY_USE_JSONFIELD = True

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y年m月d日 H点i分'

PAGINATION_DEFAULT_WINDOW = 3