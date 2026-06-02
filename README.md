# Skill de Refatoração Arquitetural Automatizada

Skill agnóstica de tecnologia para análise, auditoria e refatoração de projetos legados para o padrão MVC, utilizando Claude Code.

---

## Análise Manual

### Projeto 1 — code-smells-project (Python/Flask — API de E-commerce)

| # | Severidade | Problema | Arquivo | Justificativa |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection via concatenação de strings | `models.py:27-30, 101` | Queries construídas com `+str(id)` e concatenação direta de inputs de usuário. A função `login_usuario` permite bypass de autenticação com payloads como `' OR '1'='1`. |
| 2 | CRITICAL | Endpoint `/admin/query` executa SQL arbitrário | `app.py:59-75` | Aceita qualquer SQL do body da request sem autenticação — equivale a dar shell de banco para qualquer cliente da rede. |
| 3 | CRITICAL | Credenciais hardcoded (SECRET_KEY) | `app.py:7` | `SECRET_KEY = "minha-chave-super-secreta-123"` commitada no código-fonte; permite forjar cookies de sessão. |
| 4 | HIGH | God File — models.py com 314 LOC | `models.py:1-314` | Arquivo único mistura queries SQL, lógica de negócio, validação e formatação para 4 domínios (produtos, usuários, pedidos, relatórios). |
| 5 | HIGH | Business Logic nos Controllers (Fat Handlers) | `controllers.py:24-79` | Handlers com 50+ linhas contendo validação, regras de negócio, chamadas ao banco e formatação de resposta — impossível testar sem contexto HTTP. |
| 6 | MEDIUM | N+1 Queries nos pedidos | `models.py:163-189` | Loop que para cada pedido faz query de itens, e para cada item busca o produto — crescimento quadrático. |
| 7 | MEDIUM | Ausência de error handling centralizado | `controllers.py:1-292` | Cada handler envolve tudo em `try/except Exception` retornando `str(e)` — vaza detalhes internos (nomes de tabelas, SQL). |
| 8 | LOW | Magic numbers para descontos | `models.py:240-246` | Thresholds de desconto (10000, 5000, 1000) e taxas (0.1, 0.05, 0.02) como literais sem constantes nomeadas. |
| 9 | LOW | Senhas armazenadas em plaintext | `models.py:63-78` | Senhas gravadas como texto puro no banco e retornadas nas respostas da API. |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS API)

| # | Severidade | Problema | Arquivo | Justificativa |
|---|---|---|---|---|
| 1 | CRITICAL | God Class — AppManager.js | `src/AppManager.js:1-120` | Classe única controla banco, rotas, lógica de checkout, relatórios financeiros e exclusão de usuários. Violação completa de SRP. |
| 2 | CRITICAL | Credenciais hardcoded no utils.js | `src/utils.js:1-6` | `dbPass`, `paymentGatewayKey`, `smtpUser` em texto claro no source — comprometem produção. |
| 3 | CRITICAL | Criptografia insegura (badCrypto) | `src/utils.js:14-19` | Base64 repetido 10000x truncado em 10 chars não é hash — trivialmente reversível. |
| 4 | HIGH | Lógica de negócio aninhada nas rotas | `src/AppManager.js:26-72` | Checkout com 47 linhas de callbacks aninhados misturando HTTP + persistence + business rules. |
| 5 | HIGH | Endpoint destrutivo sem autenticação | `src/AppManager.js:109-115` | `DELETE /api/users/:id` sem auth; qualquer cliente anônimo pode deletar usuários. |
| 6 | MEDIUM | N+1 queries no relatório financeiro | `src/AppManager.js:76-107` | Iteração sobre cursos → enrollments → user + payment individualmente. |
| 7 | MEDIUM | Estado mutável compartilhado (globalCache) | `src/utils.js:8-9` | Variáveis module-level mutáveis acessadas por todas as requests simultaneamente. |
| 8 | LOW | Nomes crípticos de variáveis | `src/AppManager.js:28-32` | `u`, `e`, `p`, `cid`, `cc` sem significado aparente sem ler contexto. |
| 9 | LOW | Magic strings para status de pagamento | `src/AppManager.js:41` | `"PAID"`, `"DENIED"` espalhados como literais; `cc.startsWith("4")` como regra de negócio implícita. |

