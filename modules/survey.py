# Survey Module for meshbot 2025
# Provides a survey function to collect responses and put into a CSV file
# this module reads survey definitions from JSON files in the data/surveys directory
# Each survey is defined in a separate JSON file named <survey_name>_survey.json
# Example survey file: example_survey.json
# Example survey response file: example_responses.csv
# Each survey consists of multiple questions, which can be multiple choice, integer, or text
# Users can start a survey, answer questions, and end the survey
# Module acts like a game locking DM until the survey is complete or ended

import json
import os # For file operations
import csv
from datetime import datetime
from collections import Counter
from modules.log import *

allowedSurveys = []  # List of allowed survey names

trap_list_survey = ("survey",)

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
        try:
            """Begin a new survey session for a user."""
            if not survey_name:
                survey_name = default_survey
            if survey_name not in allowedSurveys:
                return f"error: survey '{survey_name}' is not allowed."
            self.responses[user_id] = {
                'survey_name': survey_name,
                'current_question': 0,
                'answers': [],
                'location': location if surveyRecordLocation and location is not None else 'N/A'
            }
            msg = f"'{survey_name}'📝survey\n"
            msg += self.show_question(user_id)
            msg += f"\nSend answer' or 'end'"
            return msg
        except Exception as e:
            logger.error(f"Error starting survey for user {user_id}: {e}")
            return "An error occurred while starting the survey. Please try again later."

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
                # Always write: timestamp, userID, position, answers...
                timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
                user_id_str = str(user_id)
                location = self.responses[user_id].get('location', "N/A")
                answers = list(map(str, self.responses[user_id]['answers']))
                row = [timestamp, user_id_str, str(location)] + answers
                f.write(','.join(row) + '\n')
            logger.info(f"Survey: Responses for user {user_id} saved for survey '{survey_name}' to {filename}.")
        except Exception as e:
            logger.error(f"Error saving responses to {filename}: {e}")

    def format_survey_results(self, results):
        if isinstance(results, dict) and "error" in results:
            return results["error"]
        if not results:
            return "No results found."
        msg = "📊 Survey Results:\n"
        for idx, q in enumerate(results):
            msg += f"\nQ{idx+1}: {q['question']}\n"
            if q['type'] == 'multiple_choice':
                for opt, count in q['summary'].items():
                    msg += f"  {opt}: {count}\n"
            elif q['type'] == 'integer':
                s = q['summary']
                msg += f"  Count: {s['count']}, Avg: {s['average']:.2f}, Min: {s['min']}, Max: {s['max']}\n"
            elif q['type'] == 'text':
                msg += f"  Responses: {q['summary']['responses_count']}\n"
        return msg

    def get_survey_results(self, survey_name='example'):
        if survey_name not in self.surveys:
            return {"error": f"Survey '{survey_name}' not found."}
        filename = os.path.join(self.response_dir, f'{survey_name}_responses.csv')
        questions = self.surveys[survey_name]
        results = []
        try:
            with open(filename, encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = []
                for row in reader:
                    if not row or len(row) < 4:
                        continue
                    # If location field is split due to comma, join columns 2 and 3
                    if row[2].startswith('[') and not row[2].endswith(']') and len(row) > 4:
                        location = row[2] + ',' + row[3]
                        answers = row[4:]
                    else:
                        location = row[2]
                        answers = row[3:]
                    lines.append(answers)

            for q_idx, question in enumerate(questions):
                qtype = question.get('type', 'multiple_choice')
                answers = [row[q_idx] for row in lines if len(row) > q_idx]

                summary = {}
                if qtype == 'multiple_choice':
                    counts = Counter(answers)
                    summary = {chr(65+i): counts.get(chr(65+i), 0) for i in range(len(question.get('options', [])))}

                elif qtype == 'integer':
                    ints = [int(a) for a in answers if a.isdigit()]
                    summary = {
                        "count": len(ints),
                        "average": sum(ints)/len(ints) if ints else 0,
                        "min": min(ints) if ints else None,
                        "max": max(ints) if ints else None
                    }

                elif qtype == 'text':
                    summary = {"responses_count": len([a for a in answers if a.strip()])}


                results.append({
                    "question": question['question'],
                    "type": qtype,
                    "summary": summary
                })

            return results
        except FileNotFoundError:
            return {"error": f"No responses recorded yet for '{survey_name}'."}
        except Exception as e:
            logger.error(f"Error summarizing survey results: {e}")
            return NO_ALERTS

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
                    # Valid answer record letter, not index
                    self.responses[user_id]['answers'].append(answer_char)
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
        if user_id not in self.responses:
            return "No active survey session to end."
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

