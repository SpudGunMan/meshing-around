# Written for Meshtastic mesh-bot by PD9FVH Folkert van Heusden 2025

import chess
import chess.engine
import sqlite3


db_file = 'chess.db'

def initDb():
    con = sqlite3.connect(db_file)

    cur = con.cursor()
    try:
        cur.execute('CREATE TABLE chess(ts datetime not null, fen varchar(255) not null, node_id varchar(16) not null primary key)')

    except sqlite3.OperationalError as oe:
        # should be "table already exists"
        pass
    cur.close()

    cur = con.cursor()
    cur.execute('PRAGMA journal_mode=wal')
    cur.close()

    con.commit()
    con.close()

def getFEN(nodeID):
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.execute('SELECT fen FROM chess WHERE node_id=?', (nodeID,))
    row = cur.fetchone()
    cur.close()
    con.close()

    if row == None:
        return None
    return row[0]

def putFEN(nodeID, b):
    fen = b.fen()
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.execute('INSERT INTO chess(ts, fen, node_id) VALUES(date("now"), ?, ?) ON CONFLICT(node_id) DO UPDATE SET fen=?, ts=date("now")', (fen, nodeID, fen))
    cur.close()
    con.commit()
    con.close()

def playChess(nodeID, message):
    initDb()

    parts = message.split()
    if len(parts) < 2:
        return 'Enter a move or "new"'

    if parts[1] in ('new', 'resign', 'abort', 'stop'):
        b = chess.Board()
        putFEN(nodeID, b)
        return 'Ok, new game started'

    fen = getFEN(nodeID)
    if fen == None or fen == '':
        b = chess.Board()
    else:
        b = chess.Board(fen)

    move = parts[1].replace('-', '')
    try:
        b.push(chess.Move.from_uci(move))
    except Exception as e:
        return f'{move} is an invalid move! ({e})'

    if b.is_game_over():
        return 'Game over, you won!'

    engine = chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish')
    result = engine.play(b, chess.engine.Limit(time=1.))
    engine.quit()

    b.push(result.move)
    putFEN(nodeID, b)

    if b.is_game_over():
        return f'Game over, I won! (by moving {result.move.uci()})'

    fen = b.fen().replace(' ', '_')
    return f'I move {result.move.uci()}, new board: https://lichess.org/editor/' + fen

if __name__ == "__main__":
    playChess('test', 'new')
    playChess('test', 'e2e4')
    playChess('test', 'd2d3')
