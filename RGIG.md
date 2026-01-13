# Radar - Response Generation Implementation Guide

## Profile Intelligence: Fase 1

Este documento especifica a implementação do gerador de respostas, a primeira fase do Profile Intelligence. O objetivo é permitir que o usuário gere uma resposta sugerida para um lead com base no AI Insight já existente.

---

## Visão Geral

### O que estamos construindo

Um botão "Generate Response" no AI Insight Card que:
1. Usa o contexto já analisado (post + insight + produto)
2. Gera uma resposta natural para o Reddit
3. Permite copiar e postar manualmente

### Por que isso importa

- **Reduz fricção**: Usuário não precisa pensar no que escrever
- **Mantém qualidade**: Resposta segue best practices de social selling
- **Não é spam**: Resposta é genuína e útil, não promocional

### Fluxo do Usuário

```
1. Usuário vê lead com AI Insight
2. Clica em "Generate Response"
3. Sistema gera resposta contextualizada
4. Usuário revisa/edita mentalmente
5. Clica "Copy to Clipboard"
6. Cola no Reddit e posta
```

---

## Especificação Técnica

### 1. Dados de Input (já disponíveis)

```typescript
// Post (já existe)
interface Post {
  id: string;
  title: string;
  body: string;
  subreddit: string;
  author: string;
  score: number;
  num_comments: number;
  url: string;
}

// AI Insight (já existe)
interface AIInsight {
  pain_point_summary: string;
  pain_quote: string;
  urgency: "high" | "medium" | "low";
  product_relevance: number;  // 1-10
  relevance_explanation: string;
  suggested_angle: string;
  confidence: number;
}

// Product (já existe)
interface Product {
  id: string;
  name: string;
  description: string;
  pain_signals: string[];
  intent_signals: string[];
}
```

### 2. Novo Output

```typescript
// Generated Response (novo)
interface GeneratedResponse {
  id: string;
  post_id: string;
  product_id: string;
  style: ResponseStyle;
  response_text: string;
  tokens_used: number;
  created_at: string;
}

type ResponseStyle = 
  | "empathetic"      // Para high urgency, problemas pessoais
  | "helpful_expert"  // Para perguntas técnicas
  | "casual"          // Para discussões gerais
  | "technical"       // Para audiências técnicas
  | "brief";          // Para respostas rápidas
```

---

## Backend Implementation

### 3.1 Database Schema

```sql
-- Nova tabela para respostas geradas
CREATE TABLE IF NOT EXISTS generated_responses (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    post_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    style TEXT NOT NULL DEFAULT 'empathetic',
    response_text TEXT NOT NULL,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Tracking futuro (opcional por agora)
    copied_at TIMESTAMP,
    feedback TEXT,  -- 'good', 'bad', 'edited'
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Índice para buscar histórico
CREATE INDEX IF NOT EXISTS idx_responses_post_product 
ON generated_responses(post_id, product_id);
```

### 3.2 Pydantic Models

```python
# radar/models/response.py

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

ResponseStyle = Literal["empathetic", "helpful_expert", "casual", "technical", "brief"]

class GenerateResponseRequest(BaseModel):
    """Request para gerar resposta"""
    product_id: str
    style: ResponseStyle = "empathetic"

class GeneratedResponse(BaseModel):
    """Response gerada"""
    id: str
    post_id: str
    product_id: str
    style: ResponseStyle
    response_text: str
    tokens_used: int
    created_at: datetime

class GenerateResponseResult(BaseModel):
    """Resultado da API"""
    response_text: str
    tokens_used: int
    response_id: str
    style: ResponseStyle
```

### 3.3 Prompts

