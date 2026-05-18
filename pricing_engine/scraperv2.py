import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

CACHE_FILE = Path(__file__).parent / "pricing_cache.json"
CACHE_EXPIRY_SECONDS = 24 * 60 * 60
REQUEST_TIMEOUT_SECONDS = 15

# URLs de las APIs oficiales
IBM_PRICING_URL = "https://www.ibm.com/quantum/pricing/"
IBM_CATALOG_PAYGO_URL = "https://globalcatalog.cloud.ibm.com/api/v1/5304b575-3cff-4455-90dc-ae4367762093/pricing"
AWS_PRICE_LIST_API_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBraket/current/index.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

@dataclass
class ScrapeResult:
    status: str
    provider: str
    source_url: str
    downloaded_at: str
    data: Any
    error: Optional[str] = None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def load_cache() -> Optional[dict[str, Any]]:
    if not CACHE_FILE.exists():
        return None
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as file:
            cache = json.load(file)
    except (json.JSONDecodeError, OSError):
        return None
    timestamp = cache.get("timestamp")
    if not isinstance(timestamp, (int, float)):
        return None
    if time.time() - timestamp > CACHE_EXPIRY_SECONDS:
        return None
    return cache.get("data")

def save_cache(data: dict[str, Any]) -> None:
    cache_payload = {
        "timestamp": time.time(),
        "downloaded_at": now_iso(),
        "expires_in_seconds": CACHE_EXPIRY_SECONDS,
        "data": data,
    }
    try:
        with CACHE_FILE.open("w", encoding="utf-8") as file:
            json.dump(cache_payload, file, indent=4, ensure_ascii=False)
    except OSError as error:
        print(f"[!] Error guardando caché: {error}")

def get_json(url: str) -> dict[str, Any]:
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()

