from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Iterable

# =====================================
# PADRÕES DE EXCEÇÃO 
# =====================================

class GamingPlatformError(Exception):
    """Exceção base para erros da plataforma."""
    pass

class BusinessRuleError(GamingPlatformError):
    """Violação de regra de negócio (saldo, permissões etc.)."""
    pass

class NotFoundError(GamingPlatformError):
    """Entidade não encontrada (usuário, jogo, item)."""
    pass

class FileFormatError(GamingPlatformError):
    """Erro de formato de dados externos (API, patch, fórum)."""
    pass


def safe_call(default_return=None, log=True):
    """
    Decorator para capturar exceções e continuar execução.
    → Evita quebra do fluxo em chamadas críticas.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except GamingPlatformError as e:
                if log:
                    print(f"[safe_call] {func.__name__}: {e}")
                return default_return
            except Exception as e:
                if log:
                    print(f"[safe_call:unexpected] {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator


class TryContext:
    """
    Context manager para capturar exceções previstas
    e manter o fluxo sem travar o programa.
    """
    def __init__(self, label: str = "ctx", suppress=(GamingPlatformError,)):
        self.label = label
        self.suppress = suppress

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc and issubclass(exc_type, self.suppress):
            print(f"[TryContext:{self.label}] {exc}")
            return True
        return False


class SafeDict(dict):
    """Dicionário seguro que não gera KeyError."""
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            print(f"[SafeDict] Chave ausente: {key}")
            return None


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
#   Achievements (Simples)
# ==========================
@dataclass
class Achievement:
    codigo: str
    titulo: str
    descricao: str
    pontos_minimos: int = 0


# ==========================
#   Composite - Estrutural
# ==========================
class AchievementComponent(ABC):
    @abstractmethod
    def listar(self) -> Iterable[Achievement]:
        ...


class AchievementLeaf(AchievementComponent):
    def __init__(self, ach: Achievement):
        self.ach = ach

    def listar(self) -> Iterable[Achievement]:
        yield self.ach


class AchievementPack(AchievementComponent):
    """Composição de achievements (Composite Pattern)."""
    def __init__(self, titulo: str):
        self.titulo = titulo
        self._filhos: List[AchievementComponent] = []

    def adicionar(self, comp: AchievementComponent):
        self._filhos.append(comp)

    def listar(self) -> Iterable[Achievement]:
        for c in self._filhos:
            yield from c.listar()
# ==========================
#   Patch / Update
# ==========================
@dataclass
class PatchNote:
    versao: str
    notas: str


# ==========================
#   Strategy (Comportamental)
# ==========================
class CalculadorPontuacao(ABC):
    @abstractmethod
    def calcular(self, pontos_informados: int) -> int:
        ...


class CalculadorPontuacaoNormal(CalculadorPontuacao):
    def calcular(self, pontos_informados: int) -> int:
        return int(pontos_informados)


class CalculadorPontuacaoBonus(CalculadorPontuacao):
    def calcular(self, pontos_informados: int) -> int:
        base = int(pontos_informados)
        return int(round(base * 1.10))


# ==========================
#   Adapter (Estrutural) - Fórum
# ==========================
class IForum(ABC):
    @abstractmethod
    def postar(self, autor: str, mensagem: str) -> None: ...
    @abstractmethod
    def listar(self) -> List[str]: ...


class InternalForum(IForum):
    def __init__(self):
        self._posts: List[str] = []

    def postar(self, autor: str, mensagem: str) -> None:
        self._posts.append(f"[{autor}]: {mensagem}")

    def listar(self) -> List[str]:
        return list(self._posts)


class ExternalForumAPI:
    """Simula uma API externa com formato diferente."""
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def push_message(self, payload: Dict[str, str]):
        if not isinstance(payload, dict) or "author" not in payload or "text" not in payload:
            raise FileFormatError("Payload inválido recebido pela API externa.")
        self.messages.append(payload)

    def dump(self) -> List[Dict[str, str]]:
        return list(self.messages)


class ForumAdapter(IForum):
    """Adapter que conecta a API externa à interface interna."""
    def __init__(self, external: ExternalForumAPI):
        self.external = external

    @safe_call(log=True)
    def postar(self, autor: str, mensagem: str) -> None:
        self.external.push_message({"author": autor, "text": mensagem})

    @safe_call(default_return=[], log=True)
    def listar(self) -> List[str]:
        return [f"[{m['author']}]: {m['text']}" for m in self.external.dump()]


# ==========================
#   Visitor (Comportamental)
# ==========================
class JogoVisitor(ABC):
    @abstractmethod
    def visitar_jogo(self, jogo: 'Jogo'): ...
    @abstractmethod
    def visitar_jogo_online(self, jogo: 'JogoOnline'): ...
    @abstractmethod
    def visitar_jogo_offline(self, jogo: 'JogoOffline'): ...


class JogoRankingVisitor(JogoVisitor):
    """Visitor que aplica ações sem alterar as classes de jogo."""
    def visitar_jogo(self, jogo: 'Jogo'):
        jogo.mostrar_ranking()

    def visitar_jogo_online(self, jogo: 'JogoOnline'):
        jogo.mostrar_ranking()
        print(f"\n[FÓRUM] {jogo.nome}")
        jogo.ver_forum()

    def visitar_jogo_offline(self, jogo: 'JogoOffline'):
        jogo.mostrar_ranking()
# ==========================
#   Jogos
# ==========================
class Jogo:
    def __init__(self, nome: str, preco: POOCoin, plataformas: Optional[Set[str]] = None,
                 estrategia: Optional[CalculadorPontuacao] = None):
        self.nome = nome
        self.preco = preco
        self._loja: Dict[str, POOCoin] = {}
        self.pontuacoes: Dict[str, int] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.plataformas: Set[str] = set(plataformas or {"PC"})
        self.versao_atual: str = "1.0.0"
        self.patches: List[PatchNote] = []
        self._estrategia_pontos: CalculadorPontuacao = estrategia or CalculadorPontuacaoNormal()

    # Strategy – define qual cálculo de pontuação o jogo usará
    def set_estrategia_pontuacao(self, estrategia: CalculadorPontuacao):
        self._estrategia_pontos = estrategia

    # Loja (encapsulada)
    def adicionar_item_loja(self, item: str, preco: POOCoin) -> None:
        self._loja[item] = preco

    def listar_itens_loja(self) -> Dict[str, POOCoin]:
        return dict(self._loja)

    def obter_preco_item(self, item: str) -> Optional[POOCoin]:
        return self._loja.get(item)

    # Ranking
    def adicionar_pontuacao(self, nome_usuario: str, pontos: int, notify: bool = True) -> None:
        pontos_calc = self._estrategia_pontos.calcular(pontos)
        self.pontuacoes[nome_usuario] = self.pontuacoes.get(nome_usuario, 0) + pontos_calc
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

    # Achievements (simples)
    def registrar_achievement(self, ach: Achievement) -> None:
        self.achievements[ach.codigo] = ach

    # Achievements (Composite opcional)
    def registrar_achievement_component(self, comp: AchievementComponent) -> None:
        for ach in comp.listar():
            self.registrar_achievement(ach)

    def verificar_achievements_para(self, nome_usuario: str, pontos_atuais: int) -> List[Achievement]:
        """Retorna os achievements desbloqueados com base na pontuação atual"""
        return [ach for ach in self.achievements.values() if pontos_atuais >= ach.pontos_minimos]

    # Patches
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

    # Visitor (default)
    def aceitar_visitor(self, visitor: JogoVisitor):
        visitor.visitar_jogo(self)


class JogoOffline(Jogo):
    def aceitar_visitor(self, visitor: JogoVisitor):
        visitor.visitar_jogo_offline(self)


class JogoOnline(Jogo):
    def __init__(self, nome: str, preco: POOCoin, plataformas: Optional[Set[str]] = None, forum: Optional[IForum] = None):
        super().__init__(nome, preco, plataformas)
        # Por padrão, usa fórum interno; pode receber um Adapter (IForum)
        self._forum: IForum = forum or InternalForum()

    # Mantém API original
    def postar_no_forum(self, nome_usuario: str, mensagem: str, notify: bool = True) -> None:
        self._forum.postar(nome_usuario, mensagem)
        _maybe_print("Mensagem postada no fórum!", notify)

    def ver_forum(self) -> None:
        posts = self._forum.listar()
        if not posts:
            print("O fórum está vazio.")
        else:
            for p in posts:
                print(p)

    # 🔧 Correção — herda o método de verificação de achievements da superclasse
    def verificar_achievements_para(self, nome_usuario: str, pontos_atuais: int) -> List[Achievement]:
        return super().verificar_achievements_para(nome_usuario, pontos_atuais)

    def aceitar_visitor(self, visitor: JogoVisitor):
        visitor.visitar_jogo_online(self)

# ==========================
#   Chain of Responsibility - Suporte
# ==========================
class SuporteHandler(ABC):
    def __init__(self, proximo: Optional['SuporteHandler'] = None):
        self._proximo = proximo

    @safe_call(default_return=None)
    def handle(self, ticket: Dict[str, str]):
        if not self._processa(ticket) and self._proximo:
            self._proximo.handle(ticket)

    @abstractmethod
    def _processa(self, ticket: Dict[str, str]) -> bool:
        ...


class AtendimentoBasico(SuporteHandler):
    def _processa(self, ticket: Dict[str, str]) -> bool:
        if ticket.get('categoria') in ('login', 'cadastro', 'senha'):
            print(f"[Suporte Básico] Resolvido: {ticket['problema']}")
            ticket['status'] = 'Resolvido (Básico)'
            return True
        return False


class AtendimentoAvancado(SuporteHandler):
    def _processa(self, ticket: Dict[str, str]) -> bool:
        if ticket.get('categoria') in ('pagamento', 'instalacao'):
            print(f"[Suporte Avançado] Resolvido: {ticket['problema']}")
            ticket['status'] = 'Resolvido (Avançado)'
            return True
        return False


class AtendimentoFallback(SuporteHandler):
    def _processa(self, ticket: Dict[str, str]) -> bool:
        print(f"[Suporte Nível 3] Em análise: {ticket['problema']}")
        ticket['status'] = 'Em análise'
        return True


# ==========================
#   Usuários
# ==========================
class Usuario(ABC):
    _PLAT_PERMITIDAS = {"PC", "Mobile", "Console"}

    def __init__(self, nome: str, email: str, senha: str, idade: int):
        self.nome = nome
        self.email = email
        self.__senha = senha
        self.idade = idade
        self._saldo = POOCoin(0.0)
        self._jogos_adquiridos: Dict[str, Dict[str, object]] = SafeDict()
        self.preferencias: List[str] = []
        self._tickets: List[Dict[str, str]] = []
        self._mensagens: List[str] = []
        self._preferencia_plataforma: Optional[str] = None
        self._achievements_desbloqueados: Dict[str, Set[str]] = {}

    # Saldo
    @property
    def saldo(self) -> POOCoin:
        return POOCoin(self._saldo.valor)

    # Plataforma preferida
    @property
    def preferencia_plataforma(self) -> Optional[str]:
        return self._preferencia_plataforma

    @preferencia_plataforma.setter
    def preferencia_plataforma(self, plataforma: Optional[str]):
        if plataforma is None or plataforma in self._PLAT_PERMITIDAS:
            self._preferencia_plataforma = plataforma
        else:
            raise BusinessRuleError(f"Plataforma inválida. Use: {', '.join(sorted(self._PLAT_PERMITIDAS))}")

    # Mensagens
    def adicionar_mensagem(self, msg: str) -> None:
        self._mensagens.append(msg)

    def listar_mensagens(self) -> List[str]:
        return list(self._mensagens)

    # Tickets
    def abrir_ticket(self, problema: str, categoria: str = "geral") -> None:
        self._tickets.append({'problema': problema, 'status': 'Aberto', 'categoria': categoria})

    def listar_tickets(self) -> List[Dict[str, str]]:
        return [dict(t) for t in self._tickets]

    # Segurança
    def verificar_senha(self, senha: str) -> bool:
        return self.__senha == senha

    # Preferências
    def atualizar_preferencias(self, novas_preferencias_str: str) -> None:
        self.preferencias = [p.strip() for p in novas_preferencias_str.split(',') if p.strip()]
        print(f"Preferências de {self.nome} atualizadas para: {self.preferencias}")

    def definir_preferencia_plataforma(self, plataforma: Optional[str]) -> None:
        try:
            self.preferencia_plataforma = plataforma
            print(f"Plataforma preferida de {self.nome}: {self._preferencia_plataforma or 'Sem preferência'}")
        except BusinessRuleError as e:
            print(f"[Erro de plataforma] {e}")

    # Carteira
    @safe_call(log=True)
    def adicionar_saldo(self, valor_adicionar: POOCoin, notify: bool = True) -> None:
        if valor_adicionar.valor <= 0:
            raise BusinessRuleError("O valor deve ser positivo.")
        self._saldo += valor_adicionar
        _maybe_print("Saldo adicionado!", notify)

    # Biblioteca
    def possui_jogo(self, nome_jogo: str) -> bool:
        return nome_jogo in self._jogos_adquiridos

    def listar_jogos_nomes(self) -> List[str]:
        return list(self._jogos_adquiridos.keys())

    def get_registro_jogo(self, nome_jogo: str) -> Optional[Dict[str, object]]:
        return self._jogos_adquiridos.get(nome_jogo)

    # Compras
    @safe_call(log=True)
    def comprar_jogo(self, jogo: Jogo, notify: bool = True) -> None:
        if self.possui_jogo(jogo.nome):
            raise BusinessRuleError(f"Você já possui o jogo '{jogo.nome}'.")
        if self._preferencia_plataforma and self._preferencia_plataforma not in jogo.plataformas:
            raise BusinessRuleError(f"'{jogo.nome}' não é compatível com sua plataforma preferida.")
        if self._saldo < jogo.preco:
            raise BusinessRuleError(f"Saldo insuficiente para comprar '{jogo.nome}'.")
        self._saldo -= jogo.preco
        self._jogos_adquiridos[jogo.nome] = {"obj": jogo, "versao_instalada": jogo.versao_atual}
        _maybe_print(f"Jogo '{jogo.nome}' comprado com sucesso! Saldo atual: {self.saldo}", notify)

    @safe_call(log=True)
    def comprar_item(self, jogo: Jogo, nome_item: str) -> None:
        if not self.possui_jogo(jogo.nome):
            raise NotFoundError(f"Você precisa adquirir o jogo '{jogo.nome}' para comprar itens nele.")
        preco = jogo.obter_preco_item(nome_item)
        if preco is None:
            raise NotFoundError(f"Item '{nome_item}' não encontrado.")
        if self._saldo < preco:
            raise BusinessRuleError("Saldo insuficiente.")
        self._saldo -= preco
        print(f"'{nome_item}' comprado com sucesso! Novo saldo: {self.saldo}")
    # Atualizações (patch)
    @safe_call(default_return=None, log=True)
    def atualizar_jogo(self, nome_jogo: str) -> None:
        registro = self._jogos_adquiridos.get(nome_jogo)
        if not registro:
            raise NotFoundError("Você não possui este jogo.")
        jogo: Jogo = registro["obj"]  # type: ignore
        instalado = registro["versao_instalada"]  # type: ignore
        if instalado == jogo.versao_atual:
            print(f"{nome_jogo} já está atualizado (v{instalado}).")
            return
        registro["versao_instalada"] = jogo.versao_atual
        print(f"{nome_jogo} atualizado de v{instalado} para v{jogo.versao_atual}.")

    # Achievements (encapsulados)
    @safe_call(default_return=None)
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

    @safe_call(default_return=None)
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


class UsuarioAdulto(Usuario):
    def __init__(self, nome: str, email: str, senha: str, idade: int):
        super().__init__(nome, email, senha, idade)
        self.dependentes: List[UsuarioInfantil] = []

    def obter_tipo_conta(self) -> str:
        return "Adulto"

    @safe_call(default_return=None, log=True)
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
#   Factory Method (Criacional)
# ==========================
class UsuarioFactory(ABC):
    @abstractmethod
    def criar_usuario(self, nome: str, email: str, senha: str, idade: int):
        ...


class UsuarioAdultoFactory(UsuarioFactory):
    def criar_usuario(self, nome: str, email: str, senha: str, idade: int):
        return UsuarioAdulto(nome, email, senha, idade)


class UsuarioInfantilFactory(UsuarioFactory):
    def __init__(self, responsavel_email: str):
        self.responsavel_email = responsavel_email

    def criar_usuario(self, nome: str, email: str, senha: str, idade: int):
        return UsuarioInfantil(nome, email, senha, idade, self.responsavel_email)


# ==========================
#   Builder (Criacional)
# ==========================
class UsuarioBuilder:
    def __init__(self):
        self.nome = None
        self.email = None
        self.senha = None
        self.idade = None
        self.tipo = "adulto"
        self.saldo_inicial = 0

    def com_nome(self, nome: str):
        self.nome = nome
        return self

    def com_email(self, email: str):
        self.email = email
        return self

    def com_senha(self, senha: str):
        self.senha = senha
        return self

    def com_idade(self, idade: int):
        self.idade = idade
        return self

    def como_admin(self):
        self.tipo = "admin"
        return self

    def com_saldo_inicial(self, valor: float):
        self.saldo_inicial = valor
        return self

    @safe_call()
    def construir(self):
        if self.tipo == "admin":
            usuario = Admin(self.nome, self.email, self.senha)
        else:
            usuario = UsuarioAdulto(self.nome, self.email, self.senha, self.idade)
        usuario.adicionar_saldo(POOCoin(self.saldo_inicial), notify=False)
        return usuario
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
        # cadeia de suporte (CoR)
        self._suporte_chain = AtendimentoBasico(AtendimentoAvancado(AtendimentoFallback()))

    @safe_call(default_return=None)
    def encontrar_usuario(self, nome_ou_email: str) -> Optional[Usuario]:
        for user in self.usuarios.values():
            if user.nome == nome_ou_email or user.email == nome_ou_email:
                return user
        return None

    # Chain of Responsibility – processa tickets de um usuário
    @safe_call(default_return=None)
    def processar_tickets_usuario(self, usuario: Usuario) -> None:
        for t in usuario.listar_tickets():
            if t.get('status') == 'Aberto':
                self._suporte_chain.handle(t)


# ==========================
#   Singleton (Criacional)
# ==========================
class PlataformaSingleton(Plataforma):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            Plataforma.__init__(cls._instance)
        return cls._instance


# ==========================
#   Facade (Estrutural)
# ==========================
class PlataformaFacade:
    """Fachada opcional para operações comuns; não substitui a API existente."""
    def __init__(self, plataforma: Plataforma):
        self.p = plataforma

    @safe_call()
    def cadastrar_usuario_adulto(self, nome: str, email: str, senha: str, idade: int) -> UsuarioAdulto:
        u = UsuarioAdulto(nome, email, senha, idade)
        self.p.usuarios[nome] = u
        return u

    @safe_call()
    def cadastrar_usuario_infantil(self, nome: str, email: str, senha: str, idade: int, responsavel_email: str) -> UsuarioInfantil:
        u = UsuarioInfantil(nome, email, senha, idade, responsavel_email)
        self.p.usuarios[nome] = u
        return u

    @safe_call()
    def publicar_patch(self, nome_jogo: str, versao: str, notas: str) -> None:
        jogo = self.p.jogos.get(nome_jogo)
        if jogo:
            jogo.publicar_patch(versao, notas)

    @safe_call()
    def comprar_jogo(self, usuario: Usuario, nome_jogo: str) -> None:
        jogo = self.p.jogos.get(nome_jogo)
        if jogo:
            usuario.comprar_jogo(jogo)

    @safe_call()
    def registrar_pacote_achievements(self, nome_jogo: str, pack: AchievementPack) -> None:
        jogo = self.p.jogos.get(nome_jogo)
        if jogo:
            jogo.registrar_achievement_component(pack)

