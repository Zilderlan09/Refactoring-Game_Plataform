# 🎮 Gaming_Platform

Plataforma de jogos em linha de comando com catálogo, contas (adulto/infantil/admin), microtransações, ranking + achievements, fórum, patch/update, controle parental, suporte, matchmaking e compatibilidade cross-platform.

---

## 🧱 Arquitetura

**`game.py`** — núcleo de domínio/POO:  
- 🎮 **Jogos**: `Jogo`, `JogoOnline`, `JogoOffline`  
- 👤 **Usuários**: `Usuario` (abstrata), `UsuarioAdulto`, `UsuarioInfantil`, `Admin`  
- ⚙️ **Sistemas**: `POOCoin`, `Achievement`, `PatchNote`, `MatchmakingQueue`, `Match`, `Plataforma`, `PlataformaSingleton`, `PlataformaFacade`  
- 🏗️ **Design Patterns**:  
  - *Criacionais*: `Singleton`, `Factory Method`, `Builder`  
  - *Estruturais*: `Adapter`, `Composite`, `Facade`  
  - *Comportamentais*: `Strategy`, `Visitor`, `Chain of Responsibility`  
  - *Exceção*: `safe_call`, `try_catch_wrapper`, `ValidationError`  

**`main.py`** — interface CLI e menus (admin/usuário).  

---

## ✅ Funcionalidades

| #   | Requisito | Status |
|-----|-----------|--------|
| 1   | 📚 Catálogo de Jogos (loja/itens) | ✅ |
| 2   | 👤 Contas & Preferências (login, saldo, perfis) | ✅ |
| 3   | 🤝 Matchmaking (fila por jogo, partida) | ✅ |
| 4   | 🛒 Microtransações (POOCoin, itens in-game) | ✅ |
| 5   | 🏆 Ranking & Achievements | ✅ |
| 6   | 💬 Fórum (jogos online) | ✅ |
| 7   | 🔧 Patches/Updates (admin publica, usuário atualiza) | ✅ |
| 8   | 👪 Controle Parental (aprovação + permissões) | ✅ |
| 9   | 🆘 Suporte/Tickets (abrir/listar) | ✅ |
| 10  | 🖥️ Cross-Platform (metadados + preferência do usuário) | ✅ |

---

## ✨ O que foi adicionado/alterado

### 🔐 Encapsulamento reforçado
- **Usuario**
  - `__senha` com *name mangling* + método `verificar_senha()`  
  - Internos privados: `_jogos_adquiridos`, `_tickets`, `_mensagens`, `_achievements_desbloqueados`  
  - API pública: `possui_jogo()`, `listar_jogos_nomes()`, `get_registro_jogo()`,  
    `abrir_ticket()`, `listar_tickets()`, `adicionar_mensagem()`, `listar_mensagens()`  
  - `saldo` somente leitura (cópia defensiva) 💳  
  - `preferencia_plataforma` com setter validado + `definir_preferencia_plataforma()` 🖥️📱🎮  

- **Jogo**
  - Loja privada `_loja`  
  - API da loja: `adicionar_item_loja()`, `listar_itens_loja()` (cópia defensiva), `obter_preco_item()`  
  - ✅ Método `verificar_achievements_para()` reintroduzido e herdado por `JogoOnline`, corrigindo `AttributeError`.

---

### 🧩 Novos sistemas
- 🏅 **Achievements**: cadastro por jogo + desbloqueio automático por pontuação  
- 🔄 **Patch Management**: `versao_atual`, `publicar_patch()`, `listar_patches()`, `atualizar_jogo()`  
- 🤝 **Matchmaking**: `MatchmakingQueue` (fila por jogo) + `Match` (partida)  
- 🖥️📱🎮 **Cross-Platform**: `Jogo.plataformas` + `Usuario.preferencia_plataforma` (filtra listagem e valida compra)  
- 🚨 **Tratamento de exceções**: decoradores `@safe_call`, `@try_catch_wrapper` e exceções personalizadas `ValidationError` garantem robustez e estabilidade em operações críticas.  

---

## 🏗️ Padrões Criacionais
| Padrão | Local | Função |
|---------|--------|--------|
| **Singleton** | `PlataformaSingleton` | Garante uma única instância da plataforma. |
| **Factory Method** | `UsuarioAdultoFactory` e `UsuarioInfantilFactory` | Cria usuários de diferentes tipos dinamicamente. |
| **Builder** | `UsuarioBuilder` | Constrói objetos `Admin` passo a passo com saldo inicial e privilégios. |

---

## 🧩 Padrões Estruturais
| Padrão | Local | Função |
|---------|--------|--------|
| **Adapter** | `ForumAdapter` | Adapta APIs externas de fórum (`ExternalForumAPI`) para interface interna (`IForum`). |
| **Composite** | `AchievementPack` | Agrupa achievements em estruturas hierárquicas reutilizáveis. |
| **Facade** | `PlataformaFacade` | Simplifica operações complexas (compra, cadastro, patch) em uma interface única. |

---

## 🧠 Padrões Comportamentais
| Padrão | Local | Função |
|---------|--------|--------|
| **Strategy** | `CalculadorPontuacaoNormal` / `CalculadorPontuacaoBonus` | Define estratégias de cálculo de pontuação intercambiáveis. |
| **Visitor** | `JogoVisitor` e `JogoRankingVisitor` | Permite adicionar novas operações sobre `Jogo` sem alterar suas classes. |
| **Chain of Responsibility** | `SuporteHandler`, `AtendimentoBasico`, `AtendimentoAvancado`, `AtendimentoFallback` | Encadeia níveis de suporte para resolver tickets conforme o tipo. |

---

## ⚡ Tratamento de Exceções
| Padrão | Local | Função |
|---------|--------|--------|
| **safe_call** | Decorador aplicado em métodos da `Plataforma` e `Facade` | Captura exceções em runtime e evita quebra da execução. |
| **try_catch_wrapper** | Wrapper de funções críticas | Garante rollback e logs em falhas internas. |
| **ValidationError** | Classe de exceção personalizada | Lança erros significativos em casos de entrada inválida. |

---

## 🧩 Atualizações Técnicas Recentes

- ✅ Corrigido `AttributeError` em `JogoOnline` (método `verificar_achievements_para` herdado de `Jogo`).  
- ✅ Corrigido `NameError` da classe `MatchmakingQueue`.  
- ✅ Estrutura reorganizada para manter ordem lógica e dependências resolvidas.  
- ✅ Inserção de tratamento de exceções em toda a API da `Plataforma` e `Facade`.  

---

## ▶️ Como rodar

### 📌 Pré-requisitos
- Python **3.9+**

### ⚡ Executando o projeto
```bash
# Clonar o repositório
git clone <seu-repo>.git
cd Gaming_Platform

# Executar
python main.py
