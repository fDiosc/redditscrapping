SonarPro Scraping Infrastructure - Anti-Ban Strategy
1. Threat Model
O que o Reddit detecta:
SinalRiscoDetecçãoRequests muito rápidos🔴 AltoRate limiting, 429 errorsMesmo IP, muitas requests🔴 AltoIP ban temporário/permanenteUser-Agent suspeito🟡 MédioBlock imediatoPadrões regulares (cron exato)🟡 MédioComportamento de botScraping de muitos subs de uma vez🟡 MédioSpike de tráfegoRequests sem cookies/session🟢 BaixoMenos contextoHeaders faltando🟢 BaixoFingerprinting
Consequências:

Soft ban: 429 Too Many Requests (temporário, minutos/horas)
IP ban: Seu IP bloqueado (dias/permanente)
Account ban: Se usando conta logada
Legal: Cease & desist (raro para pequenos volumes)


2. Estratégia de Defesa em Camadas
Camada 1: Request Hygiene
pythonimport random
import time
from fake_useragent import UserAgent

class RequestHygiene:
    
    # Pool de User-Agents reais (browsers modernos)
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    @staticmethod
    def get_headers():
        """Gera headers que parecem browser real."""
        ua = random.choice(RequestHygiene.USER_AGENTS)
        
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
Camada 2: Rate Limiting com Jitter
pythonimport asyncio
import random

