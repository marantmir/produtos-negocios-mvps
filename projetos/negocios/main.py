"""
MLSync Backend - Integração Mercado Livre + Sankhya ERP
FastAPI + OAuth 2.0 + coleta estruturada de dados
"""

import os
import time
import hmac
import hashlib
import logging
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis.asyncio as aioredis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Configurações ────────────────────────────────────────────────────────────

ML_CLIENT_ID     = os.getenv("ML_CLIENT_ID", "SEU_APP_ID_AQUI")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET", "SEU_SECRET_AQUI")
ML_REDIRECT_URI  = os.getenv("ML_REDIRECT_URI", "http://localhost:8000/auth/callback")
ML_BASE_URL      = "https://api.mercadolibre.com"
ML_AUTH_URL      = "https://auth.mercadolivre.com.br"

JWT_SECRET       = os.getenv("JWT_SECRET", "TROQUE-POR-SECRET-FORTE-EM-PRODUCAO")
JWT_ALGORITHM    = "HS256"
JWT_EXPIRE_HOURS = 8

REDIS_URL        = os.getenv("REDIS_URL", "redis://localhost:6379")

# ─── Modelos Pydantic ─────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class CompanyInfo(BaseModel):
    id: int
    nickname: str
    email: str
    site_id: str
    country_id: str
    registration_date: str

class MLTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: float
    user_id: int
    scope: str

class OrderSummary(BaseModel):
    id: int
    status: str
    date_created: str
    date_closed: Optional[str]
    total_amount: float
    currency_id: str
    buyer_nickname: str
    items: List[Dict[str, Any]]
    payments: List[Dict[str, Any]]
    shipping: Optional[Dict[str, Any]]

class DashboardMetrics(BaseModel):
    period: str
    total_revenue: float
    total_orders: int
    avg_ticket: float
    pending_orders: int
    cancelled_orders: int
    completed_orders: int
    top_products: List[Dict[str, Any]]
    revenue_by_day: List[Dict[str, Any]]
    health_score: Optional[Dict[str, Any]]

class WebhookPayload(BaseModel):
    resource: str
    user_id: int
    topic: str
    application_id: int
    attempts: int
    sent: str
    received: str

# ─── Lifespan / startup ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await aioredis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    logger.info("✅ Redis conectado")
    yield
    await app.state.redis.aclose()
    logger.info("Redis desconectado")

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="MLSync API",
    description="Plataforma de integração Mercado Livre ↔ Sankhya ERP com IA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Em prod: domínio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security  = HTTPBearer()
pwd_ctx   = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── Helpers JWT ──────────────────────────────────────────────────────────────

def create_jwt(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
) -> dict:
    return decode_jwt(creds.credentials)

# ─── Helpers Redis ────────────────────────────────────────────────────────────

async def save_ml_tokens(redis, user_id: int, tokens: dict):
    key = f"ml_tokens:{user_id}"
    await redis.hset(key, mapping={
        "access_token":  tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at":    str(tokens.get("expires_in", 21600) + time.time()),
        "ml_user_id":    str(tokens.get("user_id", user_id)),
        "scope":         tokens.get("scope", ""),
    })
    await redis.expire(key, 86400 * 30)

async def get_ml_tokens(redis, user_id: int) -> Optional[dict]:
    key = f"ml_tokens:{user_id}"
    data = await redis.hgetall(key)
    return data if data else None

async def cache_set(redis, key: str, value: str, ttl: int = 300):
    await redis.setex(key, ttl, value)

async def cache_get(redis, key: str) -> Optional[str]:
    return await redis.get(key)

# ─── Mercado Livre Client ─────────────────────────────────────────────────────

class MLClient:
    """Client HTTP para a API do Mercado Livre com refresh automático de token."""

    def __init__(self, access_token: str, redis=None, user_id: int = None):
        self.access_token = access_token
        self.redis        = redis
        self.user_id      = user_id
        self.headers      = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
            "X-Format-New":  "true",
        }

    async def get(self, path: str, params: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{ML_BASE_URL}{path}",
                headers=self.headers,
                params=params or {},
            )
            if resp.status_code == 401 and self.redis and self.user_id:
                await self._refresh_token()
                resp = await client.get(
                    f"{ML_BASE_URL}{path}",
                    headers=self.headers,
                    params=params or {},
                )
            resp.raise_for_status()
            return resp.json()

    async def _refresh_token(self):
        tokens = await get_ml_tokens(self.redis, self.user_id)
        if not tokens:
            raise HTTPException(status_code=401, detail="Reconecte sua conta ML")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{ML_AUTH_URL}/jms/oauth/token",
                data={
                    "grant_type":    "refresh_token",
                    "client_id":     ML_CLIENT_ID,
                    "client_secret": ML_CLIENT_SECRET,
                    "refresh_token": tokens["refresh_token"],
                },
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Falha ao renovar token ML")
            new_tokens = resp.json()
            await save_ml_tokens(self.redis, self.user_id, new_tokens)
            self.access_token  = new_tokens["access_token"]
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            logger.info(f"Token ML renovado para user {self.user_id}")

