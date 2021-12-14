
import os
import importlib

from django.urls import path
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView, TemplateView

from pydoc import locate


def setup_settings(settings, is_prod=False, **kwargs):

    base_dir = settings['BASE_DIR']

    default_settings = {
        'ROOT_URLCONF': 'core.urls',
        'ALLOWED_HOSTS': ['*'],
        'WSGI_APPLICATION': 'core.wsgi.application',
        'TIME_ZONE': 'Europe/Kiev',
        'USE_TZ': True,
        'USE_L10N': True,
        'USE_I18N': True,
        'EMAIL_USE_TLS': True,
        'SITE_ID': 1,
        'LANGUAGE_CODE': 'uk',
        'LANGUAGES': (('uk', 'UA'), ),
        'FILE_UPLOAD_PERMISSIONS': 0o755,
        'SILENCED_SYSTEM_CHECKS': ['mysql.E001', 'mysql.W002'],
        'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': settings['DB_NAME'],
                'USER': 'dev'
            }
        },
        'ADMINS': (
            ('Dev', settings.get('DEV_EMAIL', '')),
        ),
        'MANAGERS': (
            ('Dev', settings.get('DEV_EMAIL', '')),
        ),
        'LOCALE_PATHS': [
            os.path.join(base_dir, 'locale')
        ],
        'MIDDLEWARE': [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.locale.LocaleMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'pipeline.middleware.MinifyHTMLMiddleware'
        ],
        'TEMPLATES': [{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(base_dir, 'templates')
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ]
            }
        }],
        'CONTEXT_PROCESSORS': [
            'django.template.context_processors.i18n',
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages'
        ],
        'AUTH_PASSWORD_VALIDATORS': [
            {
                'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
            },
            {
                'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            },
            {
                'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
            },
            {
                'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
            },
        ]
    }

    extra_apps = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.sites',
        'django.contrib.sitemaps',
    ]

    installed_apps = settings['INSTALLED_APPS']

    for app in extra_apps:
        if app not in installed_apps:
            installed_apps.append(app)

    # CRISPY_TEMPLATE_PACK = 'bootstrap3'
    # CKEDITOR_UPLOAD_PATH = 'uploads/'
    # NOCAPTCHA = True
    # RECAPTCHA_PUBLIC_KEY = '6LdHaPsSAAAAAPinOxMD64UtSQtD1J37vp9qjsZw'
    # RECAPTCHA_PRIVATE_KEY = '6LdHaPsSAAAAAJRHOT4Edilnp-1xSOqttWNk5dar'
    # THUMBNAIL_QUALITY = 85

    if is_prod:

        domain = settings.get('DOMAIN', '')

        default_settings.update({
            'DEBUG': False,

            'EMAIL_PORT': 587,
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'smtp.gmail.com',

            'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
            'SECURE_SSL_REDIRECT': True,
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,

            'EMAIL_SUBJECT_PREFIX': '{} |'.format(domain.title()),
            'DEFAULT_FROM_EMAIL': (
                '{} <noreply@{}>'.format(domain.upper(), domain))
        })
    else:
        default_settings.update({
            'DEBUG': True,
            'EMAIL_BACKEND': 'basement.email.FileBasedEmailBackend',
            'CACHES': {
                'default': {
                    'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
                }
            },
            'EMAIL_FILE_PATH': os.path.join(base_dir, 'tmp')
        })

    for key, val in default_settings.items():
        if key not in settings:
            settings[key] = val

    for app in settings.get('INSTALLED_APPS', []):

        try:
            mod = importlib.import_module(app)

            if hasattr(mod, 'setup_settings'):
                mod.setup_settings(settings, is_prod=False, **kwargs)
        except Exception:
            pass


def setup_urlpatterns(
        urlpatterns,
        home_view=None,
        is_i18n_redirect_enabled=True,
        exclude_apps=[]):

    if home_view is None:
        home_view = TemplateView.as_view(template_name='home.html')

    urlpatterns += [
        path('raise-exception/', lambda request: 1/0)
    ]

    if is_i18n_redirect_enabled:
        urlpatterns += [
            path('', RedirectView.as_view(
                url='/{}/'.format(settings.LANGUAGE_CODE))
            )
        ]

    urlpatterns += i18n_patterns(
        path('', home_view, name='home')
    )

    for app in settings.INSTALLED_APPS:

        if app in exclude_apps:
            continue

        located_urls = locate('{}.urls.app_urls'.format(app))

        if not located_urls:
            continue

        urlpatterns += located_urls
