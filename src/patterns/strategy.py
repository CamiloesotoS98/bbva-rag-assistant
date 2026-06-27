from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseScraperStrategy(ABC):
    """Interfaz base para las estrategias de scraping."""
    @abstractmethod
    def scrape(self, url: str) -> Dict[str, Any]:
        pass