async def get_ml_client(user: dict = Depends(get_current_user), request: Request = None) -> MLClient:
    tokens = await get_ml_tokens(request.app.state.redis, user["sub"])
    if not tokens:
        raise HTTPException(
            status_code=400,
            detail="Conta do Mercado Livre não conectada. Acesse /auth/login"
        )
    if float(tokens["expires_at"]) < time.time() + 60:
        # Força refresh proativo 60s antes de expirar
        client = MLClient(tokens["access_token"], request.app.state.redis, user["sub"])
        await client._refresh_token()
        tokens = await get_ml_tokens(request.app.state.redis, user["sub"])
    return MLClient(tokens["access_token"], request.app.state.redis, user["sub"])

# ─── ROTAS: Autenticação OAuth ────────────────────────────────────────────────

@app.get("/auth/login", summary="Inicia fluxo OAuth com ML", tags=["Auth"])
async def auth_login(state: Optional[str] = None):
    """
    Redireciona para a tela de autorização do Mercado Livre.
    O parâmetro `state` pode carregar o ID interno do usuário MLSync.
    """
    params = {
        "response_type": "code",
        "client_id":     ML_CLIENT_ID,
        "redirect_uri":  ML_REDIRECT_URI,
        "state":         state or "mlsync",
    }
    url = (
        f"{ML_AUTH_URL}/authorization"
        f"?response_type={params['response_type']}"
        f"&client_id={params['client_id']}"
        f"&redirect_uri={params['redirect_uri']}"
        f"&state={params['state']}"
    )
    return RedirectResponse(url)


