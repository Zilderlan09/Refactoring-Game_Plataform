# main.py
from game import (
    Plataforma, POOCoin, JogoOnline, JogoOffline, Achievement,
    UsuarioAdulto, UsuarioInfantil, Admin, Jogo
)


def menu_admin(plataforma: Plataforma, admin: Admin):
    while True:
        print("\n[ADMIN]")
        print("1 - Gerenciar Jogos")
        print("2 - Adicionar Pontuação a um Jogador")
        print("3 - Listar Usuários")
        print("4 - Publicar Patch em um Jogo")
        print("5 - Cadastrar Achievements em um Jogo")
        print("6 - Deslogar\n")
        escolha = input("> ")

        if escolha == '1':
            gerenciar_jogos_admin(plataforma)
        elif escolha == '2':
            nome_usr = input("Adicionar pontos para qual usuário? ")
            usuario = plataforma.encontrar_usuario(nome_usr)
            if not usuario:
                print("Usuário não encontrado.")
                continue
            nome_jogo = input(f"Em qual jogo adicionar pontos para {nome_usr}? ")
            jogo = plataforma.jogos.get(nome_jogo)
            if not jogo:
                print("Jogo não encontrado.")
                continue
            if not usuario.possui_jogo(nome_jogo):
                print(f"Erro: O usuário '{usuario.nome}' não possui o jogo '{nome_jogo}'.")
                continue
            try:
                pontos = int(input("Quantos pontos? "))
                jogo.adicionar_pontuacao(usuario.nome, pontos)
                novos = jogo.verificar_achievements_para(usuario.nome, jogo.pontuacoes[usuario.nome])
                usuario.registrar_achievements_desbloqueados(jogo, novos)
            except ValueError:
                print("Valor de pontos inválido.")
        elif escolha == '3':
            for u in plataforma.usuarios.values():
                print(f"- {u.nome} ({u.obter_tipo_conta()})")
        elif escolha == '4':
            nome_jogo = input("Publicar patch para qual jogo? ")
            jogo = plataforma.jogos.get(nome_jogo)
            if not jogo:
                print("Jogo não encontrado.")
                continue
            versao = input("Nova versão (ex: 1.1.0): ").strip()
            notas = input("Notas do patch: ").strip()
            jogo.publicar_patch(versao, notas)
        elif escolha == '5':
            nome_jogo = input("Cadastrar achievements em qual jogo? ")
            jogo = plataforma.jogos.get(nome_jogo)
            if not jogo:
                print("Jogo não encontrado.")
                continue
            try:
                qtd = int(input("Quantos achievements deseja adicionar? "))
            except ValueError:
                print("Número inválido.")
                continue
            for _ in range(qtd):
                cod = input("Código (único): ").strip()
                tit = input("Título: ").strip()
                desc = input("Descrição: ").strip()
                try:
                    pmin = int(input("Pontos mínimos para desbloquear: "))
                except ValueError:
                    pmin = 0
                jogo.registrar_achievement(Achievement(codigo=cod, titulo=tit, descricao=desc, pontos_minimos=pmin))
            print("Achievements cadastrados.")
        elif escolha == '6':
            break


def gerenciar_jogos_admin(plataforma: Plataforma):
    while True:
        print("\n    Gerenciamento de Jogos\n")
        print("1 - Adicionar jogo")
        print("2 - Adicionar item a um jogo")
        print("3 - Listar patches de um jogo")
        print("4 - Voltar")
        escolha = input("> ")
        if escolha == '1':
            nome_jogo = input("Nome do jogo: ")
            if nome_jogo in plataforma.jogos:
                print("Jogo já existe.")
                continue
            try:
                preco = float(input("Preço do jogo em POOCoins: "))
                plataformas = input("Plataformas suportadas (ex: PC,Mobile,Console): ").split(",")
                plataformas = {p.strip() for p in plataformas if p.strip()}
            except ValueError:
                print("Preço inválido.")
                continue
            tipo = input("\nJogo é (1) Online ou (2) Offline? ")
            if tipo == '1':
                plataforma.jogos[nome_jogo] = JogoOnline(nome_jogo, POOCoin(preco), plataformas)
            elif tipo == '2':
                plataforma.jogos[nome_jogo] = JogoOffline(nome_jogo, POOCoin(preco), plataformas)
            else:
                print("Tipo inválido. Jogo não criado.")
                continue
            print("\nJogo adicionado!")
        elif escolha == '2':
            nome_jogo = input("Adicionar item em qual jogo? ")
            jogo = plataforma.jogos.get(nome_jogo)
            if not jogo:
                print("Jogo não encontrado.")
                continue
            item = input("Nome do item: ")
            try:
                preco = float(input("Preço em POOCoins: "))
                jogo.adicionar_item_loja(item, POOCoin(preco))
                print("Item adicionado à loja!")
            except ValueError:
                print("Preço inválido.")
        elif escolha == '3':
            nome_jogo = input("Listar patches de qual jogo? ")
            jogo = plataforma.jogos.get(nome_jogo)
            if not jogo:
                print("Jogo não encontrado.")
                continue
            jogo.listar_patches()
        elif escolha == '4':
            break