class RateLimiter:
    """Rate limiter com jitter para parecer humano."""
    
    def __init__(
        self,
        min_delay: float = 2.0,      # Mínimo entre requests
        max_delay: float = 5.0,      # Máximo entre requests
        burst_probability: float = 0.1,  # Chance de delay maior
        burst_multiplier: float = 3.0,   # Quanto maior no burst
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.burst_probability = burst_probability
        self.burst_multiplier = burst_multiplier
        self.last_request = 0
    
    async def wait(self):
        """Espera tempo variável entre requests."""
        now = time.time()
        elapsed = now - self.last_request
        
        # Calcula delay base com jitter
        base_delay = random.uniform(self.min_delay, self.max_delay)
        
        # Ocasionalmente adiciona delay maior (simula humano distraído)
        if random.random() < self.burst_probability:
            base_delay *= self.burst_multiplier
        
        # Adiciona micro-jitter (±10%)
        jitter = base_delay * random.uniform(-0.1, 0.1)
        final_delay = base_delay + jitter
        
        # Só espera se necessário
        if elapsed < final_delay:
            await asyncio.sleep(final_delay - elapsed)
        
        self.last_request = time.time()
    
    def get_delay_stats(self) -> dict:
        """Para logging/debug."""
        return {
            "min": self.min_delay,
            "max": self.max_delay,
            "avg_expected": (self.min_delay + self.max_delay) / 2,
        }


# Configurações por contexto
RATE_LIMITS = {
    "aggressive": RateLimiter(min_delay=1.0, max_delay=2.0),   # Risco alto
    "normal": RateLimiter(min_delay=2.0, max_delay=5.0),       # Padrão
    "conservative": RateLimiter(min_delay=5.0, max_delay=10.0), # Após 429
    "recovery": RateLimiter(min_delay=30.0, max_delay=60.0),   # Após ban temp
}
Camada 3: Proxy Rotation
pythonfrom typing import Optional, List
import httpx

class ProxyManager:
    """Gerencia pool de proxies para rotação."""
    
    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies = set()
        self.proxy_scores = {}  # Track success rate
    
    def add_proxy(self, proxy: str):
        """Adiciona proxy ao pool."""
        # Formato: "http://user:pass@host:port" ou "http://host:port"
        self.proxies.append(proxy)
        self.proxy_scores[proxy] = {"success": 0, "fail": 0}
    
    def get_next_proxy(self) -> Optional[str]:
        """Retorna próximo proxy disponível (round-robin com health check)."""
        if not self.proxies:
            return None
        
        available = [p for p in self.proxies if p not in self.failed_proxies]
        if not available:
            # Reset failed proxies se todos falharam
            self.failed_proxies.clear()
            available = self.proxies
        
        # Weighted selection baseado em success rate
        proxy = random.choice(available)
        return proxy
    
    def mark_success(self, proxy: str):
        """Marca proxy como bem-sucedido."""
        if proxy in self.proxy_scores:
            self.proxy_scores[proxy]["success"] += 1
    
    def mark_failed(self, proxy: str):
        """Marca proxy como falho."""
        if proxy in self.proxy_scores:
            self.proxy_scores[proxy]["fail"] += 1
            
            # Se falhou muito, remove temporariamente
            score = self.proxy_scores[proxy]
            fail_rate = score["fail"] / max(score["success"] + score["fail"], 1)
            if fail_rate > 0.5 and score["fail"] > 3:
                self.failed_proxies.add(proxy)


# Opções de proxy providers (custo/benefício)
PROXY_PROVIDERS = """
## Proxy Providers Recomendados

### Tier 1: Residenciais (Melhor para Reddit)
- **Bright Data**: $15/GB, IPs residenciais reais, baixa detecção
- **Oxylabs**: $12/GB, boa cobertura geográfica
- **Smartproxy**: $8/GB, bom custo-benefício

### Tier 2: Datacenter (Mais barato, mais detectável)
- **Webshare**: $0.5/proxy/mês, funciona para volumes baixos
- **ProxyScrape**: Free tier disponível, qualidade variável

### Tier 3: Rotating (Automático)
- **ScraperAPI**: $49/mês, 100k requests, rotação automática
- **Crawlbase**: Pay-per-request, handles JavaScript

### Recomendação para SonarPro:
- **Início**: Sem proxy, rate limiting conservador
- **Scale**: Webshare ($10/mês) para 20 proxies básicos
- **Produção**: Bright Data residencial para confiabilidade
"""
Camada 4: Backoff Exponencial
pythonclass ExponentialBackoff:
    """Backoff exponencial com jitter para retries."""
    
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 300.0,  # 5 minutos máximo
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.attempt = 0
    
    def get_delay(self) -> float:
        """Calcula próximo delay."""
        delay = self.base_delay * (self.exponential_base ** self.attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Full jitter: random entre 0 e delay calculado
            delay = random.uniform(0, delay)
        
        self.attempt += 1
        return delay
    
    def reset(self):
        """Reset após sucesso."""
        self.attempt = 0


class RetryHandler:
    """Handler de retries com backoff."""
    
    def __init__(self):
        self.backoff = ExponentialBackoff()
    
    async def execute_with_retry(
        self,
        func,
        max_retries: int = 5,
        retry_on: tuple = (429, 500, 502, 503, 504),
    ):
        """Executa função com retry automático."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                result = await func()
                self.backoff.reset()
                return result
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code in retry_on:
                    delay = self.backoff.get_delay()
                    
                    # Log para monitoramento
                    print(f"[Retry {attempt + 1}/{max_retries}] "
                          f"Status {e.response.status_code}, "
                          f"waiting {delay:.1f}s")
                    
                    await asyncio.sleep(delay)
                    last_exception = e
                else:
                    raise
                    
            except Exception as e:
                delay = self.backoff.get_delay()
                await asyncio.sleep(delay)
                last_exception = e
        
        raise last_exception
Camada 5: Session Management
pythonclass SessionManager:
    """Gerencia sessões para parecer mais natural."""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, subreddit: str) -> httpx.AsyncClient:
        """
        Mantém sessão por subreddit.
        Browsers reais mantêm cookies/sessão, bots não.
        """
        if subreddit not in self.sessions:
            self.sessions[subreddit] = httpx.AsyncClient(
                headers=RequestHygiene.get_headers(),
                timeout=30.0,
                follow_redirects=True,
            )
        return self.sessions[subreddit]
    
    async def rotate_session(self, subreddit: str):
        """Rotaciona sessão (novo 'browser')."""
        if subreddit in self.sessions:
            await self.sessions[subreddit].aclose()
        
        self.sessions[subreddit] = httpx.AsyncClient(
            headers=RequestHygiene.get_headers(),
            timeout=30.0,
            follow_redirects=True,
        )
    
    async def close_all(self):
        """Cleanup."""
        for session in self.sessions.values():
            await session.aclose()
        self.sessions.clear()

3. Scraper Robusto Completo
pythonimport asyncio
import random
import time
from dataclasses import dataclass
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup

@dataclass
class ScrapingConfig:
    """Configuração do scraper."""
    use_proxies: bool = False
    min_delay: float = 2.0
    max_delay: float = 5.0
    max_retries: int = 5
    timeout: float = 30.0
    max_concurrent: int = 3  # Requests simultâneas por subreddit
    
class RobustRedditScraper:
    """Scraper robusto com todas as proteções."""
    
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.rate_limiter = RateLimiter(
            min_delay=self.config.min_delay,
            max_delay=self.config.max_delay,
        )
        self.retry_handler = RetryHandler()
        self.session_manager = SessionManager()
        self.proxy_manager = ProxyManager()
        
        # Métricas
        self.stats = {
            "requests": 0,
            "success": 0,
            "failed": 0,
            "retries": 0,
            "rate_limited": 0,
        }
    
    async def scrape_subreddit(
        self,
        subreddit: str,
        sort: str = "new",
        limit: int = 100,
    ) -> List[dict]:
        """
        Scrape posts de um subreddit.
        
        Args:
            subreddit: Nome do subreddit (sem r/)
            sort: new, hot, top, rising
            limit: Número de posts
        """
        posts = []
        after = None
        
        while len(posts) < limit:
            # Rate limiting
            await self.rate_limiter.wait()
            
            # Build URL
            url = f"https://old.reddit.com/r/{subreddit}/{sort}/.json"
            params = {"limit": 25}  # Reddit máximo por página
            if after:
                params["after"] = after
            
            try:
                data = await self._make_request(url, params)
                
                if not data or "data" not in data:
                    break
                
                children = data["data"].get("children", [])
                if not children:
                    break
                
                for child in children:
                    post = child.get("data", {})
                    posts.append(self._parse_post(post))
                
                after = data["data"].get("after")
                if not after:
                    break
                    
            except Exception as e:
                print(f"[Error] Scraping {subreddit}: {e}")
                break
        
        return posts[:limit]
    
    async def scrape_post_with_comments(
        self,
        post_id: str,
        subreddit: str,
    ) -> dict:
        """Scrape post completo com comentários."""
        await self.rate_limiter.wait()
        
        url = f"https://old.reddit.com/r/{subreddit}/comments/{post_id}/.json"
        params = {"limit": 500, "depth": 10}
        
        data = await self._make_request(url, params)
        
        if not data or len(data) < 2:
            return None
        
        # data[0] = post, data[1] = comments
        post_data = data[0]["data"]["children"][0]["data"]
        comments_data = data[1]["data"]["children"]
        
        return {
            "post": self._parse_post(post_data),
            "comments": self._parse_comments(comments_data),
        }
    
    async def _make_request(
        self,
        url: str,
        params: dict = None,
    ) -> dict:
        """Faz request com todas as proteções."""
        
        async def _request():
            self.stats["requests"] += 1
            
            # Seleciona proxy se disponível
            proxy = None
            if self.config.use_proxies:
                proxy = self.proxy_manager.get_next_proxy()
            
            # Prepara client
            client_kwargs = {
                "headers": RequestHygiene.get_headers(),
                "timeout": self.config.timeout,
                "follow_redirects": True,
            }
            if proxy:
                client_kwargs["proxies"] = {"all://": proxy}
            
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.get(url, params=params)
                
                # Detecta rate limiting
                if response.status_code == 429:
                    self.stats["rate_limited"] += 1
                    # Aumenta delays
                    self.rate_limiter.min_delay *= 1.5
                    self.rate_limiter.max_delay *= 1.5
                    raise httpx.HTTPStatusError(
                        "Rate limited",
                        request=response.request,
                        response=response,
                    )
                
                response.raise_for_status()
                
                self.stats["success"] += 1
                if proxy:
                    self.proxy_manager.mark_success(proxy)
                
                return response.json()
        
        try:
            return await self.retry_handler.execute_with_retry(_request)
        except Exception as e:
            self.stats["failed"] += 1
            raise
    
    def _parse_post(self, data: dict) -> dict:
        """Parse post data."""
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "body": data.get("selftext", ""),
            "author": data.get("author"),
            "score": data.get("score", 0),
            "num_comments": data.get("num_comments", 0),
            "created_utc": data.get("created_utc"),
            "url": f"https://reddit.com{data.get('permalink', '')}",
            "subreddit": data.get("subreddit"),
        }
    
    def _parse_comments(self, children: list, depth: int = 0) -> list:
        """Parse comments recursivamente."""
        comments = []
        
        for child in children:
            if child.get("kind") != "t1":
                continue
            
            data = child.get("data", {})
            comment = {
                "id": data.get("id"),
                "body": data.get("body", ""),
                "author": data.get("author"),
                "score": data.get("score", 0),
                "depth": depth,
            }
            comments.append(comment)
            
            # Parse replies
            replies = data.get("replies")
            if replies and isinstance(replies, dict):
                reply_children = replies.get("data", {}).get("children", [])
                comments.extend(self._parse_comments(reply_children, depth + 1))
        
        return comments
    
    def get_stats(self) -> dict:
        """Retorna estatísticas."""
        return {
            **self.stats,
            "success_rate": self.stats["success"] / max(self.stats["requests"], 1),
            "current_rate_limit": {
                "min": self.rate_limiter.min_delay,
                "max": self.rate_limiter.max_delay,
            },
        }

4. Scheduling Inteligente
pythonfrom datetime import datetime, timedelta
import random

class IntelligentScheduler:
    """Agenda scraping de forma inteligente para evitar detecção."""
    
    def __init__(self):
        self.last_runs = {}  # subreddit -> last_run_time
    
    def should_run(self, subreddit: str) -> bool:
        """Determina se deve rodar scraping agora."""
        last_run = self.last_runs.get(subreddit)
        
        if not last_run:
            return True
        
        # Mínimo 15 minutos entre runs do mesmo sub
        min_interval = timedelta(minutes=15)
        if datetime.now() - last_run < min_interval:
            return False
        
        return True
    
    def get_optimal_schedule(
        self,
        subreddits: List[str],
        total_runs_per_day: int = 24,
    ) -> List[dict]:
        """
        Distribui scraping ao longo do dia.
        Evita padrões detectáveis.
        """
        schedule = []
        
        # Distribui uniformemente com jitter
        interval_hours = 24 / total_runs_per_day
        
        for i in range(total_runs_per_day):
            base_hour = i * interval_hours
            
            # Adiciona jitter de ±30 minutos
            jitter = random.uniform(-0.5, 0.5)
            scheduled_hour = base_hour + jitter
            
            # Seleciona subset de subreddits (não todos de uma vez)
            num_subs = random.randint(1, min(3, len(subreddits)))
            selected_subs = random.sample(subreddits, num_subs)
            
            schedule.append({
                "hour": scheduled_hour % 24,
                "subreddits": selected_subs,
            })
        
        return sorted(schedule, key=lambda x: x["hour"])
    
    def mark_run(self, subreddit: str):
        """Marca que rodou."""
        self.last_runs[subreddit] = datetime.now()


# Exemplo de uso com APScheduler ou similar
SCHEDULE_CONFIG = """
## Configuração de Schedule

### Modo Conservador (Recomendado para início)
- Scrape cada subreddit 1x por hora
- Máximo 3 subreddits por run
- Total: ~50-100 requests/hora
- Risco: Baixo

### Modo Normal (Produção)
- Scrape cada subreddit 2x por hora
- Máximo 5 subreddits por run
- Total: ~100-200 requests/hora
- Risco: Médio (requer proxies)

### Modo Agressivo (Não recomendado)
- Scrape cada subreddit 4x por hora
- Todos subreddits
- Total: ~500+ requests/hora
- Risco: Alto (ban provável sem proxies residenciais)
"""

5. Monitoramento e Alertas
pythonfrom dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class ScrapingHealth:
    """Monitora saúde do scraping."""
    
    success_rate_threshold: float = 0.8
    rate_limit_threshold: int = 5
    
    # Métricas rolling
    recent_requests: List[dict] = field(default_factory=list)
    window_minutes: int = 60
    
    def record_request(self, success: bool, status_code: int = None):
        """Registra request."""
        self.recent_requests.append({
            "timestamp": datetime.now(),
            "success": success,
            "status_code": status_code,
        })
        self._cleanup_old()
    
    def _cleanup_old(self):
        """Remove requests antigos."""
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        self.recent_requests = [
            r for r in self.recent_requests
            if r["timestamp"] > cutoff
        ]
    
    def get_health_status(self) -> dict:
        """Retorna status de saúde."""
        if not self.recent_requests:
            return {"status": "unknown", "message": "No data"}
        
        total = len(self.recent_requests)
        success = sum(1 for r in self.recent_requests if r["success"])
        rate_limits = sum(
            1 for r in self.recent_requests
            if r.get("status_code") == 429
        )
        
        success_rate = success / total
        
        if rate_limits > self.rate_limit_threshold:
            return {
                "status": "critical",
                "message": f"Too many rate limits ({rate_limits})",
                "action": "pause_scraping",
            }
        
        if success_rate < self.success_rate_threshold:
            return {
                "status": "warning", 
                "message": f"Low success rate ({success_rate:.1%})",
                "action": "increase_delays",
            }
        
        return {
            "status": "healthy",
            "message": f"Success rate: {success_rate:.1%}",
            "action": "continue",
        }

6. Checklist de Implementação
Fase 1: MVP (Sem Proxies)

 Rate limiting com jitter
 User-Agent rotation
 Headers completos
 Backoff exponencial
 Retry handler
 Integrar com scraper existente

Fase 2: Hardening

 Session management
 Health monitoring
 Alertas automáticos
 Logs estruturados

Fase 3: Scale (Se necessário)

 Proxy rotation
 Multiple IPs
 Distributed scraping
 Redis para rate limiting compartilhado


7. Custos Estimados
ComponenteCusto/mêsQuandoSem proxy$0MVPWebshare (20 proxies)$10100+ usersBright Data residencial$50-100500+ usersVPS adicional$5-20Distributed

8. Riscos Legais
Reddit Terms of Service

Scraping público é zona cinza
Não violar rate limits
Não armazenar dados pessoais além do necessário
Não usar para spam/harassment

Mitigações

Scrape apenas dados públicos
Respeite robots.txt (Reddit permite /r/*)
Mantenha cache para reduzir requests
Delete dados antigos periodicamente


Document Version: 1.0
Strategy: Conservative Start, Scale 