# Radar - Implementation Guide for Vibe Coder

Este documento detalha as 5 implementações prioritárias para melhorar o core do Radar. Cada seção é auto-contida com contexto, especificação técnica e critérios de aceite.

---

## Sumário de Prioridades

| # | Item | Esforço | Impacto | Dependências |
|---|------|---------|---------|--------------|
| 1 | Product Configuration UI | Médio | Alto | Nenhuma |
| 2 | Embedding Context Expandido | Baixo | Alto | #1 |
| 3 | Truncation Inteligente | Médio | Médio | Nenhuma |
| 4 | Prompt de AI Estruturado | Baixo | Alto | Nenhuma |
| 5 | Minimum Fit para AI Trigger | Baixo | Médio | Nenhuma |

---

# 1. Product Configuration UI

## Contexto

Atualmente os produtos são configurados via código em `products.py`. Para escalar e permitir self-service, precisamos de uma UI para CRUD de produtos.

## O que construir

### 1.1 Nova página/seção: `/settings/products`

Acessível via sidebar ou menu de configurações.

### 1.2 Lista de Produtos

```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Products                                    [+ Add New] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ 📦 PROFITDOCTOR                          [Edit] [Delete]││
│  │ Profit tracking for Shopify                             ││
│  │ 5 pain signals · 4 intents · 3 subreddits              ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ 📦 SOCIALGENIUS                          [Edit] [Delete]││
│  │ AI content creation for social media                    ││
│  │ 4 pain signals · 3 intents · 4 subreddits              ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Modal/Página de Edição

Campos do formulário:

| Campo | Tipo | Validação | Obrigatório |
|-------|------|-----------|-------------|
| `name` | text input | 2-50 chars, único | ✅ |
| `description` | textarea | 50-500 chars | ✅ |
| `pain_signals` | array de strings | mín 3 items, cada 5-100 chars | ✅ |
| `intent_signals` | array de strings | mín 2 items, cada 5-100 chars | ✅ |
| `target_subreddits` | multi-select/tags | mín 1 | ✅ |

### 1.4 Wireframe do Modal

```
┌─────────────────────────────────────────────────────────────┐
│  Edit Product                                          [X] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Name *                                                     │
│  ┌────────────────────────────────────────────────────────┐│
│  │ ProfitDoctor                                           ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  Description * (be detailed - powers AI matching)           │
│  ┌────────────────────────────────────────────────────────┐│
│  │ AI-powered profit diagnosis tool for Shopify           ││
│  │ merchants. Tracks real profit margins, COGS,           ││
│  │ shipping costs, and fees to show which products        ││
│  │ actually make money.                                   ││
│  │                                                 120/500 ││
│  └────────────────────────────────────────────────────────┘│
│  💡 Tip: Be specific about what problem you solve          │
│                                                             │
│  Pain Signals * (problems your product solves)              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ [don't know if profitable                         ×]   ││
│  │ [spreadsheet nightmare                            ×]   ││
│  │ [shipping costs eating margins                    ×]   ││
│  │ [hidden fees                                      ×]   ││
│  │ [which products make money                        ×]   ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │ Add new pain signal...                                 ││
│  └────────────────────────────────────────────────────────┘│
│  [+ Add]                                                    │
│                                                             │
│  Intent Signals * (how users search for solutions)          │
│  ┌────────────────────────────────────────────────────────┐│
│  │ [profit tracker shopify                           ×]   ││
│  │ [shopify analytics app                            ×]   ││
│  │ [margin calculator                                ×]   ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │ Add new intent signal...                               ││
│  └────────────────────────────────────────────────────────┘│
│  [+ Add]                                                    │
│                                                             │
│  Target Subreddits *                                        │
│  ┌────────────────────────────────────────────────────────┐│
│  │ ☑ r/shopify    ☑ r/ecommerce    ☐ r/dropship          ││
│  │ ☐ r/entrepreneur    ☐ r/smallbusiness                 ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │ Add custom subreddit: r/                               ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ⚡ Embedding Preview (auto-generated)                      │
│  ┌────────────────────────────────────────────────────────┐│
│  │ ProfitDoctor: AI-powered profit diagnosis tool for     ││
│  │ Shopify merchants...                                   ││
│  │                                                        ││
│  │ Problems this product solves:                          ││
│  │ - don't know if profitable                             ││
│  │ - spreadsheet nightmare                                ││
│  │ ...                                            [Expand]││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  ⚠️ Saving will regenerate embeddings. This may take       │
│     a few seconds.                                          │
│                                                             │
│  [Cancel]                    [Save & Regenerate Embedding]  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Schema do Banco (SQLite)

```sql
-- Nova tabela (ou migrar de products.py)
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,  -- slug: "profitdoctor"
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    pain_signals TEXT NOT NULL,  -- JSON array: ["signal1", "signal2"]
    intent_signals TEXT NOT NULL,  -- JSON array
    target_subreddits TEXT NOT NULL,  -- JSON array
    embedding_context TEXT,  -- Texto gerado para embedding
    embedding_id TEXT,  -- Referência no ChromaDB
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca rápida
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
```

## API Endpoints (FastAPI)

```python
# GET /api/products
# Lista todos os produtos
# Response: [{ id, name, description, pain_signals_count, intent_signals_count, subreddits_count }]

# GET /api/products/{id}
# Detalhes de um produto
# Response: { id, name, description, pain_signals, intent_signals, target_subreddits, embedding_context }

# POST /api/products
# Criar novo produto
# Body: { name, description, pain_signals, intent_signals, target_subreddits }
# Response: { id, embedding_regenerated: true }

# PUT /api/products/{id}
# Atualizar produto
# Body: { name?, description?, pain_signals?, intent_signals?, target_subreddits? }
# Response: { id, embedding_regenerated: true/false }
# Nota: embedding_regenerated = true se description, pain_signals ou intent_signals mudaram

# DELETE /api/products/{id}
# Deletar produto
# Response: { deleted: true }
# Nota: Também remove embedding do ChromaDB
```

## Lógica de Negócio

### Quando regenerar embedding:

```python
def should_regenerate_embedding(old_product, new_product) -> bool:
    """Retorna True se precisa regenerar embedding"""
    return (
        old_product.description != new_product.description or
        old_product.pain_signals != new_product.pain_signals or
        old_product.intent_signals != new_product.intent_signals
    )
    # NÃO regenera se só mudou: name, target_subreddits
```

### Gerar embedding context:

```python
def generate_embedding_context(product: Product) -> str:
    """Gera o texto que será convertido em embedding"""
    pain_list = "\n- ".join(product.pain_signals)
    intent_list = "\n- ".join(product.intent_signals)
    
    return f"""{product.name}: {product.description}

Problems this product solves:
- {pain_list}

How users search for solutions:
- {intent_list}""".strip()
```

## Critérios de Aceite

- [ ] Página de listagem de produtos funcional
- [ ] Modal/página de criação de produto funcional
- [ ] Modal/página de edição de produto funcional
- [ ] Deleção de produto com confirmação
- [ ] Validações client-side e server-side
- [ ] Preview do embedding context em tempo real
- [ ] Embedding regenerado automaticamente ao salvar (quando necessário)
- [ ] Dropdown de "Active Product" no Dashboard atualiza dinamicamente
- [ ] Migração dos produtos existentes de `products.py` para o banco

---

# 2. Embedding Context Expandido

## Contexto

Atualmente o embedding do produto é gerado apenas com `"{name}: {description}"`. Isso limita a capacidade de matching semântico.

## O que mudar

### Atual (limitado):

```python
product_embedding_text = f"{product.name}: {product.description}"
# Exemplo: "ProfitDoctor: Profit tracking for Shopify"
```

### Novo (expandido):

```python
def generate_embedding_context(product: Product) -> str:
    pain_list = "\n- ".join(product.pain_signals)
    intent_list = "\n- ".join(product.intent_signals)
    
    return f"""{product.name}: {product.description}

Problems this product solves:
- {pain_list}

How users search for solutions:
- {intent_list}""".strip()
```

### Exemplo de output:

```
ProfitDoctor: AI-powered profit diagnosis tool for Shopify merchants. 
Tracks real profit margins, COGS, shipping costs, and fees to show 
which products actually make money.

Problems this product solves:
- don't know if I'm actually profitable
- spreadsheet nightmare tracking costs
- shipping costs eating into margins
- hidden fees killing profit
- can't tell which products make money

How users search for solutions:
- profit tracker for shopify
- shopify analytics app
- margin calculator ecommerce
- profit dashboard
```

## Onde implementar

Arquivo: `radar/products.py` ou novo `radar/services/product_service.py`

```python
class ProductService:
    def __init__(self, db, chroma_client):
        self.db = db
        self.chroma = chroma_client
    
    def generate_embedding_context(self, product: Product) -> str:
        """Gera texto expandido para embedding"""
        pain_list = "\n- ".join(product.pain_signals)
        intent_list = "\n- ".join(product.intent_signals)
        
        return f"""{product.name}: {product.description}

Problems this product solves:
- {pain_list}

How users search for solutions:
- {intent_list}""".strip()
    
    def regenerate_embedding(self, product: Product) -> str:
        """Regenera embedding do produto no ChromaDB"""
        context = self.generate_embedding_context(product)
        
        # Gerar embedding via OpenAI
        embedding = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=context
        ).data[0].embedding
        
        # Atualizar no ChromaDB
        self.chroma.upsert(
            ids=[f"product_{product.id}"],
            embeddings=[embedding],
            metadatas=[{"type": "product", "product_id": product.id}]
        )
        
        # Salvar context no banco
        product.embedding_context = context
        self.db.save(product)
        
        return context
```

## Critérios de Aceite

- [ ] Função `generate_embedding_context` implementada
- [ ] Embedding usa o contexto expandido (não só name:description)
- [ ] Context é salvo no banco para debug/visualização
- [ ] Preview do context aparece na UI de edição de produto
- [ ] Produtos existentes migrados para novo formato

---

# 3. Truncation Inteligente

## Contexto

O Unified Context (Title + Body + ALL Comments) pode exceder 8,191 tokens do `text-embedding-3-small`. Atualmente o modelo trunca silenciosamente o final - perdendo os comments mais recentes.

## O que implementar

### 3.1 Função de contagem de tokens

```python
import tiktoken

def count_tokens(text: str, model: str = "text-embedding-3-small") -> int:
    """Conta tokens de um texto para o modelo especificado"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

### 3.2 Função de truncation inteligente

```python
MAX_EMBEDDING_TOKENS = 7500  # Buffer de segurança (modelo suporta 8191)
RESERVED_FOR_TITLE_BODY = 1500  # Reserva para title + body

def build_unified_context(post: Post, comments: list[Comment]) -> str:
    """
    Constrói unified context com truncation inteligente.
    Prioriza: Title > Body > Top Comments por score
    """
    
    # 1. Sempre incluir title e body
    base_context = f"Title: {post.title}\n\nBody: {post.body or '(no body)'}"
    base_tokens = count_tokens(base_context)
    
    # 2. Calcular tokens disponíveis para comments
    available_tokens = MAX_EMBEDDING_TOKENS - base_tokens
    
    if available_tokens <= 0:
        # Title + Body já excede limite (raro)
        # Truncar body mantendo início
        return truncate_to_tokens(base_context, MAX_EMBEDDING_TOKENS)
    
    # 3. Ordenar comments por score (mais votados primeiro)
    sorted_comments = sorted(comments, key=lambda c: c.score, reverse=True)
    
    # 4. Adicionar comments até atingir limite
    included_comments = []
    current_tokens = base_tokens
    
    for comment in sorted_comments:
        comment_text = f"\n\nComment (score {comment.score}): {comment.body}"
        comment_tokens = count_tokens(comment_text)
        
        if current_tokens + comment_tokens > MAX_EMBEDDING_TOKENS:
            # Não cabe mais
            break
        
        included_comments.append(comment_text)
        current_tokens += comment_tokens
    
    # 5. Montar contexto final
    unified_context = base_context + "".join(included_comments)
    
    # 6. Log se houve truncation
    if len(included_comments) < len(sorted_comments):
        logger.info(
            f"Truncation applied: {len(included_comments)}/{len(sorted_comments)} "
            f"comments included ({current_tokens} tokens)"
        )
    
    return unified_context


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Trunca texto para não exceder max_tokens"""
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens = encoding.encode(text)
    
    if len(tokens) <= max_tokens:
        return text
    
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)
```

### 3.3 Onde aplicar

No pipeline de processamento, antes de gerar embedding:

```python
# Em radar/process/embeddings.py ou similar

def process_post(post: Post) -> None:
    # Buscar comments do banco
    comments = db.get_comments_for_post(post.id)
    
    # ANTES (problemático):
    # unified_context = f"{post.title}\n{post.body}\n" + "\n".join([c.body for c in comments])
    
    # DEPOIS (com truncation inteligente):
    unified_context = build_unified_context(post, comments)
    
    # Gerar embedding
    embedding = openai.embeddings.create(
        model="text-embedding-3-small",
        input=unified_context
    ).data[0].embedding
    
    # Salvar...
```

### 3.4 Adicionar coluna de metadata (opcional mas recomendado)

```sql
ALTER TABLE posts ADD COLUMN context_tokens INTEGER;
ALTER TABLE posts ADD COLUMN comments_included INTEGER;
ALTER TABLE posts ADD COLUMN truncation_applied BOOLEAN DEFAULT FALSE;
```

## Critérios de Aceite

- [ ] Função `count_tokens` implementada usando tiktoken
- [ ] Função `build_unified_context` implementada
- [ ] Comments são ordenados por score antes de incluir
- [ ] Truncation mantém title + body completos (se possível)
- [ ] Log quando truncation é aplicada
- [ ] Metadata de truncation salva no banco (opcional)
- [ ] Testado com post real de 500+ comments

---

# 4. Prompt de AI Estruturado

## Contexto

O prompt atual é genérico e retorna Markdown não estruturado. Precisamos de output JSON consistente com campos úteis para o produto.

## Prompt Atual (problemático)

```python
system_prompt = "You are a product analyst helping a founder find leads and insights."

user_prompt = """
1. Assessment of pain point.
2. Product solution.
3. Fit rating (1-10).
"""
```

### Problemas:
- Não passa contexto do produto
- Output não é parseável
- "Fit rating 1-10" duplica o Fit score que já temos
- Não sugere ângulo de resposta

## Novo Prompt (estruturado)

```python
SYSTEM_PROMPT = """You are a lead qualification analyst for SaaS products.
Your job is to analyze Reddit discussions and identify sales opportunities.

Rules:
1. Be specific - quote exact phrases from the discussion
2. Focus on actionable insights
3. Always respond in valid JSON format
4. Never invent information not present in the discussion"""


def build_analysis_prompt(post: Post, product: Product) -> str:
    """Constrói prompt para análise de AI"""
    
    # Pegar top 5 comments por relevância
    top_comments = get_top_comments(post.id, limit=5)
    comments_text = "\n".join([
        f"- [{c.score} pts]: {c.body[:300]}" 
        for c in top_comments
    ])
    
    return f"""## Product Context
Name: {product.name}
Description: {product.description}
Key problems it solves: {", ".join(product.pain_signals[:5])}

## Discussion to Analyze
Subreddit: r/{post.subreddit}
Title: {post.title}
Body: {post.body or "(no body)"}

Top Comments:
{comments_text}

## Your Task
Analyze this discussion for sales potential. Respond with this exact JSON structure:

{{
  "pain_point_summary": "One sentence describing the specific pain expressed",
  "pain_quote": "Exact quote from the post or comments that shows the pain (max 100 chars)",
  "urgency": "exploring | considering | actively_seeking | desperate",
  "product_relevance": "strong | moderate | weak | none",
  "relevance_explanation": "Why this product does or doesn't fit (1-2 sentences)",
  "response_angle": "Suggested hook/angle for responding to this person (1-2 sentences)",
  "confidence": 0.0-1.0
}}

Important:
- "pain_quote" must be an EXACT quote from the text, not paraphrased
- "urgency" should reflect how urgently they need a solution
- "response_angle" should be natural and helpful, not salesy
- "confidence" is your confidence in this analysis"""
```

## Parsing do Response

```python
import json
from typing import Optional
from pydantic import BaseModel, Field

class AIAnalysis(BaseModel):
    """Schema para análise de AI"""
    pain_point_summary: str
    pain_quote: str
    urgency: str = Field(pattern="^(exploring|considering|actively_seeking|desperate)$")
    product_relevance: str = Field(pattern="^(strong|moderate|weak|none)$")
    relevance_explanation: str
    response_angle: str
    confidence: float = Field(ge=0.0, le=1.0)


def parse_ai_response(response_text: str) -> Optional[AIAnalysis]:
    """
    Parseia response do AI para objeto estruturado.
    Retorna None se parsing falhar.
    """
    try:
        # Limpar possíveis markdown code blocks
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        data = json.loads(cleaned.strip())
        return AIAnalysis(**data)
    
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse AI response: {e}")
        logger.debug(f"Raw response: {response_text}")
        return None


def analyze_post_with_ai(post: Post, product: Product) -> Optional[AIAnalysis]:
    """Executa análise de AI e retorna resultado estruturado"""
    
    prompt = build_analysis_prompt(post, product)
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # Baixa para output consistente
        max_tokens=500
    )
    
    result = parse_ai_response(response.choices[0].message.content)
    
    if result is None:
        # Retry uma vez com temperatura 0
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=500
        )
        result = parse_ai_response(response.choices[0].message.content)
    
    return result
```

## Atualizar Schema do Banco

```sql
-- Atualizar coluna de AI analysis para JSON estruturado
-- (se estava salvando como texto)

-- Opção 1: Nova tabela
CREATE TABLE IF NOT EXISTS post_ai_analysis (
    post_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    pain_point_summary TEXT,
    pain_quote TEXT,
    urgency TEXT,
    product_relevance TEXT,
    relevance_explanation TEXT,
    response_angle TEXT,
    confidence REAL,
    raw_response TEXT,  -- Backup do response original
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Opção 2: Manter na tabela existente como JSON
ALTER TABLE post_analysis ADD COLUMN ai_analysis_json TEXT;
```

## Atualizar UI para mostrar novos campos

Na área "AI INSIGHT FOR PROFITDOCTOR":

```
┌─────────────────────────────────────────────────────────────┐
│ ⚡ AI Insight                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🎯 Pain Point                                               │
│ User frustrated with spending hours on spreadsheets to     │
│ track profitability without clear answers.                 │
│                                                             │
│ 💬 Key Quote                                                │
│ "I'm spending 10 hours/week and still don't know which    │
│ products to kill"                                          │
│                                                             │
│ 🔥 Urgency: ACTIVELY SEEKING                               │
│ 📊 Relevance: STRONG (87% confidence)                      │
│                                                             │
│ 💡 Response Angle                                           │
│ "Empathize with the spreadsheet pain, share how automated │
│ profit tracking changed the game. Offer to show specific   │
│ example."                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Critérios de Aceite

- [ ] Novo prompt implementado com contexto do produto
- [ ] Output é JSON estruturado
- [ ] Parsing com Pydantic e validação de schema
- [ ] Retry com temperature=0 se parsing falhar
- [ ] Campo `response_angle` incluído e útil
- [ ] Campo `pain_quote` extrai citação real
- [ ] UI atualizada para mostrar novos campos
- [ ] Banco atualizado para salvar JSON estruturado

---

# 5. Minimum Fit para AI Trigger

## Contexto

Atualmente o AI trigger é:
```python
if total_relevance >= 7.0:
    trigger_ai_analysis()
```

O problema: um post pode ter Fit baixo (0.2) mas Intensity alta (10) e passar do threshold. Isso gasta tokens em leads de baixa qualidade.

### Exemplo problemático:

| Post | Fit | Intensity | Intent | Relevance | AI Triggered? |
|------|-----|-----------|--------|-----------|---------------|
| Post viral irrelevante | 0.2 | 12 | 0 | 3+12+0 = 15 | ✅ (errado!) |
| Post relevante novo | 0.7 | 2 | +5 | 10.5+2+5 = 17.5 | ✅ (correto) |

## O que implementar

### Lógica atualizada

```python
# Configurações (em config ou products.py)
AI_ANALYSIS_THRESHOLD = 7.0
AI_MINIMUM_FIT = 0.4  # Novo!

def should_trigger_ai_analysis(post_analysis: PostAnalysis) -> bool:
    """
    Determina se deve executar AI analysis.
    Requer AMBOS: relevance threshold E minimum fit.
    """
    return (
        post_analysis.total_relevance >= AI_ANALYSIS_THRESHOLD and
        post_analysis.semantic_similarity >= AI_MINIMUM_FIT
    )
```

### Onde aplicar

No pipeline de processamento:

```python
# Em radar/process/signals.py ou similar

def process_post_analysis(post: Post, product: Product) -> PostAnalysis:
    # ... calcular scores ...
    
    # Verificar se deve rodar AI
    # ANTES:
    # if analysis.total_relevance >= AI_ANALYSIS_THRESHOLD:
    #     analysis.ai_insight = analyze_with_ai(post, product)
    
    # DEPOIS:
    if should_trigger_ai_analysis(analysis):
        analysis.ai_insight = analyze_with_ai(post, product)
    else:
        analysis.ai_insight = None
        if analysis.total_relevance >= AI_ANALYSIS_THRESHOLD:
            # Log para debug: passou threshold mas não fit
            logger.debug(
                f"Skipped AI for post {post.id}: "
                f"relevance={analysis.total_relevance:.1f} but fit={analysis.semantic_similarity:.2f}"
            )
    
    return analysis
```

### Configuração por produto (opcional, avançado)

```python
class Product:
    # ... outros campos ...
    ai_threshold: float = 7.0  # Default
    ai_minimum_fit: float = 0.4  # Default
```

Isso permite ajustar por produto se necessário.

## Impacto Esperado

Baseado nos dados atuais, estimativa:

| Métrica | Antes | Depois |
|---------|-------|--------|
| Posts analisados por AI | 100% dos > 7.0 | ~70% |
| Custo de AI por sync | $0.02 | ~$0.014 |
| Qualidade dos insights | Inclui irrelevantes | Só relevantes |

## Critérios de Aceite

- [ ] Constante `AI_MINIMUM_FIT` adicionada à config
- [ ] Função `should_trigger_ai_analysis` implementada
- [ ] Lógica de trigger atualizada em todos os lugares
- [ ] Log quando post é skipado por fit baixo
- [ ] Dashboard mostra corretamente posts sem AI insight (não é erro)
- [ ] Testado com sync real e verificado economia de tokens

---

# Ordem de Implementação Recomendada

```
Semana 1:
├── #5 Minimum Fit para AI (30 min) ← Mais fácil, economiza $ imediatamente
├── #4 Prompt Estruturado (2-3h) ← Melhora qualidade dos insights
└── #3 Truncation (2-3h) ← Melhora qualidade dos embeddings

Semana 2:
├── #2 Embedding Expandido (1h) ← Depende de ter products no banco
└── #1 Product Config UI (4-6h) ← Maior esforço, mas essencial para self-service
```

## Checklist Final

### Antes de Deploy

- [ ] Todos os 5 items implementados
- [ ] Testes unitários para funções críticas
- [ ] Migração de produtos existentes
- [ ] Backup do banco antes de migração
- [ ] Testado com sync completo
- [ ] UI funcionando em todos os browsers

### Métricas para Validar Sucesso

| Métrica | Baseline | Target |
|---------|----------|--------|
| Fit score médio | ? | +10% |
| AI cost por sync | $0.02 | $0.015 |
| Posts com truncation | ? | <5% |
| AI insights com response_angle | 0% | 100% |

---

# Apêndice: Arquivos que Serão Modificados

```
radar/
├── config.py                 # Novas constantes
├── products.py               # Migrar para banco OU manter como fallback
├── models/
│   └── product.py            # Pydantic model para Product
├── services/
│   ├── product_service.py    # NOVO: CRUD de produtos
│   └── embedding_service.py  # Modificar: context expandido
├── process/
│   ├── embeddings.py         # Modificar: truncation
│   └── signals.py            # Modificar: AI trigger
├── api/
│   └── routes/
│       └── products.py       # NOVO: API endpoints
└── ui/
    └── src/
        ├── pages/
        │   └── ProductSettings.tsx  # NOVO: página de config
        └── components/
            └── ProductForm.tsx      # NOVO: formulário
```

---

*Documento gerado em: Janeiro 2026*
*Versão: 1.0*