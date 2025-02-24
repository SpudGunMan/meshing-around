# hamradio test module for meshbot DE K7MHI 2025
# depends on the JSON question data files from https://github.com/russolsen/ham_radio_question_pool

# data files which are expected to be in ../../data/hamradio/ similar to the following:
# https://raw.githubusercontent.com/russolsen/ham_radio_question_pool/refs/heads/master/technician-2022-2026/technician.json
# https://raw.githubusercontent.com/russolsen/ham_radio_question_pool/refs/heads/master/general-2023-2027/general.json
# https://raw.githubusercontent.com/russolsen/ham_radio_question_pool/refs/heads/master/extra-2024-2028/extra.json

import json
import random
import os
from modules.log import *

class HamTest:
    def __init__(self):
        self.questions = {}
        self.load_questions()
        self.game = {}

    def load_questions(self):
        for level in ['technician', 'general', 'extra']:
            try:
                with open(f'{os.path.dirname(__file__)}/../../data/hamradio/{level}.json') as f:
                    self.questions[level] = json.load(f)
            except FileNotFoundError:
                logger.error(f"File not found: ../../data/hamradio/{level}.json")
                self.questions[level] = []
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from file: ../../data/hamradio/{level}.json")
                self.questions[level] = []

    def newGame(self, id, level='technician'):
        msg = f"📻New {level} quiz started, 'end' to exit."
        if id in self.game:
            level = self.game[id]['level']
        self.game[id] = {
            'level': level,
            'score': 0,
            'total': 0,
            'errors': [],
            'qId': None,
            'question': None,
            'answers': None,
            'correct': None
        }
        # set the pool needed for the game
        if self.game[id]['level'] == 'extra':
            self.game[id]['total'] = 50
        else:
            self.game[id]['total'] = 35

        # randomize the questions
        random.shuffle(self.questions[level])

        msg += f"\n{self.nextQuestion(id)}"
        return msg
    
    def nextQuestion(self, id):
        level = self.game[id]['level']
        # if question has the word figure in it, skip it
        question = random.choice(self.questions[level])
        while 'figure' in question['question'].lower():
            question = random.choice(self.questions[level])

        self.game[id]['question'] = question['question']
        self.game[id]['answers'] = question['answers']
        self.game[id]['correct'] = question['correct']
        self.game[id]['qId'] = question['id']
        self.game[id]['total'] -= 1

        if self.game[id]['total'] == 0:
            return self.endGame(id)

        # ask the question and return answers in A, B, C, D format
        msg = f"{self.game[id]['question']}\n"
        for i, answer in enumerate(self.game[id]['answers']):
            msg += f"{chr(65+i)}. {answer}\n"
        return msg
    
    def answer(self, id, answer):
        if id not in self.game:
            return "No game in progress"
        if self.game[id]['correct'] == ord(answer.upper()) - 65:
            self.game[id]['score'] += 1
            return f"Correct👍\n" + self.nextQuestion(id)
        else:
            # record the section of the question for study aid
            section = self.game[id]['qId'][:3]
            self.game[id]['errors'].append(section)
            # provide the correct answer
            answer = [self.game[id]['correct']]
            return f"Wrong.⛔️ Correct is {chr(65+self.game[id]['correct'])}\n" + self.nextQuestion(id)
        
    def getScore(self, id):
        if id not in self.game:
            return "No game in progress"
        score = self.game[id]['score']
        total = self.game[id]['total']
        level = self.game[id]['level']
        if self.game[id]['errors']:
            areaofstudy = max(set(self.game[id]['errors']), key = self.game[id]['errors'].count)
        else:
            areaofstudy = "None"

        if level == 'extra':
            pool = 50
        else:
            pool = 35
        
        return f"Score: {score}/{pool} Questions left: {total} Area of study: {areaofstudy}"
    
    def endGame(self, id):
        if id not in self.game:
            return "No game in progress"
        
        score = self.game[id]['score']
        level = self.game[id]['level']

        if level == 'extra':
            # passing score for extra is 37
            pool = 50
        else:
            # passing score for technician and general is 26
            pool = 35

        if score >= pool:
            msg = f"Game over. Score: {score} 73! You passed the {level} exam."
        else:
            # find the most common section of the questions missed
            if self.game[id]['errors']:
                areaofstudy = max(set(self.game[id]['errors']), key = self.game[id]['errors'].count)
            else:
                areaofstudy = "None"
            msg = f"Game over. Score: {score} 73! You did not pass the {level} exam. \nYou may want to study {areaofstudy}."
        
        # remove the game[id] from the list
        del self.game[id]
        return msg

hamtestTracker = []
hamtest = HamTest()
   