def menu_dependentes(plataforma: Plataforma, usuario_adulto: UsuarioAdulto):
    print("\n    Gerenciamento de Dependentes ")
    pendentes = [u for u in plataforma.usuarios.values()
                 if isinstance(u, UsuarioInfantil)
                 and u.responsavel_email == usuario_adulto.email
                 and u.status_aprovacao == 'pendente']
    if pendentes:
        print("Contas pendentes de aprovação:")
        for i, dep in enumerate(pendentes, 1):
            print(f"{i} - {dep.nome} (Idade: {dep.idade})")
        try:
            escolha = int(input("Digite o número da conta para aprovar (ou 0 para cancelar): "))
            if 0 < escolha <= len(pendentes):
                dependente_aprovado = pendentes[escolha - 1]
                dependente_aprovado.status_aprovacao = 'aprovado'
                print(f"Conta de {dependente_aprovado.nome} aprovada!")
                usuario_adulto.definir_permissoes(dependente_aprovado)
        except ValueError:
            print("Entrada inválida.")
    else:
        print("Nenhuma conta pendente de aprovação.")


def menu_suporte(usuario):
    print("\n    Central de Suporte")
    print("1 - Abrir um ticket de suporte")
    print("2 - Ver meus tickets")
    escolha = input("> ")
    if escolha == '1':
        problema = input("Descreva seu problema: ")
        usuario.abrir_ticket(problema)
        print("Ticket aberto com sucesso!")
    elif escolha == '2':
        tickets = usuario.listar_tickets()
        if not tickets:
            print("Você não tem tickets abertos.")
        for i, ticket in enumerate(tickets, 1):
            print(f"{i}. Problema: {ticket['problema']} | Status: {ticket['status']}")


def menu_matchmaking(plataforma: Plataforma, usuario):
    print("\n[Matchmaking]")
    print("1 - Entrar na fila")
    print("2 - Tentar formar partida")
    print("3 - Voltar")
    esc = input("> ")
    if esc == '1':
        nome_jogo = input("Fila de qual jogo? ")
        if nome_jogo not in plataforma.jogos:
            print("Jogo não encontrado.")
            return
        if not usuario.possui_jogo(nome_jogo):
            print("Você precisa possuir o jogo para entrar na fila.")
            return
        plataforma.matchmaking.entrar_fila(nome_jogo, usuario.nome)
    elif esc == '2':
        nome_jogo = input("Formar partida para qual jogo? ")
        plataforma.matchmaking.tentar_formar_partida(nome_jogo)


