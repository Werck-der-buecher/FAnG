from dataclasses import dataclass


@dataclass
class GSQLSchema(object):
    CURRENT_SCHEMA_VERSION = 7

    CREATE_TABLE_GLYPH = """
            CREATE TABLE glyph(ID INTEGER, file_id TEXT, region_id TEXT, line_id TEXT, word_id TEXT, glyph_id TEXT, 
                                extension TEXT, img BLOB, embedding BLOB, height INTEGER, width INTEGER, dpi INTEGER, 
                                label TEXT, label_ocr TEXT, energy FLOAT, score FLOAT, coords_rel TEXT, coords_abs TEXT, 
                                similarity INTEGER DEFAULT -1, CONSTRAINT PK_Glyph PRIMARY KEY (file_id, glyph_id))
            """

    # SINGLE COLUMN INDEX
    CREATE_LABEL_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_label_index ON glyph (label);
        """

    CREATE_HEIGHT_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_height_index ON glyph (height);
        """

    CREATE_WIDTH_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_width_index ON glyph (width);
        """

    CREATE_SIZE_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_size_index ON glyph (height*width);
        """

    CREATE_SIMILARITY_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_similarity_index ON glyph (similarity);
        """

    CREATE_EMBEDDING_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_embedding_index ON glyph (embedding);
        """

    CREATE_ENERGY_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_embedding_index ON glyph (energy);
        """

    CREATE_SCORE_INDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_embedding_index ON glyph (score);
        """

    CREATE_UNIQUE_LABEL_ENCODING = """
            CREATE UNIQUE INDEX IF NOT EXISTS encoding_label_index ON encoding (label);
        """

    # MULTI COLUMN INDEX
    CREATE_LABEL_HEIGHT_MINDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_label_height_index ON glyph (label, height);
        """

    CREATE_LABEL_WIDTH_MINDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_label_width_index ON glyph (label, width);
        """

    CREATE_LABEL_SIZE_MINDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_label_size_index ON glyph (label, height*width);
        """

    CREATE_LABEL_SIMILARITY_MINDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_label_similarity_index ON glyph (label, similarity);
        """

    CREATE_LABEL_EMBEDDING_MINDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_label_embedding_index ON glyph (label, embedding);
        """

    CREATE_LABEL_ENERGY_MINDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_embedding_index ON glyph (label, energy);
        """

    CREATE_LABEL_SCORE_MINDEX_GLYPH = """
            CREATE INDEX IF NOT EXISTS glyph_embedding_index ON glyph (label, score);
        """

    CREATE_TABLE_ENCODING = """
            CREATE TABLE encoding(ID INTEGER CONSTRAINT PK_Encoding PRIMARY KEY autoincrement, label TEXT, status INTEGER DEFAULT 0)
        """

    CREATE_VIEW_LABEL = """
            CREATE VIEW vlabel AS 
            SELECT glyph.label AS 'Glyph', glyph.similarity as "Similarity", COUNT(*) AS 'Count' FROM glyph GROUP BY glyph.label, glyph.similarity
            UNION
            SELECT encoding.label, -1, 0 FROM encoding
            WHERE NOT exists(select 1 FROM glyph WHERE encoding.label = glyph.label)
            """

    DROP_TABLE_GLYPH = """
            DROP TABLE glyph
            """

    DROP_TABLE_ENCODING = """
            DROP TABLE encoding
            """

    DROP_VIEW_LABEL = """
            DROP VIEW vlabel
            """

    INSERT_VALS_GLYPH = """
            INSERT INTO glyph (file_id, region_id, line_id, word_id, glyph_id, extension, img, embedding, height, width, 
                                dpi, label, label_ocr, energy, score, coords_rel, coords_abs) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

    INSERT_VALS_ENCODING = """
            INSERT OR IGNORE INTO encoding (label, status) VALUES (?, ?)
            """

    SELECT_ALL_LABEL = """
            SELECT * FROM glyph WHERE label=?
            """

    SELECT_ALL_NULL_EMBD = """
            SELECT * FROM glyph WHERE embedding IS NULL
            """

    SELECT_ALL_LABEL_NULL_EMBD = """
            SELECT * FROM glyph WHERE embedding IS NULL AND label=?
            """

    SELECT_EMBEDDINGS = """
            SELECT file_id, glyph_id, embedding FROM glyph WHERE label=?
            """

    SELECT_DISTINCT_LABELS = """
            SELECT DISTINCT label FROM glyph
            """

    SELECT_GLYPHS = """        
            SELECT img, file_id, glyph_id, height, width, extension, coords_abs, coords_rel FROM glyph WHERE label=? AND similarity=COALESCE(NULLIF(?, NULL), similarity)
            """

    UPDATE_LABEL = """
            UPDATE glyph SET label=?, similarity=? WHERE label=? AND similarity=COALESCE(NULLIF(?, NULL), similarity)
            """

    DELETE_LABEL = """
            DELETE FROM glyph WHERE label=? AND similarity=COALESCE(NULLIF(?, NULL), similarity)
            """

    SELECT_DISTINCT_ENCODINGS = """
            SELECT DISTINCT label FROM glyph
            """

    UPDATE_ENCODING = """
            UPDATE encoding SET label=? WHERE label=?
            """

    DELETE_ENCODING = """
            DELETE FROM encoding WHERE label=?
            """

    UPDATE_ENCODING_STATUS = """
            UPDATE encoding SET status=? WHERE label=?
            """

    _ORDER_BY_UID_ASC = """
            ORDER BY file_id, glyph_id ASC
            """

    _ORDER_BY_UID_DESC = """
            ORDER BY file_id, glyph_id DESC
            """

    _ORDER_BY_HEIGHT_ASC = """
            ORDER BY height ASC
            """

    _ORDER_BY_HEIGHT_DESC = """
            ORDER BY height DESC
            """

    _ORDER_BY_WIDTH_ASC = """
            ORDER BY width ASC
            """

    _ORDER_BY_WIDTH_DESC = """
            ORDER BY width DESC
            """

    _ORDER_BY_SIZE_ASC = """
            ORDER BY (height*width) ASC
            """

    _ORDER_BY_SIZE_DESC = """
            ORDER BY (height*width) DESC
            """

    # ASC/DESC by purpose since we the energy from the generating neural network is given as the negative
    _ORDER_BY_ENERGY_ASC = """
            ORDER BY energy DESC
            """

    _ORDER_BY_ENERGY_DESC = """
            ORDER BY energy ASC
            """

    _ORDER_BY_SCORE_ASC = """
            ORDER BY score ASC
            """

    _ORDER_BY_SCORE_DESC = """
            ORDER BY score DESC
            """

    _ORDER_BY_SIMILARITY_ASC = """
            ORDER BY similarity ASC
            """

    _ORDER_BY_SIMILARITY_DESC = """
            ORDER BY similarity DESC
            """

    UPDATE_GLYPH_LABEL = """
            UPDATE glyph SET label=? WHERE (file_id, glyph_id)=(?,?)
            """

    SELECT_GLYPH_SIMILARITIES = """            
            SELECT similarity FROM glyph WHERE label=?
            """

    UPDATE_GLYPH_SIMILARITY = """
            UPDATE glyph SET similarity=? WHERE (file_id, glyph_id)=(?,?)
            """

    UPDATE_GLYPH_EMBEDDING = """
            UPDATE glyph SET embedding=? WHERE (file_id, glyph_id)=(?,?)
            """

    SELECT_LABEL_VIEW = """
            SELECT vlabel.Glyph, vlabel.Similarity, vlabel.Count, encoding.status AS 'Status'
            FROM vlabel
            INNER JOIN encoding
            ON vlabel.Glyph = encoding.label
            ORDER BY CASE WHEN UNICODE(Glyph) BETWEEN 65 AND 90 THEN 1 ELSE 2 END DESC, LENGTH(Glyph) ASC, Glyph ASC, Similarity ASC        
            """
    # ORDER BY LENGTH(Glyph) ASC, CASE WHEN UNICODE(Glyph) BETWEEN 65 AND 90 THEN 1 ELSE 2 END DESC, Similarity DESC

    SELECT_LABEL_COUNT = """
            SELECT COUNT(*) FROM glyph WHERE label=? AND similarity=COALESCE(NULLIF(?, NULL), similarity)
            """

    SELECT_MEAN_SHAPE = """
            SELECT CAST(round(avg(height)) AS INT), CAST(round(avg(width)) AS INT) FROM glyph WHERE label='%s'
            """

    SELECT_MEDIAN_HEIGHT = """
            SELECT height FROM glyph WHERE label='%s'
                ORDER BY height LIMIT 1 OFFSET (SELECT COUNT(*) FROM glyph WHERE label='%s') / 2
            """

    SELECT_MEDIAN_WIDTH = """
            SELECT width FROM glyph WHERE label='%s'
                ORDER BY width LIMIT 1 OFFSET (SELECT COUNT(*) FROM glyph WHERE label='%s') / 2
            """

    ### VERSIONING
    GET_USER_VERSION = """
            PRAGMA user_version
            """

    SET_USER_VERSION = """
            PRAGMA user_version=%s
            """

    ### OPTIMIZATION
    PRAGMA_JOURNAL_MODE = "PRAGMA journal_mode=WAL;"
    PRAGMA_SYNCRONOUS = "PRAGMA synchronous=1;"  # https://www.sqlite.org/wal.html
    PRAGMA_MMAP = "PRAGMA mmap_size=30000000000;"
    PRAGMA_TEMP_FILE = "PRAGMA temp_store=1;"  # FILE
    PRAGMA_TEMP_MEMORY = "PRAGMA temp_store=2;"  # MEMORY
    PRAGMA_PAGESIZE = "PRAGMA page_size=4096;"
    PRAGMA_CACHESIZE = "PRAGMA cache_size=-2000000;"
    PRAGMA_LOCKINGMODE = "PRAGMA locking_mode=NORMAL;"
    PRAGMA_ANALYSISLIMIT = "PRAGMA analysis_limit=400;"
    PRAGMA_OPTIM = "PRAGMA optimize;"
