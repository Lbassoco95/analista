#!/usr/bin/env python3
"""
GPT Estratégico Personalizado
Integra búsqueda inteligente, estrategia comercial y planner de producto
para análisis estratégico completo de mercado
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from utils.busqueda_inteligente import BusquedaInteligente
from estrategia_comercial import EstrategiaComercial
from planner_producto import PlannerProducto
from utils.chat_gpt_manager import ChatGPTManager
from utils.pinecone_manager import PineconeManager
from supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class GPTEstrategico:
    """
    GPT personalizado para análisis estratégico completo
    """
    
    def __init__(self):
        """Inicializar GPT estratégico"""
        self.busqueda = BusquedaInteligente()
        self.estrategia = EstrategiaComercial()
        self.planner = PlannerProducto()
        self.chat_manager = ChatGPTManager()
        self.pinecone_manager = PineconeManager()
        self.supabase = SupabaseClient()
        
        # Configuración del sistema
        self.config = {
            'max_analisis_concurrentes': 3,
            'tiempo_maximo_analisis': 300,  # 5 minutos
            'nivel_detalle': 'completo',  # completo, resumido, ejecutivo
            'guardar_historial': True,
            'habilitar_retroalimentacion': True
        }
        
        logger.info("✅ GPTEstrategico inicializado")
    
    async def analizar_mercado_completo(self,
                                       consulta: str,
                                       contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Análisis completo de mercado basado en consulta natural
        
        Args:
            consulta: Consulta en lenguaje natural (ej: "Queremos lanzar firma digital en México")
            contexto: Contexto adicional (opcional)
            
        Returns:
            Dict con análisis completo
        """
        logger.info(f"🧠 Iniciando análisis estratégico: {consulta}")
        
        # Extraer información de la consulta
        info_extraida = await self._extraer_info_consulta(consulta)
        
        analisis = {
            'consulta_original': consulta,
            'info_extraida': info_extraida,
            'timestamp': datetime.now().isoformat(),
            'analisis_mercado': {},
            'estrategia_comercial': {},
            'plan_producto': {},
            'insights_integrados': [],
            'recomendaciones_finales': [],
            'documentos_generados': [],
            'id_analisis': None
        }
        
        try:
            # 1. Análisis de mercado
            logger.info("📊 Realizando análisis de mercado...")
            analisis['analisis_mercado'] = await self._realizar_analisis_mercado(info_extraida)
            
            # 2. Estrategia comercial
            logger.info("🎯 Generando estrategia comercial...")
            analisis['estrategia_comercial'] = await self._generar_estrategia_comercial(info_extraida)
            
            # 3. Plan de producto
            logger.info("📋 Generando plan de producto...")
            analisis['plan_producto'] = await self._generar_plan_producto(info_extraida)
            
            # 4. Insights integrados
            logger.info("💡 Generando insights integrados...")
            analisis['insights_integrados'] = await self._generar_insights_integrados(analisis)
            
            # 5. Recomendaciones finales
            logger.info("🎯 Generando recomendaciones finales...")
            analisis['recomendaciones_finales'] = await self._generar_recomendaciones_finales(analisis)
            
            # 6. Generar documentos
            logger.info("📄 Generando documentos...")
            analisis['documentos_generados'] = await self._generar_documentos(analisis)
            
            # 7. Guardar en Supabase
            if self.config['guardar_historial']:
                logger.info("💾 Guardando análisis en Supabase...")
                analisis['id_analisis'] = await self._guardar_analisis(analisis)
            
            logger.info("✅ Análisis estratégico completado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis estratégico: {str(e)}")
            analisis['error'] = str(e)
        
        return analisis
    
    async def _extraer_info_consulta(self, consulta: str) -> Dict[str, Any]:
        """Extraer información estructurada de la consulta"""
        try:
            # Usar GPT para extraer información
            prompt = f"""
            Extrae la siguiente información de esta consulta de negocio:
            
            Consulta: "{consulta}"
            
            Extrae y responde en formato JSON:
            {{
                "producto": "nombre del producto/servicio",
                "pais": "país objetivo",
                "segmento": "segmento de mercado (si se menciona)",
                "tipo_analisis": "mercado/estrategia/plan",
                "restricciones": ["lista de restricciones mencionadas"],
                "objetivos": ["lista de objetivos mencionados"]
            }}
            """
            
            # Simular extracción (en producción usar GPT real)
            info = {
                'producto': 'Producto genérico',
                'pais': 'México',
                'segmento': None,
                'tipo_analisis': 'completo',
                'restricciones': [],
                'objetivos': ['Lanzar producto', 'Analizar mercado']
            }
            
            # Extraer información básica usando keywords
            consulta_lower = consulta.lower()
            
            # Detectar producto
            if 'firma digital' in consulta_lower:
                info['producto'] = 'Firma Digital'
            elif 'wallet' in consulta_lower:
                info['producto'] = 'Wallet Crypto'
            elif 'kyc' in consulta_lower or 'verificacion' in consulta_lower:
                info['producto'] = 'KYC/Verificación'
            elif 'onboarding' in consulta_lower:
                info['producto'] = 'Onboarding Remoto'
            
            # Detectar país
            paises = ['mexico', 'colombia', 'argentina', 'chile', 'peru', 'brasil']
            for pais in paises:
                if pais in consulta_lower:
                    info['pais'] = pais.title()
                    break
            
            # Detectar segmento
            segmentos = ['freelancers', 'empresas', 'notarias', 'abogados', 'fintechs']
            for segmento in segmentos:
                if segmento in consulta_lower:
                    info['segmento'] = segmento
                    break
            
            return info
            
        except Exception as e:
            logger.error(f"Error extrayendo información: {str(e)}")
            return {
                'producto': 'Producto',
                'pais': 'México',
                'segmento': None,
                'tipo_analisis': 'completo',
                'restricciones': [],
                'objetivos': ['Análisis de mercado']
            }
    
    async def _realizar_analisis_mercado(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Realizar análisis de mercado"""
        try:
            producto = info.get('producto', 'Producto')
            pais = info.get('pais', 'México')
            segmento = info.get('segmento')
            
            # Usar búsqueda inteligente
            analisis = await self.busqueda.buscar_mercado_completo(producto, pais, segmento)
            
            return {
                'datos_mercado': analisis,
                'resumen_ejecutivo': await self._generar_resumen_mercado(analisis),
                'tendencias_clave': analisis.get('analisis', {}).get('tendencias_clave', []),
                'oportunidades': analisis.get('analisis', {}).get('oportunidades', []),
                'riesgos': analisis.get('analisis', {}).get('riesgos', []),
                'fuentes_utilizadas': len(analisis.get('fuentes', {}))
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de mercado: {str(e)}")
            return {'error': str(e)}
    
    async def _generar_estrategia_comercial(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Generar estrategia comercial"""
        try:
            producto = info.get('producto', 'Producto')
            pais = info.get('pais', 'México')
            segmento = info.get('segmento')
            
            # Usar estrategia comercial
            estrategia = await self.estrategia.generar_estrategia_completa(
                producto, pais, segmento
            )
            
            return {
                'estrategia_completa': estrategia,
                'resumen_ejecutivo': await self.estrategia.generar_resumen_ejecutivo(estrategia),
                'precio_sugerido': estrategia.get('precio_sugerido', {}),
                'buyer_persona': estrategia.get('buyer_persona', {}),
                'estrategia_entrada': estrategia.get('estrategia_entrada', {}),
                'recursos_comerciales': estrategia.get('recursos_comerciales', {}),
                'recomendaciones': estrategia.get('recomendaciones', [])
            }
            
        except Exception as e:
            logger.error(f"Error en estrategia comercial: {str(e)}")
            return {'error': str(e)}
    
    async def _generar_plan_producto(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Generar plan de producto"""
        try:
            producto = info.get('producto', 'Producto')
            pais = info.get('pais', 'México')
            descripcion = f"Lanzamiento de {producto} en {pais}"
            restricciones = info.get('restricciones', [])
            
            # Usar planner de producto
            plan = await self.planner.generar_plan_completo(
                producto, pais, descripcion, restricciones
            )
            
            return {
                'plan_completo': plan,
                'resumen_ejecutivo': await self.planner.generar_resumen_plan(plan),
                'fases': plan.get('fases', []),
                'tareas_por_equipo': plan.get('tareas_por_equipo', {}),
                'indicadores': plan.get('indicadores', {}),
                'timeline': plan.get('timeline_detallado', {}),
                'checklist': plan.get('checklist_lanzamiento', [])
            }
            
        except Exception as e:
            logger.error(f"Error en plan de producto: {str(e)}")
            return {'error': str(e)}
    
    async def _generar_insights_integrados(self, analisis: Dict[str, Any]) -> List[str]:
        """Generar insights integrados de todo el análisis"""
        try:
            insights = []
            
            # Insights de mercado
            mercado = analisis.get('analisis_mercado', {})
            if mercado.get('oportunidades'):
                insights.append(f"🎯 Oportunidad de mercado: {mercado['oportunidades'][0]}")
            
            if mercado.get('riesgos'):
                insights.append(f"⚠️ Riesgo principal: {mercado['riesgos'][0]}")
            
            # Insights de estrategia
            estrategia = analisis.get('estrategia_comercial', {})
            precio = estrategia.get('precio_sugerido', {})
            if precio.get('precio_base'):
                insights.append(f"💰 Precio óptimo: {precio['precio_base']} USD mensual")
            
            # Insights de plan
            plan = analisis.get('plan_producto', {})
            fases = plan.get('fases', [])
            if fases:
                insights.append(f"📅 Timeline: {len(fases)} fases, {sum(f.get('duracion_semanas', 4) for f in fases)} semanas total")
            
            # Insights de recursos
            recursos = estrategia.get('recursos_comerciales', {})
            equipo = recursos.get('equipo', {})
            if equipo:
                total_equipo = sum(equipo.values())
                insights.append(f"👥 Equipo necesario: {total_equipo} personas")
            
            # Insights de presupuesto
            presupuesto = recursos.get('presupuesto_mensual', {})
            if presupuesto:
                total_presupuesto = sum(float(str(v).replace('USD ', '').replace(',', '')) for v in presupuesto.values() if isinstance(v, str) and 'USD' in v)
                insights.append(f"💰 Presupuesto mensual: USD {total_presupuesto:,.0f}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights: {str(e)}")
            return ["Error generando insights integrados"]
    
    async def _generar_recomendaciones_finales(self, analisis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar recomendaciones finales accionables"""
        try:
            recomendaciones = []
            
            # Recomendaciones de mercado
            mercado = analisis.get('analisis_mercado', {})
            if mercado.get('oportunidades'):
                recomendaciones.append({
                    'categoria': 'Mercado',
                    'recomendacion': f"Aprovechar oportunidad: {mercado['oportunidades'][0]}",
                    'prioridad': 'Alta',
                    'accion': 'Iniciar desarrollo de MVP inmediatamente',
                    'timeline': '1-2 meses'
                })
            
            # Recomendaciones de pricing
            estrategia = analisis.get('estrategia_comercial', {})
            precio = estrategia.get('precio_sugerido', {})
            if precio.get('precio_base'):
                recomendaciones.append({
                    'categoria': 'Pricing',
                    'recomendacion': f"Establecer precio base de {precio['precio_base']} USD",
                    'prioridad': 'Alta',
                    'accion': 'Validar pricing con pilotos',
                    'timeline': '2-3 meses'
                })
            
            # Recomendaciones de equipo
            recursos = estrategia.get('recursos_comerciales', {})
            equipo = recursos.get('equipo', {})
            if equipo:
                recomendaciones.append({
                    'categoria': 'Equipo',
                    'recomendacion': 'Contratar equipo comercial escalable',
                    'prioridad': 'Media',
                    'accion': 'Iniciar proceso de contratación',
                    'timeline': '1-3 meses'
                })
            
            # Recomendaciones de timeline
            plan = analisis.get('plan_producto', {})
            timeline = plan.get('timeline', {})
            if timeline.get('duracion_total'):
                recomendaciones.append({
                    'categoria': 'Timeline',
                    'recomendacion': f"Seguir timeline de {timeline['duracion_total']}",
                    'prioridad': 'Alta',
                    'accion': 'Establecer milestones semanales',
                    'timeline': 'Continuo'
                })
            
            return recomendaciones
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {str(e)}")
            return []
    
    async def _generar_documentos(self, analisis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar documentos ejecutivos"""
        try:
            documentos = []
            
            # 1. Resumen ejecutivo
            resumen_ejecutivo = await self._generar_resumen_ejecutivo_completo(analisis)
            documentos.append({
                'tipo': 'resumen_ejecutivo',
                'titulo': 'Resumen Ejecutivo - Análisis Estratégico',
                'contenido': resumen_ejecutivo,
                'formato': 'markdown'
            })
            
            # 2. Pitch de venta
            pitch_venta = await self._generar_pitch_venta(analisis)
            documentos.append({
                'tipo': 'pitch_venta',
                'titulo': 'Pitch de Venta - Presentación Ejecutiva',
                'contenido': pitch_venta,
                'formato': 'markdown'
            })
            
            # 3. Checklist operativo
            checklist = await self._generar_checklist_operativo(analisis)
            documentos.append({
                'tipo': 'checklist_operativo',
                'titulo': 'Checklist Operativo - Equipo Comercial',
                'contenido': checklist,
                'formato': 'markdown'
            })
            
            # 4. Guía técnica
            guia_tecnica = await self._generar_guia_tecnica(analisis)
            documentos.append({
                'tipo': 'guia_tecnica',
                'titulo': 'Guía Técnica - Integradores',
                'contenido': guia_tecnica,
                'formato': 'markdown'
            })
            
            return documentos
            
        except Exception as e:
            logger.error(f"Error generando documentos: {str(e)}")
            return []
    
    async def _generar_resumen_ejecutivo_completo(self, analisis: Dict[str, Any]) -> str:
        """Generar resumen ejecutivo completo"""
        try:
            info = analisis.get('info_extraida', {})
            producto = info.get('producto', 'Producto')
            pais = info.get('pais', 'País')
            
            resumen = f"""
# Resumen Ejecutivo - Análisis Estratégico

## 🎯 Objetivo
Lanzamiento de {producto} en {pais}

## 📊 Análisis de Mercado
- **Tamaño**: {analisis.get('analisis_mercado', {}).get('datos_mercado', {}).get('analisis', {}).get('resumen_ejecutivo', 'En crecimiento')}
- **Oportunidades**: {len(analisis.get('analisis_mercado', {}).get('datos_mercado', {}).get('analisis', {}).get('oportunidades', []))} identificadas
- **Riesgos**: {len(analisis.get('analisis_mercado', {}).get('datos_mercado', {}).get('analisis', {}).get('riesgos', []))} principales

## 💰 Estrategia Comercial
- **Precio Sugerido**: {analisis.get('estrategia_comercial', {}).get('precio_sugerido', {}).get('precio_base', 'N/A')} USD
- **Enfoque**: {analisis.get('estrategia_comercial', {}).get('estrategia_entrada', {}).get('enfoque', 'B2B')}
- **Timeline**: {analisis.get('plan_producto', {}).get('timeline', {}).get('duracion_total', 'N/A')}

## 📈 Indicadores Clave
- **MRR Objetivo**: {analisis.get('estrategia_comercial', {}).get('estrategia_completa', {}).get('indicadores', {}).get('ventas', {}).get('mrr_objetivo', 'N/A')}
- **Adopción Objetivo**: {analisis.get('estrategia_comercial', {}).get('estrategia_completa', {}).get('indicadores', {}).get('mercado', {}).get('adopcion_objetivo', 'N/A')}

## 🚀 Próximos Pasos
1. Aprobar estrategia comercial
2. Iniciar desarrollo de MVP
3. Contratar equipo comercial
4. Ejecutar campañas de marketing

## 💡 Insights Principales
"""
            
            insights = analisis.get('insights_integrados', [])
            for insight in insights[:5]:
                resumen += f"- {insight}\n"
            
            return resumen
            
        except Exception as e:
            logger.error(f"Error generando resumen ejecutivo: {str(e)}")
            return "Error generando resumen ejecutivo"
    
    async def _generar_pitch_venta(self, analisis: Dict[str, Any]) -> str:
        """Generar pitch de venta"""
        try:
            info = analisis.get('info_extraida', {})
            producto = info.get('producto', 'Producto')
            pais = info.get('pais', 'País')
            
            pitch = f"""
# Pitch de Venta - {producto}

## 🎯 Propuesta de Valor
{producto} es la solución definitiva para [problema específico] en {pais}.

## 💰 ROI Esperado
- **Retorno de inversión**: 300% en 12 meses
- **Tiempo de implementación**: < 30 días
- **ROI por cliente**: USD 15,000 anual

## 🏆 Diferenciadores Clave
1. **Tecnología de vanguardia**
2. **Soporte local en {pais}**
3. **Integración sencilla**
4. **Pricing competitivo**

## 📊 Casos de Éxito
- Cliente A: 40% reducción en costos
- Cliente B: 60% mejora en eficiencia
- Cliente C: 200% incremento en conversiones

## 🚀 Próximos Pasos
1. Demo personalizada
2. Piloto de 30 días
3. Implementación completa
4. Soporte continuo

## 📞 Contacto
[Información de contacto del equipo comercial]
"""
            
            return pitch
            
        except Exception as e:
            logger.error(f"Error generando pitch: {str(e)}")
            return "Error generando pitch de venta"
    
    async def _generar_checklist_operativo(self, analisis: Dict[str, Any]) -> str:
        """Generar checklist operativo"""
        try:
            checklist = analisis.get('plan_producto', {}).get('checklist', [])
            
            contenido = """
# Checklist Operativo - Equipo Comercial

## ✅ Tareas Críticas
"""
            
            for categoria in checklist:
                contenido += f"\n### {categoria['categoria']}\n"
                for item in categoria['items']:
                    contenido += f"- [ ] {item['tarea']}\n"
            
            contenido += """
## 📅 Timeline de Ejecución
- Semana 1-2: Preparación
- Semana 3-4: Piloto
- Semana 5-6: Lanzamiento
- Semana 7+: Escalamiento

## 📊 Métricas de Seguimiento
- Leads generados
- Demos realizadas
- Proposals enviadas
- Deals cerrados
- Revenue generado
"""
            
            return contenido
            
        except Exception as e:
            logger.error(f"Error generando checklist: {str(e)}")
            return "Error generando checklist operativo"
    
    async def _generar_guia_tecnica(self, analisis: Dict[str, Any]) -> str:
        """Generar guía técnica"""
        try:
            info = analisis.get('info_extraida', {})
            producto = info.get('producto', 'Producto')
            
            guia = f"""
# Guía Técnica - {producto}

## 🔧 Requisitos Técnicos
- **API REST**: Disponible 24/7
- **Documentación**: Swagger/OpenAPI
- **SDK**: JavaScript, Python, Java
- **Webhooks**: Soporte completo

## 🚀 Integración Rápida
1. **Registro**: Crear cuenta en dashboard
2. **API Keys**: Generar credenciales
3. **Webhook**: Configurar endpoints
4. **Testing**: Ambiente sandbox
5. **Go Live**: Activación producción

## 📚 Recursos de Desarrollo
- [Documentación API](link)
- [SDK Downloads](link)
- [Code Examples](link)
- [Support Portal](link)

## 🔒 Seguridad
- **Certificaciones**: SOC 2 Type II
- **Encriptación**: AES-256
- **Compliance**: GDPR, CCPA
- **Audit**: Anual independiente

## 📞 Soporte Técnico
- **Email**: tech-support@company.com
- **Chat**: Disponible 24/7
- **Phone**: +1-800-TECH-SUP
- **Response Time**: < 4 horas
"""
            
            return guia
            
        except Exception as e:
            logger.error(f"Error generando guía técnica: {str(e)}")
            return "Error generando guía técnica"
    
    async def _guardar_analisis(self, analisis: Dict[str, Any]) -> str:
        """Guardar análisis en Supabase"""
        try:
            # Preparar datos para Supabase
            datos_analisis = {
                'consulta_original': analisis['consulta_original'],
                'producto': analisis['info_extraida'].get('producto'),
                'pais': analisis['info_extraida'].get('pais'),
                'segmento': analisis['info_extraida'].get('segmento'),
                'timestamp': analisis['timestamp'],
                'analisis_completo': json.dumps(analisis),
                'estado': 'completado'
            }
            
            # Guardar en Supabase
            resultado = await self.supabase.insert_data('analisis_estrategicos', datos_analisis)
            
            if resultado and resultado.get('id'):
                return str(resultado['id'])
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error guardando análisis: {str(e)}")
            return None
    
    async def consultar_historial(self, filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Consultar historial de análisis"""
        try:
            # Consultar Supabase
            historial = await self.supabase.get_data('analisis_estrategicos', filtros)
            
            return historial or []
            
        except Exception as e:
            logger.error(f"Error consultando historial: {str(e)}")
            return []
    
    async def analizar_retroalimentacion(self, id_analisis: str, datos_ventas: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar retroalimentación de ventas y generar mejoras"""
        try:
            # Obtener análisis original
            analisis_original = await self.supabase.get_data_by_id('analisis_estrategicos', id_analisis)
            
            if not analisis_original:
                return {'error': 'Análisis no encontrado'}
            
            # Analizar datos de ventas vs predicciones
            analisis_retroalimentacion = {
                'id_analisis_original': id_analisis,
                'timestamp': datetime.now().isoformat(),
                'datos_ventas': datos_ventas,
                'comparacion_predicciones': {},
                'ajustes_recomendados': [],
                'lecciones_aprendidas': []
            }
            
            # Comparar predicciones vs realidad
            predicciones = json.loads(analisis_original.get('analisis_completo', '{}'))
            estrategia = predicciones.get('estrategia_comercial', {})
            
            # Análisis de pricing
            precio_predicho = estrategia.get('precio_sugerido', {}).get('precio_base', 0)
            precio_real = datos_ventas.get('precio_real', 0)
            
            if precio_real > 0:
                diferencia_precio = ((precio_real - precio_predicho) / precio_predicho) * 100
                analisis_retroalimentacion['comparacion_predicciones']['pricing'] = {
                    'prediccion': precio_predicho,
                    'realidad': precio_real,
                    'diferencia_porcentual': diferencia_precio,
                    'ajuste_necesario': abs(diferencia_precio) > 20
                }
            
            # Análisis de adopción
            adopcion_predicha = estrategia.get('estrategia_completa', {}).get('indicadores', {}).get('mercado', {}).get('adopcion_objetivo', '0%')
            adopcion_real = datos_ventas.get('adopcion_real', 0)
            
            analisis_retroalimentacion['comparacion_predicciones']['adopcion'] = {
                'prediccion': adopcion_predicha,
                'realidad': f"{adopcion_real}%",
                'diferencia': 'Por analizar'
            }
            
            # Generar ajustes recomendados
            if abs(diferencia_precio) > 20:
                analisis_retroalimentacion['ajustes_recomendados'].append({
                    'area': 'Pricing',
                    'ajuste': f"Ajustar precio en {diferencia_precio:.1f}%",
                    'justificacion': 'Diferencia significativa entre predicción y realidad'
                })
            
            # Guardar retroalimentación
            await self.supabase.insert_data('retroalimentacion_analisis', analisis_retroalimentacion)
            
            return analisis_retroalimentacion
            
        except Exception as e:
            logger.error(f"Error analizando retroalimentación: {str(e)}")
            return {'error': str(e)}
    
    async def generar_resumen_mercado(self, analisis: Dict[str, Any]) -> str:
        """Generar resumen de mercado"""
        try:
            datos_mercado = analisis.get('datos_mercado', {})
            analisis_data = datos_mercado.get('analisis', {})
            
            resumen = f"""
## 📊 Resumen de Mercado

**Tendencias Clave:**
{chr(10).join(f"- {tendencia}" for tendencia in analisis_data.get('tendencias_clave', []))}

**Oportunidades:**
{chr(10).join(f"- {oportunidad}" for oportunidad in analisis_data.get('oportunidades', []))}

**Riesgos:**
{chr(10).join(f"- {riesgo}" for riesgo in analisis_data.get('riesgos', []))}

**Fuentes Analizadas:** {datos_mercado.get('fuentes_utilizadas', 0)}
"""
            
            return resumen
            
        except Exception as e:
            logger.error(f"Error generando resumen de mercado: {str(e)}")
            return "Error generando resumen de mercado"

# Función de utilidad
def get_gpt_estrategico() -> GPTEstrategico:
    """Obtener instancia del GPT estratégico"""
    return GPTEstrategico() 