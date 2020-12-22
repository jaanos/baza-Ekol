CREATE TABLE podjetje (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    ime TEXT    NOT NULL
);

CREATE TABLE vrsta_odpadka (
    klasifikacijska_stevilka VARCHAR (9) PRIMARY KEY
                                         CHECK (klasifikacijska_stevilka LIKE '__ __ __%'),
    naziv                    TEXT        NOT NULL
);

CREATE TABLE skladisce (
    id  INTEGER PRIMARY KEY,
    ime TEXT    NOT NULL
);

CREATE TABLE odpadek (
    id                       INTEGER     PRIMARY KEY AUTOINCREMENT,
    teza                     INTEGER     NOT NULL,
    povzrocitelj             INTEGER     NOT NULL
                                         REFERENCES podjetje (id),
    prejemnik                INTEGER     REFERENCES podjetje (id),-- če ni obvezen podatek, brez NOT NULL
    datum_uvoza              DATE        NOT NULL,
    opomba_uvoz              TEXT,
    datum_izvoza             DATE,
    opomba_izvoz             TEXT,
    klasifikacijska_stevilka VARCHAR (9) NOT NULL
                                         REFERENCES vrsta_odpadkas(klasifikacijska_stevilka),
    skladisce                INTEGER     REFERENCES skladisce (id) 
);