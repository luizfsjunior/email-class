"""
AI Client abstraction - Interface para LLMs (OpenAI, HuggingFace, etc)
Permite trocar provider facilmente e implementa fallback strategy
"""
import json
import logging
from typing import Dict, Optional, Literal
from openai import AsyncOpenAI
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

CategoryType = Literal["Produtivo", "Improdutivo"]


class AIClient:
    """Cliente abstrato para chamadas LLM com fallback"""
    
    def __init__(self):
        self.settings = get_settings()
        
        if not self.settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada. Configure a chave em server/.env")
        
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        logger.info("OpenAI client inicializado")
    
    async def classify_email(self, text: str) -> Dict:
        """
        Classifica email usando LLM
        
        Returns:
            Dict com: category, confidence, reason
        """
        prompt = self._build_classification_prompt(text)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "Você é um classificador especialista. CALIBRE a confiança baseada em: clareza do email (0.90-0.99 se muito claro, 0.70-0.85 se ambíguo, 0.60-0.70 se confuso), completude de informações (mais dados = maior confiança), e certeza da categoria. Detecte spam por: links, linguagem marketing ('ganhe', 'promoção', '50% OFF'), urgência artificial. Seja preciso na confiança - não use sempre valores altos. Responda em JSON válido."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # DEBUG: Log da resposta RAW da OpenAI
            logger.info("=" * 60)
            logger.info("🤖 RESPOSTA RAW DA OPENAI:")
            logger.info(f"Texto analisado (primeiros 100 chars): {text[:100]}")
            logger.info(f"Resposta JSON: {content}")
            logger.info("=" * 60)
            
            result = json.loads(content)
            
            # Valida campos obrigatórios
            if "category" not in result or "confidence" not in result:
                raise ValueError("Resposta LLM sem campos obrigatórios")
            
            # Normaliza categoria
            result["category"] = self._normalize_category(result["category"])
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao chamar OpenAI: {str(e)}")
            raise
    
    async def generate_reply(self, category: CategoryType, summary: str, original_text: str) -> Dict:
        """
        Gera resposta sugerida usando LLM
        
        Returns:
            Dict com: reply, tone, max_words
        """
        prompt = self._build_reply_prompt(category, summary, original_text)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um atendente humano experiente que escreve respostas personalizadas, empáticas e contextualizadas. Nunca use templates genéricos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Temperatura mais alta para respostas criativas
                max_tokens=self.settings.LLM_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            if "reply" not in result:
                raise ValueError("Resposta LLM sem campo 'reply'")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            raise
    
    def _build_classification_prompt(self, text: str) -> str:
        """Constrói prompt de classificação"""
        return f"""Você é um classificador especialista em triagem de emails corporativos.

📋 CLASSIFICAÇÃO E PRECISÃO:

A "precisão" (confidence) reflete quão CERTO o modelo está da classificação, baseado na clareza e completude da informação.

**CATEGORIA IMPRODUTIVO** (não requer ação):
• Agradecimentos puros → Precisão: 0.95-0.99
• Felicitações/Saudações → Precisão: 0.95-0.99
• Confirmações simples → Precisão: 0.92-0.97
• Problemas JÁ resolvidos → Precisão: 0.90-0.95
• Elogios ao atendimento → Precisão: 0.93-0.98
• SPAM/Propaganda → Precisão: 0.88-0.95 (identificadores: links suspeitos, promoções genéricas, "clique aqui", "ganhe já", linguagem de marketing agressivo, ofertas não solicitadas)
• Avisos informativos → Precisão: 0.85-0.92

**CATEGORIA PRODUTIVO** (requer ação):
• Solicitação específica com dados → Precisão: 0.92-0.98
• Problema atual não resolvido → Precisão: 0.88-0.95
• Dúvida que exige resposta → Precisão: 0.85-0.93
• Reclamação que demanda ação → Precisão: 0.87-0.94
• Urgência explícita → Precisão: 0.90-0.96

**CASOS AMBÍGUOS** (reduzir precisão):
• Email misto (agradecimento + nova dúvida) → Analise qual predomina, precisão: 0.70-0.85
• Contexto incompleto → Precisão: 0.65-0.80
• Linguagem pouco clara → Precisão: 0.60-0.75

---

**EXEMPLOS COM PRECISÃO CALIBRADA:**

Email: "Obrigado!"
{{"category": "Improdutivo", "confidence": 0.98, "reason": "Agradecimento puro sem contexto adicional ou demanda. Precisão alta por clareza total."}}

Email: "PROMOÇÃO! Ganhe 50% OFF. Clique aqui: www.exemplo.com"
{{"category": "Improdutivo", "confidence": 0.92, "reason": "Spam/propaganda com linguagem de marketing agressivo e link comercial. Precisão alta."}}

Email: "Feliz Natal a todos da equipe!"
{{"category": "Improdutivo", "confidence": 0.99, "reason": "Felicitação sazonal sem qualquer solicitação. Classificação óbvia, precisão máxima."}}

Email: "Problema resolvido, funcionou!"
{{"category": "Improdutivo", "confidence": 0.94, "reason": "Confirmação de resolução sem nova demanda. Alta precisão pela clareza."}}

Email: "Preciso atualizar meu endereço para Rua das Flores, 123, São Paulo"
{{"category": "Produtivo", "confidence": 0.95, "reason": "Solicitação específica de atualização cadastral com dados completos. Precisão alta."}}

Email: "Quando fica pronto?"
{{"category": "Produtivo", "confidence": 0.78, "reason": "Dúvida válida mas contexto incompleto reduz precisão."}}

Email: "Obrigado pela ajuda. Mas tenho outra dúvida sobre taxas"
{{"category": "Produtivo", "confidence": 0.83, "reason": "Apesar do agradecimento, há nova dúvida que demanda resposta. Precisão moderada-alta."}}

Email: "Descubra como GANHAR DINHEIRO rápido! Acesse agora"
{{"category": "Improdutivo", "confidence": 0.95, "reason": "Spam clássico com linguagem sensacionalista e promessa financeira genérica. Precisão alta."}}

---

🎯 ANALISE ESTE EMAIL:

EMAIL:
\"\"\"
{text[:2000]}
\"\"\"

**INSTRUÇÕES:**
1. Identifique a intenção PRINCIPAL do email
2. Avalie clareza do contexto e dados fornecidos
3. Detecte indicadores de spam (links, linguagem marketing, "ganhe", "promoção", ofertas não solicitadas)
4. Calibre precisão baseada em CERTEZA da classificação (não em importância)
5. Seja RIGOROSO: se há agradecimento/felicitação/confirmação SEM nova demanda → Improdutivo

Responda APENAS com JSON:
{{"category": "Produtivo" | "Improdutivo", "confidence": 0.60-0.99, "reason": "explique em 25-50 palavras a decisão E por que a precisão está nesse nível"}}"""
    
    def _build_reply_prompt(self, category: CategoryType, summary: str, original_text: str) -> str:
        """Constrói prompt de geração de resposta"""
        
        # Detecta spam no texto original
        spam_indicators = [
            "promoção", "ganhe", "desconto", "clique aqui", "oferta", "grátis", "gratuito",
            "www.", "http", "click", "acesse já", "imperdível", "limitado", "exclusivo",
            "parabéns você ganhou", "foi selecionado", "prêmio", "sorteio"
        ]
        is_spam = any(indicator in original_text.lower() for indicator in spam_indicators)
        
        if is_spam:
            instruction = """Este email é SPAM/Propaganda comercial não solicitado. Gere uma resposta CURTA, FIRME e PROFISSIONAL que:
1. NÃO agradeça nem demonstre interesse
2. Informe que mensagens comerciais não são aceitas neste canal
3. Seja educada mas assertiva
4. Seja breve (1-2 linhas)

EXEMPLOS DE RESPOSTAS ADEQUADAS:
• "Esta mensagem foi identificada como spam. Não aceitamos promoções comerciais neste canal de atendimento."
• "Mensagens promocionais não solicitadas serão bloqueadas. Este não é o canal adequado para ofertas comerciais."
• "Email marcado como spam. Para contato comercial, utilize nossos canais oficiais de marketing."

NÃO use: agradecimentos, "obrigado por entrar em contato", "ficamos felizes", ou qualquer linguagem que incentive mais mensagens."""
        elif category == "Produtivo":
            instruction = """Gere uma resposta personalizada e PROATIVA que:
1. Reconheça ESPECIFICAMENTE o assunto mencionado (use detalhes do email)
2. Se houver número de protocolo/chamado/pedido, MENCIONE-O
3. Indique próximos passos CONCRETOS (ex: "vamos verificar no sistema", "nossa equipe analisará")
4. Se possível, dê prazo aproximado (24-48h úteis)
5. Use tom empático mas profissional
6. Personalize com base no contexto (urgência, tipo de problema)

Evite: "recebemos sua solicitação" (muito genérico). Seja ESPECÍFICO ao problema."""
        else:
            instruction = """Gere uma resposta CALOROSA e BREVE que:
1. Agradeça de forma PERSONALIZADA ao contexto específico
2. Reconheça o sentimento/ação expressa (agradecimento, felicitação, etc)
3. Reforce disponibilidade de forma GENUÍNA
4. Seja breve (2-3 linhas no máximo)
5. Adapte o tom ao email recebido

Evite: fórmulas prontas genéricas. Cada resposta deve parecer única."""
        
        return f"""Você é um atendente experiente de instituição financeira que escreve respostas humanizadas.

Email recebido:
\"\"\"
{original_text[:800]}
\"\"\"

Categoria: {category}
Resumo: {summary}
Spam detectado: {is_spam}

{instruction}

Responda em JSON:
{{"reply":"texto da resposta (2-5 linhas, máximo 80 palavras)", "tone":"profissional|empático|cordial|firme", "max_words":80}}"""
    
    def _normalize_category(self, category: str) -> CategoryType:
        """Normaliza categoria para valores aceitos"""
        cat_lower = category.lower().strip()
        # IMPORTANTE: Verificar "improdutivo" ANTES de "produtivo" 
        # porque "improdutivo" contém "produtivo"!
        if "improdutivo" in cat_lower:
            return "Improdutivo"
        elif "produtivo" in cat_lower or "productive" in cat_lower:
            return "Produtivo"
        return "Improdutivo"  # Default seguro


# Singleton instance
_ai_client: Optional[AIClient] = None

def get_ai_client() -> AIClient:
    """Retorna instância singleton do AI client"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