### Projeto 3 — task-manager-api (Python/Flask — API de Task Manager)

| # | Severidade | Problema | Arquivo | Justificativa |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais SMTP hardcoded | `services/notification_service.py:8-9` | Email e senha em texto puro no código-fonte. |
| 2 | CRITICAL | Hash de senha com MD5 (sem salt) | `models/user.py:26-30` | MD5 é criptograficamente quebrado para senhas; vulnerável a rainbow tables. |
| 3 | HIGH | Lógica de negócio nos route handlers | `routes/task_routes.py:12-60` | 50+ linhas de lógica inline no handler (serialização manual, cálculos, queries N+1). |
| 4 | HIGH | N+1 queries na listagem de tasks | `routes/task_routes.py:40-52` | `User.query.get()` e `Category.query.get()` dentro de loop para cada task. |
| 5 | HIGH | SECRET_KEY hardcoded | `app.py:13` | `'super-secret-key-123'` — mesma chave em todos os ambientes. |
| 6 | MEDIUM | Senha exposta na serialização | `models/user.py:16-17` | `to_dict()` inclui hash da senha; retornado em respostas da API. |
| 7 | MEDIUM | Lógica de overdue duplicada 4x | `routes/task_routes.py` (múltiplos locais) | Mesmo cálculo copy-paste em 4 lugares; método `is_overdue()` existe no model mas não é usado. |
| 8 | LOW | Imports não utilizados | `routes/task_routes.py:7` | `json, os, sys, time` importados sem uso. |
| 9 | LOW | Magic strings para status/prioridade | `routes/task_routes.py:94` | `'pending'`, `'done'`, etc. como strings literais; constantes existem em `helpers.py` mas não são usadas. |

---

## Construção da Skill

### Decisões de Design

A skill foi estruturada em 3 fases sequenciais com um `SKILL.md` como "prompt maestro" e 5 arquivos de referência como base de conhecimento:

```
.claude/skills/refactor-arch/
├── SKILL.md                                    # Orchestrador — define o fluxo das 3 fases
├── references/
│   ├── project-analysis.md                     # Heurísticas de detecção de stack
│   ├── anti-patterns-catalog.md                # 14 anti-patterns com sinais abstratos
│   ├── cross-language-signals.md               # Grid de sinais por ecossistema (8 stacks)
│   ├── mvc-architecture-guide.md               # Guidelines de arquitetura MVC alvo
│   └── refactoring-playbook.md                 # 14 padrões de transformação + exemplos
└── assets/
    └── audit-report-template.md                # Template de output da Fase 2
```

**Por que essa separação:**
- O SKILL.md funciona como prompt de alto nível — instrui *o que fazer* em cada fase
- Os arquivos de referência fornecem *conhecimento de domínio* — o agente os consulta conforme necessidade
- Isso permite editar o catálogo de anti-patterns sem mexer no fluxo principal

### Anti-Patterns no Catálogo (14 no total)

| # | Anti-Pattern | Severidade | Motivação da inclusão |
|---|---|---|---|
| 1 | God Class / God File | CRITICAL | Presente nos 3 projetos — é o problema arquitetural mais comum em código legado |
| 2 | Hardcoded Credentials | CRITICAL | Encontrado em todos os projetos; risco imediato de segurança |
| 3 | SQL Injection | CRITICAL | Presente no code-smells-project com impacto devastador |
| 4 | Fat Route Handler | HIGH | Padrão dominante nos 3 projetos — lógica presa ao HTTP |
| 5 | Tight Coupling / No DI | HIGH | Impede testabilidade e substituição de dependências |
| 6 | N+1 Query Problem | HIGH/MEDIUM | Presente nos 3 projetos; performance degrada com crescimento |
| 7 | Missing Input Validation | MEDIUM | Dados inválidos persistidos sem sanitização |
| 8 | Deprecated API Usage | MEDIUM | Necessário para detectar APIs obsoletas por framework |
| 9 | Magic Numbers/Strings | LOW | Melhoria de manutenibilidade encontrada nos 3 projetos |
| 10 | Poor Naming | LOW | Legibilidade; especialmente grave no ecommerce-api-legacy |
| 11 | Unprotected Destructive Endpoints | CRITICAL | Endpoints admin sem auth = risco total |
| 12 | No Error Handling / Bare Exceptions | MEDIUM | Vaza informação interna; dificulta debugging |
| 13 | Sync I/O in Async Context | HIGH | Relevante para Node.js e frameworks async |
| 14 | Mutable Shared State | MEDIUM | globalCache no ecommerce-api — race conditions |

