#!/usr/bin/env python3
"""
API de Retroalimentación para GPT Personalizado
Recibe feedback desde el chat de GPT y lo almacena en Supabase
"""

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import logging
import json
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    """Modelo para solicitudes de retroalimentación"""
    producto: str = Field(..., description="Nombre del producto o solución evaluada")
    mercado: str = Field(..., description="País o sector donde se aplicó")
    observacion: str = Field(..., description="Retroalimentación o aprendizaje clave")
    categoria: Optional[str] = Field(None, description="Categoría del feedback (precio, producto, mercado, etc.)")
    impacto: Optional[str] = Field(None, description="Impacto del feedback (alto, medio, bajo)")
    accion_recomendada: Optional[str] = Field(None, description="Acción recomendada basada en el feedback")
    fuente: Optional[str] = Field("gpt_chat", description="Fuente del feedback")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

class FeedbackResponse(BaseModel):
    """Modelo para respuestas de retroalimentación"""
    id: str
    status: str
    mensaje: str
    timestamp: str

@router.post("/guardar_feedback/", response_model=FeedbackResponse)
async def guardar_feedback(feedback: FeedbackRequest):
    """
    Guarda feedback en Supabase usando la API REST
    """
    try:
        # Preparar los datos para insertar
        data = {
            "producto": feedback.producto,
            "mercado": feedback.mercado,
            "observacion": feedback.observacion,
            "categoria": feedback.categoria,
            "impacto": feedback.impacto,
            "accion_recomendada": feedback.accion_recomendada,
            "fuente": feedback.fuente,
            "metadata": feedback.metadata,
            "fecha": datetime.now().isoformat(),
            "estado": "activo"
        }
        
        # URL de la API REST de Supabase para la tabla retroalimentacion
        url = f"{SUPABASE_URL}/rest/v1/retroalimentacion"
        
        # Headers necesarios para Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Hacer la petición POST a Supabase
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            # Supabase devuelve el registro insertado
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                inserted_id = result[0].get('id', 'unknown')
            else:
                inserted_id = 'unknown'
                
            return FeedbackResponse(
                id=str(inserted_id),
                status="success",
                mensaje="Feedback guardado exitosamente",
                timestamp=datetime.now().isoformat()
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al guardar en Supabase: {response.text}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/obtener_feedback/", response_model=List[Dict[str, Any]])
async def obtener_feedback(
    producto: Optional[str] = None,
    mercado: Optional[str] = None,
    categoria: Optional[str] = None,
    limite: int = 50
):
    """
    Obtiene retroalimentación filtrada
    
    Args:
        producto: Filtrar por producto
        mercado: Filtrar por mercado
        categoria: Filtrar por categoría
        limite: Número máximo de resultados
        
    Returns:
        Lista de feedbacks
    """
    try:
        logger.info(f"🔍 Consultando feedback - Producto: {producto}, Mercado: {mercado}")
        
        # Construir filtros
        filtros = {}
        if producto:
            filtros['producto'] = producto
        if mercado:
            filtros['mercado'] = mercado
        if categoria:
            filtros['categoria'] = categoria
        
        # URL de la API REST de Supabase para obtener datos
        url = f"{SUPABASE_URL}/rest/v1/retroalimentacion?select=*&order=fecha.desc"
        
        # Headers necesarios para Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        # Hacer la petición GET a Supabase
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ {len(data)} feedbacks encontrados")
            return data['data'] or []
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al obtener datos: {response.text}"
            )
            
    except Exception as e:
        logger.error(f"❌ Error consultando feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/analizar_feedback/{producto}/{mercado}")
async def analizar_feedback_producto(producto: str, mercado: str):
    """
    Analiza retroalimentación específica de un producto en un mercado
    
    Args:
        producto: Nombre del producto
        mercado: País o mercado
        
    Returns:
        Análisis de retroalimentación
    """
    try:
        logger.info(f"📊 Analizando feedback para {producto} en {mercado}")
        
        # Obtener feedbacks específicos
        url = f"{SUPABASE_URL}/rest/v1/retroalimentacion?select=*&order=fecha.desc"
        
        # Headers necesarios para Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        # Hacer la petición GET a Supabase
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            feedbacks = data['data']
            
            if not feedbacks:
                return {
                    'producto': producto,
                    'mercado': mercado,
                    'total_feedbacks': 0,
                    'analisis': 'No hay feedback disponible'
                }
            
            # Analizar feedbacks
            categorias = {}
            impactos = {'alto': 0, 'medio': 0, 'bajo': 0}
            observaciones_comunes = []
            
            for feedback in feedbacks:
                # Contar categorías
                categoria = feedback.get('categoria', 'general')
                categorias[categoria] = categorias.get(categoria, 0) + 1
                
                # Contar impactos
                impacto = feedback.get('impacto', 'medio')
                if impacto in impactos:
                    impactos[impacto] += 1
                
                # Recolectar observaciones
                observacion = feedback.get('observacion', '')
                if observacion:
                    observaciones_comunes.append(observacion)
            
            # Generar análisis
            analisis = {
                'producto': producto,
                'mercado': mercado,
                'total_feedbacks': len(feedbacks),
                'categorias_mas_comunes': sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:3],
                'distribucion_impactos': impactos,
                'observaciones_clave': observaciones_comunes[:5],
                'fecha_analisis': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Análisis completado: {len(feedbacks)} feedbacks analizados")
            return analisis
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al obtener datos: {response.text}"
            )
            
    except Exception as e:
        logger.error(f"❌ Error analizando feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/procesar_retroalimentacion/")
