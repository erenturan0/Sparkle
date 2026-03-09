from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='unsafe-build-secret-key')

DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = [
    'www.sparkleblog.app',
    'sparkleblog.app',
    'sparkle-292533913305.europe-west1.run.app',
    'localhost',
    '127.0.0.1',
]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smart_home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

CSRF_TRUSTED_ORIGINS = [
    'https://*.run.app',
    'https://sparkleblog.app',
    'https://www.sparkleblog.app',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'smart_home.context_processors.pending_requests',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DB_HOST = env('DB_HOST', default='')

if DB_HOST:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='postgres'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': DB_HOST,
            'PORT': env('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': 5,
            },
        }
    }
else:
    DATABASES = {
        'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3'),
    }
    if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        DATABASES['default'].setdefault('OPTIONS', {})
        DATABASES['default']['OPTIONS']['connect_timeout'] = 5

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'smart_home/static',
]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'

JAZZMIN_SETTINGS = {
    'site_title': 'Sparkle Yönetici',
    'site_header': 'Sparkle',
    'site_brand': 'Sparkle',
    'site_logo_classes': 'img-circle',
    'welcome_sign': 'Sparkle Yönetim Paneli',
    'copyright': 'Sparkle Smart Home 2026',
    'topmenu_links': [
        {'name': 'Siteyi Görüntüle', 'url': '/', 'new_window': False, 'permissions': ['auth.view_user']},
    ],
    'search_model': ['auth.User', 'smart_home.SmartDevice'],
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'smart_home.SmartDevice': 'fas fa-plug',
        'smart_home.ShareRequest': 'fas fa-share-alt',
    },
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': True,
    'show_ui_builder': False,
    'changeform_format': 'horizontal_tabs',
    'custom_css': 'smart_home/css/admin_theme.css',
    'custom_js': 'smart_home/js/admin_theme.js',
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-purple',
    'accent': 'accent-teal',
    'navbar': 'navbar-light bg-white',
    'no_navbar_border': False,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-purple',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'button_classes': {
        'primary': 'btn-sparkle-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-sparkle-success',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-sparkle-success',
    },
}
