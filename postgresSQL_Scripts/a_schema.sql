-- scripts de criação de tabelas em postgresql
/*==============================================================*/
/* DBMS name:      POSTGRESQL                                   */
/* Created on:     18/10/2024 23:59:59                          */
/* Last Modified:  31/10/2024 23:59:59                          */
/*==============================================================*/



 /** 
  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |    _______   | || |     ______   | || |  ____  ____  | || |  _________   | || | ____    ____ | || |      __      | || |    _______   | |
| |   /  ___  |  | || |   .' ___  |  | || | |_   ||   _| | || | |_   ___  |  | || ||_   \  /   _|| || |     /  \     | || |   /  ___  |  | |
| |  |  (__ \_|  | || |  / .'   \_|  | || |   | |__| |   | || |   | |_  \_|  | || |  |   \/   |  | || |    / /\ \    | || |  |  (__ \_|  | |
| |   '.___`-.   | || |  | |         | || |   |  __  |   | || |   |  _|  _   | || |  | |\  /| |  | || |   / ____ \   | || |   '.___`-.   | |
| |  |`\____) |  | || |  \ `.___.'\  | || |  _| |  | |_  | || |  _| |___/ |  | || | _| |_\/_| |_ | || | _/ /    \ \_ | || |  |`\____) |  | |
| |  |_______.'  | || |   `._____.'  | || | |____||____| | || | |_________|  | || ||_____||_____|| || ||____|  |____|| || |  |_______.'  | |
| |              | || |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'
 **/
-- CREATE SCHEMA IF NOT EXISTS MANAGEMENT;
-- CREATE SCHEMA IF NOT EXISTS ROOM_MANAGEMENT;
-- CREATE SCHEMA IF NOT EXISTS HR;
-- CREATE SCHEMA IF NOT EXISTS FINANCE;
-- CREATE SCHEMA IF NOT EXISTS SEC;
-- CREATE SCHEMA IF NOT EXISTS RESERVES;




/*
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.   
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |  
| |     ______   | || |  _______     | || |  _________   | || |      __      | || |  _________   | || |  _________   | |  
| |   .' ___  |  | || | |_   __ \    | || | |_   ___  |  | || |     /  \     | || | |  _   _  |  | || | |_   ___  |  | |  
| |  / .'   \_|  | || |   | |__) |   | || |   | |_  \_|  | || |    / /\ \    | || | |_/ | | \_|  | || |   | |_  \_|  | |  
| |  | |         | || |   |  __ /    | || |   |  _|  _   | || |   / ____ \   | || |     | |      | || |   |  _|  _   | |  
| |  \ `.___.'\  | || |  _| |  \ \_  | || |  _| |___/ |  | || | _/ /    \ \_ | || |    _| |_     | || |  _| |___/ |  | |  
| |   `._____.'  | || | |____| |___| | || | |_________|  | || ||____|  |____|| || |   |_____|    | || | |_________|  | |  
| |              | || |              | || |              | || |              | || |              | || |              | |  
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |  
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'   
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.   
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |  
| |  _________   | || |      __      | || |   ______     | || |   _____      | || |  _________   | || |    _______   | |  
| | |  _   _  |  | || |     /  \     | || |  |_   _ \    | || |  |_   _|     | || | |_   ___  |  | || |   /  ___  |  | |  
| | |_/ | | \_|  | || |    / /\ \    | || |    | |_) |   | || |    | |       | || |   | |_  \_|  | || |  |  (__ \_|  | |  
| |     | |      | || |   / ____ \   | || |    |  __'.   | || |    | |   _   | || |   |  _|  _   | || |   '.___`-.   | |  
| |    _| |_     | || | _/ /    \ \_ | || |   _| |__) |  | || |   _| |__/ |  | || |  _| |___/ |  | || |  |`\____) |  | |  
| |   |_____|    | || ||____|  |____|| || |  |_______/   | || |  |________|  | || | |_________|  | || |  |_______.'  | |  
| |              | || |              | || |              | || |              | || |              | || |              | |  
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |  
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
*/


/*==============================================================*/
/* Table: HOTEL                                                 */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "management.hotel" (
    ID                  SERIAL,
    H_NAME              VARCHAR(100)        NOT NULL,
    FULL_ADDRESS        VARCHAR(160)        NOT NULL,
    POSTAL_CODE         VARCHAR(8)          NOT NULL,
    CITY                VARCHAR(100)        NOT NULL,
    EMAIL               VARCHAR(100)        NOT NULL,
    TELEPHONE           VARCHAR(20)         NOT NULL,
    DETAILS             VARCHAR(200)        NOT NULL,
    STARS               INT                 NOT NULL,

    CONSTRAINT      PK_HOTEL             PRIMARY KEY (ID)
);


