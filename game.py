# game.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


# ==========================
#   Helpers
# ==========================
def _maybe_print(msg: str, notify: bool):
    if notify:
        print(msg)


# ==========================
#   Currency
# ==========================
class POOCoin:
    def __init__(self, valor: float):
        self.valor = round(float(valor), 2)

    def __str__(self) -> str:
        return f"P$ {self.valor:.2f}"

    def __add__(self, other):
        return POOCoin(self.valor + other.valor) if isinstance(other, POOCoin) else NotImplemented

    def __sub__(self, other):
        return POOCoin(self.valor - other.valor) if isinstance(other, POOCoin) else NotImplemented

    def __lt__(self, other):
        return self.valor < other.valor if isinstance(other, POOCoin) else NotImplemented


# ==========================
#   Achievements
# ==========================
@dataclass
class Achievement:
    codigo: str
    titulo: str
    descricao: str
    pontos_minimos: int = 0


# ==========================
#   Patch / Update
# ==========================
@dataclass
class PatchNote:
    versao: str
    notas: str


# ==========================
#   Jogos
# ==========================
class Jogo:
    def __init__(self, nome: str, preco: POOCoin, plataformas: Optional[Set[str]] = None):
        self.nome = nome
        self.preco = preco
        self._loja: Dict[str, POOCoin] = {}          # <- privado
        self.pontuacoes: Dict[str, int] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.plataformas: Set[str] = set(plataformas or {"PC"})
        self.versao_atual: str = "1.0.0"
        self.patches: List[PatchNote] = []

    # ---- Loja (encapsulada)
    def adicionar_item_loja(self, item: str, preco: POOCoin) -> None:
        self._loja[item] = preco

    def listar_itens_loja(self) -> Dict[str, POOCoin]:
        return dict(self._loja)  # cópia defensiva

    def obter_preco_item(self, item: str) -> Optional[POOCoin]:
        return self._loja.get(item)

    # ---- Ranking
    def adicionar_pontuacao(self, nome_usuario: str, pontos: int, notify: bool = True) -> None:
        self.pontuacoes[nome_usuario] = self.pontuacoes.get(nome_usuario, 0) + int(pontos)
        _maybe_print(
            f"Pontuação de {nome_usuario} em {self.nome} atualizada para {self.pontuacoes[nome_usuario]} pontos.",
            notify
        )

    def mostrar_ranking(self) -> None:
        print(f"\n {self.nome} (v{self.versao_atual})")
        if not self.pontuacoes:
            print("  Ranking: Ninguém marcou pontos neste jogo ainda.")
            return
        ranking_ordenado = sorted(self.pontuacoes.items(), key=lambda item: item[1], reverse=True)
        print("  Ranking:")
        for i, (nome, pontos) in enumerate(ranking_ordenado, 1):
            print(f"    {i}. {nome} - {pontos} pontos")

    # ---- Achievements
    def registrar_achievement(self, ach: Achievement) -> None:
        self.achievements[ach.codigo] = ach

    def verificar_achievements_para(self, nome_usuario: str, pontos_atuais: int) -> List[Achievement]:
        return [ach for ach in self.achievements.values() if pontos_atuais >= ach.pontos_minimos]

    # ---- Patches
    def publicar_patch(self, versao: str, notas: str) -> None:
        self.versao_atual = versao
        self.patches.append(PatchNote(versao=versao, notas=notas))
        print(f"Patch {versao} publicado para {self.nome}.")

    def listar_patches(self) -> None:
        if not self.patches:
            print("Sem patches publicados.")
            return
        print(f"Patches de {self.nome}:")
        for p in self.patches:
            print(f"- v{p.versao}: {p.notas}")


class JogoOffline(Jogo):
    pass


class JogoOnline(Jogo):
    def __init__(self, nome: str, preco: POOCoin, plataformas: Optional[Set[str]] = None):
        super().__init__(nome, preco, plataformas)
        self.forum: List[str] = []

    def postar_no_forum(self, nome_usuario: str, mensagem: str, notify: bool = True) -> None:
        self.forum.append(f"[{nome_usuario}]: {mensagem}")
        _maybe_print("Mensagem postada no fórum!", notify)

    def ver_forum(self) -> None:
        print(f"\n    Fórum de {self.nome}")
        if not self.forum:
            print("O fórum está vazio.")
        else:
            for post in self.forum:
                print(post)


