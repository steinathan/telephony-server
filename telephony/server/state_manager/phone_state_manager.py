from telephony.server.conversation.abstract_phone_conversation import AbstractPhoneConversation
from telephony.server.state_manager.state_manager import ConversationStateManager


class PhoneConversationStateManager(ConversationStateManager):
    def __init__(self, conversation: "AbstractPhoneConversation"):
        ConversationStateManager.__init__(self, conversation)
        self._phone_conversation = conversation

    def get_config_manager(self):
        return self._phone_conversation.config_manager

    def get_to_phone(self):
        return self._phone_conversation.to_phone

    def get_from_phone(self):
        return self._phone_conversation.from_phone

    def get_direction(self):
        return self._phone_conversation.direction