/*==============================================================*/
/* TYPEs for roomTypes                                          */
/*==============================================================*/
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'room_view_type') THEN
        CREATE TYPE "room_management.room_view_type" AS ENUM ('P', 'M', 'S', 'N'); -- P - Piscina, M - Mar, S - Serra, N - Nenhuma
    END IF;
END $$;
--CREATE TYPE room_view_type AS ENUM ('P', 'M', 'S', 'N'); -- P - Piscina, M - Mar, S - Serra, N - Nenhuma
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'room_quality_type') THEN
        CREATE TYPE "room_management.room_quality_type" AS ENUM ('B', 'S'); -- B - Baixa, S - Superior
    END IF;
END $$;
--CREATE TYPE room_quality_type AS ENUM ('B', 'S'); -- B - Baixa, S - Superior

/*==============================================================*/
/* Table: ROOM_TYPES                                            */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "room_management.room_types" (
    ID                  SERIAL ,
    TYPE_INITIALS       VARCHAR(100)            NOT NULL, -- is it really necessary? will see --
    ROOM_VIEW           "room_management.room_view_type" ,
    ROOM_QUALITY        "room_management.room_quality_type" ,

    CONSTRAINT      PK_ROOM_TYPES           PRIMARY KEY (ID)
); 

/*==============================================================*/
/* Table: COMMODITY                                             */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "room_management.commodity" (
    ID                  SERIAL,
    DETAILS             VARCHAR(100)            NOT NULL, -- wifi, safe, minibar, AC, 

    CONSTRAINT      PK_COMMODITY            PRIMARY KEY (ID)
);
/*==============================================================*/
/* TYPE for capacity_type                                       */
/*==============================================================*/
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ROOM_MANAGEMENT.capacity_type') THEN
        CREATE TYPE "ROOM_MANAGEMENT.capacity_type" AS ENUM ('S', 'D', 'T', 'Q', 'K', 'F');
    END IF;
END $$;
--CREATE TYPE capacity_type AS ENUM ('S', 'D', 'T', 'Q', 'K', 'F'); -- S - Single, D - Double, T - Triple, Q - Quad, K - King, F - Family
/*==============================================================*/
/* Table: ROOM                                                  */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "room_management.room" (
    ID                  SERIAL ,
    TYPE_ID             INT                 NOT NULL,
    HOTEL_ID            INT                 NOT NULL,
    ROOM_NUMBER         INT                 NOT NULL, 
    BASE_PRICE          NUMERIC(10, 2)      NOT NULL, -- changed from float for more appropriate data type
    CONDITION           INT                 NOT NULL, -- 0 - livre, 1 - Sujo, 2 - Limpeza, 3 - manutenção
    CAPACITY            "ROOM_MANAGEMENT.capacity_type",

    CONSTRAINT      PK_ROOM                     PRIMARY KEY (ID),
    CONSTRAINT      FK_ROOM_TYPES               FOREIGN KEY (TYPE_ID)           REFERENCES "room_management.room_types"(ID),
    CONSTRAINT      FK_ROOM_HOTEL               FOREIGN KEY (HOTEL_ID)          REFERENCES "management.hotel"(ID),
    CONSTRAINT      UC_ROOM_NUM_PER_HOTEL       UNIQUE(HOTEL_ID, ROOM_NUMBER)
);


/*==============================================================*/
/* Table: SEASON                                                */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "finance.season" (
    ID              SERIAL ,
    DESCRIPTIVE     CHAR(1)     NOT NULL, -- A - Alta, B - Baixa, F - Festividades
    BEGIN_DATE      DATE        NOT NULL,
    END_DATE        DATE        NOT NULL,

    CONSTRAINT      PK_SEASON       PRIMARY KEY (ID)
);
/*==============================================================*/
/* Table: PRICE_PER_SEASON                                      */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "finance.price_per_season" (
    ID                  SERIAL ,
    SEASON_ID           INT         NOT NULL,
    TAX                 FLOAT       NOT NULL,

    CONSTRAINT      PK_PRICE_PER_SEASON       PRIMARY KEY (ID),
    CONSTRAINT      FK_PRICE_SEASON           FOREIGN KEY (SEASON_ID)      REFERENCES "finance.season"(ID) 
);
/*==============================================================*/
/* Table: ROOM_COMMODITY                                        */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "room_management.room_commodity" (
    ROOM_ID             INT         NOT NULL,
    COMMODITY_ID        INT         NOT NULL,
    
    CONSTRAINT      PK_ROOM_COMMODITY        PRIMARY KEY (ROOM_ID, COMMODITY_ID),
    CONSTRAINT      FK_RC_ROOM               FOREIGN KEY (ROOM_ID)               REFERENCES "finance.season"(ID),
    CONSTRAINT      FK_RC_COMMODITY          FOREIGN KEY(COMMODITY_ID)           REFERENCES "finance.season"(ID) 
);
/*==============================================================*/
/* Table: ACC_PERMISSIONS                                       */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "sec.acc_permissions" (
    ID                      SERIAL ,
    PERM_DESCRIPTION        VARCHAR(100)        NOT NULL,
    PERM_LEVEL              INT                 NOT NULL,

    CONSTRAINT      PK_ACC_PERMISSIONS      PRIMARY KEY (ID)
);

