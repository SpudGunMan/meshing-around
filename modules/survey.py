# Survey Module for meshbot 2025
# Provides a survey function to collect responses and put into a CSV file

import json
import os # For file operations
from collections import Counter
from modules.log import *

allowedSurveys = []  # List of allowed survey names

trap_list_survey = ("survey", "s:")

class SurveyModule:
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.survey_dir = os.path.join(self.base_dir, '..', 'data', 'surveys') # Directory for survey JSON files
        self.response_dir = os.path.join(self.base_dir, '..', 'data', 'surveys') # Directory for survey response CSV files
        self.surveys = {}
        self.responses = {}
        self.load_surveys()

    def load_surveys(self):
        """Load all surveys from the surveys directory with _survey.json suffix."""
        global allowedSurveys
        allowedSurveys.clear()
        try:
            for filename in os.listdir(self.survey_dir):
                if filename.endswith('_survey.json'):
                    survey_name = filename[:-12]  # Remove '_survey.json'
                    allowedSurveys.append(survey_name)
                    path = os.path.join(self.survey_dir, filename)
                    try:
                        with open(path, encoding='utf-8') as f:
                            self.surveys[survey_name] = json.load(f)
                    except FileNotFoundError:
                        logger.error(f"File not found: {path}")
                        self.surveys[survey_name] = []
                    except json.JSONDecodeError:
                        logger.error(f"Error decoding JSON from file: {path}")
                        self.surveys[survey_name] = []
        except Exception as e:
            logger.error(f"Survey: Error loading surveys: {e}")

    def start_survey(self, user_id, survey_name='example', location=None):
        """Begin a new survey session for a user."""
        if not survey_name:
            survey_name = 'example'
        if survey_name not in allowedSurveys:
            return f"error: survey '{survey_name}' is not allowed."
        self.responses[user_id] = {
            'survey_name': survey_name,
            'current_question': 0,
            'answers': [],
            'location': location if surveyRecordLocation and location is not None else 'N/A'
        }
        msg = f"'{survey_name}'📝survey\nSend 's: <answer>' 'end' to exit."
        msg += self.show_question(user_id)
        return msg

    def show_question(self, user_id):
        """Show the current question for the user, or end the survey."""
        survey_name = self.responses[user_id]['survey_name']
        current = self.responses[user_id]['current_question']
        questions = self.surveys.get(survey_name, [])
        if current >= len(questions):
            return self.end_survey(user_id)
        question = questions[current]
        msg = f"{question['question']}\n"
        if question.get('type', 'multiple_choice') == 'multiple_choice':
            for i, option in enumerate(question['options']):
                msg += f"{chr(65+i)}. {option}\n"
        elif question['type'] == 'integer':
            msg += "(Please enter a number)\n"
        elif question['type'] == 'text':
            msg += "(Please enter your response)\n"
        msg = msg.rstrip('\n')
        return msg

    def save_responses(self, user_id):
        """Save user responses to a CSV file."""
        survey_name = self.responses[user_id]['survey_name']
        if survey_name not in self.surveys:
            logger.warning(f"Survey '{survey_name}' not loaded. Responses not saved.")
            return
        filename = os.path.join(self.response_dir, f'{survey_name}_responses.csv')
        try:
            with open(filename, 'a', encoding='utf-8') as f:
                row = list(map(str, self.responses[user_id]['answers']))
                if surveyRecordID:
                    row.insert(0, str(user_id))
                if surveyRecordLocation:
                    location = self.responses[user_id].get('location')
                    row.insert(1 if surveyRecordID else 0, str(location) if location is not None else "N/A")
                f.write(','.join(row) + '\n')
            logger.info(f"Responses saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving responses to {filename}: {e}")

    def answer(self, user_id, answer, location=None):
        try:
            """Record an answer and return the next question or end message."""
            if user_id not in self.responses:
                return self.start_survey(user_id, location=location)
            question_index = self.responses[user_id]['current_question']
            survey_name = self.responses[user_id]['survey_name']
            questions = self.surveys.get(survey_name, [])
            if question_index < 0 or question_index >= len(questions):
                return "No current question to answer."
            question = questions[question_index]
            qtype = question.get('type', 'multiple_choice')
            if qtype == 'multiple_choice':
                answer_char = answer.strip().upper()[:1]
                if len(answer_char) != 1 or not answer_char.isalpha():
                    return "Please answer with a letter (A, B, C, ...)."
                option_index = ord(answer_char) - 65
                if 0 <= option_index < len(question['options']):
                    self.responses[user_id]['answers'].append(str(option_index))
                    self.responses[user_id]['current_question'] += 1
                    return f"Recorded..\n" + self.show_question(user_id)
                else:
                    print(f"Invalid option index {option_index} for question with {len(question['options'])} options. user entered '{answer}'")
                    return "Invalid answer option. Please try again."
            elif qtype == 'integer':
                try:
                    int_answer = int(answer)
                    self.responses[user_id]['answers'].append(str(int_answer))
                    self.responses[user_id]['current_question'] += 1
                    return f"Recorded..\n" + self.show_question(user_id)
                except ValueError:
                    return "Please enter a valid integer."
            elif qtype == 'text':
                self.responses[user_id]['answers'].append(answer.strip())
                self.responses[user_id]['current_question'] += 1
                return f"Recorded..\n" + self.show_question(user_id)
            else:
                return f"error: unknown question type '{qtype}' and cannot record answer '{answer}'"
        except Exception as e:
            logger.error(f"Error recording answer for user {user_id}: {e}")
            return "An error occurred while recording your answer. Please try again."

    def end_survey(self, user_id):
        """End the survey for the user and save responses."""
        self.save_responses(user_id)
        self.responses.pop(user_id, None)
        return "✅ Survey complete. Thank you for your responses!"

    def quiz_report(self, survey_name='example'):
        """
        Generate a quick poll report: counts of each answer per question.
        Returns a string summary.
        """
        filename = os.path.join(self.response_dir, f'{survey_name}_responses.csv')
        questions = self.surveys.get(survey_name, [])
        if not questions:
            logger.warning(f"No survey found for '{survey_name}'.")
            return f"No survey found for '{survey_name}'."
        all_answers = []
        try:
            with open(filename, encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if surveyRecordID:
                        answers = [int(x) for x in parts[1:] if x.strip().isdigit()]
                    else:
                        answers = [int(x) for x in parts if x.strip().isdigit()]
                    all_answers.append(answers)
        except FileNotFoundError:
            logger.info(f"No responses recorded yet for '{survey_name}'.")
            return "No responses recorded yet."
        report = f"📊 Poll Report for '{survey_name}':\n"
        for q_idx, question in enumerate(questions):
            counts = Counter(ans[q_idx] for ans in all_answers if len(ans) > q_idx)
            report += f"\nQ{q_idx+1}: {question['question']}\n"
            for opt_idx, option in enumerate(question.get('options', [])):
                count = counts.get(opt_idx, 0)
                report += f"  {chr(65+opt_idx)}. {option}: {count}\n"
        return report

# Initialize the survey module
survey_module = SurveyModule()