# ==========================
#   Usuários
# ==========================
class Usuario(ABC):
    _PLAT_PERMITIDAS = {"PC", "Mobile", "Console"}

    def __init__(self, nome: str, email: str, senha: str, idade: int):
        self.nome = nome
        self.email = email
        self.__senha = senha                     # <- privado (name mangling)
        self.idade = idade
        self._saldo = POOCoin(0.0)               # protegido
        self._jogos_adquiridos: Dict[str, Dict[str, object]] = {}   # privado lógico
        self.preferencias: List[str] = []
        self._tickets: List[Dict[str, str]] = [] # privado lógico
        self._mensagens: List[str] = []          # privado lógico
        self._preferencia_plataforma: Optional[str] = None
        self._achievements_desbloqueados: Dict[str, Set[str]] = {}

    # ---- Saldo (só leitura)
    @property
    def saldo(self) -> POOCoin:
        return POOCoin(self._saldo.valor)  # cópia para evitar aliasing

    # ---- Plataforma preferida (setter validado)
    @property
    def preferencia_plataforma(self) -> Optional[str]:
        return self._preferencia_plataforma

    @preferencia_plataforma.setter
    def preferencia_plataforma(self, plataforma: Optional[str]):
        if plataforma is None or plataforma in self._PLAT_PERMITIDAS:
            self._preferencia_plataforma = plataforma
        else:
            print(f"Plataforma inválida. Use: {', '.join(sorted(self._PLAT_PERMITIDAS))}")

    # ---- Mensagens (inbox)
    def adicionar_mensagem(self, msg: str) -> None:
        self._mensagens.append(msg)

    def listar_mensagens(self) -> List[str]:
        return list(self._mensagens)

    # ---- Tickets (helpdesk)
    def abrir_ticket(self, problema: str) -> None:
        self._tickets.append({'problema': problema, 'status': 'Aberto'})

    def listar_tickets(self) -> List[Dict[str, str]]:
        return [dict(t) for t in self._tickets]

    # ---- Segurança
    def verificar_senha(self, senha: str) -> bool:
        return self.__senha == senha

    # ---- Preferências
    def atualizar_preferencias(self, novas_preferencias_str: str) -> None:
        self.preferencias = [p.strip() for p in novas_preferencias_str.split(',') if p.strip()]
        print(f"Preferências de {self.nome} atualizadas para: {self.preferencias}")

    def definir_preferencia_plataforma(self, plataforma: Optional[str]) -> None:
        self.preferencia_plataforma = plataforma
        print(f"Plataforma preferida de {self.nome}: {self._preferencia_plataforma or 'Sem preferência'}")

    # ---- Carteira
    def adicionar_saldo(self, valor_adicionar: POOCoin, notify: bool = True) -> None:
        if valor_adicionar.valor > 0:
            self._saldo += valor_adicionar
            _maybe_print("Saldo adicionado!", notify)
        else:
            _maybe_print("O valor deve ser positivo.", notify)

    # ---- Biblioteca (encapsulada)
    def possui_jogo(self, nome_jogo: str) -> bool:
        return nome_jogo in self._jogos_adquiridos

    def listar_jogos_nomes(self) -> List[str]:
        return list(self._jogos_adquiridos.keys())

    def get_registro_jogo(self, nome_jogo: str) -> Optional[Dict[str, object]]:
        reg = self._jogos_adquiridos.get(nome_jogo)
        return dict(reg) if reg else None  # cópia defensiva

    # ---- Compras
    def comprar_jogo(self, jogo: Jogo, notify: bool = True) -> None:
        if self.possui_jogo(jogo.nome):
            _maybe_print(f"Você já possui o jogo '{jogo.nome}'.", notify)
            return
        if self._preferencia_plataforma and self._preferencia_plataforma not in jogo.plataformas:
            _maybe_print(
                f"'{jogo.nome}' não é compatível com sua plataforma preferida ({self._preferencia_plataforma}).",
                notify
            )
            return
        if self._saldo < jogo.preco:
            _maybe_print(f"Saldo insuficiente para comprar '{jogo.nome}'.", notify)
            return
        self._saldo -= jogo.preco
        self._jogos_adquiridos[jogo.nome] = {"obj": jogo, "versao_instalada": jogo.versao_atual}
        _maybe_print(f"Jogo '{jogo.nome}' comprado com sucesso! Saldo atual: {self.saldo}", notify)

    def comprar_item(self, jogo: Jogo, nome_item: str) -> None:
        if not self.possui_jogo(jogo.nome):
            print(f"Você precisa adquirir o jogo '{jogo.nome}' para comprar itens nele.")
            return
        preco = jogo.obter_preco_item(nome_item)
        if preco is None:
            print(f"Item '{nome_item}' não encontrado.")
            return
        if self._saldo < preco:
            print("Saldo insuficiente.")
            return
        self._saldo -= preco
        print(f"'{nome_item}' comprado com sucesso! Novo saldo: {self.saldo}")

    # ---- Atualizações (patch)
    def atualizar_jogo(self, nome_jogo: str) -> None:
        registro = self._jogos_adquiridos.get(nome_jogo)
        if not registro:
            print("Você não possui este jogo.")
            return
        jogo: Jogo = registro["obj"]  # type: ignore
        instalado = registro["versao_instalada"]  # type: ignore
        if instalado == jogo.versao_atual:
            print(f"{nome_jogo} já está atualizado (v{instalado}).")
            return
        registro["versao_instalada"] = jogo.versao_atual  # type: ignore
        print(f"{nome_jogo} atualizado de v{instalado} para v{jogo.versao_atual}.")

    # ---- Achievements (encapsulados)
    def registrar_achievements_desbloqueados(self, jogo: Jogo, novos: List[Achievement], notify: bool = True) -> None:
        if not novos:
            return
        s = self._achievements_desbloqueados.setdefault(jogo.nome, set())
        adicionados = 0
        for ach in novos:
            if ach.codigo not in s:
                s.add(ach.codigo)
                adicionados += 1
                _maybe_print(f"[Achievement] {self.nome} desbloqueou: {ach.titulo} - {ach.descricao}", notify)
        if adicionados == 0 and notify:
            _maybe_print("Nenhum novo achievement desbloqueado.", notify)

    def listar_achievements_usuario(self, jogo: Jogo) -> None:
        print(f"\nAchievements de {self.nome} em {jogo.nome}:")
        todos = jogo.achievements
        desbloq = self._achievements_desbloqueados.get(jogo.nome, set())
        if not todos:
            print("  Jogo não possui achievements cadastrados.")
            return
        for cod, ach in todos.items():
            status = "✅" if cod in desbloq else "—"
            print(f"  [{status}] {ach.titulo} (min {ach.pontos_minimos}) - {ach.descricao}")


