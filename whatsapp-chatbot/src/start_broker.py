from messageBroker.src.message_broker import MessageBroker

from .action_handlers import process_action

if __name__ == "__main__":
    broker = MessageBroker()
    broker.consume("action_queue", process_action)