def menu_usuario(plataforma: Plataforma, usuario):
    # Verifica aprovação no caso de infantil
    if isinstance(usuario, UsuarioInfantil) and usuario.status_aprovacao == 'pendente':
        print("\nSua conta está pendente de aprovação. Peça para seu responsável liberá-la.")
        return

    while True:
        print(f"\n    Menu: {usuario.nome} | Saldo: {usuario.saldo} | Plataforma: {usuario.preferencia_plataforma or '—'}\n")
        if hasattr(usuario, "dependentes"):
            print("0 - Gerenciar Dependentes")
        print("1 - Loja de Jogos")
        print("2 - Comprar Item")
        print("3 - Adicionar Saldo")
        print("4 - Ver Catálogo de Jogos e Rankings")
        print("5 - Gerenciar Preferências")
        print("6 - Acessar Fórum (Jogos Online)")
        print("7 - Suporte ao Usuário")
        print("8 - Ver Minhas Mensagens")
        print("9 - Definir Plataforma Preferida (PC/Mobile/Console)")
        print("10 - Matchmaking")
        print("11 - Atualizações (Patch) dos meus jogos")
        print("12 - Achievements dos meus jogos")
        print("13 - Deslogar")
        escolha = input("> ")

        if escolha == '1':
            print("\n    Loja de Jogos Disponíveis")
            jogos_a_venda = {}
            for nome, jogo in plataforma.jogos.items():
                if not usuario.possui_jogo(nome):
                    if usuario.preferencia_plataforma and usuario.preferencia_plataforma not in jogo.plataformas:
                        continue
                    jogos_a_venda[nome] = jogo
            if not jogos_a_venda:
                print("Não há jogos compatíveis disponíveis ou você já possui todos.")
            else:
                for nome, jogo in jogos_a_venda.items():
                    print(f"- {nome} | Preço: {jogo.preco} | Plataformas: {', '.join(sorted(jogo.plataformas))} | v{jogo.versao_atual}")
                jogo_a_comprar = input("Digite o nome do jogo que deseja comprar (ou enter para voltar): ").strip()
                if jogo_a_comprar in jogos_a_venda:
                    usuario.comprar_jogo(jogos_a_venda[jogo_a_comprar])
                elif jogo_a_comprar:
                    print("Jogo não encontrado na loja.")

        elif escolha == '2':
            print("\n    Sua Biblioteca de Jogos")
            nomes = usuario.listar_jogos_nomes()
            if not nomes:
                print("Você ainda não possui jogos.")
            else:
                for nome_jogo in nomes:
                    print(f"- {nome_jogo}")
                nome_jogo = input("Comprar item de qual jogo? ").strip()
                if usuario.possui_jogo(nome_jogo):
                    jogo = plataforma.jogos.get(nome_jogo)
                    itens = jogo.listar_itens_loja()
                    if not itens:
                        print("Este jogo não possui itens à venda.")
                    else:
                        print("Itens disponíveis:")
                        for item, preco in itens.items():
                            print(f"- {item}: {preco}")
                        item = input("Qual item? ").strip()
                        usuario.comprar_item(jogo, item)
                else:
                    print("Você não possui este jogo.")

        elif escolha == '3':
            try:
                valor = float(input("Digite o valor em POOCoins para adicionar: "))
                usuario.adicionar_saldo(POOCoin(valor))
            except ValueError:
                print("Valor inválido.")

        elif escolha == '4':
            for jogo in plataforma.jogos.values():
                jogo.mostrar_ranking()

        elif escolha == '5':
            prefs = input("Digite suas preferências, separadas por vírgula (ex: RPG, Aventura): ")
            usuario.atualizar_preferencias(prefs)

        elif escolha == '6':
            nome_jogo = input("Acessar fórum de qual jogo? ").strip()
            jogo = plataforma.jogos.get(nome_jogo)
            if isinstance(jogo, JogoOnline):
                if usuario.possui_jogo(jogo.nome):
                    jogo.ver_forum()
                    postar = input("Deseja postar uma mensagem? (s/n) ").lower()
                    if postar == 's':
                        msg = input("Sua mensagem: ")
                        jogo.postar_no_forum(usuario.nome, msg)
                else:
                    print("Você precisa possuir este jogo para acessar o fórum.")
            else:
                print("Este jogo não é online ou não existe.")

        elif escolha == '7':
            menu_suporte(usuario)

        elif escolha == '8':
            print("\n    Caixa de Entrada\n")
            mensagens = usuario.listar_mensagens()
            if not mensagens:
                print("Nenhuma mensagem.")
            for msg in mensagens:
                print(f"- {msg}")

        elif escolha == '9':
            plat = input("Informe sua plataforma preferida (PC/Mobile/Console) ou deixe em branco para limpar: ").strip()
            usuario.definir_preferencia_plataforma(plat if plat else None)

        elif escolha == '10':
            menu_matchmaking(plataforma, usuario)

        elif escolha == '11':
            nomes = usuario.listar_jogos_nomes()
            if not nomes:
                print("Você não possui jogos.")
            else:
                for nome_jogo in nomes:
                    reg = usuario.get_registro_jogo(nome_jogo)
                    jogo = reg["obj"]
                    inst = reg["versao_instalada"]
                    print(f"- {nome_jogo}: instalado v{inst} | atual v{jogo.versao_atual}")
                alvo = input("Atualizar qual jogo? (enter para cancelar) ").strip()
                if alvo:
                    usuario.atualizar_jogo(alvo)

        elif escolha == '12':
            nomes = usuario.listar_jogos_nomes()
            if not nomes:
                print("Você não possui jogos.")
            else:
                for nome_jogo in nomes:
                    jogo = plataforma.jogos.get(nome_jogo)
                    usuario.listar_achievements_usuario(jogo)

        elif escolha == '0' and hasattr(usuario, "dependentes"):
            menu_dependentes(plataforma, usuario)  # type: ignore

        elif escolha == '13':
            break


