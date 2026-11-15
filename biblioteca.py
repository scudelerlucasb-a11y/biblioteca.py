import sqlite3

conexao = sqlite3.connect('biblioteca.db')
conexao.execute("PRAGMA foreign_keys = ON")


conexao.execute('''
CREATE TABLE IF NOT EXISTS categoria(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    genero TEXT NOT NULL UNIQUE,
    bloco TEXT NOT NULL
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS livro(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'fisico'
        CHECK (tipo IN ('fisico', 'digital')),
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categoria (id)
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS autor(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS livro_autor(
    id_livro INTEGER NOT NULL,
    id_autor INTEGER NOT NULL,
    PRIMARY KEY (id_livro, id_autor),
    FOREIGN KEY (id_livro) REFERENCES livro (id) ON DELETE CASCADE,
    FOREIGN KEY (id_autor) REFERENCES autor (id) ON DELETE CASCADE
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS exemplar(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    estado TEXT NOT NULL DEFAULT 'bom'
        CHECK (estado IN ('bom', 'danificado', 'perdido')),
    status TEXT NOT NULL DEFAULT 'livre'
        CHECK (status IN ('livre', 'emprestado', 'reservado')),
    id_livro INTEGER NOT NULL,
    FOREIGN KEY (id_livro) REFERENCES livro (id)
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS socio(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    data_nascimento TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    data_cadastro TEXT NOT NULL DEFAULT (date('now'))
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS funcionario(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cargo TEXT NOT NULL
        CHECK (cargo IN ('bibliotecaria', 'logistica', 'dono')),
    cracha TEXT NOT NULL UNIQUE,
    bloco TEXT
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS emprestimo(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_emprestimo TEXT NOT NULL DEFAULT (date('now')),
    data_prevista TEXT NOT NULL,
    data_devolucao TEXT,
    id_socio INTEGER NOT NULL,
    id_exemplar INTEGER NOT NULL,
    id_funcionario INTEGER NOT NULL,
    CHECK (data_prevista >= data_emprestimo),
    FOREIGN KEY (id_socio) REFERENCES socio (id),
    FOREIGN KEY (id_exemplar) REFERENCES exemplar (id),
    FOREIGN KEY (id_funcionario) REFERENCES funcionario (id)
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS reserva(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_reserva TEXT NOT NULL DEFAULT (date('now')),
    ativa TEXT NOT NULL DEFAULT 'sim'
        CHECK (ativa IN ('sim', 'nao')),
    id_socio INTEGER NOT NULL,
    id_livro INTEGER NOT NULL,
    FOREIGN KEY (id_socio) REFERENCES socio (id),
    FOREIGN KEY (id_livro) REFERENCES livro (id)
)
''')


conexao.execute('''
CREATE TABLE IF NOT EXISTS multa(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor REAL NOT NULL CHECK (valor >= 0),
    pago TEXT NOT NULL DEFAULT 'nao'
        CHECK (pago IN ('sim', 'nao')),
    data_geracao TEXT NOT NULL DEFAULT (date('now')),
    id_emprestimo INTEGER NOT NULL,
    FOREIGN KEY (id_emprestimo) REFERENCES emprestimo (id)
)
''')

conexao.commit()

conexao.execute("INSERT OR IGNORE INTO categoria (genero, bloco) VALUES ('Romance', 'A')")
conexao.execute("INSERT OR IGNORE INTO categoria (genero, bloco) VALUES ('Tecnologia', 'B')")
conexao.execute("INSERT OR IGNORE INTO categoria (genero, bloco) VALUES ('Historia', 'C')")
conexao.execute("INSERT OR IGNORE INTO funcionario (nome, cargo, cracha) VALUES ('Maria', 'bibliotecaria', '001')")
conexao.execute("INSERT INTO livro (titulo, tipo, id_categoria) SELECT 'Dom Casmurro', 'fisico', 1 WHERE NOT EXISTS (SELECT 1 FROM livro)")
conexao.execute("UPDATE exemplar SET codigo = '1001' WHERE codigo = 'EX001'")
conexao.execute("INSERT OR IGNORE INTO exemplar (codigo, id_livro) VALUES ('1001', 1)")
conexao.commit()

opcao1 = "1 - Listar livros"
opcao2 = "2 - Cadastrar livros"
opcao3 = "3 - Cadastrar sócio"
opçao4 = "4 - Registrar empréstimo"
opçao5 = "5 - Registrar devolução (gera multa se atrasou)"
opçao6 = "6 - Ver empréstimos em aberto / atrasados"
opçao7 = "7 - Cadastrar funcionário"
opçao8 = "8 - Cadastrar exemplar"
opçao9 = "9 - Sair"

