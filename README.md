# Refactoring-Game_Plataform

Plataforma de jogos em linha de comando com **gestão de catálogo**, **contas (adulto/infantil/admin)**, **microtransações**, **ranking e achievements**, **fórum**, **patch/update**, **controle parental**, **suporte**, **matchmaking** e **compatibilidade cross-platform**.

## Sumário
- [Arquitetura](#arquitetura)
- [Funcionalidades](#funcionalidades)
- [O que foi adicionado/alterado](#o-que-foi-adicionado e alterado)
- [Como rodar](#como-rodar)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Comandos principais no CLI](#comandos-principais-no-cli)
- [Próximos passos](#próximos-passos)
- [Licença](#licença)

## Arquitetura

- **`game.py`**: núcleo de domínio/POO (modelos, regras e serviços).
  - Tipos de jogo: `Jogo`, `JogoOnline`, `JogoOffline`
  - Usuários: `Usuario` (abstrata), `UsuarioAdulto`, `UsuarioInfantil`, `Admin`
  - Sistemas: `POOCoin`, `Achievement`, `PatchNote`, `MatchmakingQueue`, `Match`, `Plataforma`
- **`main.py`**: interface **CLI** e menus (admin/usuário).

## Funcionalidades

| # | Requisito | Status |
|---|-----------|--------|
| 1 | **Game Library Management**: catálogo/loja de jogos, itens por jogo | ✅ |
| 2 | **User Account Management**: criação de contas, login, preferências, saldo | ✅ |
| 3 | **Multiplayer Matchmaking**: fila por jogo e criação de partida | ✅ |
| 4 | **In-Game Purchases**: compra de itens com `POOCoin` | ✅ |
| 5 | **Leaderboards & Achievements**: ranking por jogo + achievements por pontuação | ✅ |
| 6 | **Community/Social**: fórum por jogo online (listar/postar) | ✅ |
| 7 | **Game Update/Patch**: publicação admin + atualização local do usuário | ✅ |
| 8 | **Parental Control**: aprovação de contas infantis e permissões de compra | ✅ |
| 9 | **User Support/Helpdesk**: abertura e listagem de tickets | ✅ |
| 10 | **Cross-Platform**: metadados de plataformas + preferência do usuário | ✅ |

## O que foi adicionado/alterado

### Encapsulamento
- `Usuario`:
  - `__senha` (name mangling), `verificar_senha()` público.
  - Atributos internos privatizados: `_jogos_adquiridos`, `_tickets`, `_mensagens`, `_achievements_desbloqueados`.
  - API pública para acesso/ação: `possui_jogo`, `listar_jogos_nomes`, `get_registro_jogo`, `abrir_ticket`, `listar_tickets`, `adicionar_mensagem`, `listar_mensagens`.
  - `saldo` com `@property` (somente leitura por cópia defensiva).
  - `preferencia_plataforma` com setter validado e método `definir_preferencia_plataforma`.
- `Jogo`:
  - Loja agora é privada (`_loja`).
  - Métodos: `adicionar_item_loja`, `listar_itens_loja` (cópia defensiva), `obter_preco_item`.

### Novos sistemas
- **Achievements**: cadastro via admin (`registrar_achievement`) e desbloqueio automático em `registrar_achievements_desbloqueados`.
- **Patch Management**: publicação (`publicar_patch`) com `versao_atual` + `listar_patches`; cliente atualiza com `atualizar_jogo`.
- **Matchmaking**: `MatchmakingQueue` (fila por jogo) e `Match` (partida).
- **Cross-Platform**: `Jogo.plataformas` e `Usuario.preferencia_plataforma` filtram listagem/compras.

### Qualidade de vida
- Flag `notify=False` para suprimir prints na pré-configuração.
- Correção de indentação no `menu_usuario` (erro anterior `IndentationError`).

## Como rodar

Pré-requisitos: **Python 3.9+**

```bash
# Clonar
git clone <seu-repo>.git
cd Gaming_Platform

# Rodar
python main.py