class UsuarioInfantil(Usuario):
    def __init__(self, nome: str, email: str, senha: str, idade: int, responsavel_email: str):
        super().__init__(nome, email, senha, idade)
        self.responsavel_email = responsavel_email
        self.status_aprovacao = 'pendente'
        self.permissoes = {'pode_comprar_itens': False, 'pode_comprar_jogos': False}

    def obter_tipo_conta(self) -> str:
        return "Infantil"

    def comprar_jogo(self, jogo: Jogo, notify: bool = True) -> None:
        if self.status_aprovacao != 'aprovado':
            _maybe_print("Sua conta precisa ser aprovada por um responsável.", notify)
            return
        if not self.permissoes['pode_comprar_jogos']:
            _maybe_print("Você não tem permissão para comprar jogos.", notify)
            return
        super().comprar_jogo(jogo, notify=notify)

    def comprar_item(self, jogo: Jogo, nome_item: str) -> None:
        if self.status_aprovacao != 'aprovado':
            print("Sua conta precisa ser aprovada por um responsável.")
            return
        if not self.permissoes['pode_comprar_itens']:
            print("Você não tem permissão para comprar itens.")
            return
        super().comprar_item(jogo, nome_item)


class UsuarioAdulto(Usuario):
    def __init__(self, nome: str, email: str, senha: str, idade: int):
        super().__init__(nome, email, senha, idade)
        self.dependentes: List[UsuarioInfantil] = []

    def obter_tipo_conta(self) -> str:
        return "Adulto"

    def definir_permissoes(self, dependente: UsuarioInfantil) -> None:
        print(f"\nConfigurando permissões para '{dependente.nome}':")
        perm_itens = input("Permitir que este usuário compre ITENS nos jogos? (s/n): ").lower()
        dependente.permissoes['pode_comprar_itens'] = (perm_itens == 's')
        perm_jogos = input("Permitir que este usuário compre JOGOS da loja? (s/n): ").lower()
        dependente.permissoes['pode_comprar_jogos'] = (perm_jogos == 's')
        print("Permissões salvas.")


class Admin(Usuario):
    def __init__(self, nome: str, email: str, senha: str):
        super().__init__(nome, email, senha, 23)

    def obter_tipo_conta(self) -> str:
        return "Admin"


# ==========================
#   Matchmaking
# ==========================
@dataclass
class Match:
    jogo: str
    jogadores: List[str] = field(default_factory=list)

    def iniciar(self) -> None:
        print(f"Partida iniciada em {self.jogo} com jogadores: {', '.join(self.jogadores)}")


class MatchmakingQueue:
    def __init__(self, tamanho_partida: int = 2):
        self.filas: Dict[str, List[str]] = {}
        self.tamanho_partida = max(2, int(tamanho_partida))

    def entrar_fila(self, jogo: str, usuario: str) -> None:
        fila = self.filas.setdefault(jogo, [])
        if usuario in fila:
            print("Você já está na fila.")
            return
        fila.append(usuario)
        print(f"{usuario} entrou na fila de {jogo}.")

    def tentar_formar_partida(self, jogo: str) -> Optional[Match]:
        fila = self.filas.get(jogo, [])
        if len(fila) >= self.tamanho_partida:
            jogadores = [fila.pop(0) for _ in range(self.tamanho_partida)]
            partida = Match(jogo=jogo, jogadores=jogadores)
            partida.iniciar()
            return partida
        print(f"Aguardando mais jogadores para formar partida em {jogo} ({len(fila)}/{self.tamanho_partida}).")
        return None


# ==========================
#   Plataforma
# ==========================
class Plataforma:
    def __init__(self):
        self.usuarios: Dict[str, Usuario] = {}
        self.jogos: Dict[str, Jogo] = {}
        self.matchmaking = MatchmakingQueue(tamanho_partida=2)
        # Admin padrão
        self.usuarios["admin"] = Admin("lucas", "POO@ic.com", "admin123")

    def encontrar_usuario(self, nome_ou_email: str) -> Optional[Usuario]:
        for user in self.usuarios.values():
            if user.nome == nome_ou_email or user.email == nome_ou_email:
                return user
        return None
