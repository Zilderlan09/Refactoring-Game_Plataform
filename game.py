from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Iterable

# ================================================================
# EXCEPTIONS
# ================================================================

class ValidationError(Exception):
    """Erro genérico de validação/regra de negócio."""
    pass

class BusinessRuleError(ValidationError):
    """Quebra de regra de negócio (ex.: saldo insuficiente, permissão negada)."""
    pass

class NotFoundError(LookupError):
    """Recurso não encontrado (ex.: jogo/usuário/item inexistente)."""
    pass

class FileFormatError(ValueError):
    """Formato/conteúdo inesperado em arquivo/entrada externa."""
    pass

# --- Decorators de segurança ------------------------------------

def safe_call(func=None, **outer_kwargs):
    """
    Decorator genérico para capturar exceções inesperadas.
    Aceita parâmetros opcionais, como:
      @safe_call
      @safe_call(log=True)
      @safe_call(default_return=[], log=True)
    """
    log = outer_kwargs.get("log", False)
    default_return = outer_kwargs.get("default_return", None)

    def decorator(inner_func):
        def wrapper(*args, **kwargs):
            try:
                return inner_func(*args, **kwargs)
            except Exception as e:
                if log:
                    print(f"[safe_call] {inner_func.__name__} falhou: {e}")
                return default_return
        return wrapper

    if func is not None and callable(func):
        return decorator(func)
    return decorator


