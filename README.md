# 📋 SGT — Sistema de Gerenciamento de Tarefas
### TechFlow Solutions · Engenharia de Software · UniFECAF

---

## 🎯 Objetivo

Sistema web de gerenciamento de tarefas desenvolvido para uma startup de logística.
Permite criar, visualizar, editar e excluir tarefas com controle de prioridade e status em tempo real.

## 📦 Escopo Inicial

- Autenticação de usuários (login/logout com JWT)
- CRUD completo de tarefas
- Prioridade: Alta, Média, Baixa
- Status: A Fazer → Em Progresso → Concluído
- API REST documentada

## 🔄 Mudança de Escopo — Sprint 3

**Feature adicionada:** Módulo de Notificações por E-mail

**Justificativa:** O cliente identificou que atrasos nas entregas eram causados pela falta de
alertas automáticos. A funcionalidade envia e-mails quando o prazo de uma tarefa se
aproxima (48h) ou quando seu status é alterado por outro membro da equipe.

**Adaptações realizadas:**
- Novo card criado no Kanban: "Implementar módulo de notificações por e-mail"
- Classe `NotificacaoService` adicionada em `src/services/`
- Testes unitários com mock SMTP adicionados em `tests/`
- Commit: `feat(notificacao): adiciona envio de e-mail por prazo e mudança de status`

## 🛠️ Metodologia

Abordagem híbrida **Scrumban** (Scrum + Kanban):
- Sprints semanais com backlog priorizado
- Quadro Kanban no GitHub Projects (A Fazer | Em Progresso | Concluído)
- WIP limit: máximo 3 cards em progresso
- Commits semânticos seguindo Conventional Commits

## 🚀 Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sgt-techflow.git
cd sgt-techflow

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python src/app.py

# 5. Acesse no navegador: http://localhost:5000
```

## 🧪 Executar Testes

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

## 📁 Estrutura de Diretórios

```
sgt-techflow/
├── src/
│   ├── app.py                    # Ponto de entrada Flask
│   ├── models/
│   │   ├── tarefa.py             # Modelo Tarefa com validações
│   │   └── usuario.py            # Modelo Usuário com autenticação
│   ├── routes/
│   │   ├── tarefas.py            # Endpoints CRUD de tarefas
│   │   └── auth.py               # Endpoints de autenticação
│   └── services/
│       └── notificacao.py        # Serviço de notificações por e-mail
├── tests/
│   ├── test_tarefa.py            # Testes unitários — Tarefa
│   ├── test_auth.py              # Testes de autenticação
│   ├── test_api.py               # Testes de integração da API
│   └── test_notificacao.py       # Testes do serviço de notificação
├── docs/
│   └── api.md                    # Documentação dos endpoints
├── .github/workflows/ci.yml      # Pipeline GitHub Actions
├── requirements.txt
└── README.md
```

## 📚 Referências

- Pressman, R. S. *Engenharia de Software: Uma Abordagem Profissional*. 8. ed. AMGH, 2016.
- GitHub Docs — Actions: https://docs.github.com/en/actions