INSERT INTO "sec.acc_permissions" (ID, PERM_DESCRIPTION, PERM_LEVEL)
VALUES (1, 'Admin', 1),
       (2, 'Manager', 2),
       (3, 'Funcionário', 3)
ON CONFLICT (ID) DO NOTHING;

/*==============================================================*/
/* Table: USERS                                                 */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "hr.users"(
    ID                      SERIAL,
    FIRST_NAME              VARCHAR(100)            NOT NULL,
    LAST_NAME               VARCHAR(100)            NOT NULL,
    EMAIL                   VARCHAR(100)            NOT NULL,
    HASHED_PASSWORD         VARCHAR(255)            NOT NULL,
    INACTIVE                BOOLEAN                 NOT NULL, 
    NIF                     VARCHAR(20)             NOT NULL,
    PHONE                   VARCHAR(20)             NOT NULL,
    FULL_ADDRESS            VARCHAR(160)            NOT NULL,
    POSTAL_CODE             VARCHAR(8)              NOT NULL,
    CITY                    VARCHAR(100)            NOT NULL,
    utp                     CHAR(1)                 NOT NULL        DEFAULT 'C', -- C - Cliente, F - Funcionário, 

    CONSTRAINT      PK_USERS        PRIMARY KEY (ID),
    CONSTRAINT      UC_EMAIL        UNIQUE(EMAIL),
    CONSTRAINT      UC_NIF          UNIQUE(NIF),
    CONSTRAINT      UC_PHONE        UNIQUE(PHONE),
    CONSTRAINT      CK_UTP          CHECK (utp IN ('C', 'F'))
);     -- PARTITION BY LIST (UTP);

-- INHERITANCE VS PARTIOTIONING 
-- Partition for CLIENT (UTP = 'C')
-- CREATE TABLE IF NOT EXISTS CLIENT PARTITION OF USERS
-- FOR VALUES IN ('C');

-- -- Partition for EMPLOYEE (UTP = 'F')
-- CREATE TABLE IF NOT EXISTS EMPLOYEE (
--     ROLE_ID int NOT NULL REFERENCES ACC_PERMISSIONS(ID),
--     SOCIAL_SECURITY INT NOT NULL
-- ) PARTITION OF USERS
-- FOR VALUES IN ('F');


CREATE TABLE IF NOT EXISTS "hr.u_client" (
    CHECK (utp = 'C')
) INHERITS ("hr.users");
CREATE TABLE IF NOT EXISTS "hr.u_employee" (
    ROLE_ID             INT         NOT NULL        REFERENCES "sec.acc_permissions"(ID),
    SOCIAL_SECURITY     INT         NOT NULL,
    CHECK (utp = 'F')
) INHERITS ("hr.users");





