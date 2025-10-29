# 🎮 Gaming_Platform

Plataforma de jogos em linha de comando com catálogo, contas (adulto/infantil/admin), microtransações, ranking + achievements, fórum, patch/update, controle parental, suporte, matchmaking e compatibilidade cross-platform.

---

## 🧱 Arquitetura

**`game.py`** — núcleo de domínio/POO:  
- 🎮 **Jogos**: `Jogo`, `JogoOnline`, `JogoOffline`  
- 👤 **Usuários**: `Usuario` (abstrata), `UsuarioAdulto`, `UsuarioInfantil`, `Admin`  
- ⚙️ **Sistemas**: `POOCoin`, `Achievement`, `PatchNote`, `MatchmakingQueue`, `Match`, `Plataforma`, `PlataformaSingleton`  
- 🏗️ **Design Patterns**: `UsuarioFactory`, `UsuarioBuilder`, `PlataformaFacade`, `ForumAdapter`, `AchievementComposite`

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
| 6   | 💬 Fórum (jogos online + adaptador externo) | ✅ |
| 7   | 🔧 Patches/Updates (admin publica, usuário atualiza) | ✅ |
| 8   | 👪 Controle Parental (aprovação + permissões) | ✅ |
| 9   | 🆘 Suporte/Tickets (Chain of Responsibility) | ✅ |
| 10  | 🖥️ Cross-Platform (metadados + preferência do usuário) | ✅ |

---

## ✨ O que foi adicionado/alterado

### 🔐 Encapsulamento reforçado
- **Usuario**
  - `__senha` com *name mangling* + método `verificar_senha()`  
  - Internos privados: `_jogos_adquiridos`, `_tickets`, `_mensagens`, `_achievements_desbloqueados`  
  - API pública: `possui_jogo()`, `listar_jogos_nomes()`, `abrir_ticket()`, `listar_tickets()`, `adicionar_mensagem()`, `listar_mensagens()`  
  - `saldo` somente leitura 💳  
  - `preferencia_plataforma` validada via setter 🖥️📱🎮  

- **Jogo**
  - Loja privada `_loja`  
  - Métodos seguros: `adicionar_item_loja()`, `listar_itens_loja()`, `obter_preco_item()`  

---

### 🧩 Novos sistemas
- 🏅 **Achievements**: cadastro e desbloqueio automáticos  
- 🔄 **Patch Management**: `versao_atual`, `publicar_patch()`, `listar_patches()`, `atualizar_jogo()`  
- 🤝 **Matchmaking**: `MatchmakingQueue` (fila) + `Match` (partida)  
- 🖥️📱🎮 **Cross-Platform**: `Jogo.plataformas` + `Usuario.preferencia_plataforma`  
- 🧾 **Suporte automatizado**: tickets processados via cadeia de responsabilidade  

---

## 🏗️ Padrões de Projeto

### 🧠 **Criacionais**
| Padrão | Onde | Objetivo |
|--------|------|-----------|
| **Singleton** | `PlataformaSingleton` | Garante uma única instância da plataforma. |
| **Factory Method** | `UsuarioFactory` (`Adulto/Infantil`) | Criação encapsulada de usuários com regras específicas. |
| **Builder** | `UsuarioBuilder` | Montagem passo a passo de `Admin` com saldo e permissões. |

---

### 🎭 **Comportamentais**
| Padrão | Onde | Função |
|--------|------|--------|
| **Strategy** | `CalculadorPontuacao` + `Jogo` | Permite trocar a regra de cálculo de pontuação (normal/bônus). |
| **Visitor** | `JogoVisitor`, `JogoRankingVisitor`, `aceitar_visitor()` | Executa ações em `JogoOnline`/`JogoOffline` sem alterar suas classes. |
| **Chain of Responsibility** | `SuporteHandler`, `AtendimentoBasico/Avancado/Fallback` | Encadeia níveis de suporte para tickets (login, pagamento, geral). |

**👉 Benefício:** comportamento flexível e expansível sem alterar código-base.  

---

### 🧱 **Estruturais**
| Padrão | Onde | Função |
|--------|------|--------|
| **Adapter** | `IForum`, `ForumAdapter`, `ExternalForumAPI` | Permite usar um fórum externo como se fosse interno. |
| **Composite** | `AchievementComponent`, `AchievementLeaf`, `AchievementPack` | Permite tratar vários achievements como um grupo único. |
| **Facade** | `PlataformaFacade` | Simplifica chamadas complexas (cadastro, compra, patch) com uma interface unificada. |

**👉 Benefício:** organização, desacoplamento e reuso de estruturas.  

---

## 💡 Exemplos rápidos

- **Strategy** → `jogo.set_estrategia_pontuacao(CalculadorPontuacaoVIP())` muda a regra de pontuação em tempo real.  
- **Visitor** → `jogo.aceitar_visitor(JogoRankingVisitor())` mostra ranking + fórum (para jogos online).  
- **Chain** → Ticket “senha” é resolvido por `AtendimentoBasico`; “instalação” vai para `AtendimentoAvancado`.  
- **Adapter** → Fórum externo plugado via `ForumAdapter(ExternalForumAPI())`.  
- **Composite** → `AchievementPack` agrupa vários achievements e registra todos de uma vez.  
- **Facade** → `facade.cadastrar_usuario_adulto("João", "joao@mail.com", "123")` em uma única chamada.  

---

## 🧹 Melhorias gerais
- `notify=False` para logs silenciosos na pré-configuração.  
- Padronização de saídas e exibição de menus.  
- Correção de indentação e mensagens no menu do usuário.  

---

## ▶️ Como rodar

### 📌 Pré-requisitos
- Python **3.9+**

### ⚡ Execução
```bash
# Clonar repositório
git clone <seu-repo>.git
cd Gaming_Platform

# Executar
python main.py