def try_catch_wrapper(func):
    """Trata exceções específicas e imprime mensagens amigáveis."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BusinessRuleError as be:
            print(f"[Regra de Negócio] {be}")
        except ValidationError as ve:
            print(f"[Validação] {ve}")
        except NotFoundError as nf:
            print(f"[Não encontrado] {nf}")
        except FileFormatError as ff:
            print(f"[Arquivo/Formato] {ff}")
        except Exception as e:
            print(f"[Erro inesperado] {e}")
    return wrapper

# --- SafeDict: dicionário seguro --------------------------------

class SafeDict(dict):
    """
    Dicionário tolerante:
      - strict=True -> lança NotFoundError se chave não existir
      - strict=False -> retorna default
    """
    def __init__(self, *args, default=None, strict: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self._default = default
        self._strict = bool(strict)

    def __missing__(self, key):
        if self._strict:
            raise NotFoundError(f"Chave não encontrada: {key}")
        return self._default

# ================================================================
#   Helpers
# ================================================================
def _maybe_print(msg: str, notify: bool):
    if notify:
        print(msg)

# ================================================================
#   Currency
# ================================================================
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

# ================================================================
#   Achievements (Simples e Composite)
# ================================================================
@dataclass
class Achievement:
    codigo: str
    titulo: str
    descricao: str
    pontos_minimos: int = 0

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
    """Composição de achievements (ex.: pacotes de objetivos)."""
    def __init__(self, titulo: str):
        self.titulo = titulo
        self._filhos: List[AchievementComponent] = []

    def adicionar(self, comp: AchievementComponent):
        self._filhos.append(comp)

    def listar(self) -> Iterable[Achievement]:
        for c in self._filhos:
            for ach in c.listar():
                yield ach

# ================================================================
#   Patch / Update
# ================================================================
@dataclass
class PatchNote:
    versao: str
    notas: str


# ================================================================
#   Strategy (Comportamental) - Cálculo de Pontuação
# ================================================================
class CalculadorPontuacao(ABC):
    @abstractmethod
    def calcular(self, pontos_informados: int) -> int:
        """Define a interface para diferentes estratégias de pontuação."""
        ...

class CalculadorPontuacaoNormal(CalculadorPontuacao):
    def calcular(self, pontos_informados: int) -> int:
        # Estratégia padrão: usa o valor informado sem modificações.
        return int(pontos_informados)

class CalculadorPontuacaoBonus(CalculadorPontuacao):
    def calcular(self, pontos_informados: int) -> int:
        # Estratégia alternativa: aplica bônus de 10%.
        base = int(pontos_informados)
        return int(round(base * 1.10))


# ================================================================
#   Adapter (Estrutural) - Fórum externo
# ================================================================
class IForum(ABC):
    @abstractmethod
    def postar(self, autor: str, mensagem: str) -> None: ...
    @abstractmethod
    def listar(self) -> List[str]: ...

class InternalForum(IForum):
    """Implementação padrão do fórum interno."""
    def __init__(self):
        self._posts: List[str] = []

    @safe_call(log=True)
    def postar(self, autor: str, mensagem: str) -> None:
        self._posts.append(f"[{autor}]: {mensagem}")

    @safe_call(default_return=[], log=True)
    def listar(self) -> List[str]:
        return list(self._posts)

class ExternalForumAPI:
    """Simula uma API externa com interface diferente (terceirizada)."""
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def push_message(self, payload: Dict[str, str]):
        self.messages.append(payload)

    def dump(self) -> List[Dict[str, str]]:
        return list(self.messages)

class ForumAdapter(IForum):
    """
    Adapter que conecta uma API externa ao sistema, traduzindo
    a interface externa (push_message/dump) para o padrão interno.
    """
    def __init__(self, external: ExternalForumAPI):
        self.external = external

    @safe_call(log=True)
    def postar(self, autor: str, mensagem: str) -> None:
        self.external.push_message({"author": autor, "text": mensagem})

    @safe_call(default_return=[], log=True)
    def listar(self) -> List[str]:
        return [f"[{m['author']}]: {m['text']}" for m in self.external.dump()]


# ================================================================
#   Visitor (Comportamental)
# ================================================================
class JogoVisitor(ABC):
    """Define a interface para visitas em tipos diferentes de Jogo."""
    @abstractmethod
    def visitar_jogo(self, jogo: 'Jogo'): ...
    @abstractmethod
    def visitar_jogo_online(self, jogo: 'JogoOnline'): ...
    @abstractmethod
    def visitar_jogo_offline(self, jogo: 'JogoOffline'): ...

class JogoRankingVisitor(JogoVisitor):
    """Visitor concreto para exibir ranking e fórum (quando aplicável)."""
    def visitar_jogo(self, jogo: 'Jogo'):
        jogo.mostrar_ranking()

    def visitar_jogo_online(self, jogo: 'JogoOnline'):
        jogo.mostrar_ranking()
        print(f"\n[FÓRUM] {jogo.nome}")
        jogo.ver_forum()

    def visitar_jogo_offline(self, jogo: 'JogoOffline'):
        jogo.mostrar_ranking()


# ================================================================
#   Jogos
# ================================================================
class Jogo:
    """Classe base para jogos (padrão Template + Strategy)."""
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

    # STRATEGY — permite alternar forma de pontuação dinamicamente
    def set_estrategia_pontuacao(self, estrategia: CalculadorPontuacao):
        self._estrategia_pontos = estrategia

    # Loja (encapsulada)
    def adicionar_item_loja(self, item: str, preco: POOCoin) -> None:
        self._loja[item] = preco

    def listar_itens_loja(self) -> Dict[str, POOCoin]:
        return dict(self._loja)

    def obter_preco_item(self, item: str) -> Optional[POOCoin]:
        if item not in self._loja:
            raise NotFoundError(f"Item '{item}' não encontrado na loja do jogo '{self.nome}'.")
        return self._loja.get(item)

    # Ranking
    @try_catch_wrapper
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

    # Achievements
    def registrar_achievement(self, ach: Achievement) -> None:
        self.achievements[ach.codigo] = ach

    def registrar_achievement_component(self, comp: 'AchievementComponent') -> None:
        for ach in comp.listar():
            self.registrar_achievement(ach)

    def verificar_achievements_para(self, nome_usuario: str, pontos_atuais: int) -> List[Achievement]:
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

    # VISITOR — permite aplicar ações externas (exibir ranking/fórum)
    def aceitar_visitor(self, visitor: JogoVisitor):
        visitor.visitar_jogo(self)


class JogoOffline(Jogo):
    def aceitar_visitor(self, visitor: JogoVisitor):
        visitor.visitar_jogo_offline(self)


class JogoOnline(Jogo):
    def __init__(self, nome: str, preco: POOCoin, plataformas: Optional[Set[str]] = None, forum: Optional[IForum] = None):
        super().__init__(nome, preco, plataformas)
        # Por padrão usa fórum interno; pode receber Adapter externo
        self._forum: IForum = forum or InternalForum()

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

    def aceitar_visitor(self, visitor: JogoVisitor):
        visitor.visitar_jogo_online(self)

# ================================================================
#   Chain of Responsibility (Comportamental) - Suporte
# ================================================================
class SuporteHandler(ABC):
    """Handler base da cadeia de suporte."""
    def __init__(self, proximo: Optional['SuporteHandler'] = None):
        self._proximo = proximo

    def handle(self, ticket: Dict[str, str]):
        # Se o handler atual não resolver, passa para o próximo
        if not self._processa(ticket) and self._proximo:
            self._proximo.handle(ticket)

    @abstractmethod
    def _processa(self, ticket: Dict[str, str]) -> bool:
        ...


class AtendimentoBasico(SuporteHandler):
    """Resolve problemas simples: login, cadastro, senha."""
    def _processa(self, ticket: Dict[str, str]) -> bool:
        if ticket.get('categoria') in ('login', 'cadastro', 'senha'):
            print(f"[Suporte Básico] Resolvido: {ticket['problema']}")
            ticket['status'] = 'Resolvido (Básico)'
            return True
        return False


class AtendimentoAvancado(SuporteHandler):
    """Resolve problemas de pagamento e instalação."""
    def _processa(self, ticket: Dict[str, str]) -> bool:
        if ticket.get('categoria') in ('pagamento', 'instalacao'):
            print(f"[Suporte Avançado] Resolvido: {ticket['problema']}")
            ticket['status'] = 'Resolvido (Avançado)'
            return True
        return False


class AtendimentoFallback(SuporteHandler):
    """Fallback para casos não cobertos: marca como 'Em análise'."""
    def _processa(self, ticket: Dict[str, str]) -> bool:
        print(f"[Suporte Nível 3] Em análise: {ticket['problema']}")
        ticket['status'] = 'Em análise'
        return True


# ================================================================
#   Usuários
# ================================================================
class Usuario(ABC):
    _PLAT_PERMITIDAS = {"PC", "Mobile", "Console"}

    def __init__(self, nome: str, email: str, senha: str, idade: int):
        self.nome = nome
        self.email = email
        self.__senha = senha                     # privado
        self.idade = idade
        self._saldo = POOCoin(0.0)               # protegido
        self._jogos_adquiridos: Dict[str, Dict[str, object]] = {}
        self.preferencias: List[str] = []
        self._tickets: List[Dict[str, str]] = []
        self._mensagens: List[str] = []
        self._preferencia_plataforma: Optional[str] = None
        self._achievements_desbloqueados: Dict[str, Set[str]] = {}

    # Saldo (somente leitura)
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
            print(f"Plataforma inválida. Use: {', '.join(sorted(self._PLAT_PERMITIDAS))}")

    # Mensagens (inbox)
    def adicionar_mensagem(self, msg: str) -> None:
        self._mensagens.append(msg)

    def listar_mensagens(self) -> List[str]:
        return list(self._mensagens)

    # Tickets (helpdesk)
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
        self.preferencia_plataforma = plataforma
        print(f"Plataforma preferida de {self.nome}: {self._preferencia_plataforma or 'Sem preferência'}")

    # Carteira
    def adicionar_saldo(self, valor_adicionar: POOCoin, notify: bool = True) -> None:
        if valor_adicionar.valor > 0:
            self._saldo += valor_adicionar
            _maybe_print("Saldo adicionado!", notify)
        else:
            _maybe_print("O valor deve ser positivo.", notify)

    # Biblioteca (encapsulada)
    def possui_jogo(self, nome_jogo: str) -> bool:
        return nome_jogo in self._jogos_adquiridos

    def listar_jogos_nomes(self) -> List[str]:
        return list(self._jogos_adquiridos.keys())

    def get_registro_jogo(self, nome_jogo: str) -> Optional[Dict[str, object]]:
        reg = self._jogos_adquiridos.get(nome_jogo)
        return dict(reg) if reg else None

    # Compras
    def comprar_jogo(self, jogo: 'Jogo', notify: bool = True) -> None:
        if self.possui_jogo(jogo.nome):
            _maybe_print(f"Você já possui o jogo '{jogo.nome}'.", notify)
            return
        if self._preferencia_plataforma and self._preferencia_plataforma not in jogo.plataformas:
            _maybe_print(f"'{jogo.nome}' não é compatível com sua plataforma preferida.", notify)
            return
        if self._saldo < jogo.preco:
            _maybe_print(f"Saldo insuficiente para comprar '{jogo.nome}'.", notify)
            return
        self._saldo -= jogo.preco
        self._jogos_adquiridos[jogo.nome] = {"obj": jogo, "versao_instalada": jogo.versao_atual}
        _maybe_print(f"Jogo '{jogo.nome}' comprado com sucesso! Saldo atual: {self.saldo}", notify)

    def comprar_item(self, jogo: 'Jogo', nome_item: str) -> None:
        if not self.possui_jogo(jogo.nome):
            print(f"Você precisa adquirir o jogo '{jogo.nome}' para comprar itens nele.")
            return
        try:
            preco = jogo.obter_preco_item(nome_item)
        except NotFoundError as e:
            print(str(e))
            return
        if self._saldo < preco:
            print("Saldo insuficiente.")
            return
        self._saldo -= preco
        print(f"'{nome_item}' comprado com sucesso! Novo saldo: {self.saldo}")

    # Atualizações (patch)
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
        registro["versao_instalada"] = jogo.versao_atual
        print(f"{nome_jogo} atualizado de v{instalado} para v{jogo.versao_atual}.")

    # Achievements (encapsulados)
    def registrar_achievements_desbloqueados(self, jogo: 'Jogo', novos: List[Achievement], notify: bool = True) -> None:
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

    def listar_achievements_usuario(self, jogo: 'Jogo') -> None:
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
    # Restrições específicas são mantidas via fluxo de aprovação no menu (main)


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


# ================================================================
#   Factory Method (Criacional)
# ================================================================
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


# ================================================================
#   Builder (Criacional)
# ================================================================
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

    def construir(self):
        if self.tipo == "admin":
            usuario = Admin(self.nome, self.email, self.senha)
        else:
            usuario = UsuarioAdulto(self.nome, self.email, self.senha, self.idade)
        usuario.adicionar_saldo(POOCoin(self.saldo_inicial), notify=False)
        return usuario

# ================================================================
#   Matchmaking
# ================================================================
@dataclass
class Match:
    jogo: str
    jogadores: List[str] = field(default_factory=list)

    def iniciar(self) -> None:
        print(f"Partida iniciada em {self.jogo} com jogadores: {', '.join(self.jogadores)}")


class MatchmakingQueue:
    """Gerencia filas de matchmaking para jogos online."""
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


# ================================================================
#   Plataforma
# ================================================================
class Plataforma:
    """Camada central que coordena usuários, jogos e suporte."""
    def __init__(self):
        # Usa SafeDict em vez de dict simples, tolerando erros de chave
        self.usuarios: Dict[str, Usuario] = SafeDict(default=None)
        self.jogos: Dict[str, Jogo] = SafeDict(default=None)
        self.matchmaking = MatchmakingQueue(tamanho_partida=2)
        # Cadeia de suporte (Chain of Responsibility)
        self._suporte_chain = AtendimentoBasico(AtendimentoAvancado(AtendimentoFallback()))

    def encontrar_usuario(self, nome_ou_email: str) -> Optional[Usuario]:
        for user in self.usuarios.values():
            if user and (user.nome == nome_ou_email or user.email == nome_ou_email):
                return user
        return None

    # Chain of Responsibility – processa tickets de um usuário
    @safe_call(log=True)
    def processar_tickets_usuario(self, usuario: Usuario) -> None:
        for t in usuario.listar_tickets():
            if t.get('status') == 'Aberto':
                self._suporte_chain.handle(t)


# ================================================================
#   Singleton (Criacional)
# ================================================================
class PlataformaSingleton(Plataforma):
    """Garante que exista apenas uma instância da Plataforma."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            Plataforma.__init__(cls._instance)
        return cls._instance


