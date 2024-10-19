-- scripts de criação de tabelas em postgresql

CREATE TABLE IF NOT EXISTS hotel (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    morada VARCHAR(160) NOT NULL,
    codpostal VARCHAR(8) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    estrelas int NOT NULL
);

CREATE TABLE IF NOT EXISTS tipoQuarto (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,
    vista char(1) NOT NULL, -- P - Piscina, M - Mar, S - Serra, N - Nenhuma
    qualidade char(1) NOT NULL -- B - Baixa, S - Superior
); 

CREATE TABLE IF NOT EXISTS comodidade (
    id SERIAL PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS quarto (
    id SERIAL PRIMARY KEY,
    tipoID int NOT NULL REFERENCES tipoQuarto(id),
    hotelID int NOT NULL REFERENCES hotel(id),
    numero int NOT NULL,
    precoBase float NOT NULL,
    estado int not null, -- 0 - livre, 1 - Sujo, 2 - manutenção
    capacidade char(1) not null -- S - Single, D - Double, T - Triple, Q - Quad, K - King, F - Family
);

CREATE TABLE IF NOT EXISTS epoca (
    id SERIAL PRIMARY KEY,
    epoca char(1) NOT NULL, -- A - Alta, B - Baixa, F - Festividades
    dataInicio DATE NOT NULL,
    dataFim DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS precoEpoca (
    id SERIAL PRIMARY KEY,
    epocaID int NOT NULL REFERENCES epoca(id),
    taxa float NOT NULL
);

CREATE TABLE IF NOT EXISTS quartoComodidade (
    quartoID int NOT NULL REFERENCES quarto(id),
    comodidadeID int NOT NULL REFERENCES comodidade(id),
    PRIMARY KEY (quartoID, comodidadeID)
);

CREATE TABLE IF NOT EXISTS permissoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    nivel int not null
);

Insert into permissoes (id, nome, nivel)
values (1, 'Admin', 1),
       (2, 'Manager', 2),
       (3, 'Funcionário', 3);


CREATE TABLE IF NOT EXISTS utilizador (
    id SERIAL PRIMARY KEY,
    pNome VARCHAR(100) NOT NULL,
    uNome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hashedPassword VARCHAR(100) NOT NULL,
    inactivo BOOLEAN NOT NULL, 
    nif VARCHAR(20) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    morada VARCHAR(160) NOT NULL,
    codpostal VARCHAR(8) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    tipo char(1) NOT NULL default 'C', -- C - Cliente, F - Funcionário, 
    roleID int null REFERENCES permissoes(id)    
);

CREATE TABLE IF NOT EXISTS reserva (
    id SERIAL PRIMARY KEY,
    clienteID int NOT NULL REFERENCES utilizador(id),
    dataInicio DATE NOT NULL,
    dataFim DATE NOT NULL,
    estado char(1) NOT NULL, -- P - Pendente, C - Confirmada, R - Rejeitada, 
    valorTotal float NOT NULL
);

CREATE TABLE IF NOT EXISTS reservaQuarto (
    reservaID int NOT NULL REFERENCES reserva(id),
    quartoID int NOT NULL REFERENCES quarto(id),
    PRIMARY KEY (reservaID, quartoID)
);

CREATE TABLE IF NOT EXISTS hospedes (
    id SERIAL PRIMARY KEY,
    reservaID int NOT NULL REFERENCES reserva(id),
    nome VARCHAR(100) NOT NULL,
    ccpass VARCHAR(20) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    morada VARCHAR(160) NOT NULL,
    codpostal VARCHAR(8) NOT NULL,
    cidade VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS metodoPagamento (
    id SERIAL PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL
);

CREATE table if not exists fatura (
    id SERIAL PRIMARY KEY,
    reservaID int NOT NULL REFERENCES reserva(id),
    clienteID int NOT NULL REFERENCES utilizador(id),
    valorFinal float NOT NULL,
    dataEmissao DATE NOT NULL,
    dataVencimento DATE NOT NULL,
    paga BOOLEAN NOT NULL, 
    metodoPagamentoID int NOT NULL REFERENCES metodoPagamento(id)
);
/*
CREATE TABLE IF NOT EXISTS faturaDetalhes (
    faturaID int NOT NULL REFERENCES fatura(id),
    descricao VARCHAR(100) NOT NULL,
    valorUbitario float NOT NULL,
    quantidade int NOT NULL,
    valorFinal float NOT NULL,
    PRIMARY KEY (faturaID, descricao)
);*/