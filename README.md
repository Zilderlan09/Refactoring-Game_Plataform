# 🎮 Gaming_Platform

Plataforma de jogos em linha de comando com catálogo, contas (adulto/infantil/admin), microtransações, ranking + achievements, fórum, patch/update, controle parental, suporte, matchmaking e compatibilidade cross-platform.

---

## 🧱 Arquitetura

**`game.py`** — núcleo de domínio/POO:  
- 🎮 **Jogos**: `Jogo`, `JogoOnline`, `JogoOffline`  
- 👤 **Usuários**: `Usuario` (abstrata), `UsuarioAdulto`, `UsuarioInfantil`, `Admin`  
- ⚙️ **Sistemas**: `POOCoin`, `Achievement`, `PatchNote`, `MatchmakingQueue`, `Match`, `Plataforma`, `PlataformaSingleton`  
- 🏗️ **Design Patterns**: `UsuarioFactory`, `UsuarioAdultoFactory`, `UsuarioInfantilFactory`, `UsuarioBuilder`

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

---

### 🧩 Novos sistemas
- 🏅 **Achievements**: cadastro por jogo + desbloqueio automático por pontuação  
- 🔄 **Patch Management**: `versao_atual`, `publicar_patch()`, `listar_patches()`, `atualizar_jogo()`  
- 🤝 **Matchmaking**: `MatchmakingQueue` (fila por jogo) + `Match` (partida)  
- 🖥️📱🎮 **Cross-Platform**: `Jogo.plataformas` + `Usuario.preferencia_plataforma` (filtra listagem e valida compra)  

---

### 🏗️ Padrões Criacionais
- 🔹 **Singleton** → `PlataformaSingleton`, garante uma única instância da plataforma.  
- 🔹 **Factory Method** → `UsuarioAdultoFactory` e `UsuarioInfantilFactory`, responsáveis por criar usuários.  
- 🔹 **Builder** → `UsuarioBuilder`, usado para criar Admin passo a passo (com saldo inicial e privilégios).  

---

### 🧠 Padrões Comportamentais Adicionados

- 🔹 **Visitor**:  
  Permite adicionar novas operações a objetos sem alterar suas classes. No contexto da plataforma de jogos, o padrão Visitor foi utilizado para aplicar ações ou verificações nos objetos do tipo **Jogo** sem modificar suas classes.  
  - **Exemplo**: A funcionalidade de aplicar um "desconto" nos jogos ou gerar relatórios de desempenho pode ser realizada com o Visitor, sem mexer diretamente no código das classes **Jogo**.

- 🔹 **Strategy**:  
  Define uma família de algoritmos, encapsula cada um deles e os torna intercambiáveis. O padrão Strategy foi utilizado para aplicar diferentes métodos de cálculo ou validação de pontos, ou até mesmo definir diferentes maneiras de interação do jogador com o jogo (como diferentes tipos de **ranking** ou **achievements**).  
  - **Exemplo**: O método de **atualizar ranking** poderia ser alterado de forma dinâmica (por exemplo, utilizando **Strategy** para diferentes tipos de jogos com diferentes regras de pontuação).

---

### 🧹 Correções e melhorias
- 🔇 `notify=False` para silenciar logs na pré-configuração.  
- 🧹 Correções de indentação no `menu_usuario` (resolvido *IndentationError*).  

---

## ▶️ Como rodar

### 📌 Pré-requisitos
- Python **3.9+**  

### ⚡ Rodando o projeto
```bash
# Clonar
git clone <seu-repo>.git
cd Gaming_Platform

# Executar
python main.py
