# API de Usuários e Endereços

API RESTful construída com FastAPI, SQLAlchemy e PostgreSQL.

## Melhorias Implementadas

✅ **Schemas com Validação**: Uso de Pydantic com validações robustas (EmailStr, min_length, max_length)  
✅ **CRUD Completo**: Criar, ler, atualizar e deletar usuários e endereços  
✅ **Paginação**: Listar usuários com skip/limit  
✅ **Tratamento de Erros**: HTTPException com status codes apropriados  
✅ **Timestamps**: Data de criação em todas as tabelas  
✅ **Relacionamentos**: Cascade delete para manter integridade  
✅ **Documentação Automática**: Swagger UI em `/docs`  
✅ **Variáveis de Ambiente**: Configuração segura via `.env`  
✅ **Type Hints**: Tipagem completa do código  
✅ **Status Codes Corretos**: 201 para criação, 204 para deleção  

## Instalação

### 1. Pré-requisitos
- Python 3.8+
- PostgreSQL instalado e rodando

### 2. Clonar/Criar o Projeto
```bash
cd seu_projeto
```

### 3. Criar Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar Banco de Dados
Copie `.env.example` para `.env` e atualize:
```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:
```
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/seu_banco
```

### 6. Executar
```bash
uvicorn app:app --reload
```

A API estará disponível em `http://localhost:8000`

## Endpoints

### Usuários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/usuarios` | Criar novo usuário |
| GET | `/usuarios` | Listar usuários (com paginação) |
| GET | `/usuarios/{usuario_id}` | Obter usuário com endereços |
| PUT | `/usuarios/{usuario_id}` | Atualizar usuário |
| DELETE | `/usuarios/{usuario_id}` | Deletar usuário |

### Endereços

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/usuarios/{usuario_id}/enderecos` | Criar endereço |
| GET | `/usuarios/{usuario_id}/enderecos` | Listar endereços do usuário |
| PUT | `/enderecos/{endereco_id}` | Atualizar endereço |
| DELETE | `/enderecos/{endereco_id}` | Deletar endereço |

## Exemplos de Uso

### Criar Usuário
```bash
curl -X POST "http://localhost:8000/usuarios" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com"
  }'
```

### Criar Endereço
```bash
curl -X POST "http://localhost:8000/usuarios/1/enderecos" \
  -H "Content-Type: application/json" \
  -d '{
    "rua": "Rua das Flores, 123",
    "cidade": "São Paulo",
    "cep": "01234-567"
  }'
```

### Obter Usuário com Endereços
```bash
curl "http://localhost:8000/usuarios/1"
```

## Documentação Interativa

Acesse em seu navegador:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Estrutura do Banco

### Tabela: usuarios
- `id` (PK): Integer
- `nome`: String(255)
- `email`: String(255) - Único
- `criado_em`: DateTime

### Tabela: enderecos
- `id` (PK): Integer
- `rua`: String(255)
- `cidade`: String(100)
- `cep`: String(10)
- `usuario_id` (FK): Integer
- `criado_em`: DateTime

## Recursos

- ✅ Validação de email (Pydantic EmailStr)
- ✅ Prevenção de emails duplicados
- ✅ Cascade delete (deleta endereços ao deletar usuário)
- ✅ Índices em campos chave
- ✅ Status codes HTTP apropriados
- ✅ Mensagens de erro descritivas