/*==============================================================*/
/* Table: RESERVATION                                           */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "reserves.reservation" (
    ID                  SERIAL ,
    CLIENT_ID           INT                 NOT NULL,
    BEGIN_DATE          DATE                NOT NULL,
    END_DATE            DATE                NOT NULL,
    R_DETAIL            CHAR(2)             NOT NULL, -- P - Pendente, C - Confirmada, R - Rejeitada, CC- Cancelado
    SEASON_ID           INT                 NOT NULL, 
    TOTAL_VALUE         NUMERIC(10, 2)      NOT NULL,
    CHECK_IN            TIMESTAMP           NULL,
    CHECK_OUT           TIMESTAMP           NULL,

    CONSTRAINT      PK_RESERVATION          PRIMARY KEY (ID),
    CONSTRAINT      FK_RESERV_CLIENT        FOREIGN KEY (CLIENT_ID)         REFERENCES "hr.users"(ID),
    CONSTRAINT      FK_RESERV_SEASON        FOREIGN KEY (SEASON_ID)         REFERENCES "finance.season"(ID)
);
/*==============================================================*/
/* Table: ROOM_RESERVATION                                      */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "reserves.room_reservation" (
    RESERVATION_ID          INT                 NOT NULL,
    ROOM_ID                 INT                 NOT NULL,
    PRICE_RESERVATION       NUMERIC(10, 2)      NOT NULL,

    CONSTRAINT      PK_ROOM_RESERVATION         PRIMARY KEY (RESERVATION_ID, ROOM_ID),
    CONSTRAINT      FK_RESERV                   FOREIGN KEY (RESERVATION_ID)                REFERENCES "reserves.reservation"(ID),
    CONSTRAINT      FK_ROOM_RESERV              FOREIGN KEY (ROOM_ID)                       REFERENCES "room_management.room"(ID)
);
/*==============================================================*/
/* Table: GUESTS                                                */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "reserves.guests" (
    ID                      SERIAL ,
    RESERVATION_ID          INT                     NOT NULL,
    FULL_NAME               VARCHAR(100)            NOT NULL,
    CC_PASS                 VARCHAR(20)             NOT NULL, --CC OR PASSPORT
    PHONE                   VARCHAR(20)             NOT NULL,
    FULL_ADDRESS            VARCHAR(160)            NOT NULL,
    POSTAL_CODE             VARCHAR(8)              NOT NULL,
    CITY                    VARCHAR(100)            NOT NULL,

    CONSTRAINT      PK_GUESTS               PRIMARY KEY (ID),
    CONSTRAINT      FK_GUEST_RESERV         FOREIGN KEY (RESERVATION_ID)        REFERENCES "reserves.reservation"(ID)
);
/*==============================================================*/
/* Table: PAYMENT_METHOD                                        */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "finance.payment_method" (
    ID                  SERIAL ,
    DESCRIPTIVE         VARCHAR(100)        NOT NULL,

    CONSTRAINT      PK_PAYMENT_METHOD       PRIMARY KEY (ID),
    CONSTRAINT      UC_DESCRIP              UNIQUE (DESCRIPTIVE)
);

/*==============================================================*/
/* Table: PAYMENTS                                              */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "finance.payments" (
    ID                          SERIAL,
    INVOICE_ID                  INT                     NOT NULL,
    PAYMENT_AMOUNT              NUMERIC(10, 2)          NOT NULL,
    PAYMENT_DATE                DATE                    NOT NULL,
    PAYMENT_METHOD_ID           INT                     NOT NULL,

    CONSTRAINT      PK_PAY               PRIMARY KEY (ID),
    --CONSTRAINT      FK_PAY_INV           FOREIGN KEY (INVOICE_ID)            REFERENCES finance.invoice(ID),
    CONSTRAINT      FK_PAY_TYPE          FOREIGN KEY (PAYMENT_METHOD_ID)     REFERENCES "finance.payment_method"(ID)
);
/*==============================================================*/
/* Table: INVOICE                                               */
/*==============================================================*/
CREATE table if not exists "finance.invoice" (
    ID                          SERIAL,
    RESERVATION_ID              INT                     NOT NULL,
    CLIENT_ID                   INT                     NOT NULL,
    FINAL_VALUE                 NUMERIC(10, 2)          NOT NULL,
    EMISSION_DATE               DATE                    NOT NULL,
    BILLING_DATE                DATE                    NOT NULL,
    INVOICE_STATUS              BOOLEAN                 NOT NULL, 
    PAYMENT_ID                  INT                     NOT NULL,

    CONSTRAINT      PK_INVOICE          PRIMARY KEY (ID),
    CONSTRAINT      FK_INV_RESERV       FOREIGN KEY (RESERVATION_ID)        REFERENCES "reserves.reservation"(ID),
    --CONSTRAINT      FK_INV_CLIENT       FOREIGN KEY (CLIENT_ID)             REFERENCES hr.users(ID),
    CONSTRAINT      FK_INV_PAY          FOREIGN KEY (PAYMENT_ID)            REFERENCES "finance.payments"(ID)
);
ALTER TABLE "finance.payments" DROP CONSTRAINT IF EXISTS FK_PAY_INV;
ALTER TABLE "finance.invoice" DROP CONSTRAINT IF EXISTS FK_INV_PAY;
ALTER TABLE "finance.payments"
ADD CONSTRAINT FK_PAY_INV FOREIGN KEY (INVOICE_ID) REFERENCES "finance.invoice"(ID);
ALTER TABLE "finance.invoice"
ADD CONSTRAINT FK_INV_PAY FOREIGN KEY (PAYMENT_ID) REFERENCES "finance.payments"(ID);




