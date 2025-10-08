import json
import os
import random
from modules.log import *

QUIZ_JSON = os.path.join(os.path.dirname(__file__), '../', '../', 'data', 'quiz_questions.json')
QUIZMASTER_ID = bbs_admin_list

trap_list_quiz = ("quiz", "q:")
help_text_quiz = "quiz",

class QuizGame:
    def __init__(self):
        self.quizmaster = QUIZMASTER_ID
        self.active = False
        self.players = {}  # user_id: {'score': int, 'current_q': int, 'answered': set()}
        self.questions = []  # Loaded from JSON
        self.first_correct = {}  # q_idx: user_id
        self.load_questions()

    def start_game(self, quizmaster_id):
        if str(quizmaster_id) not in self.quizmaster:
            return "Only the quizmaster can start the quiz."
        if self.active:
            return "Quiz already running."
        self.active = True
        logger.debug(f"QuizMaster: {quizmaster_id} started a new quiz round.")
        self.players = {}
        self.first_correct = {}  # Reset on new game
        self.load_questions()
        return "Quiz started! Players can now join."
    
    def load_questions(self):
        try:
            with open(QUIZ_JSON, 'r') as f:
                self.questions = json.load(f)
            # Shuffle questions to ensure randomness each game
            #random.shuffle(self.questions)
        except Exception as e:
            logger.error(f"Failed to load quiz questions: {e}")
            self.questions = []

    def stop_game(self, quizmaster_id):
        if not self.active or str(quizmaster_id) not in self.quizmaster:
            return "Only the quizmaster can stop the quiz."
        return_msg = "Quiz stopped! Final scores:\n" + self.top_three()
        logger.debug(f"QuizMaster: {quizmaster_id} stopped the quiz.")
        self.active = False
        self.players = {}
        return return_msg

    def join(self, user_id):
        if not self.active:
            return "No quiz running. Wait for the quizmaster to start."
        if user_id in self.players:
            return "You are already in the quiz."
        self.players[user_id] = {'score': 0, 'current_q': 0, 'answered': set()}
        reminder = f"Joined!\n'Q: <Answer>' 'Q: ?' for more.\n"
        logger.debug(f"QuizMaster: Player {user_id} joined the round.")
        return reminder + self.next_question(user_id)

    def leave(self, user_id):
        if user_id in self.players:
            del self.players[user_id]
            logger.debug(f"QuizMaster: Player {user_id} left the round.")
            return "You left the quiz."
        return "You are not in the quiz."

    def next_question(self, user_id):
        if user_id not in self.players:
            return "Join the quiz first."
        player = self.players[user_id]
        while player['current_q'] < len(self.questions) and player['current_q'] in player['answered']:
            player['current_q'] += 1
        if player['current_q'] >= len(self.questions):
            return f"No more questions. Your final score: {player['score']}."
        q = self.questions[player['current_q']]
        msg = f"Q{player['current_q']+1}: {q['question']}\n"
        if "answers" in q:
            for i, opt in enumerate(q['answers']):
                msg += f"{chr(65+i)}. {opt}\n"
            msg = msg.strip()
        return msg

    def answer(self, user_id, answer):
        if user_id not in self.players:
            return "Join the quiz first."
        player = self.players[user_id]
        q_idx = player['current_q']
        if q_idx >= len(self.questions):
            return "No more questions."
        if q_idx in player['answered']:
            return "Already answered. Type 'next' for another question."
        q = self.questions[q_idx]
        # Check if it's multiple choice or free-text
        if "answers" in q and "correct" in q:
            try:
                ans_idx = ord(answer.upper()) - 65
                if ans_idx == q['correct']:
                    player['score'] += 1
                    # Track first correct answer
                    if q_idx not in self.first_correct:
                        self.first_correct[q_idx] = user_id
                        logger.info(f"QuizMaster: Question {q_idx+1} first user with correct answer by {user_id}")
                    result = "Correct! 🎉"
                else:
                    result = f"Wrong. Correct answer: {chr(65+q['correct'])}"
                player['answered'].add(q_idx)
                player['current_q'] += 1
                return f"{result}\n" + self.next_question(user_id)
            except Exception:
                return "Invalid answer. Use A, B, C, etc."
        elif "answer" in q:
            user_ans = answer.strip().lower()
            correct_ans = str(q['answer']).strip().lower()
            if user_ans == correct_ans:
                player['score'] += 1
                if q_idx not in self.first_correct:
                    self.first_correct[q_idx] = user_id
                    logger.info(f"QuizMaster: Question {q_idx+1} first user with correct answer by {user_id}")
                result = "Correct! 🎉"
            else:
                result = f"Wrong. Correct answer: {q['answer']}"
            player['answered'].add(q_idx)
            player['current_q'] += 1
            return f"{result}\n" + self.next_question(user_id)
        else:
            return "Invalid question format."

    def top_three(self):
        if not self.players:
            return "No players in the quiz."
        ranking = sorted(self.players.items(), key=lambda x: x[1]['score'], reverse=True)
        count = min(3, len(ranking))
        msg = f"🏆 Top {count} Player{'s' if count > 1 else ''}:\n"
        for idx, (uid, pdata) in enumerate(ranking[:count], start=1):
            msg += f"{idx}. {uid}: @{pdata['score']}\n"
        return msg

    def broadcast(self, quizmaster_id, message):
        msgToAll = {}
        if quizmaster_id and str(quizmaster_id) not in self.quizmaster:
            return "Only the quizmaster can broadcast."
        if not self.players:
            return "No players to broadcast to."
        # set up message
        message_to_send = f"📢 From Quizmaster: {message}"
        msgToAll['message'] = message_to_send
        # setup players
        for uid in self.players.keys():
            msgToAll.setdefault('players', []).append(uid)
        return msgToAll
                
# Initialize the quiz game
quizGamePlayer = QuizGame()
