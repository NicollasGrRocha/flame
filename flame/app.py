# API em Python usando FastAPI + SQLAlchemy + PostgreSQL
# Exemplo completo com boas práticas

# Para rodar:
# 1. Instale dependências: pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
# 2. Configure o banco PostgreSQL e ajuste a URL em DATABASE_URL
# 3. Execute: uvicorn app:app --reload

from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from datetime import datetime
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
# Se for usar MySQL, defina a variável `DATABASE_URL` no formato:
#   mysql+pymysql://usuario:senha@host:porta/nome_do_banco
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://usuario:senha@localhost:3306/nome_do_banco"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELS (SQLAlchemy) ====================

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    enderecos = relationship("Endereco", back_populates="usuario", cascade="all, delete-orphan")

class Endereco(Base):
    __tablename__ = "enderecos"
    
    id = Column(Integer, primary_key=True, index=True)
    rua = Column(String(255), nullable=False)
    cidade = Column(String(100), nullable=False)
    cep = Column(String(10), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", back_populates="enderecos")

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

# ==================== SCHEMAS (Pydantic) ====================

class EnderecoBase(BaseModel):
    rua: str = Field(..., min_length=1, max_length=255)
    cidade: str = Field(..., min_length=1, max_length=100)
    cep: Optional[str] = Field(None, max_length=10)

class EnderecoCreate(EnderecoBase):
    usuario_id: int

class EnderecoResponse(EnderecoBase):
    id: int
    usuario_id: int
    criado_em: datetime
    
    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioResponse(UsuarioBase):
    id: int
    criado_em: datetime
    
    class Config:
        from_attributes = True

class UsuarioComEnderecos(UsuarioResponse):
    enderecos: List[EnderecoResponse] = []

# ==================== DEPENDÊNCIAS ====================

def get_db():
    """Dependência para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== INICIALIZAR APP ====================

app = FastAPI(
    title="API de Usuários e Endereços",
    description="API exemplo com FastAPI, SQLAlchemy e PostgreSQL",
    version="1.0.0"
)

# ==================== ROTAS - USUÁRIOS ====================

@app.post("/usuarios", response_model=UsuarioResponse, status_code=201)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Criar um novo usuário"""
    # Validar se email já existe
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    novo_usuario = Usuario(nome=usuario.nome, email=usuario.email)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@app.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Listar todos os usuários com paginação"""
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=UsuarioComEnderecos)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obter um usuário específico com seus endereços"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Atualizar dados de um usuário"""
    usuario_db = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se novo email já existe (excluindo o próprio usuário)
    email_existente = db.query(Usuario).filter(
        Usuario.email == usuario.email,
        Usuario.id != usuario_id
    ).first()
    if email_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    usuario_db.nome = usuario.nome
    usuario_db.email = usuario.email
    db.commit()
    db.refresh(usuario_db)
    return usuario_db

@app.delete("/usuarios/{usuario_id}", status_code=204)
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Deletar um usuário e seus endereços"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(usuario)
    db.commit()

# ==================== ROTAS - ENDEREÇOS ====================

@app.post("/usuarios/{usuario_id}/enderecos", response_model=EnderecoResponse, status_code=201)
def criar_endereco(usuario_id: int, endereco: EnderecoBase, db: Session = Depends(get_db)):
    """Criar um novo endereço para um usuário"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    novo_endereco = Endereco(
        rua=endereco.rua,
        cidade=endereco.cidade,
        cep=endereco.cep,
        usuario_id=usuario_id
    )
    db.add(novo_endereco)
    db.commit()
    db.refresh(novo_endereco)
    return novo_endereco

@app.get("/usuarios/{usuario_id}/enderecos", response_model=List[EnderecoResponse])
def obter_enderecos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obter todos os endereços de um usuário"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario.enderecos

@app.put("/enderecos/{endereco_id}", response_model=EnderecoResponse)
def atualizar_endereco(endereco_id: int, endereco: EnderecoBase, db: Session = Depends(get_db)):
    """Atualizar um endereço"""
    endereco_db = db.query(Endereco).filter(Endereco.id == endereco_id).first()
    if not endereco_db:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")
    
    endereco_db.rua = endereco.rua
    endereco_db.cidade = endereco.cidade
    endereco_db.cep = endereco.cep
    db.commit()
    db.refresh(endereco_db)
    return endereco_db

@app.delete("/enderecos/{endereco_id}", status_code=204)
def deletar_endereco(endereco_id: int, db: Session = Depends(get_db)):
    """Deletar um endereço"""
    endereco = db.query(Endereco).filter(Endereco.id == endereco_id).first()
    if not endereco:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")
    
    db.delete(endereco)
    db.commit()

# ==================== ROTA RAIZ ====================

@app.get("/", tags=["Root"])
def read_root():
    """Rota raiz da API"""
    return {
        "mensagem": "Bem-vindo à API de Usuários",
        "documentacao": "/docs",
        "docs_alternativa": "/redoc"
    }
