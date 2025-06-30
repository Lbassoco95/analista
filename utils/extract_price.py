"""
Utilidades para extracción de precios y limpieza de texto.
Optimizado para trabajar con modelos de Hugging Face.
"""

import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Limpiar y normalizar texto para análisis.
    
    Args:
        text: Texto original
        
    Returns:
        Texto limpio y normalizado
    """
    if not text:
        return ""
    
    # Convertir a string si no lo es
    text = str(text)
    
    # Eliminar caracteres especiales pero mantener estructura
    text = re.sub(r'[^\w\s\.\,\$\€\£\¥\-\+\%\d]', ' ', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text)
    
    # Normalizar separadores de miles
    text = re.sub(r'(\d),(\d{3})', r'\1\2', text)
    
    # Limpiar espacios al inicio y final
    text = text.strip()
    
    return text

def extract_price_from_text(text: str) -> Optional[str]:
    """
    Extraer precio del texto usando patrones optimizados.
    
    Args:
        text: Texto del que extraer precio
        
    Returns:
        Precio extraído o None
    """
    if not text:
        return None
    
    # Limpiar texto
    cleaned_text = clean_text(text)
    
    # Patrones de precios optimizados
    price_patterns = [
        # Dólares con diferentes formatos
        r'\$\s*([\d,]+(?:\.\d{2})?)',
        r'USD\s*([\d,]+(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',
        
        # Euros
        r'€\s*([\d,]+(?:\.\d{2})?)',
        r'EUR\s*([\d,]+(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*euros?',
        
        # Libras
        r'£\s*([\d,]+(?:\.\d{2})?)',
        r'GBP\s*([\d,]+(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*pounds?',
        
        # Números con palabras clave de precio
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:price|cost|fee|charge)',
        r'(?:price|cost|fee|charge)\s*[:\-]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        
        # Rango de precios
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'from\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*to\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        
        # Precios mensuales/anuales
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*per\s*(?:month|year|annum)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:monthly|yearly|annual)',
        
        # Setup fees
        r'setup\s*(?:fee|cost)\s*[:\-]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*setup',
    ]
    
    # Buscar precios
    found_prices = []
    
    for pattern in price_patterns:
        matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                # Para rangos de precios
                for price in match:
                    if price:
                        found_prices.append(normalize_price(price))
            else:
                found_prices.append(normalize_price(match))
    
    # Si no se encontraron precios, buscar números grandes
    if not found_prices:
        large_numbers = re.findall(r'(\d{4,}(?:,\d{3})*(?:\.\d{2})?)', cleaned_text)
        for number in large_numbers:
            found_prices.append(normalize_price(number))
    
    # Retornar el precio más relevante
    if found_prices:
        # Priorizar precios que parecen ser costos reales
        for price in found_prices:
            if is_likely_price(price, cleaned_text):
                return price
        
        # Si no hay uno claro, retornar el primero
        return found_prices[0]
    
    return None

def normalize_price(price_str: str) -> str:
    """
    Normalizar formato de precio.
    
    Args:
        price_str: Precio como string
        
    Returns:
        Precio normalizado
    """
    if not price_str:
        return ""
    
    # Limpiar el precio
    price = re.sub(r'[^\d\.]', '', price_str)
    
    # Convertir a float y de vuelta para normalizar
    try:
        price_float = float(price)
        
        # Formatear según el tamaño
        if price_float >= 1000:
            return f"${price_float:,.0f}"
        elif price_float >= 1:
            return f"${price_float:.2f}"
        else:
            return f"${price_float:.2f}"
    except ValueError:
        return price_str

def is_likely_price(price: str, context: str) -> bool:
    """
    Determinar si un número es probablemente un precio real.
    
    Args:
        price: Precio a evaluar
        context: Texto de contexto
        
    Returns:
        True si es probablemente un precio real
    """
    try:
        price_value = float(re.sub(r'[^\d\.]', '', price))
        context_lower = context.lower()
        
        # Palabras clave que indican que es un precio real
        price_keywords = [
            'price', 'cost', 'fee', 'charge', 'setup', 'monthly', 'annual',
            'subscription', 'license', 'package', 'plan', 'tier'
        ]
        
        # Verificar si el contexto contiene palabras clave de precio
        has_price_keywords = any(keyword in context_lower for keyword in price_keywords)
        
        # Verificar si el valor es razonable para un precio
        is_reasonable_value = 1 <= price_value <= 1000000
        
        return has_price_keywords and is_reasonable_value
        
    except (ValueError, TypeError):
        return False

def extract_price_range(text: str) -> Optional[Dict[str, str]]:
    """
    Extraer rango de precios del texto.
    
    Args:
        text: Texto del que extraer rango
        
    Returns:
        Diccionario con min y max, o None
    """
    if not text:
        return None
    
    cleaned_text = clean_text(text)
    
    # Patrones para rangos de precios
    range_patterns = [
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'from\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*to\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'between\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*and\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*to\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    ]
    
    for pattern in range_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            min_price = normalize_price(match.group(1))
            max_price = normalize_price(match.group(2))
            
            return {
                "min": min_price,
                "max": max_price
            }
    
    return None

def extract_currency(text: str) -> Optional[str]:
    """
    Extraer moneda del texto.
    
    Args:
        text: Texto del que extraer moneda
        
    Returns:
        Código de moneda o None
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Mapeo de monedas
    currency_map = {
        'dollar': 'USD',
        'dollars': 'USD',
        '$': 'USD',
        'usd': 'USD',
        'euro': 'EUR',
        'euros': 'EUR',
        '€': 'EUR',
        'eur': 'EUR',
        'pound': 'GBP',
        'pounds': 'GBP',
        '£': 'GBP',
        'gbp': 'GBP',
        'yen': 'JPY',
        '¥': 'JPY',
        'jpy': 'JPY',
    }
    
    for currency_name, currency_code in currency_map.items():
        if currency_name in text_lower:
            return currency_code
    
    return None