# ================================================================
#   Facade (Estrutural)
# ================================================================
class PlataformaFacade:
    """
    Fachada para simplificar o uso da Plataforma, encapsulando
    operações comuns sem expor a complexidade interna.
    """
    def __init__(self, plataforma: Plataforma):
        self.p = plataforma

    @try_catch_wrapper
    def cadastrar_usuario_adulto(self, nome: str, email: str, senha: str, idade: int) -> UsuarioAdulto:
        u = UsuarioAdulto(nome, email, senha, idade)
        self.p.usuarios[nome] = u
        return u

    @try_catch_wrapper
    def cadastrar_usuario_infantil(self, nome: str, email: str, senha: str, idade: int, responsavel_email: str) -> UsuarioInfantil:
        u = UsuarioInfantil(nome, email, senha, idade, responsavel_email)
        self.p.usuarios[nome] = u
        return u

    @try_catch_wrapper
    def publicar_patch(self, nome_jogo: str, versao: str, notas: str) -> None:
        jogo = self.p.jogos.get(nome_jogo)
        if not jogo:
            raise NotFoundError(f"Jogo '{nome_jogo}' não encontrado.")
        jogo.publicar_patch(versao, notas)

    @try_catch_wrapper
    def comprar_jogo(self, usuario: Usuario, nome_jogo: str) -> None:
        jogo = self.p.jogos.get(nome_jogo)
        if not jogo:
            raise NotFoundError(f"Jogo '{nome_jogo}' não encontrado.")
        usuario.comprar_jogo(jogo)

    @try_catch_wrapper
    def registrar_pacote_achievements(self, nome_jogo: str, pack: AchievementPack) -> None:
        jogo = self.p.jogos.get(nome_jogo)
        if not jogo:
            raise NotFoundError(f"Jogo '{nome_jogo}' não encontrado.")
        jogo.registrar_achievement_component(pack)