```python
# radar/services/response_generator.py

RESPONSE_SYSTEM_PROMPT = """You are a helpful Reddit community member who genuinely wants to help others.
You have experience with {product_name} but you NEVER directly promote it or mention it by name.

Your responses must:
1. Feel authentic and human - NOT like marketing copy or AI-generated
2. Provide genuine value and insight FIRST
3. Show empathy by referencing their specific situation
4. Only hint at solutions existing after establishing connection
5. End with an engaging question to continue the conversation
6. Be 80-150 words (Reddit sweet spot for engagement)

CRITICAL RULES - NEVER BREAK THESE:
- NEVER say "I work for [product]" or "You should try [product]"
- NEVER use marketing phrases like "game-changer", "revolutionary", "amazing tool"
- NEVER start with "Hey there!" or "Great question!" (too generic)
- NEVER use bullet points or formatted lists (not natural for Reddit)
- DO reference their specific words/situation to show you read their post
- DO share genuine experiences and subtle hints about solutions
- DO sound like a real person who's been in their shoes
- DO use casual language, contractions, and occasional typos feel OK

Remember: You're a community member FIRST, not a salesperson."""


STYLE_MODIFIERS = {
    "empathetic": """
Tone: Warm, understanding, supportive
Focus: Acknowledge their feelings first, then offer perspective
Voice: Like a friend who's been through something similar
Example phrases: "I totally get it", "Been there", "That's rough"
""",
    "helpful_expert": """
Tone: Knowledgeable but approachable
Focus: Share specific actionable insights
Voice: Like a mentor or experienced colleague
Example phrases: "What worked for me was", "The key thing I learned", "One approach that helps"
""",
    "casual": """
Tone: Relaxed, conversational, friendly
Focus: Light touch, relatable
Voice: Like chatting with a peer
Example phrases: "Yeah honestly", "Haha same", "Lowkey"
""",
    "technical": """
Tone: Detailed, precise, informative
Focus: Specifics and how-tos
Voice: Like a knowledgeable community expert
Example phrases: "Specifically", "The way this works", "In practice"
""",
    "brief": """
Tone: Concise, direct, helpful
Focus: Quick value, no fluff
Voice: Like a busy person giving their best tip
Length: 40-80 words max
Example phrases: "Quick tip:", "Honestly just", "The move is"
"""
}


def build_response_prompt(
    post_title: str,
    post_body: str,
    subreddit: str,
    ai_insight: dict,
    product: dict,
    style: str = "empathetic"
) -> str:
    """Constrói o prompt para geração de resposta"""
    
    # Truncar body se muito longo
    body_preview = post_body[:800] if post_body else "(no body)"
    
    # Pegar pain signals relevantes
    pain_signals = ", ".join(product.get("pain_signals", [])[:5])
    
    style_modifier = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["empathetic"])
    
    return f"""## The Reddit Post You're Responding To

Subreddit: r/{subreddit}
Title: {post_title}

Post Content:
{body_preview}

---

## What We Know About This Person (from analysis)

Their Core Struggle: {ai_insight.get('pain_point_summary', 'Not specified')}

Their Exact Words: "{ai_insight.get('pain_quote', 'Not available')}"

How Urgent This Is: {ai_insight.get('urgency', 'medium')}

---

## Recommended Approach

{ai_insight.get('suggested_angle', 'Be helpful and empathetic')}

---

## Context About Solutions (DO NOT mention directly)

Your experience is with tools that help with: {pain_signals}

General category: {product.get('description', '')[:200]}

---

## Style Instructions

{style_modifier}

---

## Your Task

Write a Reddit comment responding to this post.

Requirements:
1. Start by connecting with their specific situation (reference something they said)
2. Share a relevant insight or experience
3. If appropriate, hint that solutions/tools exist WITHOUT naming any
4. End with a question that invites them to share more

Write the response now (plain text, no markdown formatting):"""
```

### 3.4 Service Layer

