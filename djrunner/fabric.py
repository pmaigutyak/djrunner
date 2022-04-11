
from fabric.api import env, run, sudo, cd, prefix
from contextlib import contextmanager


@contextmanager
def source(domain):
    with prefix('source ~/sites/{}/env/bin/activate'.format(domain)):
        yield


def pull(domain, project_name):
    with goto(domain, project_name):
        run('git pull origin master')


def goto(domain, project_name):
    return cd('~/sites/{}/{}/'.format(domain, project_name))


def deploy(domain, project_name, has_celery=False):

    pull(domain, project_name)

    with goto(domain, project_name):

        with source(domain):
            run('pip install -r ./requirements.txt')
            run('python manage.py migrate')
            run('python manage.py collectstatic --noinput')
            run('python manage.py sync_translation_fields --noinput')

    restart(domain, project_name, has_celery)


def restart(domain, project_name, has_celery=False):

    pull(domain, project_name)

    sudo('sudo supervisorctl restart {}'.format(project_name))

    if has_celery:
        sudo('sudo supervisorctl restart {}_celery'.format(project_name))
        sudo('sudo supervisorctl restart {}_celery_beat'.format(project_name))