while True:
    print("\nEscolha uma das opçoes abaixo")
    print(opcao1)
    print(opcao2)
    print(opcao3)
    print(opçao4)
    print(opçao5)
    print(opçao6)
    print(opçao7)
    print(opçao8)
    print(opçao9)

    try:
        resposta = int(input('Digite o numero da opçao desejada : '))
    except ValueError:
        print("Digite apenas números")
        continue

    if resposta == 1:
        lista = conexao.execute("SELECT livro.titulo, livro.tipo, categoria.genero FROM livro JOIN categoria ON categoria.id = livro.id_categoria")
        check = lista.fetchall()
        if not check:
            print("Ainda nenhum livro")
        else:
            for titulo, tipo, genero in check:
                print(f"{titulo}: {tipo} e sua categoria é {genero}")

    elif resposta == 2:
        titulo = input("\nDigite o titulo do livro: ")
        tipo = input("Digite se o livro é (digital ou fisico): ").strip().lower().replace("í", "i")
        categoria = input("Digite o categoria do livro ex:(Romance, Tecnologia, Historia): ")
        procura = conexao.execute("SELECT id FROM categoria WHERE genero = ? COLLATE NOCASE", (categoria.strip(),))
        check = procura.fetchall()
        if not check:
            print("Categoria não encontrada")
            continue
        id_categoria = check[0][0]
        try:
            adicionar = conexao.execute("INSERT INTO livro(titulo, tipo, id_categoria) VALUES (?, ?, ?)", (titulo, tipo, id_categoria))
            conexao.commit()
            print("Livro adicionado com sucesso")
            if tipo == "fisico":
                print("Para emprestar, cadastre um exemplar dele na opção 8")
            else:
                print("Livro digital não tem exemplar e não pode ser emprestado")
        except sqlite3.IntegrityError:
            print("Erro: o tipo deve ser digital ou fisico")

    elif resposta == 3:
        cpf = input("\nDigite o CPF do sócio: ")
        procura = conexao.execute("SELECT id, nome FROM socio WHERE cpf = ?", (cpf,))
        check = procura.fetchall()
        if check:
            print("Esse sócio já está cadastrado")
        else:
            nome = input("Digite o nome do sócio: ")
            nascimento = input("Digite a data de nascimento (AAAA-MM-DD): ")
            if conexao.execute("SELECT julianday(?)", (nascimento,)).fetchone()[0] is None:
                print("Data inválida. Use o formato AAAA-MM-DD")
                continue
            telefone = input("Digite o telefone: ")
            email = input("Digite o e-mail: ")
            adicionar = conexao.execute("INSERT INTO socio(nome, cpf, data_nascimento, telefone, email) VALUES (?, ?, ?, ?, ?)", (nome, cpf, nascimento, telefone, email))
            conexao.commit()
            print("Sócio adicionado com sucesso")
            print(f"Bem vindo: {nome}")

    elif resposta == 4:
        cpf = input("\nDigite o CPF do sócio: ")
        procura = conexao.execute("SELECT id, nome FROM socio WHERE cpf = ?", (cpf,))
        check = procura.fetchall()
        if not check:
            print("Sócio não cadastrado. Use a opção 3 para cadastrar primeiro.")
            continue
        id_socio = check[0][0]
        lista = conexao.execute(
            "SELECT exemplar.codigo, livro.titulo FROM exemplar JOIN livro ON livro.id = exemplar.id_livro WHERE exemplar.status = 'livre' AND exemplar.estado = 'bom'")
        check = lista.fetchall()
        if not check:
            print("Nenhum exemplar livre")
            continue
        for codigo, titulo in check:
            print(f"{codigo}: {titulo}")
        codigo = input("\nDigite o código do exemplar (só números): ")
        if not codigo.isdigit():
            print("O código deve ter apenas números")
            continue
        procura = conexao.execute("SELECT id FROM exemplar WHERE codigo = ? AND status = 'livre' AND estado = 'bom'", (codigo,))
        check = procura.fetchall()
        if not check:
            print("Exemplar não encontrado ou não está livre")
            continue
        id_exemplar = check[0][0]
        cracha = input("\nDigite o crachá do funcionário: ")
        procura = conexao.execute("SELECT id FROM funcionario WHERE cracha = ?", (cracha,))
        check = procura.fetchall()
        if not check:
            print("Funcionário não encontrado")
            continue
        id_funcionario = check[0][0]
        data = input("\nDigite a data do emprestimo (AAAA-MM-DD): ")
        previsao = input("Digite a previsão (AAAA-MM-DD): ")
        datas = conexao.execute("SELECT julianday(?), julianday(?)", (data, previsao)).fetchone()
        if None in datas:
            print("Data inválida. Use o formato AAAA-MM-DD")
            continue
        try:
            adicionar = conexao.execute(
                "INSERT INTO emprestimo(data_emprestimo, data_prevista, id_socio, id_exemplar, id_funcionario) VALUES (?, ?, ?, ?, ?)",
                (data, previsao, id_socio, id_exemplar, id_funcionario))
            conexao.execute("UPDATE exemplar SET status = 'emprestado' WHERE id = ?", (id_exemplar,))
            conexao.commit()
            print("Empréstimo registrado com sucesso")
        except sqlite3.IntegrityError:
            print("Erro: a previsão não pode ser antes da data do empréstimo")

    elif resposta == 5:
        codigo = input("\nDigite o código do exemplar devolvido (só números): ")
        if not codigo.isdigit():
            print("O código deve ter apenas números")
            continue
        procura = conexao.execute("SELECT emprestimo.id, emprestimo.data_prevista, exemplar.id FROM emprestimo JOIN exemplar ON exemplar.id = emprestimo.id_exemplar WHERE exemplar.codigo = ? AND emprestimo.data_devolucao IS NULL", (codigo,))
        check = procura.fetchall()
        if not check:
            print("Nenhum empréstimo em aberto para esse exemplar")
        else:
            id_emprestimo, previsao, id_exemplar = check[0]
            devolucao = input("Digite a data da devolução (AAAA-MM-DD): ")
            dias = conexao.execute("SELECT julianday(?) - julianday(?)", (devolucao, previsao)).fetchone()[0]
            if dias is None:
                print("Data inválida. Use o formato AAAA-MM-DD")
            else:
                conexao.execute("UPDATE emprestimo SET data_devolucao = ? WHERE id = ?", (devolucao, id_emprestimo))
                conexao.execute("UPDATE exemplar SET status = 'livre' WHERE id = ?", (id_exemplar,))
                if dias > 0:
                    valor = int(dias) * 2
                    conexao.execute("INSERT INTO multa(valor, id_emprestimo) VALUES (?, ?)", (valor, id_emprestimo))
                    print(f"Devolução registrada com {int(dias)} dia(s) de atraso. Multa de R$ {valor:.2f}")
                else:
                    print("Devolução registrada no prazo")
                conexao.commit()

    elif resposta == 6:
        lista = conexao.execute("SELECT socio.nome, livro.titulo, emprestimo.data_prevista FROM emprestimo JOIN socio ON socio.id = emprestimo.id_socio JOIN exemplar ON exemplar.id = emprestimo.id_exemplar JOIN livro ON livro.id = exemplar.id_livro WHERE emprestimo.data_devolucao IS NULL")
        check = lista.fetchall()
        if not check:
            print("Nenhum empréstimo em aberto")
        else:
            hoje = conexao.execute("SELECT date('now')").fetchone()[0]
            for nome, titulo, previsao in check:
                if previsao < hoje:
                    print(f"{nome} - {titulo} - previsto para {previsao} - ATRASADO")
                else:
                    print(f"{nome} - {titulo} - previsto para {previsao} - no prazo")

    elif resposta == 7:
        cracha = input("\nDigite o crachá do funcionário: ")
        procura = conexao.execute("SELECT id, nome FROM funcionario WHERE cracha = ?", (cracha,))
        check = procura.fetchall()
        if check:
            print("Esse crachá já está cadastrado")
        else:
            nome = input("Digite o nome do funcionário: ")
            cargo = input("Digite o cargo (bibliotecaria, logistica ou dono): ")
            bloco = input("Digite o bloco (ou deixe vazio): ")
            try:
                adicionar = conexao.execute("INSERT INTO funcionario(nome, cargo, cracha, bloco) VALUES (?, ?, ?, ?)", (nome, cargo, cracha, bloco))
                conexao.commit()
                print("Funcionário adicionado com sucesso")
            except sqlite3.IntegrityError:
                print("Erro: o cargo deve ser bibliotecaria, logistica ou dono")

    elif resposta == 8:
        lista = conexao.execute("SELECT id, titulo FROM livro WHERE tipo = 'fisico'")
        check = lista.fetchall()
        if not check:
            print("Nenhum livro físico cadastrado")
            continue
        for id_livro, titulo in check:
            print(f"{id_livro} - {titulo}")
        id_livro = input("\nDigite o número do livro: ")
        procura = conexao.execute("SELECT id FROM livro WHERE id = ? AND tipo = 'fisico'", (id_livro,))
        check = procura.fetchall()
        if not check:
            print("Livro físico não encontrado")
            continue
        codigo = input("Digite o código do exemplar (só números): ")
        if not codigo.isdigit():
            print("O código deve ter apenas números")
            continue
        try:
            adicionar = conexao.execute("INSERT INTO exemplar(codigo, id_livro) VALUES (?, ?)", (codigo, check[0][0]))
            conexao.commit()
            print("Exemplar adicionado com sucesso")
        except sqlite3.IntegrityError:
            print("Erro: esse código de exemplar já existe")

    elif resposta == 9:
        break

conexao.close()