### Agnosticismo de Tecnologia

A skill é agnóstica porque:

1. **Sinais abstratos:** O catálogo define anti-patterns por conceito (e.g., "valor sensível como literal em código fonte") — não por sintaxe
2. **Grid de sinais por linguagem:** O `cross-language-signals.md` mapeia como cada anti-pattern se manifesta em Python, JavaScript, Go, Ruby, Rust, Java, TypeScript e PHP
3. **Fallback para stacks desconhecidas:** O playbook inclui uma seção "Pattern X on an Unknown Stack" com procedimento genérico
4. **Heurísticas de detecção progressivas:** `project-analysis.md` usa manifest → imports → file patterns para identificar qualquer stack
5. **Target architecture adaptável:** O `mvc-architecture-guide.md` mapeia o padrão MVC para cada ecossistema, respeitando idiomas (e.g., Express usa `controllers/` com classes, Flask usa blueprints)

### Desafios e Soluções

| Desafio | Solução |
|---|---|
| Projetos com níveis diferentes de organização | A Fase 1 classifica a arquitetura atual (monolítica, parcialmente organizada, etc.) e a Fase 3 adapta as transformações — não força MVC puro em quem já tem separação |
| Node.js com callbacks vs Python síncrono | Playbook tem exemplos before/after nas duas linguagens para cada transformação |
| Evitar false positives em audit | Sinais de detecção exigem 2+ critérios combinados antes de reportar um finding |
| Validação pós-refatoração | Fase 3 tenta boot + test de endpoints; itera até 3x se falhar |

---

## Resultados

### Resumo dos Relatórios de Auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| code-smells-project | 4 | 3 | 3 | 2 | 12 |
| ecommerce-api-legacy | 3 | 2 | 3 | 2 | 10 |
| task-manager-api | 2 | 3 | 3 | 2 | 10 |

### Comparação Antes/Depois

#### Projeto 1 — code-smells-project

**Antes:**
```
code-smells-project/
├── app.py              (monolito — routes + admin endpoints)
├── controllers.py      (292 LOC — fat handlers)
├── models.py           (314 LOC — god file)
├── database.py         (global state)
└── requirements.txt
```

**Depois:**
```
code-smells-project/
├── src/
│   ├── app.py                     (composition root)
│   ├── config/
│   │   └── database.py            (config via env vars)
│   ├── controllers/
│   │   ├── order_controller.py
│   │   ├── product_controller.py
│   │   └── user_controller.py
│   ├── models/
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   ├── routes/
│   │   ├── admin_routes.py
│   │   ├── order_routes.py
│   │   ├── product_routes.py
│   │   └── user_routes.py
│   ├── middlewares/
│   │   └── error_handler.py
│   └── utils/
└── requirements.txt
```

#### Projeto 2 — ecommerce-api-legacy

**Antes:**
```
ecommerce-api-legacy/src/
├── app.js
├── AppManager.js       (god class — 120 LOC, tudo junto)
└── utils.js            (credenciais + crypto insegura)
```

**Depois:**
```
ecommerce-api-legacy/src/
├── app.js                          (composition root com DI)
├── config/
│   ├── settings.js                 (env vars)
│   └── constants.js
├── controllers/
│   ├── checkoutController.js
│   ├── reportController.js
│   └── userController.js
├── models/
│   ├── database.js
│   ├── userModel.js
│   ├── courseModel.js
│   ├── enrollmentModel.js
│   ├── paymentModel.js
│   └── auditLogModel.js
├── routes/
│   └── index.js
└── middlewares/
    └── errorHandler.js
```

#### Projeto 3 — task-manager-api