def criar_usuario(plataforma: Plataforma):
    nome = input("Digite o nome do novo usuário: ").strip()
    if plataforma.encontrar_usuario(nome):
        print("Nome de usuário já existe!")
        return
    email = input("Digite seu e-mail: ").strip()
    if plataforma.encontrar_usuario(email):
        print("E-mail já cadastrado!")
        return
    try:
        idade = int(input("Digite sua idade: "))
    except ValueError:
        print("Idade inválida.")
        return
    senha = input("Digite sua senha: ").strip()

    if idade < 18:
        email_resp = input("Por ser menor de idade, digite o e-mail de um responsável já cadastrado: ").strip()
        responsavel = plataforma.encontrar_usuario(email_resp)
        if isinstance(responsavel, UsuarioAdulto):
            novo_usuario = UsuarioInfantil(nome, email, senha, idade, email_resp)
            plataforma.usuarios[nome] = novo_usuario
            responsavel.adicionar_mensagem(
                f"Sistema: O usuário '{nome}' ({idade} anos) solicitou aprovação como seu dependente."
            )
            print("\nConta criada! Peça ao seu responsável para checar as mensagens e aprovar seu cadastro.")
        else:
            print("\nE-mail do responsável não encontrado ou não é uma conta de adulto. Cadastro cancelado.")
    else:
        novo_usuario = UsuarioAdulto(nome, email, senha, idade)
        plataforma.usuarios[nome] = novo_usuario
        print("\nConta criada com sucesso!\n")


def login(plataforma: Plataforma):
    nome_usuario = input("Digite seu nome de usuário ou e-mail: ").strip()
    senha = input("Digite sua senha: ").strip()
    usuario = plataforma.encontrar_usuario(nome_usuario)

    if usuario and usuario.verificar_senha(senha):
        print(f"\nLogin bem-sucedido! Bem-vindo, {usuario.nome}!\n")
        if isinstance(usuario, Admin):
            menu_admin(plataforma, usuario)
        else:
            menu_usuario(plataforma, usuario)
    else:
        print("\nUsuário ou senha inválidos.\n")


def executar(plataforma: Plataforma):
    while True:
        print("\n    MENU PRINCIPAL\n")
        print("1 - Login")
        print("2 - Criar nova conta")
        print("3 - Sair")
        escolha = input("\nEscolha uma opção: ")

        if escolha == "1":
            login(plataforma)
        elif escolha == "2":
            criar_usuario(plataforma)
        elif escolha == "3":
            print("Obrigado por jogar! Saindo...")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    # ================= Pré-configuração (silenciosa) =================
    plataforma_gaming = Plataforma()

    # Jogos com plataformas
    jogo1 = JogoOnline("Aventuras_em_POO", POOCoin(100.0), {"PC", "Console"})
    jogo2 = JogoOffline("Semestre_Rush", POOCoin(50.0), {"PC"})
    plataforma_gaming.jogos[jogo1.nome] = jogo1
    plataforma_gaming.jogos[jogo2.nome] = jogo2

    # Itens e fórum (silencioso)
    jogo1.adicionar_item_loja('Ponto_Extra', POOCoin(10.0))
    jogo1.postar_no_forum("lucas", "Não sei programar em Python! :(", notify=False)

    # Achievements exemplo
    jogo1.registrar_achievement(Achievement("P100", "Primeiros Passos", "Marque ao menos 100 pontos.", 100))
    jogo1.registrar_achievement(Achievement("P1000", "Veterano", "Marque ao menos 1000 pontos.", 1000))

    # Usuários
    luu = UsuarioAdulto("luu", "luu@ic.com", "luu123", 30)
    rafael = UsuarioInfantil("rafael", "rafael@email.com", "rafael123", 12, "luu@ic.com")
    maria = UsuarioInfantil("maria", "maria@email.com", "maria123", 10, "luu@ic.com")
    plataforma_gaming.usuarios.update({luu.nome: luu, rafael.nome: rafael, maria.nome: maria})

    # Saldos (silencioso)
    luu.adicionar_saldo(POOCoin(250), notify=False)
    rafael.adicionar_saldo(POOCoin(75), notify=False)

    # Aprovação e permissões do infantil
    rafael.status_aprovacao = 'aprovado'
    rafael.permissoes['pode_comprar_itens'] = True
    rafael.permissoes['pode_comprar_jogos'] = False

    # Mensagem para o responsável (via API)
    luu.adicionar_mensagem(
        f"Sistema: A usuária '{maria.nome}' ({maria.idade} anos) solicitou aprovação como sua dependente."
    )

    # Pontuações e achievements (silenciosos)
    jogo1.adicionar_pontuacao(luu.nome, 2100, notify=False)
    jogo1.adicionar_pontuacao(rafael.nome, 1250, notify=False)
    for u in (luu, rafael):
        pontos = jogo1.pontuacoes.get(u.nome, 0)
        novos = jogo1.verificar_achievements_para(u.nome, pontos)
        u.registrar_achievements_desbloqueados(jogo1, novos, notify=False)

    # Compra do jogo apenas para o adulto (silenciosa)
    luu.comprar_jogo(jogo1, notify=False)

    # ================= Executar CLI =================
    executar(plataforma_gaming)
