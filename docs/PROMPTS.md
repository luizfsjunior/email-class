# 🤖 Prompts para LLM - Email Classifier

Este documento contém os prompts utilizados pelo sistema para classificação de emails e geração de respostas, incluindo variações para A/B testing.

---

## 📋 Índice

1. [Prompt de Classificação](#prompt-de-classificação)
2. [Prompt de Geração de Resposta](#prompt-de-geração-de-resposta)
3. [Variações para A/B Testing](#variações-para-ab-testing)
4. [Boas Práticas](#boas-práticas)

---

## 🎯 Prompt de Classificação

### Versão Principal (Produção)

**Localização:** `server/app/services/ai_client.py` → `_build_classification_prompt()`

**Instruções do System Message:**
```
Você é um classificador especialista. CALIBRE a confiança baseada em: clareza do email (0.90-0.99 se muito claro, 0.70-0.85 se ambíguo, 0.60-0.70 se confuso), completude de informações (mais dados = maior confiança), e certeza da categoria. Detecte spam por: links, linguagem marketing ('ganhe', 'promoção', '50% OFF'), urgência artificial. Seja preciso na confiança - não use sempre valores altos. Responda em JSON válido.
```

**User Prompt (resumido):**
```
Você é um classificador especialista em triagem de emails corporativos.

📋 CLASSIFICAÇÃO E PRECISÃO:

A "precisão" (confidence) reflete quão CERTO o modelo está da classificação, baseado na clareza e completude da informação.

**CATEGORIA IMPRODUTIVO** (não requer ação):
• Agradecimentos puros → Precisão: 0.95-0.99
• Felicitações/Saudações → Precisão: 0.95-0.99
• Confirmações simples → Precisão: 0.92-0.97
• Problemas JÁ resolvidos → Precisão: 0.90-0.95
• Elogios ao atendimento → Precisão: 0.93-0.98
• SPAM/Propaganda → Precisão: 0.88-0.95 (links suspeitos, "clique aqui", "ganhe já", linguagem marketing)
• Avisos informativos → Precisão: 0.85-0.92

**CATEGORIA PRODUTIVO** (requer ação):
• Solicitação específica com dados → Precisão: 0.92-0.98
• Problema atual não resolvido → Precisão: 0.88-0.95
• Dúvida que exige resposta → Precisão: 0.85-0.93
• Reclamação que demanda ação → Precisão: 0.87-0.94
• Urgência explícita → Precisão: 0.90-0.96

**CASOS AMBÍGUOS** (reduzir precisão):
• Email misto → Precisão: 0.70-0.85
• Contexto incompleto → Precisão: 0.65-0.80
• Linguagem pouco clara → Precisão: 0.60-0.75

[8 exemplos detalhados com precisão calibrada]

EMAIL:
{{EMAIL_TEXT}}

Responda APENAS com JSON:
{"category": "Produtivo" | "Improdutivo", "confidence": 0.60-0.99, "reason": "explique em 25-50 palavras a decisão E por que a precisão está nesse nível"}
```

**Configuração:**
- Model: `gpt-4o-mini`
- Temperature: `0.3` (baixa criatividade, mais consistência)
- Max Tokens: `500`
- Response Format: `json_object` (força JSON válido)

**Exemplo de Response:**
```json
{
  "category": "Produtivo",
  "confidence": 0.92,
  "reason": "Email solicita atualização de chamado com prazo definido. Alta precisão pela clareza da demanda e dados fornecidos."
}
```

**Indicadores de Spam Detectados:**
- Links suspeitos (www., http)
- Linguagem marketing: "promoção", "ganhe", "desconto", "clique aqui", "oferta", "grátis"
- Urgência artificial: "imperdível", "limitado", "exclusivo", "acesse já"
- Fraude: "parabéns você ganhou", "foi selecionado", "prêmio", "sorteio"

---

## ✉️ Prompt de Geração de Resposta

### Versão Principal (Produção)

**Localização:** `server/app/services/ai_client.py` → `_build_reply_prompt()`

**Instruções do System Message:**
```
Você é um atendente humano experiente que escreve respostas personalizadas, empáticas e contextualizadas. Nunca use templates genéricos.
```

**User Prompt (estrutura):**
```
Você é um atendente experiente de instituição financeira que escreve respostas humanizadas.

Email recebido:
{{ORIGINAL_TEXT}}

Categoria: {{CATEGORY}}
Resumo: {{SUMMARY}}
Spam detectado: {{IS_SPAM}}

[Instruções condicionais baseadas em categoria/spam]

Responda em JSON:
{"reply":"texto da resposta (2-5 linhas, máximo 80 palavras)", "tone":"profissional|empático|cordial|firme", "max_words":80}
```

**Instruções Condicionais:**

1. **Se SPAM:**
```
Gere uma resposta CURTA, FIRME e PROFISSIONAL que:
- NÃO agradeça nem demonstre interesse
- Informe que mensagens comerciais não são aceitas neste canal
- Seja educada mas assertiva
- Seja breve (1-2 linhas)

Exemplo: "Esta mensagem foi identificada como spam. Não aceitamos promoções comerciais neste canal de atendimento."
```

2. **Se PRODUTIVO:**
```
Gere uma resposta personalizada e PROATIVA que:
- Reconheça ESPECIFICAMENTE o assunto mencionado (use detalhes do email)
- Se houver número de protocolo/chamado/pedido, MENCIONE-O
- Indique próximos passos CONCRETOS (ex: "vamos verificar no sistema")
- Se possível, dê prazo aproximado (24-48h úteis)
- Use tom empático mas profissional
- Personalize com base no contexto (urgência, tipo de problema)

Evite: "recebemos sua solicitação" (muito genérico). Seja ESPECÍFICO.
```

3. **Se IMPRODUTIVO:**
```
Gere uma resposta CALOROSA e BREVE que:
- Agradeça de forma PERSONALIZADA ao contexto específico
- Reconheça o sentimento/ação expressa (agradecimento, felicitação, etc)
- Reforce disponibilidade de forma GENUÍNA
- Seja breve (2-3 linhas no máximo)
- Adapte o tom ao email recebido

Evite: fórmulas prontas genéicas. Cada resposta deve parecer única.
```

**Configuração:**
- Model: `gpt-4o-mini`
- Temperature: `0.7` (maior criatividade para respostas personalizadas)
- Max Tokens: `500`

**Exemplo de Response:**
```json
{
  "reply": "Olá! Verificamos sua solicitação sobre o chamado #12345. Nossa equipe técnica já iniciou a análise e você receberá uma atualização detalhada em até 24 horas úteis. Agradecemos a paciência!",
  "tone": "empático",
  "max_words": 35
}
```

---

## 🧪 Propostas para A/B Testing Futuro

O sistema atual usa prompts otimizados (documentados acima). Abaixo estão **propostas experimentais** para testes futuros.

### Estratégias de Teste

#### Teste 1: Ajuste de Precisão

| Versão | Configuração | Hipótese |
|--------|-------------|----------|
| A (atual) | Escala 0.60-0.99 com faixas | Calibração precisa |
| B | Escala 0.70-1.0 (mais confiante) | Usuários preferem alta confiança |
| C | Escala 0.50-0.95 (mais ampla) | Melhor diferenciação de casos |

**Métrica:** Correlação entre confiança e feedback humano

---

#### Teste 2: Quantidade de Exemplos

| Versão | Estrutura | Hipótese |
|--------|-----------|----------|
| A (atual) | 8 exemplos detalhados | Equilíbrio atual |
| B | 3-4 exemplos (simplificado) | Menor latência, mesma acurácia |
| C | 12+ exemplos (expandido) | Maior acurácia em casos edge |

**Métrica:** Acurácia vs latência vs custo

---

#### Teste 3: Tratamento de Spam

| Versão | Abordagem | Trade-off |
|--------|----------|-----------|
| A (atual) | 15 indicadores, resposta firme | Equilíbrio atual |
| B | 5 indicadores (conservador) | Menos falsos positivos |
| C | 25+ indicadores (agressivo) | Maior recall, possíveis falsos positivos |

**Métrica:** Precision vs Recall de detecção de spam

---

**Métrica:** Precision vs Recall de detecção de spam

---

#### Teste 4: Temperature de Respostas

| Versão | Temperature | Hipótese |
|--------|-------------|----------|
| A (atual) | 0.7 | Equilíbrio criatividade/consistência |
| B | 0.5 | Respostas mais consistentes |
| C | 0.9 | Máxima personalização |

**Métrica:** Taxa de edição + rating de qualidade

---

#### Teste 5: Tamanho de Contexto

| Versão | Input Truncado | Trade-off |
|--------|---------------|-----------|
| A (atual) | 2000 chars | Equilíbrio atual |
| B | 1000 chars | Menor custo, mais rápido |
| C | 4000 chars | Contexto completo, mais caro |

**Métrica:** Custo vs acurácia vs latência

---

## 📊 Monitoramento e Otimização

### Métricas a Acompanhar

1. **Acurácia de Classificação**
   - Target: >90%
   - Medição: Comparar com labels humanos

2. **Qualidade de Resposta**
   - Rating médio (1-5 estrelas)
   - Taxa de edição (% respostas editadas)
   - NPS (feedback qualitativo)

3. **Performance**
   - Latência média (target: <2s)
   - Taxa de erro OpenAI
   - Custo por classificação
   - Taxa de detecção de spam (precision/recall)

---

## ✅ Boas Práticas

### Prompt Engineering

1. **Seja Específico**: Defina exatamente o formato de output
2. **Use JSON Schema**: Force estrutura com `response_format`
3. **Limite Output**: Defina `max_tokens` para evitar respostas longas
4. **Temperature Calibrada**: Use 0.3 para classificação (consistência), 0.7 para respostas (criatividade)
5. **System Message**: Sempre defina contexto geral e comportamento esperado
6. **Sanitize Input**: Limite tamanho de input (evite custos excessivos)
7. **Calibração de Confiança**: Use escalas baseadas em clareza (0.60-0.99), não em importância
8. **Detecção de Spam**: Liste indicadores específicos no prompt para identificação consistente

### Segurança

1. **Não exponha dados sensíveis**: Remova PII antes de enviar ao LLM
2. **Rate Limiting**: Implemente throttling
3. **Timeout**: Defina timeout de 10s max
4. **Log de Prompts**: Salve prompts para auditoria (sem dados sensíveis)

### Otimização de Custos

1. **Cache de Respostas**: Mesma pergunta = mesma resposta (hash do texto)
2. **Batch Processing**: Agrupe múltiplas classificações quando possível
3. **Modelo Adequado**: GPT-4o-mini (~$0.15/1M tokens) vs GPT-4 (~$30/1M tokens) - 200x diferença
4. **Truncate Input**: Primeiros 2000 chars geralmente suficientes
5. **Monitor Usage**: Alerta quando ultrapassar budget
6. **Temperature Apropriada**: 0.3 para classificação economiza tokens vs 0.7+

---

## 🔄 Versionamento de Prompts

### Como Versionar

1. Cada mudança significativa = nova versão
2. Documente em git commit
3. Salve métricas de cada versão
4. A/B test antes de rollout completo

### Template de Changelog

```markdown
## v1.2 - 2025-11-10

### Classificação
- Adicionada calibração de precisão (0.60-0.99 baseado em clareza)
- Implementada detecção de spam com 15+ indicadores
- System message expandido com instruções de calibração
- Aumentado confidence threshold de 0.7 para 0.8

### Geração de Respostas
- Temperature alterada de 0.3 para 0.7 (respostas mais personalizadas)
- Adicionado tratamento específico para spam (tom firme)
- Instruções condicionais por categoria (Produtivo/Improdutivo/Spam)
- System message focado em humanização

### Resultados
- Precisão: 87% → 91%
- Latência: 1.8s → 1.5s
- Custo: $0.002 → $0.0015 por classificação
- Spam detection: 0% → 94% recall
```

---


## 📚 Referências

- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangChain Prompt Templates](https://python.langchain.com/docs/modules/model_io/prompts/)

---

**Versão do sistema:** 1.0.0  
**Modelo primário:** gpt-4o-mini
