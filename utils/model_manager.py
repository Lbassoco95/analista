"""
Gestor de modelos basado en Hugging Face Transformers y Safetensors.
Optimiza el análisis de textos usando modelos locales y distribuidos.
"""

import os
import json
import torch
import numpy as np
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import logging

# Hugging Face imports
from transformers import (
    AutoTokenizer, 
    AutoModel, 
    AutoModelForSequenceClassification,
    pipeline,
    TextClassificationPipeline
)
from safetensors.torch import save_file, load_file
from datasets import Dataset
import accelerate

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Gestor de modelos que utiliza Hugging Face Transformers y Safetensors
    para optimizar el análisis de textos extraídos.
    """
    
    def __init__(self, model_cache_dir: str = "./models_cache"):
        """
        Inicializar el gestor de modelos.
        
        Args:
            model_cache_dir: Directorio para cachear modelos
        """
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(exist_ok=True)
        
        # Configurar device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Modelos cargados
        self.loaded_models = {}
        self.tokenizers = {}
        
        # Configurar accelerate para optimizaciones
        self.accelerator = accelerate.Accelerator()
        
        # Modelos predefinidos para diferentes tareas
        self.model_configs = {
            "classification": {
                "model_name": "microsoft/DialoGPT-medium",
                "task": "text-classification",
                "max_length": 512
            },
            "embedding": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "task": "feature-extraction",
                "max_length": 256
            },
            "summarization": {
                "model_name": "facebook/bart-large-cnn",
                "task": "summarization",
                "max_length": 1024
            }
        }
    
    def load_model(self, model_type: str, model_name: Optional[str] = None) -> Any:
        """
        Cargar modelo usando Safetensors para optimización de memoria.
        
        Args:
            model_type: Tipo de modelo (classification, embedding, summarization)
            model_name: Nombre específico del modelo (opcional)
            
        Returns:
            Modelo cargado
        """
        if model_type in self.loaded_models:
            return self.loaded_models[model_type]
        
        config = self.model_configs.get(model_type, {})
        model_name = model_name or config.get("model_name")
        
        if not model_name:
            raise ValueError(f"Model type {model_type} not configured")
        
        logger.info(f"Loading model: {model_name}")
        
        try:
            # Intentar cargar desde cache local primero
            cache_path = self.model_cache_dir / f"{model_name.replace('/', '_')}"
            
            if cache_path.exists():
                logger.info(f"Loading from cache: {cache_path}")
                model = self._load_from_cache(cache_path, model_type)
            else:
                logger.info(f"Downloading model: {model_name}")
                model = self._download_and_cache_model(model_name, model_type, cache_path)
            
            self.loaded_models[model_type] = model
            return model
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
    
    def _load_from_cache(self, cache_path: Path, model_type: str) -> Any:
        """Cargar modelo desde cache local usando Safetensors."""
        try:
            # Cargar configuración
            config_path = cache_path / "config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Cargar tokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(cache_path))
            self.tokenizers[model_type] = tokenizer
            
            # Cargar modelo según el tipo
            if model_type == "classification":
                model = AutoModelForSequenceClassification.from_pretrained(
                    str(cache_path), 
                    torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
                )
            elif model_type == "embedding":
                model = AutoModel.from_pretrained(
                    str(cache_path),
                    torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
                )
            else:
                model = AutoModel.from_pretrained(str(cache_path))
            
            model.to(self.device)
            model.eval()
            
            return model
            
        except Exception as e:
            logger.warning(f"Failed to load from cache: {str(e)}")
            return None
    
    def _download_and_cache_model(self, model_name: str, model_type: str, cache_path: Path) -> Any:
        """Descargar y cachear modelo usando Safetensors."""
        cache_path.mkdir(exist_ok=True)
        
        # Descargar tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(str(cache_path))
        self.tokenizers[model_type] = tokenizer
        
        # Descargar modelo
        if model_type == "classification":
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )
        elif model_type == "embedding":
            model = AutoModel.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )
        else:
            model = AutoModel.from_pretrained(model_name)
        
        # Guardar modelo usando Safetensors para optimización
        model.save_pretrained(str(cache_path), safe_serialization=True)
        
        model.to(self.device)
        model.eval()
        
        return model
    
    def analyze_text_with_local_model(self, text: str, task: str = "classification") -> Dict[str, Any]:
        """
        Analizar texto usando modelo local en lugar de OpenAI.
        
        Args:
            text: Texto a analizar
            task: Tipo de tarea (classification, embedding, summarization)
            
        Returns:
            Resultado del análisis
        """
        try:
            model = self.load_model(task)
            tokenizer = self.tokenizers.get(task)
            
            if not model or not tokenizer:
                raise ValueError(f"Model or tokenizer not loaded for task: {task}")
            
            # Tokenizar texto
            inputs = tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=self.model_configs[task].get("max_length", 512),
                return_tensors="pt"
            ).to(self.device)
            
            # Inferencia
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Procesar resultados según la tarea
            if task == "classification":
                return self._process_classification_output(outputs, text)
            elif task == "embedding":
                return self._process_embedding_output(outputs, text)
            elif task == "summarization":
                return self._process_summarization_output(outputs, text)
            
        except Exception as e:
            logger.error(f"Error in local model analysis: {str(e)}")
            return self._get_fallback_analysis()
    
    def _process_classification_output(self, outputs, text: str) -> Dict[str, Any]:
        """Procesar salida de clasificación."""
        # Simular clasificación de módulos basada en el texto
        text_lower = text.lower()
        
        # Clasificación basada en palabras clave
        module_keywords = {
            "Wallet Base": ["wallet", "crypto", "digital currency"],
            "KYC/KYB": ["kyc", "kyb", "verification", "identity", "compliance"],
            "Trading Platform": ["trading", "exchange", "broker", "market"],
            "Payment Gateway": ["payment", "gateway", "transaction", "processing"],
            "White Label Solution": ["white label", "whitelabel", "customizable"]
        }
        
        scores = {}
        for module, keywords in module_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[module] = score / len(keywords)
        
        # Obtener la clasificación con mayor score
        best_module = max(scores.items(), key=lambda x: x[1])
        
        return {
            "clasificacion_modulo": best_module[0] if best_module[1] > 0 else "General Service",
            "confianza_analisis": "alta" if best_module[1] > 0.5 else "media",
            "scores": scores
        }
    
    def _process_embedding_output(self, outputs, text: str) -> Dict[str, Any]:
        """Procesar salida de embeddings."""
        # Extraer embeddings del último hidden state
        embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        
        return {
            "embedding": embeddings.tolist(),
            "embedding_dim": embeddings.shape[1],
            "text_length": len(text)
        }
    
    def _process_summarization_output(self, outputs, text: str) -> Dict[str, Any]:
        """Procesar salida de resumen."""
        # Para resumen, necesitaríamos un modelo específico de summarization
        # Por ahora, devolvemos un resumen simple
        words = text.split()
        summary = " ".join(words[:50]) + "..." if len(words) > 50 else text
        
        return {
            "resumen": summary,
            "longitud_original": len(text),
            "longitud_resumen": len(summary)
        }
    
    def extract_price_with_bert(self, text: str) -> Optional[str]:
        """
        Extraer precios usando BERT para mejor precisión.
        
        Args:
            text: Texto del que extraer precios
            
        Returns:
            Precio extraído o None
        """
        try:
            # Usar modelo de clasificación para identificar secciones de precios
            model = self.load_model("classification")
            tokenizer = self.tokenizers.get("classification")
            
            # Dividir texto en chunks para análisis
            chunks = self._split_text_into_chunks(text, max_length=256)
            
            price_chunks = []
            for chunk in chunks:
                # Clasificar si el chunk contiene información de precios
                inputs = tokenizer(
                    chunk,
                    truncation=True,
                    padding=True,
                    return_tensors="pt"
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = model(**inputs)
                
                # Si el chunk parece contener precios, agregarlo
                if self._contains_price_info(chunk):
                    price_chunks.append(chunk)
            
            # Extraer precio del chunk más relevante
            if price_chunks:
                return self._extract_price_from_chunks(price_chunks)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting price with BERT: {str(e)}")
            return None
    
    def _split_text_into_chunks(self, text: str, max_length: int = 256) -> List[str]:
        """Dividir texto en chunks para procesamiento."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _contains_price_info(self, text: str) -> bool:
        """Verificar si el texto contiene información de precios."""
        price_keywords = ["$", "€", "USD", "EUR", "price", "cost", "fee", "monthly", "setup"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in price_keywords)
    
    def _extract_price_from_chunks(self, chunks: List[str]) -> Optional[str]:
        """Extraer precio de los chunks identificados."""
        import re
        
        for chunk in chunks:
            # Patrones de precios
            price_patterns = [
                r'\$[\d,]+(?:\.\d{2})?',
                r'€[\d,]+(?:\.\d{2})?',
                r'[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP)',
                r'[\d,]+(?:\.\d{2})?\s*(?:dollars?|euros?|pounds?)'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, chunk, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
        
        return None
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Análisis de respaldo cuando falla el modelo local."""
        return {
            "clasificacion_modulo": "No clasificado",
            "confianza_analisis": "baja",
            "error": "Modelo local no disponible"
        }
    
    def save_model_state(self, model_type: str, filepath: str):
        """Guardar estado del modelo usando Safetensors."""
        if model_type not in self.loaded_models:
            raise ValueError(f"Model {model_type} not loaded")
        
        model = self.loaded_models[model_type]
        model.save_pretrained(filepath, safe_serialization=True)
        logger.info(f"Model {model_type} saved to {filepath}")
    
    def load_model_state(self, model_type: str, filepath: str):
        """Cargar estado del modelo usando Safetensors."""
        if model_type == "classification":
            model = AutoModelForSequenceClassification.from_pretrained(filepath)
        else:
            model = AutoModel.from_pretrained(filepath)
        
        model.to(self.device)
        model.eval()
        self.loaded_models[model_type] = model
        logger.info(f"Model {model_type} loaded from {filepath}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información de los modelos cargados."""
        info = {
            "device": str(self.device),
            "models_loaded": list(self.loaded_models.keys()),
            "cache_directory": str(self.model_cache_dir),
            "memory_usage": {}
        }
        
        # Información de memoria por modelo
        for model_type, model in self.loaded_models.items():
            if hasattr(model, 'parameters'):
                total_params = sum(p.numel() for p in model.parameters())
                trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
                info["memory_usage"][model_type] = {
                    "total_parameters": total_params,
                    "trainable_parameters": trainable_params,
                    "model_size_mb": total_params * 4 / (1024 * 1024)  # Aproximado
                }
        
        return info 