def extract_pricing_terms(text: str) -> Dict[str, Any]:
    """
    Extraer términos de precios del texto.
    
    Args:
        text: Texto del que extraer términos
        
    Returns:
        Diccionario con términos extraídos
    """
    if not text:
        return {}
    
    cleaned_text = clean_text(text)
    text_lower = cleaned_text.lower()
    
    terms = {
        "setup_fee": None,
        "monthly_cost": None,
        "annual_cost": None,
        "transaction_fees": None,
        "minimum_requirements": None,
        "billing_cycle": None,
        "currency": extract_currency(text)
    }
    
    # Setup fee
    setup_patterns = [
        r'setup\s*(?:fee|cost)\s*[:\-]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*setup',
        r'one.?time\s*(?:fee|cost)\s*[:\-]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    ]
    
    for pattern in setup_patterns:
        match = re.search(pattern, text_lower)
        if match:
            terms["setup_fee"] = normalize_price(match.group(1))
            break
    
    # Monthly cost
    monthly_patterns = [
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*per\s*month',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*monthly',
        r'monthly\s*(?:cost|fee|charge)\s*[:\-]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    ]
    
    for pattern in monthly_patterns:
        match = re.search(pattern, text_lower)
        if match:
            terms["monthly_cost"] = normalize_price(match.group(1))
            break
    
    # Annual cost
    annual_patterns = [
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*per\s*year',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*annual',
        r'annual\s*(?:cost|fee|charge)\s*[:\-]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    ]
    
    for pattern in annual_patterns:
        match = re.search(pattern, text_lower)
        if match:
            terms["annual_cost"] = normalize_price(match.group(1))
            break
    
    # Transaction fees
    transaction_patterns = [
        r'(\d+(?:\.\d+)?%)\s*per\s*transaction',
        r'transaction\s*fee\s*[:\-]?\s*(\d+(?:\.\d+)?%)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*per\s*transaction',
    ]
    
    for pattern in transaction_patterns:
        match = re.search(pattern, text_lower)
        if match:
            terms["transaction_fees"] = match.group(1)
            break
    
    # Billing cycle
    if any(word in text_lower for word in ['monthly', 'per month']):
        terms["billing_cycle"] = "monthly"
    elif any(word in text_lower for word in ['annual', 'yearly', 'per year']):
        terms["billing_cycle"] = "annual"
    elif any(word in text_lower for word in ['quarterly', 'per quarter']):
        terms["billing_cycle"] = "quarterly"
    
    return terms

def validate_price_extraction(text: str, extracted_price: str) -> Dict[str, Any]:
    """
    Validar la extracción de precio.
    
    Args:
        text: Texto original
        extracted_price: Precio extraído
        
    Returns:
        Diccionario con validación
    """
    validation = {
        "is_valid": False,
        "confidence": 0.0,
        "issues": [],
        "suggestions": []
    }
    
    if not extracted_price:
        validation["issues"].append("No se encontró precio")
        return validation
    
    try:
        # Extraer valor numérico
        price_value = float(re.sub(r'[^\d\.]', '', extracted_price))
        
        # Validaciones básicas
        if price_value <= 0:
            validation["issues"].append("Precio debe ser mayor a 0")
        
        if price_value > 1000000:
            validation["issues"].append("Precio parece demasiado alto")
        
        # Verificar contexto
        context_score = 0.0
        price_keywords = ['price', 'cost', 'fee', 'charge', 'setup', 'monthly']
        text_lower = text.lower()
        
        for keyword in price_keywords:
            if keyword in text_lower:
                context_score += 0.2
        
        validation["confidence"] = min(context_score, 1.0)
        
        # Determinar si es válido
        validation["is_valid"] = (
            len(validation["issues"]) == 0 and 
            validation["confidence"] > 0.3
        )
        
        # Sugerencias
        if validation["confidence"] < 0.5:
            validation["suggestions"].append("Revisar contexto del precio")
        
        if price_value < 1:
            validation["suggestions"].append("Verificar si el precio está en la moneda correcta")
        
    except (ValueError, TypeError) as e:
        validation["issues"].append(f"Error procesando precio: {str(e)}")
    
    return validation

def extract_white_label_info(text: str) -> List[tuple]:
    """
    Extraer información relevante sobre white label, wallet y otros módulos.
    
    Args:
        text: Texto completo a analizar
        
    Returns:
        Lista de tuplas (modulo, texto_relevante)
    """
    if not text:
        return []
    
    # Definir módulos y sus palabras clave
    modules_keywords = {
        'White Label Wallet': ['white label', 'whitelabel', 'wallet', 'crypto wallet', 'digital wallet'],
        'KYC/KYB': ['kyc', 'kyb', 'verification', 'identity', 'compliance', 'onboarding'],
        'Crypto Trading': ['trading', 'exchange', 'crypto exchange', 'trading platform'],
        'Payment Gateway': ['payment', 'gateway', 'fiat', 'onramp', 'offramp'],
        'Digital Signature': ['signature', 'digital signature', 'e-signature', 'certificate'],
        'Custody': ['custody', 'custodial', 'cold storage', 'hot wallet'],
        'Cross Border': ['cross border', 'crossborder', 'international', 'remittance']
    }
    
    results = []
    paragraphs = text.split('\n\n')
    
    for module, keywords in modules_keywords.items():
        relevant_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            
            # Verificar si el párrafo contiene palabras clave del módulo
            if any(keyword.lower() in paragraph_lower for keyword in keywords):
                # Verificar que el párrafo tenga contenido sustancial
                if len(paragraph.strip()) > 50:  # Mínimo 50 caracteres
                    relevant_paragraphs.append(paragraph.strip())
        
        # Si se encontraron párrafos relevantes, agregar a resultados
        if relevant_paragraphs:
            # Combinar párrafos relevantes del mismo módulo
            combined_text = ' '.join(relevant_paragraphs)
            results.append((module, combined_text))
    
    return results

def extract_latam_metadata(text: str) -> Dict[str, Any]:
    """
    Extraer metadata específica para LATAM/México.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Diccionario con metadata extraída
    """
    metadata = {
        'pais': None,
        'region': None,
        'moneda': None,
        'fecha_publicacion': None,
        'tipo_fuente': 'web',
        'confianza': 0.0
    }
    
    # Países LATAM
    latam_countries = {
        'México': ['mexico', 'méxico', 'mx'],
        'Argentina': ['argentina', 'ar'],
        'Colombia': ['colombia', 'co'],
        'Chile': ['chile', 'cl'],
        'Perú': ['peru', 'perú', 'pe'],
        'Uruguay': ['uruguay', 'uy'],
        'Paraguay': ['paraguay', 'py'],
        'Bolivia': ['bolivia', 'bo'],
        'Ecuador': ['ecuador', 'ec'],
        'Venezuela': ['venezuela', 've'],
        'Guatemala': ['guatemala', 'gt'],
        'Honduras': ['honduras', 'hn'],
        'El Salvador': ['el salvador', 'sv'],
        'Nicaragua': ['nicaragua', 'ni'],
        'Costa Rica': ['costa rica', 'cr'],
        'Panamá': ['panama', 'panamá', 'pa'],
        'Cuba': ['cuba', 'cu'],
        'República Dominicana': ['republica dominicana', 'dominican republic', 'do'],
        'Puerto Rico': ['puerto rico', 'pr']
    }
    
    text_lower = text.lower()
    
    # Detectar país
    for country, keywords in latam_countries.items():
        if any(keyword in text_lower for keyword in keywords):
            metadata['pais'] = country
            metadata['region'] = 'México' if country == 'México' else 'LATAM'
            break
    
    # Detectar moneda
    currency_patterns = {
        'USD': [r'\$', r'usd', r'dollars?', r'dólares?'],
        'EUR': [r'€', r'eur', r'euros?'],
        'MXN': [r'mxn', r'pesos? mexicanos?', r'mexican pesos?'],
        'ARS': [r'ars', r'pesos? argentinos?', r'argentine pesos?'],
        'COP': [r'cop', r'pesos? colombianos?', r'colombian pesos?'],
        'CLP': [r'clp', r'pesos? chilenos?', r'chilean pesos?'],
        'PEN': [r'pen', r'soles?', r'peruvian soles?'],
        'BRL': [r'brl', r'reais?', r'brazilian reais?']
    }
    
    for currency, patterns in currency_patterns.items():
        if any(re.search(pattern, text_lower) for pattern in patterns):
            metadata['moneda'] = currency
            break
    
    # Detectar fecha (patrones básicos)
    date_patterns = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                # Intentar parsear la fecha
                date_str = match.group(0)
                metadata['fecha_publicacion'] = date_str
                break
            except:
                continue
    
    # Calcular confianza básica
    confidence = 0.0
    if metadata['pais']:
        confidence += 30
    if metadata['moneda']:
        confidence += 20
    if metadata['fecha_publicacion']:
        confidence += 10
    
    # Ajustar confianza basada en la calidad del texto
    if len(text.strip()) > 200:
        confidence += 20
    if any(keyword in text_lower for keyword in ['price', 'cost', 'fee', 'pricing']):
        confidence += 20
    
    metadata['confianza'] = min(confidence, 100.0)
    
    return metadata

def validate_cross_reference(text1: str, text2: str, module: str) -> Dict[str, Any]:
    """
    Validar si dos textos se refieren al mismo dato usando análisis semántico.
    
    Args:
        text1: Primer texto
        text2: Segundo texto
        module: Módulo que se está comparando
        
    Returns:
        Diccionario con resultado de validación
    """
    # Extraer precios de ambos textos
    price1 = extract_price_from_text(text1)
    price2 = extract_price_from_text(text2)
    
    # Extraer metadata
    metadata1 = extract_latam_metadata(text1)
    metadata2 = extract_latam_metadata(text2)
    
    validation_result = {
        'same_module': False,
        'same_price': False,
        'same_country': False,
        'same_currency': False,
        'confidence': 0.0,
        'validation_method': 'cross_reference'
    }
    
    # Verificar si es el mismo módulo
    if module.lower() in text1.lower() and module.lower() in text2.lower():
        validation_result['same_module'] = True
        validation_result['confidence'] += 30
    
    # Verificar si es el mismo precio
    if price1 and price2:
        # Normalizar precios para comparación
        norm_price1 = normalize_price(price1)
        norm_price2 = normalize_price(price2)
        
        if norm_price1 == norm_price2:
            validation_result['same_price'] = True
            validation_result['confidence'] += 40
        else:
            # Verificar si están en el mismo rango (diferencia < 20%)
            try:
                val1 = float(re.sub(r'[^\d\.]', '', norm_price1))
                val2 = float(re.sub(r'[^\d\.]', '', norm_price2))
                if abs(val1 - val2) / max(val1, val2) < 0.2:
                    validation_result['same_price'] = True
                    validation_result['confidence'] += 30
            except:
                pass
    
    # Verificar si es el mismo país
    if metadata1['pais'] and metadata2['pais']:
        if metadata1['pais'] == metadata2['pais']:
            validation_result['same_country'] = True
            validation_result['confidence'] += 20
    
    # Verificar si es la misma moneda
    if metadata1['moneda'] and metadata2['moneda']:
        if metadata1['moneda'] == metadata2['moneda']:
            validation_result['same_currency'] = True
            validation_result['confidence'] += 10
    
    return validation_result 