# utils/context.py
"""Глобальный контекст для избежания циклических импортов"""

class BotContext:
    def __init__(self):
        self.bot = None
        self.auto_message_scheduler = None

# Глобальный экземпляр
context = BotContext()

def set_bot(bot):
    context.bot = bot

def set_scheduler(scheduler):
    context.auto_message_scheduler = scheduler