# 📖 Documentação da API — SGT

Base URL: `http://localhost:5000`

---

## Tarefas

### `GET /tarefas`
Lista todas as tarefas. Aceita filtro `?status=A_FAZER|EM_PROGRESSO|CONCLUIDO`.

**Resposta 200:**
```json
[
  {
    "id": 1,
    "titulo": "Revisar relatório",
    "descricao": "",
    "prioridade": "ALTA",
    "status": "A_FAZER",
    "prazo": "30/06/2026",
    "usuario_email": "dev@techflow.com",
    "criado_em": "03/04/2026 10:00"
  }
]
```

---

### `GET /tarefas/<id>`
Retorna uma tarefa específica.

| Código | Descrição |
|--------|-----------|
| 200    | Tarefa encontrada |
| 404    | Tarefa não encontrada |

---

### `POST /tarefas`
Cria uma nova tarefa.

**Corpo:**
```json
{
  "titulo": "Nome da tarefa",       // obrigatório
  "prioridade": "ALTA",            // opcional — ALTA, MEDIA, BAIXA (padrão: MEDIA)
  "descricao": "Detalhes...",      // opcional
  "prazo": "DD/MM/AAAA",          // opcional
  "usuario_email": "user@mail.com" // opcional
}
```

| Código | Descrição |
|--------|-----------|
| 201    | Tarefa criada com sucesso |
| 400    | Dados inválidos |

---

### `PUT /tarefas/<id>`
Atualiza campos de uma tarefa. Apenas os campos enviados serão modificados.

**Corpo (exemplo):**
```json
{
  "status": "EM_PROGRESSO",
  "titulo": "Novo título"
}
```

| Código | Descrição |
|--------|-----------|
| 200    | Atualizado com sucesso |
| 400    | Dados inválidos |
| 404    | Tarefa não encontrada |

---

### `DELETE /tarefas/<id>`
Remove uma tarefa permanentemente.

| Código | Descrição |
|--------|-----------|
| 200    | Removida com sucesso |
| 404    | Tarefa não encontrada |

---

## Autenticação

### `POST /auth/registro`
Cadastra um novo usuário.

**Corpo:**
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "minhasenha",
  "perfil": "USUARIO"
}
```

---

### `POST /auth/login`
Autentica um usuário e retorna token de acesso.

**Corpo:**
```json
{
  "email": "joao@email.com",
  "senha": "minhasenha"
}
```

**Resposta 200:**
```json
{
  "mensagem": "Login realizado com sucesso.",
  "usuario": { "nome": "João Silva", "email": "joao@email.com", "perfil": "USUARIO" },
  "token": "jwt-simulado-joao@email.com"
}
```
