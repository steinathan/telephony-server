from abc import ABC, abstractmethod


class BaseStreamingProvider(ABC):
    @abstractmethod
    async def start(self):
        pass
    
    @abstractmethod
    async def stop(self):
        pass