/*
CREATE TABLE IF NOT EXISTS faturaDetalhes (
    faturaID int NOT NULL REFERENCES fatura(id),
    descricao VARCHAR(100) NOT NULL,
    valorUbitario float NOT NULL,
    quantidade int NOT NULL,
    valorFinal float NOT NULL NUMERIC(10, 2) GENERATED ALWAYS AS (valorUnitario * quantidade) STORED,,
    PRIMARY KEY (faturaID, descricao)
);*/


--TABLES FOR AUDITORING AND STATISTICS/PERFORMANCE/ MARKETING OPERATIONS ETC

/*==============================================================*/
/* Table: USER_PASSWORDS_DICTIONARY                             */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "sec.user_passwords_dictionary" ( -- for employees ONLY
	USER_ID                 INT				        NOT NULL,
	HASHED_PASSWD			VARCHAR(255)	        NOT NULL,
	ValidFrom               TIMESTAMP               NOT NULL     DEFAULT CURRENT_TIMESTAMP,
    ValidTo                 TIMESTAMP               NOT NULL, -- Set to six months from ValidFrom for each new record 

	--CONSTRAINT      PK_ACCOUNTS_ID      PRIMARY KEY(USER_ID),
	CONSTRAINT      FK_USER_PASSWD      FOREIGN KEY(USER_ID)        REFERENCES "hr.users"(ID)
);

/*==============================================================*/
/* Table: USER_LOGIN_AUDIT                                      */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "sec.user_login_audit" (
    USER_ID                 INT                     NOT NULL,
    LOGIN_TIMESTAMP         TIMESTAMP               NOT NULL,

    CONSTRAINT  FK_USER_LOGIN       FOREIGN KEY(USER_ID) REFERENCES "hr.users" (ID)
);
/*==============================================================*/
/* Table: ERROR_LOG                                             */
/*==============================================================*/
CREATE table if not exists "sec.error_log" (
    ID                          SERIAL,
    ERROR_MESSAGE	            VARCHAR(4000),
	ERROR_HINT                  VARCHAR(400),
	ERROR_CONTEXT               VARCHAR(400),
    ERROR_TIMESTAMP             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	CONSTRAINT      PK_ERRORS           PRIMARY KEY (ID)
);
/*==============================================================*/
/* Table: CHANGE_LOG                                            */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "sec.change_log" (
    ID SERIAL PRIMARY KEY,
    TABLE_NAME TEXT NOT NULL,
    OPERATION_TYPE TEXT NOT NULL, -- INSERT, UPDATE, DELETE
    ROW_ID INT NOT NULL,
    CHANGED_BY TEXT, -- User or System Identifier
    CHANGE_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*==============================================================*/
/* Table: AUDIT_LOG                                             */
/*==============================================================*/
CREATE TABLE IF NOT EXISTS "sec.audit_log" (
    ID SERIAL PRIMARY KEY,
    USERNAME TEXT NOT NULL,
    ACTION_TYPE TEXT NOT NULL, -- e.g., CREATE_RESERVATION, UPDATE_RESERVATION (FOR CLIENTS) | MANAGE ROOMS, OTHER MANAGER ACTIONS (EMPLOYEES, MANAGER, ADMIN)
    TABLE_NAME TEXT,
    ROW_ID INT,
    ACTION_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



/*==============================================================*/
/* INDEXES                                                      */
/*==============================================================*/
--INDEXES FOR PERFORMANCE
-- CREATE INDEX idx_room_hotelID ON ROOM(HOTEL_ID);
-- CREATE INDEX idx_reservation_clientID ON RESERVATION(CLIENT_ID);
-- CREATE INDEX idx_invoice_clientID ON INVOICE(CLIENT_ID);

-- maybe index  ON reserves.room_reservation for ROOM_ID, BEGIN_DATE, and END_DATE to make RESERVES.trg_check_room_availability have less overhead for performance optimization

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
          AND indexname = 'idx_room_hotelid'
    ) THEN
        CREATE INDEX idx_room_hotelid ON "room_management.room"(HOTEL_ID);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
          AND indexname = 'idx_reservation_clientid'
    ) THEN
        CREATE INDEX idx_reservation_clientid ON "reserves.reservation"(CLIENT_ID);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
          AND indexname = 'idx_invoice_clientid'
    ) THEN
        CREATE INDEX idx_invoice_clientid ON "finance.invoice"(CLIENT_ID);
    END IF;
END $$;