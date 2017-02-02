from fabric.api import sudo, cd, prefix, run, settings

def deploy_app():
    "Deploy to the server specified"
    root_path = '/usr/local/my_env'

    with cd(root_path):
        with prefix("source %s/bin/activate" % root_path):
            with cd('flask_catalog_deployment'):
                run('git pull')
                run('python setup.py install')

            sudo('bin/supervisorctl restart all')

def deploy_app_to_server():
    "Deploy to the server hardcoded"
    with settings(host_string='my.remote.server'):
        deploy_app()

