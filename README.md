# lunn
Lunn é uma aplicação web de organização acadêmica desenvolvida com Python e Django. O projeto busca ajudar estudantes a gerenciar tarefas, anotações, calendário e produtividade em um só lugar, com recursos personalizados para cada usuário e foco em uma experiência de estudo organizada e intuitiva.

Funcionalidades

Cadastro e login: acesso individual para cada usuário.

Gerenciamento de tarefas: organização das atividades acadêmicas.

Calendário: planejamento de compromissos e acompanhamento de prazos.

Anotações e matérias: espaço para registrar e organizar conteúdos de estudo.

Dashboard: visão geral da organização acadêmica.

LunnIA: espaço planejado para integrar recursos de inteligência artificial.

Pomodoro: área dedicada à gestão do tempo e à concentração.

O projeto está em desenvolvimento, e novas funcionalidades estão sendo implementadas gradualmente.

Tecnologias

Python — lógica e desenvolvimento do backend.

Django — framework web e gerenciamento da aplicação.

HTML5 — estrutura das páginas.

CSS3 — identidade visual e estilização.

JavaScript — interatividade no frontend.

SQLite — banco de dados utilizado no desenvolvimento.

Identidade visual

O Lunn possui uma identidade inspirada no céu noturno, com tons de roxo, lilás e branco. A proposta visual busca transmitir tranquilidade, organização e foco.

Objetivos do projeto

Aplicar conhecimentos de desenvolvimento web na prática.

Aprender e aprofundar o uso do Django e de bancos de dados.

Implementar autenticação e separação de dados por usuário.

Desenvolver uma interface intuitiva e responsiva.

Explorar possibilidades de integração com inteligência artificial.

Executando o projeto localmente

1. Clone o repositório

git clone https://github.com/leticiacampelo137-code/lunn.git
cd lunn

2. Crie um ambiente virtual

python -m venv .venv

3. Ative o ambiente virtual

No Windows, usando PowerShell:

.\.venv\Scripts\Activate.ps1

4. Instale as dependências

pip install -r requirements.txt

5. Configure as variáveis de ambiente

Crie um arquivo .env na raiz do projeto e configure a variável DJANGO_SECRET_KEY com uma chave secreta própria para o ambiente local.

Importante: não publique o arquivo .env no GitHub.

6. Execute as migrações

python manage.py migrate

7. Inicie o servidor

python manage.py runserver

Acesse http://127.0.0.1:8000/ no navegador.

Aprendizados

O desenvolvimento do Lunn faz parte da minha jornada de aprendizado em programação e desenvolvimento web. Por meio dele, busco transformar conhecimentos teóricos em funcionalidades reais, aprimorando minhas habilidades em Python, Django, organização de dados e construção de interfaces.
