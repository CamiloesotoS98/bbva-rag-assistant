import json
import logging
import time
import random
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth 

# Importamos la interfaz desde nuestra nueva carpeta de patrones
from patterns.strategy import BaseScraperStrategy

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BBVAStealthScraperStrategy(BaseScraperStrategy):
    """
    Estrategia concreta para extraer información de BBVA Colombia usando Playwright en modo Stealth.
    Diseñado para evadir el WAF (Akamai/Cloudflare) del banco usando la v2.x.
    """
    def scrape(self, url: str) -> dict[str, any]:
        logging.info(f"Iniciando scraping STEALTH en: {url}")
        try:
            with Stealth().use_sync(sync_playwright()) as p:
                
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-CO',
                    timezone_id='America/Bogota'
                )
                
                page = context.new_page()
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                
                tiempo_espera = random.uniform(3.0, 6.0)
                logging.info(f"Esperando {tiempo_espera:.2f} segundos para simular lectura humana...")
                time.sleep(tiempo_espera)
                
                html_content = page.content()
                browser.close()

            soup = BeautifulSoup(html_content, 'html.parser')

            for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                element.decompose()

            clean_text = soup.get_text(separator=' ', strip=True)
            
            return {
                "url": url,
                "raw_html": html_content,
                "clean_text": clean_text,
                "status": "success"
            }

        except Exception as e:
            logging.error(f"Error al acceder a {url} con Playwright: {e}")
            return {
                "url": url,
                "raw_html": None,
                "clean_text": None,
                "status": f"error: {str(e)}"
            }

class WebScraperContext:
    """Maneja la lógica de negocio para guardar los datos."""
    def __init__(self, strategy: BaseScraperStrategy):
        self._strategy = strategy
        self.base_dir = Path(__file__).resolve().parent.parent
        self.raw_dir = self.base_dir / "data" / "raw"
        self.clean_dir = self.base_dir / "data" / "clean"
        
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.clean_dir.mkdir(parents=True, exist_ok=True)

    def set_strategy(self, strategy: BaseScraperStrategy) -> None:
        self._strategy = strategy

    def execute_and_save(self, url: str, filename_prefix: str) -> None:
        result = self._strategy.scrape(url)
        
        if result["status"] == "success":
            raw_path = self.raw_dir / f"{filename_prefix}_raw.html"
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(result["raw_html"])
            
            clean_path = self.clean_dir / f"{filename_prefix}_clean.json"
            clean_data = {
                "url": result["url"],
                "content": result["clean_text"]
            }
            with open(clean_path, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, ensure_ascii=False, indent=4)
                
            logging.info(f"✅ Datos guardados exitosamente para {filename_prefix}")
        else:
            logging.warning(f"❌ No se pudieron guardar los datos para {url}")

# ==========================================
# Ejecución
# ==========================================
if __name__ == "__main__":
    urls_to_scrape = [
        ("https://www.bbva.com.co/", "bbva_home"),
        ("https://www.bbva.com.co/personas/productos/tarjetas/credito.html", "bbva_tarjetas")
    ]

    scraper_context = WebScraperContext(BBVAStealthScraperStrategy())

    for url, prefix in urls_to_scrape:
        scraper_context.execute_and_save(url, prefix)