**Antes:**
```
task-manager-api/
├── app.py              (SECRET_KEY hardcoded)
├── database.py
├── models/             (MD5 password hash)
├── routes/             (fat handlers com N+1 queries)
├── services/           (credenciais SMTP hardcoded)
└── utils/
```

**Depois:**
```
task-manager-api/
├── app.py              (config via env vars)
├── config.py           (centralizado)
├── database.py
├── controllers/        (lógica extraída dos routes)
│   ├── task_controller.py
│   ├── user_controller.py
│   └── report_controller.py
├── models/             (password hash com werkzeug)
├── routes/             (thin handlers — parse → call → respond)
├── services/           (credenciais via env)
└── utils/
```

### Checklist de Validação

#### Projeto 1 — code-smells-project

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce API)
- [x] Número de arquivos analisados condiz com a realidade (4)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (12 encontrados)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro (src/app.py)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 2 — ecommerce-api-legacy

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (JavaScript)
- [x] Framework detectado corretamente (Express 4.18.2)
- [x] Domínio da aplicação descrito corretamente (LMS API com checkout)
- [x] Número de arquivos analisados condiz com a realidade (3)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] Mínimo de 5 findings identificados (10 encontrados)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para config/settings.js (env vars)
- [x] Models criados (User, Course, Enrollment, Payment, AuditLog)
- [x] Routes separadas
- [x] Controllers com DI (recebem models no construtor)
- [x] Error handling centralizado (errorHandler middleware)
- [x] Entry point claro (src/app.js como composition root)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 3 — task-manager-api

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0)
- [x] Domínio da aplicação descrito corretamente (Task Manager)
- [x] Número de arquivos analisados condiz com a realidade (11)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] Mínimo de 5 findings identificados (10 encontrados)
- [x] Detecção de APIs deprecated incluída (MD5 → werkzeug hashing)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC (preservou organização existente + adicionou controllers)
- [x] Configuração extraída para config.py (env vars)
- [x] Models com hash seguro de senha
- [x] Routes thin (delegam para controllers)
- [x] Controllers concentram lógica de negócio
- [x] Error handling centralizado
- [x] Entry point claro (app.py)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

### Observações sobre Comportamento Cross-Stack

- **Python/Flask monolito (P1):** A skill reestruturou completamente — criou `src/` com separação total de camadas
- **Node.js/Express (P2):** Decomposição do God Class em 6 models + 3 controllers com DI via construtor; padrão idiomático do Express
- **Python/Flask parcialmente organizado (P3):** A skill *preservou* a estrutura existente (models/, routes/, services/) e *adicionou* controllers/ para extrair lógica dos route handlers — demonstrando adaptação ao contexto

---

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e configurado
- Python 3.10+ (para projetos 1 e 3)
- Node.js 18+ (para projeto 2)

### Execução da Skill

```bash
# Projeto 1 — code-smells-project
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api
cd ../task-manager-api
claude "/refactor-arch"
```

A skill executa 3 fases sequencialmente:
1. **Fase 1** — Detecta stack e imprime resumo
2. **Fase 2** — Gera relatório de auditoria e **pede confirmação** antes de prosseguir
3. **Fase 3** — Refatora para MVC e valida que a aplicação funciona

### Validação Pós-Refatoração

```bash
# Projeto 1
cd code-smells-project
pip install -r requirements.txt
python -m src.app
# Testar: curl http://localhost:5000/health

# Projeto 2
cd ecommerce-api-legacy
npm install
npm start
# Testar: curl http://localhost:3000/api/admin/financial-report

# Projeto 3
cd task-manager-api
pip install -r requirements.txt
python app.py
# Testar: curl http://localhost:5000/health
```

### Estrutura do Repositório

```
.
├── README.md
├── code-smells-project/
│   ├── .claude/skills/refactor-arch/    ← Skill original
│   └── src/                             ← Código refatorado
├── ecommerce-api-legacy/
│   ├── .claude/skills/refactor-arch/    ← Cópia da skill
│   └── src/                             ← Código refatorado
├── task-manager-api/
│   ├── .claude/skills/refactor-arch/    ← Cópia da skill
│   └── (estrutura preservada + controllers/)
└── reports/
    ├── audit-project-1.md
    ├── audit-project-2.md
    └── audit-project-3.md
```