def get_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.text

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def extract_ibm_public_plans(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    text = normalize_text(soup.get_text(" ", strip=True))
    expected_plans = ["Open Plan", "Pay-As-You-Go Plan", "Flex Plan", "Premium Plan", "On-Prem Plan"]
    
    fixed_rules = {
        "Open Plan": {"price_label": "Free", "price_usd_per_minute": 0.0, "price_usd_per_second": 0.0},
        "On-Prem Plan": {"price_label": "Contact for quote", "price_usd_per_minute": None, "price_usd_per_second": None},
    }

    plans = []
    for index, plan_name in enumerate(expected_plans):
        start = text.find(plan_name)
        if start == -1: continue
        
        next_positions = [text.find(p, start + len(plan_name)) for p in expected_plans[index + 1:]]
        next_positions = [pos for pos in next_positions if pos != -1]
        end = min(next_positions) if next_positions else min(len(text), start + 500)
        segment = text[start:end]

        if plan_name in fixed_rules:
            rule = fixed_rules[plan_name]
            plans.append({"plan": plan_name, **rule})
            continue

        price_label = "not_found"
        price_per_min = None
        price_per_sec = None

        match = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*USD\s*/\s*minute", segment, re.I)
        if match:
            price_per_min = float(match.group(1))
            price_per_sec = price_per_min / 60
            price_label = f"${price_per_min:g} USD / minute"
        elif re.search(r"requires quote|contact for quote", segment, re.I):
            price_label = "Contact for quote"

        plans.append({
            "plan": plan_name,
            "price_label": price_label,
            "price_usd_per_minute": price_per_min,
            "price_usd_per_second": price_per_sec
        })
    return plans

def fetch_ibm_quantum_api() -> dict[str, Any]:
    """Obtiene los precios de IBM Quantum híbrido (Web Scraping + API Catalog) como prefirió el usuario."""
    downloaded_at = now_iso()
    try:
        # 1. Scraping HTML para tener TODOS los planes
        html = get_html(IBM_PRICING_URL)
        plans = extract_ibm_public_plans(html)
        
        # 2. Petición a la API Catalog como Fallback para el Pay-As-You-Go
        payload = get_json(IBM_CATALOG_PAYGO_URL)
        extracted_data = None
        for metric in payload.get("metrics", []):
            charge_unit = metric.get("charge_unit_display_name")
            for amount in metric.get("amounts", []):
                if amount.get("country") == "USA" and amount.get("currency") == "USD":
                    prices = amount.get("prices", [])
                    if prices:
                        raw_price = prices[0].get("price")
                        extracted_data = {
                            "plan": "Pay-As-You-Go Plan",
                            "charge_unit_display_name": charge_unit,
                            "price_usd_per_second": raw_price,
                            "price_usd_per_minute": raw_price * 60,
                        }
                        break
                        
        return asdict(
            ScrapeResult(
                status="success",
                provider="IBM Quantum",
                source_url=IBM_PRICING_URL,
                downloaded_at=downloaded_at,
                data={
                    "plans": plans,
                    "catalog_paygo_fallback": extracted_data,
                    "notes": ["Se realizó Web Scraping para todos los planes como solicitado, y fallback con API para el paygo."]
                }
            )
        )
    except Exception as error:
        return asdict(ScrapeResult("error", "IBM Quantum", IBM_PRICING_URL, downloaded_at, {}, str(error)))

def fetch_aws_braket_api() -> dict[str, Any]:
    """Obtiene los precios de AWS Braket desde la API oficial de AWS Price List."""
    downloaded_at = now_iso()
    try:
        payload = get_json(AWS_PRICE_LIST_API_URL)
        products = payload.get("products", {})
        terms = payload.get("terms", {}).get("OnDemand", {})
        
        # Mapearemos familia de QPU -> {per_task, per_shot}
        qpus = {}
        
        for sku, product in products.items():
            attributes = product.get("attributes", {})
            family = product.get("productFamily")
            
            if family in ["Quantum Task", "Quantum Task-Shot"]:
                provider = attributes.get("provider")
                devicename = attributes.get("devicename")
                
                # Obtener el precio desde el término de demanda
                sku_terms = terms.get(sku, {})
                if not sku_terms:
                    continue
                # El dict suele tener una única llave con el ID del rate
                offer_term = list(sku_terms.values())[0]
                price_dims = offer_term.get("priceDimensions", {})
                price_dim = list(price_dims.values())[0]
                price_usd = float(price_dim.get("pricePerUnit", {}).get("USD", 0))
                
                # Agrupar por proveedor y dispositivo
                key = f"{provider} - {devicename}"
                if key not in qpus:
                    qpus[key] = {"hardware_provider": provider, "qpu_family": devicename, "per_task_usd": None, "per_shot_usd": None}
                
                if family == "Quantum Task":
                    qpus[key]["per_task_usd"] = price_usd
                else:
                    qpus[key]["per_shot_usd"] = price_usd
                    
        # Convertir a lista de dicts
        qpu_list = list(qpus.values())
        
        return asdict(
            ScrapeResult(
                status="success",
                provider="AWS Braket",
                source_url=AWS_PRICE_LIST_API_URL,
                downloaded_at=downloaded_at,
                data={"qpu_prices": qpu_list}
            )
        )
    except Exception as error:
        return asdict(ScrapeResult("error", "AWS Braket", AWS_PRICE_LIST_API_URL, downloaded_at, {}, str(error)))

def get_pricing_data(force_refresh: bool = False) -> dict[str, Any]:
    if not force_refresh:
        cached_data = load_cache()
        if cached_data is not None:
            print("[!] Cargando precios desde caché local.")
            return cached_data

    print("[!] Caché expirado/No encontrado. Obteniendo datos vía APIs Oficiales...")
    data = {
        "generated_at": now_iso(),
        "providers": {
            "ibm_quantum": fetch_ibm_quantum_api(),
            "aws_braket": fetch_aws_braket_api(),
        },
    }
    save_cache(data)
    print("[+] Datos de API guardados en caché.")
    return data

if __name__ == "__main__":
    pricing_data = get_pricing_data(force_refresh=True)
    print(json.dumps(pricing_data, indent=4, ensure_ascii=False))