async def procesar_retroalimentacion(producto: str, mercado: str):
    """
    Procesa retroalimentación y genera recomendaciones de mejora
    
    Args:
        producto: Nombre del producto
        mercado: País o mercado
        
    Returns:
        Recomendaciones basadas en feedback
    """
    try:
        logger.info(f"🔄 Procesando retroalimentación para {producto} en {mercado}")
        
        # Obtener análisis de feedback
        analisis = await analizar_feedback_producto(producto, mercado)
        
        if analisis['total_feedbacks'] == 0:
            return {
                'producto': producto,
                'mercado': mercado,
                'recomendaciones': ['No hay suficiente feedback para generar recomendaciones'],
                'prioridad': 'baja'
            }
        
        # Generar recomendaciones basadas en el análisis
        recomendaciones = []
        
        # Analizar categorías más comunes
        categorias_comunes = analisis['categorias_mas_comunes']
        for categoria, count in categorias_comunes:
            if categoria == 'precio' and count > 2:
                recomendaciones.append("Revisar estrategia de pricing basado en feedback de clientes")
            elif categoria == 'producto' and count > 2:
                recomendaciones.append("Mejorar funcionalidades del producto según feedback")
            elif categoria == 'mercado' and count > 2:
                recomendaciones.append("Ajustar estrategia de mercado basado en insights")
        
        # Analizar impactos
        impactos = analisis['distribucion_impactos']
        if impactos['alto'] > impactos['medio'] + impactos['bajo']:
            recomendaciones.append("Priorizar atención a feedbacks de alto impacto")
        
        # Recomendaciones generales
        if analisis['total_feedbacks'] > 10:
            recomendaciones.append("Considerar realizar análisis de sentimiento detallado")
        
        if len(recomendaciones) == 0:
            recomendaciones.append("Continuar monitoreando feedback para identificar patrones")
        
        return {
            'producto': producto,
            'mercado': mercado,
            'total_feedbacks': analisis['total_feedbacks'],
            'recomendaciones': recomendaciones,
            'prioridad': 'alta' if impactos['alto'] > 3 else 'media',
            'fecha_procesamiento': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando retroalimentación: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.delete("/eliminar_feedback/{feedback_id}")
async def eliminar_feedback(feedback_id: str):
    """
    Elimina un feedback específico (soft delete)
    
    Args:
        feedback_id: ID del feedback a eliminar
        
    Returns:
        Confirmación de eliminación
    """
    try:
        logger.info(f"🗑️ Eliminando feedback: {feedback_id}")
        
        # URL de la API REST de Supabase para eliminar un registro
        url = f"{SUPABASE_URL}/rest/v1/retroalimentacion?id=eq.{feedback_id}"
        
        # Headers necesarios para Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        # Hacer la petición DELETE a Supabase
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 204:
            return {
                'id': feedback_id,
                'status': 'success',
                'mensaje': 'Feedback eliminado exitosamente',
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al eliminar feedback: {response.text}"
            )
            
    except Exception as e:
        logger.error(f"❌ Error eliminando feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Función de utilidad para obtener estadísticas
@router.get("/estadisticas/")
async def obtener_estadisticas():
    """
    Obtiene estadísticas generales de retroalimentación
    
    Returns:
        Estadísticas de feedback
    """
    try:
        logger.info("📊 Obteniendo estadísticas de feedback")
        
        # URL de la API REST de Supabase para obtener datos
        url = f"{SUPABASE_URL}/rest/v1/retroalimentacion?select=*&order=fecha.desc"
        
        # Headers necesarios para Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        # Hacer la petición GET a Supabase
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            feedbacks = data['data']
            
            if not feedbacks:
                return {
                    'total_feedbacks': 0,
                    'productos_unicos': 0,
                    'mercados_unicos': 0,
                    'categorias': {},
                    'feedbacks_por_mes': {}
                }
            
            # Calcular estadísticas
            productos = set()
            mercados = set()
            categorias = {}
            feedbacks_por_mes = {}
            
            for feedback in feedbacks:
                productos.add(feedback.get('producto', ''))
                mercados.add(feedback.get('mercado', ''))
                
                categoria = feedback.get('categoria', 'general')
                categorias[categoria] = categorias.get(categoria, 0) + 1
                
                # Agrupar por mes
                fecha = feedback.get('fecha', '')
                if fecha:
                    mes = fecha[:7]  # YYYY-MM
                    feedbacks_por_mes[mes] = feedbacks_por_mes.get(mes, 0) + 1
            
            return {
                'total_feedbacks': len(feedbacks),
                'productos_unicos': len(productos),
                'mercados_unicos': len(mercados),
                'categorias': categorias,
                'feedbacks_por_mes': feedbacks_por_mes,
                'fecha_estadisticas': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al obtener datos: {response.text}"
            )
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") 