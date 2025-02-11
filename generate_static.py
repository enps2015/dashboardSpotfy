import os
import shutil
from app import app

def generate_static_site():
    # Criar diretório docs (GitHub Pages usa este diretório por padrão)
    if os.path.exists('docs'):
        shutil.rmtree('docs')
    os.makedirs('docs')

    # Copiar arquivos estáticos
    shutil.copytree('static', 'docs/static')
    
    # Copiar o arquivo index.html para docs
    shutil.copy('templates/index.html', 'docs/index.html')

if __name__ == '__main__':
    generate_static_site()
    print("Site estático gerado com sucesso na pasta 'docs'!")