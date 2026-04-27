# MLSync — Integração Mercado Livre × Sankhya ERP

Plataforma SaaS para automatizar a gestão de vendedores do Mercado Livre com integração nativa ao Sankhya ERP e IA embarcada.

---

## Arquitetura

```
Mercado Livre APIs  →  MLSync Backend (FastAPI)  →  Sankhya ERP
                              ↓
                    Redis (cache + filas)
                              ↓
                    Dashboard (Next.js / React)
```

---

## Pré-requisitos

- Python 3.11+
- Docker + Docker Compose
- Conta de desenvolvedor no Mercado Livre: https://developers.mercadolivre.com.br

---

## Setup rápido

### 1. Clone e configure variáveis

```bash
git clone <repo>
cd mlsync
cp .env.example .env
```

Edite `.env`:
```env
ML_CLIENT_ID=seu_app_id_aqui
ML_CLIENT_SECRET=seu_client_secret_aqui
ML_REDIRECT_URI=http://localhost:8000/auth/callback
JWT_SECRET=string-aleatoria-forte-minimo-32-chars
REDIS_URL=redis://redis:6379
```

### 2. Crie o App no Mercado Livre

1. Acesse https://developers.mercadolivre.com.br/devcenter
2. Clique em "Criar aplicação"
3. Preencha nome, descrição e **Redirect URI**: `http://localhost:8000/auth/callback`
4. Copie o **App ID** (Client ID) e o **Client Secret** para o `.env`
5. Habilite os scopes: `read`, `write`, `offline_access`

### 3. Inicie com Docker

```bash
docker-compose up -d
```

Serviços disponíveis:
- **Backend API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

### 4. Instale dependências Python (desenvolvimento local)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Fluxo de autenticação OAuth 2.0

```
Usuário clica "Conectar ML"
        ↓
GET /auth/login
        ↓ redireciona para
https://auth.mercadolivre.com.br/authorization?...
        ↓ usuário autoriza
GET /auth/callback?code=XXXX
        ↓
Troca code → access_token + refresh_token (salvo no Redis)
        ↓
Gera JWT MLSync (válido 8h)
        ↓
Frontend armazena JWT e usa em todas as chamadas
```

O token ML é **renovado automaticamente** antes de expirar.

---

## Endpoints principais

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/auth/login` | Inicia OAuth ML |
| GET | `/auth/callback` | Callback OAuth |
| GET | `/auth/status` | Status da conexão |
| POST | `/auth/disconnect` | Desconecta conta |
| GET | `/company/info` | Dados da conta ML |
| GET | `/company/health` | Reputação do vendedor |
| GET | `/orders` | Lista pedidos |
| GET | `/orders/{id}` | Detalhe de pedido |
| GET | `/financial/summary` | Resumo financeiro |
| GET | `/financial/movements` | Extrato ML |
| GET | `/listings` | Anúncios ativos |
| GET | `/dashboard/metrics` | Métricas consolidadas |
| POST | `/webhooks/mercadolivre` | Webhook ML |
| GET | `/health` | Health check |

---

## Segurança implementada

- **OAuth 2.0** com PKCE para autorização ML
- **JWT** assinado (HS256) com expiração configurável
- **Refresh automático** de tokens ML
- **HMAC SHA-256** para validação de webhooks
- **Redis** com TTL para armazenamento seguro de tokens
- **Rate limiting** via middleware (próxima versão)
- **CORS** configurado por ambiente
- **Criptografia AES-256** para dados sensíveis (próxima versão)
- **Audit log** de todas as operações (próxima versão)

---

## Cache (Redis)

| Chave | TTL | Conteúdo |
|-------|-----|----------|
| `ml_tokens:{user_id}` | 30 dias | Tokens OAuth ML |
| `company_info:{user_id}` | 10 min | Dados da conta |
| `dashboard:{user_id}:{days}` | 3 min | Métricas |
| `fin_summary:{user_id}:{days}` | 5 min | Resumo financeiro |

Webhooks invalidam cache automaticamente.

---

## Próximos módulos

### Módulo 2 — Integração Sankhya ERP
- Mapeamento de pedidos ML → Pedidos de venda Sankhya
- Emissão automática de NF-e
- Lançamentos financeiros automáticos
- Conciliação de contas a receber

### Módulo 3 — Motor de IA (Claude API)
- Insights automáticos de performance
- Detecção de anomalias em pedidos e pagamentos
- Sugestões de reprecificação
- Previsão de demanda por SKU
- Alertas inteligentes

### Módulo 4 — Dashboard SaaS Multi-tenant
- Gestão de múltiplas contas ML
- Relatórios exportáveis (PDF, Excel)
- Alertas por e-mail e WhatsApp
- White-label para revendas

---

## Monetização sugerida

| Plano | Faturamento ML/mês | Preço/mês |
|-------|-------------------|-----------|
| Starter | até R$ 50k | R$ 397 |
| Growth | até R$ 200k | R$ 797 |
| Enterprise | acima R$ 200k | R$ 1.497 + setup |
| White-label | qualquer | royalty 30% |

---

## Estrutura do projeto

```
mlsync/
├── backend/
│   ├── main.py           # API FastAPI completa
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html        # Dashboard HTML/JS
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Licença

Proprietário — uso comercial mediante licença.