@app.get("/auth/callback", summary="Callback OAuth ML → troca code por token", tags=["Auth"])
async def auth_callback(code: str, state: str = "mlsync", request: Request = None):
    """
    Mercado Livre redireciona aqui após autorização do usuário.
    Troca o authorization code por access_token + refresh_token.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ML_AUTH_URL}/jms/oauth/token",
            data={
                "grant_type":    "authorization_code",
                "client_id":     ML_CLIENT_ID,
                "client_secret": ML_CLIENT_SECRET,
                "code":          code,
                "redirect_uri":  ML_REDIRECT_URI,
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Falha OAuth ML: {resp.text}")

    ml_tokens = resp.json()
    ml_user_id = ml_tokens.get("user_id")

    # Salva tokens no Redis
    await save_ml_tokens(request.app.state.redis, ml_user_id, ml_tokens)

    # Gera JWT MLSync para o usuário
    jwt_token = create_jwt({
        "sub":       ml_user_id,
        "ml_uid":    ml_user_id,
        "connected": True,
    })

    logger.info(f"Usuário ML {ml_user_id} autenticado com sucesso")

    # Em produção: redirecionar para o frontend com o token
    return {
        "message":    "✅ Conta Mercado Livre conectada com sucesso!",
        "jwt_token":  jwt_token,
        "ml_user_id": ml_user_id,
        "expires_in": JWT_EXPIRE_HOURS * 3600,
        "scope":      ml_tokens.get("scope", ""),
    }


@app.post("/auth/disconnect", summary="Desconecta conta ML", tags=["Auth"])
async def auth_disconnect(
    user: dict = Depends(get_current_user),
    request: Request = None,
):
    await request.app.state.redis.delete(f"ml_tokens:{user['sub']}")
    return {"message": "Conta desconectada com sucesso"}


@app.get("/auth/status", summary="Status da conexão ML", tags=["Auth"])
async def auth_status(
    user: dict = Depends(get_current_user),
    request: Request = None,
):
    tokens = await get_ml_tokens(request.app.state.redis, user["sub"])
    if not tokens:
        return {"connected": False}
    expires_at = float(tokens.get("expires_at", 0))
    return {
        "connected":   True,
        "ml_user_id":  tokens.get("ml_user_id"),
        "expires_at":  datetime.fromtimestamp(expires_at).isoformat(),
        "token_valid": expires_at > time.time(),
        "scope":       tokens.get("scope", ""),
    }

# ─── ROTAS: Dados da empresa ──────────────────────────────────────────────────

@app.get("/company/info", response_model=CompanyInfo, tags=["Empresa"])
async def get_company_info(
    ml: MLClient = Depends(get_ml_client),
    request: Request = None,
    user: dict = Depends(get_current_user),
):
    """Dados cadastrais da conta ML: nome, email, reputação."""
    cache_key = f"company_info:{user['sub']}"
    cached = await cache_get(request.app.state.redis, cache_key)
    if cached:
        import json; return json.loads(cached)

    data = await ml.get("/users/me")
    import json
    await cache_set(request.app.state.redis, cache_key, json.dumps(data), ttl=600)
    return data


@app.get("/company/health", tags=["Empresa"])
async def get_company_health(
    ml: MLClient = Depends(get_ml_client),
    user: dict = Depends(get_current_user),
    request: Request = None,
):
    """Reputação e saúde da conta no Mercado Livre."""
    data = await ml.get(f"/users/{user['sub']}/seller_reputation")
    return {
        "level":           data.get("level_id"),
        "power_seller":    data.get("power_seller_status"),
        "transactions":    data.get("transactions", {}),
        "metrics":         data.get("metrics", {}),
        "real_level":      data.get("real_level"),
        "protection_end":  data.get("protection_end_date"),
    }

# ─── ROTAS: Pedidos ───────────────────────────────────────────────────────────

@app.get("/orders", tags=["Pedidos"])
async def list_orders(
    status:       str = "paid",
    days:         int = 30,
    limit:        int = 50,
    offset:       int = 0,
    ml: MLClient  = Depends(get_ml_client),
    user: dict    = Depends(get_current_user),
    request: Request = None,
):
    """
    Lista pedidos do período, filtrados por status.
    status: paid | pending | cancelled | all
    """
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00.000-03:00")
    params = {
        "seller": user["sub"],
        "limit":  min(limit, 50),
        "offset": offset,
        "order.date_created.from": date_from,
    }
    if status != "all":
        params["order.status"] = status

    data = await ml.get("/orders/search", params=params)

    orders = []
    for o in data.get("results", []):
        orders.append({
            "id":           o["id"],
            "status":       o["status"],
            "date_created": o["date_created"],
            "date_closed":  o.get("date_closed"),
            "total_amount": o.get("total_amount", 0),
            "currency_id":  o.get("currency_id", "BRL"),
            "buyer":        o.get("buyer", {}).get("nickname", "—"),
            "items": [
                {
                    "title":     i.get("item", {}).get("title"),
                    "quantity":  i.get("quantity"),
                    "unit_price": i.get("unit_price"),
                    "sku":       i.get("item", {}).get("seller_sku"),
                }
                for i in o.get("order_items", [])
            ],
            "payments": [
                {
                    "id":               p.get("id"),
                    "status":           p.get("status"),
                    "transaction_amount": p.get("transaction_amount"),
                    "payment_method":   p.get("payment_method_id"),
                    "date_approved":    p.get("date_approved"),
                }
                for p in o.get("payments", [])
            ],
            "shipping_id": o.get("shipping", {}).get("id") if o.get("shipping") else None,
        })

    return {
        "total":   data.get("paging", {}).get("total", 0),
        "offset":  offset,
        "limit":   limit,
        "results": orders,
    }


@app.get("/orders/{order_id}", tags=["Pedidos"])
async def get_order_detail(
    order_id: int,
    ml: MLClient = Depends(get_ml_client),
):
    """Detalhe completo de um pedido específico."""
    return await ml.get(f"/orders/{order_id}")

# ─── ROTAS: Financeiro ────────────────────────────────────────────────────────

@app.get("/financial/account", tags=["Financeiro"])
async def get_account_balance(
    ml: MLClient = Depends(get_ml_client),
    user: dict   = Depends(get_current_user),
):
    """Saldo disponível e a liberar na conta ML."""
    return await ml.get(f"/users/{user['sub']}/mercadopago_account_balances")


@app.get("/financial/movements", tags=["Financeiro"])
async def get_movements(
    limit:      int = 50,
    offset:     int = 0,
    ml: MLClient = Depends(get_ml_client),
    user: dict   = Depends(get_current_user),
):
    """Extrato de movimentações financeiras."""
    return await ml.get(
        f"/users/{user['sub']}/mercadopago_account_movements",
        params={"limit": limit, "offset": offset},
    )


@app.get("/financial/summary", tags=["Financeiro"])
async def get_financial_summary(
    days: int    = 30,
    ml: MLClient = Depends(get_ml_client),
    user: dict   = Depends(get_current_user),
    request: Request = None,
):
    """
    Resumo financeiro consolidado: receita bruta, comissões ML,
    frete, custos e margem estimada.
    """
    cache_key = f"fin_summary:{user['sub']}:{days}"
    cached = await cache_get(request.app.state.redis, cache_key)
    if cached:
        import json; return json.loads(cached)

    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00.000-03:00")
    data = await ml.get("/orders/search", params={
        "seller":                  user["sub"],
        "order.status":            "paid",
        "order.date_created.from": date_from,
        "limit":                   50,
    })

    total_revenue    = 0.0
    total_commission = 0.0
    total_shipping   = 0.0

    for o in data.get("results", []):
        total_revenue += float(o.get("total_amount", 0))
        for p in o.get("payments", []):
            total_commission += float(p.get("marketplace_fee", 0) or 0)
            total_shipping   += float(p.get("shipping_cost", 0) or 0)

    summary = {
        "period_days":       days,
        "gross_revenue":     round(total_revenue, 2),
        "ml_commission":     round(total_commission, 2),
        "shipping_costs":    round(total_shipping, 2),
        "estimated_net":     round(total_revenue - total_commission - total_shipping, 2),
        "commission_rate":   round((total_commission / total_revenue * 100) if total_revenue else 0, 2),
        "total_paid_orders": data.get("paging", {}).get("total", 0),
        "generated_at":      datetime.utcnow().isoformat(),
    }

    import json
    await cache_set(request.app.state.redis, cache_key, json.dumps(summary), ttl=300)
    return summary

# ─── ROTAS: Anúncios & Estoque ────────────────────────────────────────────────

@app.get("/listings", tags=["Anúncios"])
async def list_active_listings(
    limit:      int = 50,
    offset:     int = 0,
    ml: MLClient = Depends(get_ml_client),
    user: dict   = Depends(get_current_user),
):
    """Lista anúncios ativos com estoque e preço."""
    data = await ml.get(
        f"/users/{user['sub']}/items/search",
        params={"status": "active", "limit": limit, "offset": offset},
    )
    item_ids = data.get("results", [])
    if not item_ids:
        return {"results": [], "total": 0}

    # Busca detalhes em lote (max 20 por request)
    items_detail = []
    for batch in [item_ids[i:i+20] for i in range(0, len(item_ids), 20)]:
        ids_str = ",".join(batch)
        detail = await ml.get(f"/items", params={"ids": ids_str})
        for item in detail:
            if item.get("code") == 200:
                b = item["body"]
                items_detail.append({
                    "id":            b.get("id"),
                    "title":         b.get("title"),
                    "price":         b.get("price"),
                    "currency_id":   b.get("currency_id"),
                    "available_qty": b.get("available_quantity"),
                    "sold_qty":      b.get("sold_quantity"),
                    "status":        b.get("status"),
                    "thumbnail":     b.get("thumbnail"),
                    "permalink":     b.get("permalink"),
                    "sku":           b.get("seller_custom_field"),
                    "listing_type":  b.get("listing_type_id"),
                    "health":        b.get("health"),
                })

    return {
        "total":   data.get("paging", {}).get("total", 0),
        "results": items_detail,
    }

# ─── ROTAS: Dashboard ─────────────────────────────────────────────────────────

@app.get("/dashboard/metrics", tags=["Dashboard"])
async def get_dashboard_metrics(
    days: int    = 30,
    ml: MLClient = Depends(get_ml_client),
    user: dict   = Depends(get_current_user),
    request: Request = None,
):
    """
    Métricas consolidadas para o dashboard principal.
    Agrega: pedidos, receita, ticket médio, top produtos.
    """
    cache_key = f"dashboard:{user['sub']}:{days}"
    cached = await cache_get(request.app.state.redis, cache_key)
    if cached:
        import json; return json.loads(cached)

    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00.000-03:00")

    # Busca em paralelo: pedidos pagos + pendentes + cancelados
    async with httpx.AsyncClient(timeout=30) as client:
        base_params = {
            "seller": user["sub"],
            "order.date_created.from": date_from,
            "limit": 50,
        }
        tokens = await get_ml_tokens(request.app.state.redis, user["sub"])
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        paid_task      = client.get(f"{ML_BASE_URL}/orders/search", headers=headers, params={**base_params, "order.status": "paid"})
        pending_task   = client.get(f"{ML_BASE_URL}/orders/search", headers=headers, params={**base_params, "order.status": "payment_in_process"})
        cancelled_task = client.get(f"{ML_BASE_URL}/orders/search", headers=headers, params={**base_params, "order.status": "cancelled"})

        paid_resp, pending_resp, cancelled_resp = await asyncio.gather(
            paid_task, pending_task, cancelled_task
        )

    paid_data      = paid_resp.json()
    pending_data   = pending_resp.json()
    cancelled_data = cancelled_resp.json()

    # Agrega dados
    total_revenue = 0.0
    product_sales: Dict[str, Dict] = {}
    revenue_by_day: Dict[str, float] = {}

    for o in paid_data.get("results", []):
        amount = float(o.get("total_amount", 0))
        total_revenue += amount

        day = o["date_created"][:10]
        revenue_by_day[day] = revenue_by_day.get(day, 0) + amount

        for item in o.get("order_items", []):
            title = item.get("item", {}).get("title", "Sem título")
            sku   = item.get("item", {}).get("seller_sku", "—")
            qty   = int(item.get("quantity", 1))
            rev   = float(item.get("unit_price", 0)) * qty
            if title not in product_sales:
                product_sales[title] = {"title": title, "sku": sku, "qty": 0, "revenue": 0.0}
            product_sales[title]["qty"]     += qty
            product_sales[title]["revenue"] += rev

    total_paid    = paid_data.get("paging", {}).get("total", 0)
    avg_ticket    = (total_revenue / total_paid) if total_paid else 0

    top_products  = sorted(product_sales.values(), key=lambda x: x["revenue"], reverse=True)[:10]
    rev_by_day    = [{"date": d, "revenue": round(v, 2)} for d, v in sorted(revenue_by_day.items())]

    metrics = {
        "period_days":       days,
        "total_revenue":     round(total_revenue, 2),
        "total_orders":      total_paid,
        "avg_ticket":        round(avg_ticket, 2),
        "pending_orders":    pending_data.get("paging", {}).get("total", 0),
        "cancelled_orders":  cancelled_data.get("paging", {}).get("total", 0),
        "completed_orders":  total_paid,
        "top_products":      top_products,
        "revenue_by_day":    rev_by_day,
        "generated_at":      datetime.utcnow().isoformat(),
    }

    import json
    await cache_set(request.app.state.redis, cache_key, json.dumps(metrics), ttl=180)
    return metrics

# ─── ROTAS: Webhooks ML ───────────────────────────────────────────────────────

@app.post("/webhooks/mercadolivre", tags=["Webhooks"])
async def receive_webhook(
    payload: WebhookPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: Optional[str] = None,
):
    """
    Endpoint para notificações em tempo real do ML.
    Valida assinatura HMAC e processa em background.
    """
    # Validação de assinatura (segurança)
    if x_signature and ML_CLIENT_SECRET:
        body = await request.body()
        expected = hmac.new(
            ML_CLIENT_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, x_signature):
            raise HTTPException(status_code=401, detail="Assinatura inválida")

    background_tasks.add_task(process_webhook_event, payload.dict(), request.app.state.redis)
    return {"status": "received"}


async def process_webhook_event(event: dict, redis):
    """Processa evento recebido do webhook em background."""
    topic    = event.get("topic")
    resource = event.get("resource", "")
    user_id  = event.get("user_id")

    logger.info(f"Webhook recebido: topic={topic} user={user_id} resource={resource}")

    # Invalida cache relevante
    if topic == "orders":
        await redis.delete(f"dashboard:{user_id}:7")
        await redis.delete(f"dashboard:{user_id}:30")
        await redis.delete(f"fin_summary:{user_id}:30")
        logger.info(f"Cache invalidado para user {user_id} após evento de pedido")

    elif topic == "items":
        await redis.delete(f"listings:{user_id}")
        logger.info(f"Cache de anúncios invalidado para user {user_id}")

    elif topic == "payments":
        await redis.delete(f"fin_summary:{user_id}:30")
        logger.info(f"Cache financeiro invalidado para user {user_id}")

# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["Sistema"])
async def health(request: Request):
    try:
        await request.app.state.redis.ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return {
        "status":    "ok" if redis_ok else "degraded",
        "redis":     "connected" if redis_ok else "disconnected",
        "version":   "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
