
from telephony.utils.redis_conversation_message_queue import RedisConversationMessageQueue


class ConversationStateManager:
    def __init__(self, conversation):
        self._conversation = conversation
        if not hasattr(self, "redis_message_queue"):
            self.redis_message_queue = RedisConversationMessageQueue()

    @property
    def transcript(self):
        return self._conversation.transcript

    def disable_synthesis(self):
        self._conversation.synthesis_enabled = False

    def enable_synthesis(self):
        self._conversation.synthesis_enabled = True

    def mute_agent(self):
        self._conversation.agent.is_muted = True

    def unmute_agent(self):
        self._conversation.agent.is_muted = False


    async def terminate_conversation(self):
        self._conversation.mark_terminated()

    def set_call_check_for_idle_paused(self, value: bool):
        if not self._conversation:
            return
        self._conversation.set_check_for_idle_paused(value)

    def get_conversation_id(self):
        return self._conversation.id