```python
# radar/services/response_generator.py

import openai
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Serviço para geração de respostas"""
    
    def __init__(self, db, openai_client=None):
        self.db = db
        self.openai = openai_client or openai.OpenAI()
    
    def generate_response(
        self,
        post_id: str,
        product_id: str,
        style: str = "empathetic"
    ) -> Optional[dict]:
        """
        Gera uma resposta para um post específico.
        
        Args:
            post_id: ID do post
            product_id: ID do produto
            style: Estilo da resposta
            
        Returns:
            Dict com response_text, tokens_used, response_id
        """
        
        # 1. Buscar dados necessários
        post = self.db.get_post(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")
        
        ai_insight = self.db.get_ai_insight(post_id, product_id)
        if not ai_insight:
            raise ValueError(f"No AI insight for post {post_id} and product {product_id}")
        
        product = self.db.get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # 2. Construir prompt
        prompt = build_response_prompt(
            post_title=post.title,
            post_body=post.body or "",
            subreddit=post.subreddit,
            ai_insight=ai_insight,
            product=product,
            style=style
        )
        
        system_prompt = RESPONSE_SYSTEM_PROMPT.format(
            product_name=product.get("name", "your product")
        )
        
        # 3. Chamar OpenAI
        try:
            completion = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.85,  # Mais criativo para parecer natural
                max_tokens=350,
                presence_penalty=0.1,  # Evita repetição
                frequency_penalty=0.1
            )
            
            response_text = completion.choices[0].message.content.strip()
            tokens_used = completion.usage.total_tokens
            
        except Exception as e:
            logger.error(f"OpenAI error generating response: {e}")
            raise
        
        # 4. Salvar no banco
        response_id = self.db.save_generated_response(
            post_id=post_id,
            product_id=product_id,
            style=style,
            response_text=response_text,
            tokens_used=tokens_used
        )
        
        # 5. Retornar resultado
        return {
            "response_text": response_text,
            "tokens_used": tokens_used,
            "response_id": response_id,
            "style": style
        }
    
    def get_response_history(
        self,
        post_id: str,
        product_id: str,
        limit: int = 5
    ) -> list:
        """Retorna histórico de respostas geradas para um post"""
        return self.db.get_generated_responses(
            post_id=post_id,
            product_id=product_id,
            limit=limit
        )
    
    def get_default_style(self, ai_insight: dict) -> str:
        """Determina estilo default baseado no insight"""
        urgency = ai_insight.get("urgency", "medium").lower()
        
        if urgency == "high":
            return "empathetic"
        elif urgency == "low":
            return "casual"
        else:
            return "helpful_expert"
```

### 3.5 API Endpoints

```python
# radar/api/routes/responses.py

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/responses", tags=["responses"])

@router.post("/generate/{post_id}")
async def generate_response(
    post_id: str,
    request: GenerateResponseRequest,
    generator: ResponseGenerator = Depends(get_response_generator)
):
    """
    Gera uma resposta sugerida para um post.
    
    - **post_id**: ID do post para responder
    - **product_id**: ID do produto (para contexto)
    - **style**: Estilo da resposta (empathetic, helpful_expert, casual, technical, brief)
    """
    try:
        result = generator.generate_response(
            post_id=post_id,
            product_id=request.product_id,
            style=request.style
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


@router.get("/history/{post_id}")
async def get_response_history(
    post_id: str,
    product_id: str,
    limit: int = 5,
    generator: ResponseGenerator = Depends(get_response_generator)
):
    """
    Retorna histórico de respostas geradas para um post.
    """
    return generator.get_response_history(
        post_id=post_id,
        product_id=product_id,
        limit=limit
    )


@router.post("/{response_id}/feedback")
async def submit_feedback(
    response_id: str,
    feedback: str,  # "good", "bad", "edited"
    db = Depends(get_db)
):
    """
    Registra feedback sobre uma resposta gerada.
    Útil para melhorar o sistema no futuro.
    """
    db.update_response_feedback(response_id, feedback)
    return {"status": "ok"}
```

### 3.6 Database Functions

```python
# radar/db/responses.py (adicionar ao módulo de DB existente)

def save_generated_response(
    self,
    post_id: str,
    product_id: str,
    style: str,
    response_text: str,
    tokens_used: int
) -> str:
    """Salva resposta gerada e retorna ID"""
    
    response_id = generate_id()  # Sua função de gerar IDs
    
    self.execute("""
        INSERT INTO generated_responses 
        (id, post_id, product_id, style, response_text, tokens_used)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (response_id, post_id, product_id, style, response_text, tokens_used))
    
    return response_id


def get_generated_responses(
    self,
    post_id: str,
    product_id: str,
    limit: int = 5
) -> list:
    """Retorna histórico de respostas para um post"""
    
    rows = self.fetch_all("""
        SELECT id, style, response_text, tokens_used, created_at
        FROM generated_responses
        WHERE post_id = ? AND product_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (post_id, product_id, limit))
    
    return [dict(row) for row in rows]


def update_response_feedback(self, response_id: str, feedback: str):
    """Atualiza feedback de uma resposta"""
    
    self.execute("""
        UPDATE generated_responses
        SET feedback = ?
        WHERE id = ?
    """, (feedback, response_id))
```

---

## Frontend Implementation

