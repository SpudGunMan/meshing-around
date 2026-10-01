#!/usr/bin/env python3
# Inspired by classic Yahtzee rules and adapted for Meshtastic mesh-bot
import random
import time


class YatzGame:
	CATEGORIES = [
		"ones", "twos", "threes", "fours", "fives", "sixes",
		"three_kind", "four_kind", "full_house", "small_straight",
		"large_straight", "chance", "yatz"
	]

	CATEGORY_ALIASES = {
		"1": "ones", "ones": "ones",
		"2": "twos", "twos": "twos",
		"3": "threes", "threes": "threes",
		"4": "fours", "fours": "fours",
		"5": "fives", "fives": "fives",
		"6": "sixes", "sixes": "sixes",
		"3k": "three_kind", "threekind": "three_kind", "three_kind": "three_kind",
		"4k": "four_kind", "fourkind": "four_kind", "four_kind": "four_kind",
		"fh": "full_house", "fullhouse": "full_house", "full_house": "full_house",
		"ss": "small_straight", "smallstraight": "small_straight", "small_straight": "small_straight",
		"ls": "large_straight", "largestraight": "large_straight", "large_straight": "large_straight",
		"ch": "chance", "chance": "chance",
		"yz": "yatz", "yahtzee": "yatz", "yatz": "yatz",
	}

	sessions = {}
	player_sessions = {}
	open_tables = []
	_next_table_id = 1000

	@classmethod
	def _new_table_id(cls):
		cls._next_table_id += 1
		return str(cls._next_table_id)

	@classmethod
	def _blank_scorecard(cls):
		return {cat: None for cat in cls.CATEGORIES}

	@classmethod
	def _new_turn_state(cls):
		return {"dice": [0, 0, 0, 0, 0], "held": [False, False, False, False, False], "rolls": 0}

	@classmethod
	def _new_session(cls, mode, players, open_join=False):
		sid = cls._new_table_id()
		session = {
			"id": sid,
			"mode": mode,
			"players": list(players),
			"open_join": open_join,
			"started": mode == "solo",
			"finished": False,
			"current_turn": 0,
			"scorecards": {pid: cls._blank_scorecard() for pid in players},
			"turn": cls._new_turn_state(),
			"winner": None,
			"last_played": time.time(),
		}
		cls.sessions[sid] = session
		for pid in players:
			cls.player_sessions[pid] = sid
		return session

	@classmethod
	def help_text(cls):
		return (
			"🎲YATZ!🎲\n"
			"Commands: roll, hold, score, card, end\n"
			"Dice slots are A B C D E. Hold letters like 'A C E' or 'hold A,C,E'.\n"
			"Categories: ones twos threes fours fives sixes 3k 4k fh ss ls chance yatz"
		)

	@classmethod
	def new_solo(cls, player_id):
		if player_id in cls.player_sessions:
			return "Already in a game. Use 'yatz end' first.", cls.player_sessions[player_id]
		ai_id = f"ai-{player_id}"
		session = cls._new_session("solo", [player_id, ai_id], open_join=False)
		session["started"] = True
		return (
			"New solo 🎲 started vs AI.\n"
			"Your turn first. Use 'roll' to begin.\n"
			+ cls.help_text(),
			session["id"],
		)

	@classmethod
	def new_table(cls, host_id):
		if host_id in cls.player_sessions:
			return "Already in a game. Use 'yatz end' first.", None
		session = cls._new_session("multi", [host_id], open_join=True)
		cls.open_tables.append(session["id"])
		return (
			f"New Yatz table #{session['id']} open (2-4 players).\n"
			"Others can join with 'yatz join'. Host may also wait using 'yatz lobby'.",
			session["id"],
		)

	@classmethod
	def lobby(cls):
		open_ids = [sid for sid in cls.open_tables if sid in cls.sessions and cls.sessions[sid]["open_join"]]
		if not open_ids:
			return "No open 🎲 tables right now. Start one with 'yatz new'."
		lines = ["Open 🎲 tables:"]
		for sid in open_ids[:8]:
			s = cls.sessions[sid]
			lines.append(f"#{sid} players:{len(s['players'])}/4")
		return "\n".join(lines)

	@classmethod
	def join_table(cls, player_id, table_id=None):
		if player_id in cls.player_sessions:
			return "Already in a game. Use 'yatz end' first.", None

		session = None
		if table_id:
			session = cls.sessions.get(str(table_id))
			if not session or not session.get("open_join"):
				return "That table is unavailable.", None
		else:
			for sid in list(cls.open_tables):
				s = cls.sessions.get(sid)
				if s and s.get("open_join") and len(s["players"]) < 4:
					session = s
					break

		if not session:
			return "No open table found. Use 'yatz new' to create one.", None
		if len(session["players"]) >= 4:
			return "That table is already full.", None

		session["players"].append(player_id)
		session["scorecards"][player_id] = cls._blank_scorecard()
		cls.player_sessions[player_id] = session["id"]
		session["last_played"] = time.time()

		# Match battleship behavior: joining player gets the first turn once table starts.
		if len(session["players"]) == 2 and not session["started"]:
			session["current_turn"] = 1

		if len(session["players"]) == 4:
			session["open_join"] = False
			if session["id"] in cls.open_tables:
				cls.open_tables.remove(session["id"])

		return (
			f"Joined 🎲 table #{session['id']} ({len(session['players'])}/4).\n"
			"Use 'roll' when it is your turn.",
			session["id"],
		)

	@classmethod
	def _roll_dice(cls, turn):
		if turn["rolls"] == 0:
			for i in range(5):
				turn["dice"][i] = random.randint(1, 6)
		else:
			for i in range(5):
				if not turn["held"][i]:
					turn["dice"][i] = random.randint(1, 6)
		turn["rolls"] += 1

	@classmethod
	def _fmt_dice(cls, turn):
		letters = ["A", "B", "C", "D", "E"]
		parts = []
		for i, die in enumerate(turn["dice"]):
			marker = "H" if turn["held"][i] else "-"
			parts.append(f"{letters[i]}:{die}{marker}")
		return "🎲 " + " ".join(parts)

	@classmethod
	def _upper_total(cls, scorecard):
		return sum(scorecard[c] or 0 for c in ["ones", "twos", "threes", "fours", "fives", "sixes"])

	@classmethod
	def _total_score(cls, scorecard):
		upper = cls._upper_total(scorecard)
		bonus = 35 if upper >= 63 else 0
		lower = sum(scorecard[c] or 0 for c in [
			"three_kind", "four_kind", "full_house", "small_straight", "large_straight", "chance", "yatz"
		])
		return upper + bonus + lower

	@classmethod
	def _score_value(cls, dice, category):
		counts = {n: dice.count(n) for n in range(1, 7)}
		unique_sorted = sorted(set(dice))
		total = sum(dice)

		if category == "ones":
			return counts[1] * 1
		if category == "twos":
			return counts[2] * 2
		if category == "threes":
			return counts[3] * 3
		if category == "fours":
			return counts[4] * 4
		if category == "fives":
			return counts[5] * 5
		if category == "sixes":
			return counts[6] * 6
		if category == "three_kind":
			return total if max(counts.values()) >= 3 else 0
		if category == "four_kind":
			return total if max(counts.values()) >= 4 else 0
		if category == "full_house":
			vals = sorted(counts.values())
			return 25 if vals[-1] == 3 and vals[-2] == 2 else 0
		if category == "small_straight":
			straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
			return 30 if any(st.issubset(set(unique_sorted)) for st in straights) else 0
		if category == "large_straight":
			return 40 if unique_sorted in ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]) else 0
		if category == "chance":
			return total
		if category == "yatz":
			return 50 if max(counts.values()) == 5 else 0
		return 0

	@classmethod
	def _normalize_category(cls, text):
		key = (text or "").strip().lower().replace("-", "_").replace(" ", "")
		return cls.CATEGORY_ALIASES.get(key)

	@classmethod
	def _parse_indices(cls, hold_str):
		raw = hold_str.strip().lower()
		if raw in ("none", "n", "clear"):
			return []
		for sep in [",", ".", " "]:
			if sep in raw:
				items = [x for x in raw.split(sep) if x]
				break
		else:
			items = list(raw)

		idx = []
		for item in items:
			if item not in ("a", "b", "c", "d", "e"):
				raise ValueError("slot")
			idx.append("abcde".index(item))
		return sorted(set(idx))

	@classmethod
	def _current_player(cls, session):
		return session["players"][session["current_turn"]]

	@classmethod
	def _display_name(cls, session, player_id):
		if session.get("player_names") and player_id in session["player_names"]:
			return session["player_names"][player_id]
		return str(player_id)

	@classmethod
	def get_session_for_player(cls, player_id):
		sid = cls.player_sessions.get(player_id)
		if not sid:
			return None
		return cls.sessions.get(sid)

	@classmethod
	def start_if_ready(cls, session):
		if session["mode"] == "multi" and not session["started"] and len(session["players"]) >= 2:
			session["started"] = True
			session["open_join"] = len(session["players"]) < 4
			if session["id"] in cls.open_tables and not session["open_join"]:
				cls.open_tables.remove(session["id"])

	@classmethod
	def status(cls, player_id):
		session = cls.get_session_for_player(player_id)
		if not session:
			return "No active Yatz-game. Use 'yatz' or 'yatz new'."

		if session["mode"] == "multi" and not session["started"]:
			return (
				f"Table #{session['id']} waiting for players ({len(session['players'])}/4).\n"
				"Use 'yatz join' from another node, then 'roll' when ready."
			)

		if session.get("finished"):
			return "Game over. Use 'card' to review scores or 'end' to close."

		turn_player = cls._current_player(session)
		turn = session["turn"]
		msg = f"Yatz table #{session['id']} turn:{cls._display_name(session, turn_player)} roll:{turn['rolls']}/3\n"
		if turn["rolls"] > 0:
			msg += cls._fmt_dice(turn) + "\n"
		msg += "Use: roll | hold A,C,E | score <cat> | card"
		return msg

	@classmethod
	def hold(cls, player_id, hold_str):
		session = cls.get_session_for_player(player_id)
		if not session:
			return "No active Yatz-game."
		if session.get("finished"):
			return "Game over. Use 'yatz end' to close this game."
		if cls._current_player(session) != player_id:
			return "Not your turn."
		if session["turn"]["rolls"] == 0:
			return "Roll first using 'roll'."
		try:
			idx = cls._parse_indices(hold_str)
		except Exception:
			return "Invalid hold list. Example: hold A,C,E"

		current = session["turn"]["held"][:]
		if not idx:
			current = [False for _ in range(5)]
		else:
			for i in idx:
				current[i] = True
		session["turn"]["held"] = current
		session["last_played"] = time.time()
		return cls._fmt_dice(session["turn"]) + "\nHolds updated. Use 'roll' or 'score <cat>'."

	@classmethod
	def roll(cls, player_id):
		session = cls.get_session_for_player(player_id)
		if not session:
			return "No active Yatz-game."
		if session.get("finished"):
			return "Game over. Use 'yatz end' to close this game."

		cls.start_if_ready(session)

		if session["mode"] == "multi" and not session["started"]:
			return "Need at least 2 players to start."
		if cls._current_player(session) != player_id:
			return "Not your turn. waiting for " + cls._display_name(session, cls._current_player(session))

		turn = session["turn"]
		if turn["rolls"] >= 3:
			return "No rolls left. Use 'score <cat>'."

		cls._roll_dice(turn)
		session["last_played"] = time.time()
		left = 3 - turn["rolls"]
		return cls._fmt_dice(turn) + f"\nRolls left:{left}. Hold dice then roll, or score a category."

	@classmethod
	def _unused_categories(cls, scorecard):
		return [c for c in cls.CATEGORIES if scorecard[c] is None]

	@classmethod
	def score(cls, player_id, category_text):
		session = cls.get_session_for_player(player_id)
		if not session:
			return "No active Yatz-game."
		if session.get("finished"):
			return "Game over. Use 'yatz card' to review scores or 'yatz end' to close."
		cls.start_if_ready(session)

		if cls._current_player(session) != player_id:
			return "Not your turn."
		if session["turn"]["rolls"] == 0:
			return "Roll first using 'roll'."

		category = cls._normalize_category(category_text)
		if not category:
			return "Unknown category. Try: ones twos ... 3k 4k fh ss ls chance yatz"

		card = session["scorecards"][player_id]
		if card[category] is not None:
			return "That category is already used. Pick another."

		dice = session["turn"]["dice"]
		pts = cls._score_value(dice, category)
		card[category] = pts
		msg = f"Scored {pts} in {category}."

		done = all(all(v is not None for v in c.values()) for c in session["scorecards"].values())
		if done:
			session["finished"] = True
			ranking = []
			for pid, sc in session["scorecards"].items():
				ranking.append((pid, cls._total_score(sc)))
			ranking.sort(key=lambda x: x[1], reverse=True)
			top_score = ranking[0][1]
			winners = [str(pid) for pid, score in ranking if score == top_score]
			session["winner"] = winners
			lines = ["Game over."]
			for pid, score in ranking:
				lines.append(f"{pid}: {score}")
			if len(winners) == 1:
				lines.append(f"Winner: {winners[0]}")
			else:
				lines.append("Tie: " + ", ".join(winners))
			msg += "\n" + "\n".join(lines)
			return msg

		# Next turn setup
		session["current_turn"] = (session["current_turn"] + 1) % len(session["players"])
		session["turn"] = cls._new_turn_state()
		session["last_played"] = time.time()

		# AI turns happen automatically in solo mode.
		if session["mode"] == "solo" and str(cls._current_player(session)).startswith("ai-"):
			msg += "\n" + cls._play_ai_turn(session)

		next_player = cls._current_player(session)
		if str(next_player).startswith("ai-"):
			# If AI finished and gave turn back, refresh label.
			next_player = cls._current_player(session)
		msg += f"\nNext turn: {cls._display_name(session, next_player)}."
		return msg

	@classmethod
	def _play_ai_turn(cls, session):
		ai_id = cls._current_player(session)
		card = session["scorecards"][ai_id]
		turn = session["turn"]

		for _ in range(3):
			cls._roll_dice(turn)
			counts = {n: turn["dice"].count(n) for n in range(1, 7)}
			best_face = max(counts, key=counts.get)
			turn["held"] = [d == best_face for d in turn["dice"]]
			if turn["rolls"] == 3:
				break

		unused = cls._unused_categories(card)
		best_cat = None
		best_pts = -1
		for cat in unused:
			pts = cls._score_value(turn["dice"], cat)
			if pts > best_pts:
				best_pts = pts
				best_cat = cat
		card[best_cat] = best_pts

		ai_msg = f"🤖 scored {best_pts} in {best_cat}."

		done = all(all(v is not None for v in c.values()) for c in session["scorecards"].values())
		if done:
			session["finished"] = True
			ranking = []
			for pid, sc in session["scorecards"].items():
				ranking.append((pid, cls._total_score(sc)))
			ranking.sort(key=lambda x: x[1], reverse=True)
			lines = ["Game over."]
			for pid, score in ranking:
				lines.append(f"{pid}: {score}")
			ai_msg += "\n" + "\n".join(lines)
			return ai_msg

		session["current_turn"] = (session["current_turn"] + 1) % len(session["players"])
		session["turn"] = cls._new_turn_state()
		session["last_played"] = time.time()
		return ai_msg

	@classmethod
	def show_card(cls, player_id):
		session = cls.get_session_for_player(player_id)
		if not session:
			return "No active Yatz-game."
		card = session["scorecards"][player_id]
		upper = cls._upper_total(card)
		bonus = 35 if upper >= 63 else 0
		total = cls._total_score(card)

		lines = ["Your card:"]
		for c in cls.CATEGORIES:
			value = "-" if card[c] is None else str(card[c])
			lines.append(f"{c}:{value}")
		lines.append(f"upper:{upper} bonus:{bonus} total:{total}")
		return "\n".join(lines)

	@classmethod
	def current_turn_player(cls, session_id):
		session = cls.sessions.get(session_id)
		if not session:
			return None
		return cls._current_player(session)

	@classmethod
	def is_multiplayer_started(cls, session_id):
		session = cls.sessions.get(session_id)
		return bool(session and session["mode"] == "multi" and session["started"])

	@classmethod
	def end_player_game(cls, player_id):
		sid = cls.player_sessions.get(player_id)
		if not sid:
			return "No active Yatz-game."
		session = cls.sessions.get(sid)
		if not session:
			cls.player_sessions.pop(player_id, None)
			return "Yatz-game closed."

		# Solo closes everything.
		if session["mode"] == "solo":
			for pid in list(session["players"]):
				cls.player_sessions.pop(pid, None)
			cls.sessions.pop(sid, None)
			if sid in cls.open_tables:
				cls.open_tables.remove(sid)
			return "Solo 🎲 ended."

		# Multiplayer removes player; table closes when fewer than 2 remain.
		if player_id in session["players"]:
			idx = session["players"].index(player_id)
			session["players"].pop(idx)
		cls.player_sessions.pop(player_id, None)
		session["scorecards"].pop(player_id, None)

		if len(session["players"]) < 2:
			for pid in list(session["players"]):
				cls.player_sessions.pop(pid, None)
			cls.sessions.pop(sid, None)
			if sid in cls.open_tables:
				cls.open_tables.remove(sid)
			return "🎲 table closed (not enough players)."

		if session["current_turn"] >= len(session["players"]):
			session["current_turn"] = 0
		session["last_played"] = time.time()
		return "You left the 🎲 table."


yatz = YatzGame()
