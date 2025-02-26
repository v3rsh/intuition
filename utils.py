import random

def is_correct_answer(user_text: str, correct_text: str) -> bool:
    """
    Сравнение ответов без учёта регистра и ведущих/замыкающих пробелов
    """
    return user_text.strip().lower() == correct_text.strip().lower()