### 4.1 Componente: GenerateResponseButton

```tsx
// ui/src/components/GenerateResponseButton.tsx

import { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';

interface Props {
  postId: string;
  productId: string;
  defaultStyle?: string;
  onGenerated: (response: GeneratedResponse) => void;
}

export function GenerateResponseButton({ 
  postId, 
  productId, 
  defaultStyle = 'empathetic',
  onGenerated 
}: Props) {
  const [loading, setLoading] = useState(false);
  
  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/responses/generate/${postId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          product_id: productId, 
          style: defaultStyle 
        })
      });
      
      if (!response.ok) throw new Error('Failed to generate');
      
      const data = await response.json();
      onGenerated(data);
      
    } catch (error) {
      console.error('Error generating response:', error);
      // TODO: Show error toast
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <button
      onClick={handleGenerate}
      disabled={loading}
      className="w-full flex items-center justify-center gap-2 px-4 py-3 
                 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800
                 text-white font-medium rounded-lg transition-colors"
    >
      {loading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          Generating...
        </>
      ) : (
        <>
          <Sparkles className="w-4 h-4" />
          Generate Response
        </>
      )}
    </button>
  );
}
```

### 4.2 Componente: ResponseCard

```tsx
// ui/src/components/ResponseCard.tsx

import { useState } from 'react';
import { Copy, Check, RefreshCw, ExternalLink, ChevronDown } from 'lucide-react';

interface Props {
  response: {
    response_text: string;
    style: string;
    tokens_used: number;
    response_id: string;
  };
  postUrl: string;
  onRegenerate: (style: string) => void;
  availableStyles: string[];
}

const STYLE_LABELS: Record<string, string> = {
  empathetic: '💜 Empathetic',
  helpful_expert: '🎓 Helpful Expert',
  casual: '😊 Casual',
  technical: '🔧 Technical',
  brief: '⚡ Brief'
};

export function ResponseCard({ 
  response, 
  postUrl, 
  onRegenerate,
  availableStyles 
}: Props) {
  const [copied, setCopied] = useState(false);
  const [selectedStyle, setSelectedStyle] = useState(response.style);
  const [showStyleDropdown, setShowStyleDropdown] = useState(false);
  
  const handleCopy = async () => {
    await navigator.clipboard.writeText(response.response_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    
    // Track copy event
    fetch(`/api/responses/${response.response_id}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback: 'copied' })
    });
  };
  
  const handleStyleChange = (style: string) => {
    setSelectedStyle(style);
    setShowStyleDropdown(false);
    onRegenerate(style);
  };
  
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
        <div className="flex items-center gap-2 text-purple-400">
          <span className="text-lg">💬</span>
          <span className="font-medium">Suggested Response</span>
        </div>
        
        {/* Style Selector */}
        <div className="relative">
          <button
            onClick={() => setShowStyleDropdown(!showStyleDropdown)}
            className="flex items-center gap-2 px-3 py-1.5 text-sm 
                       bg-slate-700 hover:bg-slate-600 rounded-md transition-colors"
          >
            {STYLE_LABELS[selectedStyle] || selectedStyle}
            <ChevronDown className="w-4 h-4" />
          </button>
          
          {showStyleDropdown && (
            <div className="absolute right-0 top-full mt-1 w-48 
                            bg-slate-700 border border-slate-600 rounded-lg 
                            shadow-xl z-10 overflow-hidden">
              {availableStyles.map(style => (
                <button
                  key={style}
                  onClick={() => handleStyleChange(style)}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-slate-600
                             ${style === selectedStyle ? 'bg-slate-600' : ''}`}
                >
                  {STYLE_LABELS[style] || style}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Response Text */}
      <div className="p-4">
        <div className="bg-slate-900/50 rounded-lg p-4 text-slate-200 
                        whitespace-pre-wrap leading-relaxed">
          {response.response_text}
        </div>
        
        {/* Token count */}
        <div className="mt-2 text-xs text-slate-500 text-right">
          {response.tokens_used} tokens used
        </div>
      </div>
      
      {/* Actions */}
      <div className="flex items-center gap-3 px-4 py-3 border-t border-slate-700 bg-slate-800/30">
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-4 py-2 
                     bg-purple-600 hover:bg-purple-700 
                     text-white font-medium rounded-lg transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              Copy to Clipboard
            </>
          )}
        </button>
        
        <a
          href={postUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 
                     bg-slate-700 hover:bg-slate-600 
                     text-slate-200 font-medium rounded-lg transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          Open in Reddit
        </a>
        
        <button
          onClick={() => onRegenerate(selectedStyle)}
          className="flex items-center gap-2 px-4 py-2 
                     bg-slate-700 hover:bg-slate-600 
                     text-slate-200 font-medium rounded-lg transition-colors ml-auto"
        >
          <RefreshCw className="w-4 h-4" />
          Regenerate
        </button>
      </div>
    </div>
  );
}
```

### 4.3 Integração no AI Insight Card

```tsx
// Modificar o componente existente do AI Insight Card

import { useState } from 'react';
import { GenerateResponseButton } from './GenerateResponseButton';
import { ResponseCard } from './ResponseCard';

interface AIInsightCardProps {
  postId: string;
  productId: string;
  insight: AIInsight;
  postUrl: string;
}

export function AIInsightCard({ postId, productId, insight, postUrl }: AIInsightCardProps) {
  const [generatedResponse, setGeneratedResponse] = useState<GeneratedResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const availableStyles = ['empathetic', 'helpful_expert', 'casual', 'technical', 'brief'];
  
  // Determinar estilo default baseado no urgency
  const getDefaultStyle = () => {
    if (insight.urgency === 'high') return 'empathetic';
    if (insight.urgency === 'low') return 'casual';
    return 'helpful_expert';
  };
  
  const handleGenerate = async (style?: string) => {
    setIsGenerating(true);
    try {
      const response = await fetch(`/api/responses/generate/${postId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          product_id: productId, 
          style: style || getDefaultStyle()
        })
      });
      
      if (!response.ok) throw new Error('Failed to generate');
      
      const data = await response.json();
      setGeneratedResponse(data);
      
    } catch (error) {
      console.error('Error generating response:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700">
        <span className="text-yellow-400">⚡</span>
        <span className="font-medium text-slate-200">AI Insight</span>
      </div>
      
      {/* Insight Content (existente) */}
      <div className="p-4 space-y-4">
        {/* Pain Point Summary - Headline */}
        <div className="flex items-start justify-between gap-4">
          <p className="text-lg font-medium text-slate-100 leading-snug">
            {insight.pain_point_summary}
          </p>
          <span className={`shrink-0 px-2 py-1 text-xs font-bold rounded
            ${insight.urgency === 'high' ? 'bg-red-500/20 text-red-400' : ''}
            ${insight.urgency === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : ''}
            ${insight.urgency === 'low' ? 'bg-green-500/20 text-green-400' : ''}
          `}>
            {insight.urgency.toUpperCase()} URGENCY
          </span>
        </div>
        
        {/* Pain Quote */}
        <p className="text-slate-400 italic border-l-2 border-slate-600 pl-3">
          "{insight.pain_quote}"
        </p>
        
        {/* Relevance Score */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-purple-500 rounded-full"
              style={{ width: `${insight.product_relevance * 10}%` }}
            />
          </div>
          <span className="text-sm text-slate-400">
            {insight.product_relevance}/10
          </span>
        </div>
        
        {/* Why It Matters */}
        <div>
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
            Why It Matters
          </h4>
          <p className="text-sm text-slate-300">
            {insight.relevance_explanation}
          </p>
        </div>
        
        {/* Suggested Angle */}
        <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-purple-400 uppercase tracking-wide mb-1 flex items-center gap-1">
            <span>💡</span> Suggested Angle
          </h4>
          <p className="text-sm text-purple-200 italic">
            {insight.suggested_angle}
          </p>
        </div>
      </div>
      
      {/* Generate Response Section */}
      <div className="border-t border-slate-700 p-4">
        {!generatedResponse ? (
          <GenerateResponseButton
            postId={postId}
            productId={productId}
            defaultStyle={getDefaultStyle()}
            onGenerated={setGeneratedResponse}
          />
        ) : (
          <ResponseCard
            response={generatedResponse}
            postUrl={postUrl}
            onRegenerate={handleGenerate}
            availableStyles={availableStyles}
          />
        )}
      </div>
    </div>
  );
}
```

---

## Wireframes Finais

### Estado Inicial (antes de gerar)

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚡ AI INSIGHT                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ The user is an independent music artist seeking to      [HIGH]  │
│ maintain a consistent social media presence while       URGENCY │
│ avoiding the stress and burnout...                              │
│                                                                 │
│ "I'm trying to stay OFF social media for my own sanity         │
│  but still need to post consistently."                          │
│                                                                 │
│ ████████████████████░░░░ 9/10                                  │
│                                                                 │
│ WHY IT MATTERS                                                  │
│ SocialGenius can automate the content posting process...        │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 💡 SUGGESTED ANGLE                                          ││
│ │ Empathetic and supportive, highlighting how SocialGenius    ││
│ │ can help them achieve their goals without the stress...     ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            ✨ Generate Response                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Estado Loading

```
┌─────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            ⟳ Generating...                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Estado com Resposta Gerada

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚡ AI INSIGHT                                                   │
├─────────────────────────────────────────────────────────────────┤
│ [... insight content ...]                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 💬 Suggested Response                    [💜 Empathetic ▼]     │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │                                                             ││
│ │ Hey, I really feel you on this one. The pressure to        ││
│ │ constantly show up on social media while trying to         ││
│ │ protect your mental space is such a real struggle,         ││
│ │ especially as an artist.                                   ││
│ │                                                             ││
│ │ What's worked for some creators I know is basically        ││
│ │ treating it like meal prep - batch creating a month's      ││
│ │ worth of content in one focused session, then letting      ││
│ │ it auto-post while they stay logged off.                   ││
│ │                                                             ││
│ │ There are definitely tools out there now that can handle   ││
│ │ the scheduling and even help generate caption ideas if     ││
│ │ you hit a wall.                                            ││
│ │                                                             ││
│ │ Out of curiosity - what type of content works best for     ││
│ │ your music? Reels, behind-the-scenes, or more polished     ││
│ │ posts?                                                      ││
│ │                                                             ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                    245 tokens   │
│                                                                 │
│ [📋 Copy to Clipboard]  [🔗 Open in Reddit]  [🔄 Regenerate]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Critérios de Aceite

### Funcionalidade Core
- [ ] Botão "Generate Response" aparece no AI Insight Card
- [ ] Clicar no botão chama a API e mostra loading state
- [ ] Resposta gerada aparece em área dedicada
- [ ] Resposta é salva no banco de dados
- [ ] Botão "Copy to Clipboard" copia o texto
- [ ] Botão "Open in Reddit" abre o post original
- [ ] Botão "Regenerate" gera nova versão

### Style Selector
- [ ] Dropdown com 5 estilos disponíveis
- [ ] Estilo default baseado no urgency do insight
- [ ] Trocar estilo regenera a resposta
- [ ] Label do estilo visível no dropdown

### Qualidade da Resposta
- [ ] Resposta tem 80-150 palavras
- [ ] Resposta não menciona produto diretamente
- [ ] Resposta referencia situação específica do usuário
- [ ] Resposta termina com pergunta engajadora
- [ ] Resposta parece natural (não AI-generated)

### Edge Cases
- [ ] Funciona mesmo se post não tem body
- [ ] Mostra erro gracefully se API falhar
- [ ] Não permite gerar se não tem AI Insight
- [ ] Loading state previne cliques duplos

---

## Estimativas

| Item | Tempo Estimado |
|------|----------------|
| Backend (DB + Service + API) | 2-3 horas |
| Frontend (Components + Integration) | 3-4 horas |
| Testes e ajustes | 1-2 horas |
| **Total** | **6-9 horas** |

---

## Próximas Fases (Preview)

### Fase 2: Response Styles Avançados
- Adicionar mais estilos customizados
- Permitir usuário criar seus próprios estilos
- Salvar preferência de estilo por produto

### Fase 3: Reddit Profile Indexing
- Ingerir histórico do usuário no Reddit
- Analisar tom e vocabulário
- Criar "voice profile"

### Fase 4: Voice Matching
- Usar voice profile na geração
- Resposta soa como o usuário escreveria
- A/B test de conversão

### Fase 5: Chrome Extension
- Overlay no Reddit
- Generate response inline
- One-click post

---

*Documento criado em: Janeiro 2026*
*Versão: 1.0*
*Autor: Claude + Felipe*