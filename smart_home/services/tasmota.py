import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 3


def send_command(ip_address: str, command: str) -> Optional[dict]:
    url = f"http://{ip_address}/cm"
    params = {"cmnd": command}

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        logger.error("Bağlantı hatası: %s adresine ulaşılamıyor.", ip_address)
    except requests.Timeout:
        logger.error("Zaman aşımı: %s yanıt vermiyor.", ip_address)
    except requests.RequestException as exc:
        logger.error("İstek hatası (%s): %s", ip_address, exc)

    return None


def turn_on(ip_address: str) -> Optional[dict]:
    return send_command(ip_address, "Power On")


def turn_off(ip_address: str) -> Optional[dict]:
    return send_command(ip_address, "Power Off")


def toggle(ip_address: str) -> Optional[dict]:
    return send_command(ip_address, "Power Toggle")


def get_status(ip_address: str) -> Optional[dict]:
    return send_command(ip_address, "Status 0")


def get_power_state(ip_address: str) -> Optional[str]:
    result = send_command(ip_address, "Power")
    if result and "POWER" in result:
        return result["POWER"]
    return None
