import click
import os
import shutil
from pathlib import Path
import platform

@click.command()
@click.option('--name', prompt='Project name', help='Name of the Flask project')
@click.option('--database', type=click.Choice(['sqlite', 'postgresql', 'mysql', 'none']), default='none', prompt=True, help='Database to use')
@click.option('--auth/--no-auth', default=False, prompt=True, help='Include authentication system')
@click.option('--api/--no-api', default=False, prompt=True, help='Include REST API setup')
def create_flask_app(name, database, auth, api):
    project_dir = Path(name)
    os_name = platform.system()

    if project_dir.exists():
        if not click.confirm(f'Directory {name} already exists. Overwrite?'):
            return
        shutil.rmtree(project_dir)
    
    project_dir.mkdir()

    create_directory_structure(project_dir)
    create_basic_files(project_dir, name, database, auth, api)
    create_requirements(project_dir, database, auth, api)
    
    click.echo(f"\nFlask project '{name}' created successfully!")
    click.echo("\nTo get started:")
    click.echo(f"  cd {name}")
    click.echo("  python -m venv venv")
    if os_name == "Windows":
        click.echo("  venv\\Scripts\\activate")
    else:
        click.echo("  source venv/bin/activate")
    click.echo("  pip install -r requirements.txt")
    click.echo("  flask run")

def create_directory_structure(project_dir):
    directories = [
        'app',
        'app/templates',
        'app/static',
        'app/static/css',
        'app/static/js',
        'app/models',
        'app/views',
        'tests',
    ]
    
    for directory in directories:
        Path(project_dir / directory).mkdir(parents=True)

def create_basic_files(project_dir, name, database, auth, api):

    init_content = generate_init_file(database, auth, api)
    with open(project_dir / 'app' / '__init__.py', 'w') as f:
        f.write(init_content)

    config_content = generate_config_file(name, database)
    with open(project_dir / 'config.py', 'w') as f:
        f.write(config_content)

    run_content = """from app import app

if __name__ == '__main__':
    app.run(debug=True)
"""
    with open(project_dir / 'run.py', 'w') as f:
        f.write(run_content)

    gitignore_content = """venv/
*.pyc
__pycache__/
.env
instance/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
"""
    with open(project_dir / '.gitignore', 'w') as f:
        f.write(gitignore_content)

def generate_init_file(database, auth, api):
    content = """from flask import Flask
from config import Config
"""
    
    if database != 'none':
        content += "from flask_sqlalchemy import SQLAlchemy\n"
        content += "from flask_migrate import Migrate\n\n"
        content += "db = SQLAlchemy()\n"
        content += "migrate = Migrate()\n"
    
    if auth:
        content += "from flask_login import LoginManager\n"
        content += "login_manager = LoginManager()\n"
    
    content += "\napp = Flask(__name__)\n"
    content += "app.config.from_object(Config)\n\n"
    
    if database != 'none':
        content += "db.init_app(app)\n"
        content += "migrate.init_app(app, db)\n"
    
    if auth:
        content += "login_manager.init_app(app)\n"
        content += "login_manager.login_view = 'auth.login'\n"
    
    content += "\nfrom app import views\n"
    
    return content

def generate_config_file(name, database):
    content = """import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
"""
    
    if database != 'none':
        if database == 'sqlite':
            content += f"    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \\\n"
            content += f"        'sqlite:///' + str(Path(__file__).parent / 'app.db')\n"
        else:
            content += f"    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')\n"
        content += "    SQLALCHEMY_TRACK_MODIFICATIONS = False\n"
    
    return content

def create_requirements(project_dir, database, auth, api):
    requirements = [
        "flask",
        "python-dotenv",
        "click",
    ]
    
    if database != 'none':
        requirements.extend([
            "flask-sqlalchemy",
            "flask-migrate",
        ])
        if database == 'postgresql':
            requirements.append("psycopg2-binary")
        elif database == 'mysql':
            requirements.append("mysqlclient")
    
    if auth:
        requirements.append("flask-login")
    
    if api:
        requirements.append("flask-restful")
    
    with open(project_dir / 'requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))

if __name__ == '__main__':
    create_flask_app()