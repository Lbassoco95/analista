#!/usr/bin/env python3
"""
Módulo Planner de Producto
Genera planes de lanzamiento completos con fases, tareas e indicadores
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio

from estrategia_comercial import EstrategiaComercial
from utils.busqueda_inteligente import BusquedaInteligente
from utils.chat_gpt_manager import ChatGPTManager

logger = logging.getLogger(__name__)

class PlannerProducto:
    """
    Generador de planes de producto con fases, tareas e indicadores
    """
    
    def __init__(self):
        """Inicializar planner de producto"""
        self.estrategia = EstrategiaComercial()
        self.busqueda = BusquedaInteligente()
        self.chat_manager = ChatGPTManager()
        
        # Templates de planes por tipo de producto
        self.plan_templates = {
            'onboarding': {
                'fases': ['Investigación', 'Diseño', 'Desarrollo', 'Testing', 'Lanzamiento'],
                'duracion_total': '4-6 meses',
                'equipos': ['Producto', 'Legal', 'Ventas', 'Marketing', 'Tecnología']
            },
            'wallet': {
                'fases': ['MVP', 'Piloto', 'Lanzamiento', 'Escalamiento'],
                'duracion_total': '6-8 meses',
                'equipos': ['Producto', 'Compliance', 'Ventas', 'Soporte', 'Tecnología']
            },
            'kyc': {
                'fases': ['Compliance', 'Desarrollo', 'Certificación', 'Lanzamiento'],
                'duracion_total': '3-5 meses',
                'equipos': ['Legal', 'Producto', 'Ventas', 'Soporte', 'Tecnología']
            },
            'payment': {
                'fases': ['Integración', 'Certificación', 'Piloto', 'Lanzamiento'],
                'duracion_total': '4-6 meses',
                'equipos': ['Producto', 'Compliance', 'Ventas', 'Soporte', 'Tecnología']
            }
        }
        
        logger.info("✅ PlannerProducto inicializado")
    
    async def generar_plan_completo(self,
                                   producto: str,
                                   pais: str,
                                   descripcion: str = None,
                                   restricciones: List[str] = None) -> Dict[str, Any]:
        """
        Generar plan completo de lanzamiento de producto
        
        Args:
            producto: Producto a lanzar
            pais: País objetivo
            descripcion: Descripción adicional del producto
            restricciones: Restricciones o consideraciones especiales
            
        Returns:
            Dict con plan completo de lanzamiento
        """
        logger.info(f"📋 Generando plan de producto: {producto} en {pais}")
        
        plan = {
            'producto': producto,
            'pais': pais,
            'descripcion': descripcion,
            'restricciones': restricciones or [],
            'timestamp': datetime.now().isoformat(),
            'estrategia': {},
            'fases': [],
            'tareas_por_equipo': {},
            'indicadores': {},
            'benchmarks': {},
            'riesgos': [],
            'recursos': {},
            'timeline_detallado': {},
            'checklist_lanzamiento': []
        }
        
        try:
            # 1. Generar estrategia comercial
            logger.info("🎯 Generando estrategia comercial...")
            plan['estrategia'] = await self.estrategia.generar_estrategia_completa(
                producto, pais
            )
            
            # 2. Definir fases del proyecto
            logger.info("📅 Definiendo fases del proyecto...")
            plan['fases'] = await self._definir_fases(producto, pais, descripcion)
            
            # 3. Definir tareas por equipo
            logger.info("👥 Definiendo tareas por equipo...")
            plan['tareas_por_equipo'] = await self._definir_tareas_equipos(producto, pais)
            
            # 4. Definir indicadores de éxito
            logger.info("📊 Definiendo indicadores de éxito...")
            plan['indicadores'] = await self._definir_indicadores_exito(producto, pais)
            
            # 5. Definir benchmarks
            logger.info("🎯 Definiendo benchmarks...")
            plan['benchmarks'] = await self._definir_benchmarks(producto, pais)
            
            # 6. Identificar riesgos
            logger.info("⚠️ Identificando riesgos...")
            plan['riesgos'] = await self._identificar_riesgos(producto, pais, restricciones)
            
            # 7. Definir recursos necesarios
            logger.info("💰 Definiendo recursos...")
            plan['recursos'] = await self._definir_recursos(producto, pais)
            
            # 8. Generar timeline detallado
            logger.info("⏱️ Generando timeline detallado...")
            plan['timeline_detallado'] = await self._generar_timeline_detallado(plan)
            
            # 9. Generar checklist de lanzamiento
            logger.info("✅ Generando checklist de lanzamiento...")
            plan['checklist_lanzamiento'] = await self._generar_checklist_lanzamiento(plan)
            
            logger.info("✅ Plan de producto generado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error generando plan: {str(e)}")
            plan['error'] = str(e)
        
        return plan
    
    async def _definir_fases(self, producto: str, pais: str, descripcion: str = None) -> List[Dict[str, Any]]:
        """Definir fases del proyecto"""
        try:
            tipo_producto = self._identificar_tipo_producto(producto)
            template = self.plan_templates.get(tipo_producto, self.plan_templates['onboarding'])
            
            fases = []
            duracion_base = 4  # semanas por fase
            
            for i, fase_nombre in enumerate(template['fases']):
                fase = {
                    'id': i + 1,
                    'nombre': fase_nombre,
                    'duracion_semanas': duracion_base,
                    'objetivos': await self._generar_objetivos_fase(fase_nombre, producto, pais),
                    'entregables': await self._generar_entregables_fase(fase_nombre, producto),
                    'dependencias': await self._identificar_dependencias_fase(i, template['fases']),
                    'equipos_involucrados': await self._identificar_equipos_fase(fase_nombre, template['equipos']),
                    'presupuesto_estimado': await self._estimar_presupuesto_fase(fase_nombre, producto),
                    'riesgos_fase': await self._identificar_riesgos_fase(fase_nombre, producto, pais)
                }
                fases.append(fase)
            
            return fases
            
        except Exception as e:
            logger.error(f"Error definiendo fases: {str(e)}")
            return []
    
    async def _generar_objetivos_fase(self, fase: str, producto: str, pais: str) -> List[str]:
        """Generar objetivos específicos para cada fase"""
        objetivos = {
            'Investigación': [
                f'Analizar mercado de {producto} en {pais}',
                'Identificar competidores principales',
                'Definir buyer personas',
                'Validar demanda del producto'
            ],
            'Diseño': [
                'Diseñar arquitectura del producto',
                'Crear wireframes y prototipos',
                'Definir experiencia de usuario',
                'Establecer estándares de diseño'
            ],
            'Desarrollo': [
                'Desarrollar MVP del producto',
                'Implementar funcionalidades core',
                'Integrar APIs necesarias',
                'Realizar pruebas internas'
            ],
            'Testing': [
                'Ejecutar pruebas de calidad',
                'Realizar pruebas de seguridad',
                'Validar con usuarios beta',
                'Optimizar rendimiento'
            ],
            'Lanzamiento': [
                'Lanzar producto al mercado',
                'Ejecutar campañas de marketing',
                'Activar canales de venta',
                'Monitorear métricas clave'
            ]
        }
        
        return objetivos.get(fase, ['Completar fase de desarrollo'])
    
    async def _generar_entregables_fase(self, fase: str, producto: str) -> List[str]:
        """Generar entregables específicos para cada fase"""
        entregables = {
            'Investigación': [
                'Reporte de análisis de mercado',
                'Documento de buyer personas',
                'Análisis de competencia',
                'Validación de demanda'
            ],
            'Diseño': [
                'Arquitectura del producto',
                'Wireframes y prototipos',
                'Guía de diseño',
                'Especificaciones técnicas'
            ],
            'Desarrollo': [
                'MVP funcional',
                'Documentación técnica',
                'APIs integradas',
                'Base de datos configurada'
            ],
            'Testing': [
                'Reporte de pruebas',
                'Certificaciones de seguridad',
                'Feedback de usuarios beta',
                'Optimizaciones implementadas'
            ],
            'Lanzamiento': [
                'Producto en producción',
                'Campañas activas',
                'Equipo comercial operativo',
                'Sistema de monitoreo'
            ]
        }
        
        return entregables.get(fase, ['Entregable de la fase'])
    
    async def _identificar_dependencias_fase(self, indice_fase: int, fases: List[str]) -> List[str]:
        """Identificar dependencias entre fases"""
        if indice_fase == 0:
            return []
        else:
            return [fases[indice_fase - 1]]
    
    async def _identificar_equipos_fase(self, fase: str, equipos: List[str]) -> List[str]:
        """Identificar equipos involucrados en cada fase"""
        mapeo_equipos = {
            'Investigación': ['Producto', 'Marketing'],
            'Diseño': ['Producto', 'Tecnología'],
            'Desarrollo': ['Tecnología', 'Producto'],
            'Testing': ['Tecnología', 'Producto', 'Soporte'],
            'Lanzamiento': ['Ventas', 'Marketing', 'Soporte', 'Producto']
        }
        
        return mapeo_equipos.get(fase, equipos)
    
    async def _estimar_presupuesto_fase(self, fase: str, producto: str) -> Dict[str, Any]:
        """Estimar presupuesto para cada fase"""
        presupuestos = {
            'Investigación': {'desarrollo': 5000, 'marketing': 3000, 'legal': 2000},
            'Diseño': {'desarrollo': 8000, 'diseño': 5000, 'producto': 3000},
            'Desarrollo': {'desarrollo': 15000, 'infraestructura': 5000, 'testing': 3000},
            'Testing': {'testing': 5000, 'seguridad': 8000, 'optimización': 3000},
            'Lanzamiento': {'marketing': 10000, 'ventas': 8000, 'soporte': 5000}
        }
        
        return presupuestos.get(fase, {'desarrollo': 5000})
    
    async def _identificar_riesgos_fase(self, fase: str, producto: str, pais: str) -> List[str]:
        """Identificar riesgos específicos de cada fase"""
        riesgos = {
            'Investigación': [
                'Información de mercado insuficiente',
                'Cambios regulatorios durante el proceso'
            ],
            'Diseño': [
                'Diseño no alineado con necesidades del mercado',
                'Complejidad técnica mayor a la esperada'
            ],
            'Desarrollo': [
                'Retrasos en desarrollo',
                'Problemas de integración con APIs'
            ],
            'Testing': [
                'Problemas de seguridad no detectados',
                'Baja adopción en pruebas beta'
            ],
            'Lanzamiento': [
                'Baja respuesta del mercado',
                'Problemas de escalabilidad'
            ]
        }
        
        return riesgos.get(fase, ['Riesgo general de la fase'])
    
    async def _definir_tareas_equipos(self, producto: str, pais: str) -> Dict[str, List[Dict[str, Any]]]:
        """Definir tareas específicas por equipo"""
        try:
            tareas = {
                'Producto': [
                    {
                        'tarea': 'Definir roadmap del producto',
                        'duracion': '2 semanas',
                        'responsable': 'Product Manager',
                        'prioridad': 'Alta',
                        'dependencias': []
                    },
                    {
                        'tarea': 'Crear especificaciones funcionales',
                        'duracion': '3 semanas',
                        'responsable': 'Product Manager',
                        'prioridad': 'Alta',
                        'dependencias': ['Definir roadmap del producto']
                    },
                    {
                        'tarea': 'Validar con usuarios objetivo',
                        'duracion': '2 semanas',
                        'responsable': 'UX Researcher',
                        'prioridad': 'Media',
                        'dependencias': ['Crear especificaciones funcionales']
                    }
                ],
                'Tecnología': [
                    {
                        'tarea': 'Arquitectura técnica',
                        'duracion': '3 semanas',
                        'responsable': 'Tech Lead',
                        'prioridad': 'Alta',
                        'dependencias': []
                    },
                    {
                        'tarea': 'Desarrollo MVP',
                        'duracion': '8 semanas',
                        'responsable': 'Equipo de desarrollo',
                        'prioridad': 'Alta',
                        'dependencias': ['Arquitectura técnica']
                    },
                    {
                        'tarea': 'Testing y QA',
                        'duracion': '4 semanas',
                        'responsable': 'QA Team',
                        'prioridad': 'Alta',
                        'dependencias': ['Desarrollo MVP']
                    }
                ],
                'Legal': [
                    {
                        'tarea': 'Análisis regulatorio',
                        'duracion': '4 semanas',
                        'responsable': 'Legal Counsel',
                        'prioridad': 'Alta',
                        'dependencias': []
                    },
                    {
                        'tarea': 'Preparar documentación legal',
                        'duracion': '3 semanas',
                        'responsable': 'Legal Counsel',
                        'prioridad': 'Alta',
                        'dependencias': ['Análisis regulatorio']
                    }
                ],
                'Ventas': [
                    {
                        'tarea': 'Definir estrategia de ventas',
                        'duracion': '2 semanas',
                        'responsable': 'Sales Director',
                        'prioridad': 'Media',
                        'dependencias': []
                    },
                    {
                        'tarea': 'Preparar materiales de venta',
                        'duracion': '3 semanas',
                        'responsable': 'Sales Enablement',
                        'prioridad': 'Media',
                        'dependencias': ['Definir estrategia de ventas']
                    },
                    {
                        'tarea': 'Entrenar equipo comercial',
                        'duracion': '2 semanas',
                        'responsable': 'Sales Director',
                        'prioridad': 'Alta',
                        'dependencias': ['Preparar materiales de venta']
                    }
                ],
                'Marketing': [
                    {
                        'tarea': 'Desarrollar estrategia de marketing',
                        'duracion': '2 semanas',
                        'responsable': 'Marketing Director',
                        'prioridad': 'Media',
                        'dependencias': []
                    },
                    {
                        'tarea': 'Crear campañas de lanzamiento',
                        'duracion': '4 semanas',
                        'responsable': 'Marketing Team',
                        'prioridad': 'Alta',
                        'dependencias': ['Desarrollar estrategia de marketing']
                    }
                ]
            }
            
            return tareas
            
        except Exception as e:
            logger.error(f"Error definiendo tareas por equipo: {str(e)}")
            return {}
    
    async def _definir_indicadores_exito(self, producto: str, pais: str) -> Dict[str, Any]:
        """Definir indicadores de éxito del proyecto"""
        try:
            indicadores = {
                'producto': {
                    'funcionalidad_completa': '100%',
                    'performance_objetivo': '99.9% uptime',
                    'seguridad': 'Certificación ISO 27001',
                    'usabilidad': 'Score > 8.5/10'
                },
                'mercado': {
                    'adopcion_objetivo': '70% en 6 meses',
                    'satisfaccion_cliente': '> 8.5/10',
                    'retencion': '> 90%',
                    'referencias': '> 20%'
                },
                'negocio': {
                    'mrr_objetivo': 'USD 50,000 en 6 meses',
                    'cac_objetivo': '< USD 500',
                    'ltv_objetivo': '> USD 5,000',
                    'roi_objetivo': '> 300% en 12 meses'
                },
                'operacional': {
                    'tiempo_implementacion': '< 30 días',
                    'soporte_response_time': '< 4 horas',
                    'escalabilidad': 'Soporte 10x crecimiento'
                }
            }
            
            return indicadores
            
        except Exception as e:
            logger.error(f"Error definiendo indicadores: {str(e)}")
            return {}
    
    async def _definir_benchmarks(self, producto: str, pais: str) -> Dict[str, Any]:
        """Definir benchmarks del mercado"""
        try:
            # Buscar información de mercado
            analisis_mercado = await self.busqueda.buscar_mercado_completo(producto, pais)
            
            benchmarks = {
                'competencia': {
                    'precio_promedio': 'USD 25-50 mensual',
                    'tiempo_implementacion': '2-4 semanas',
                    'satisfaccion_cliente': '7.5-8.5/10',
                    'cuota_mercado_top3': '60-80%'
                },
                'mercado': {
                    'tasa_crecimiento': '15-25% anual',
                    'penetracion_mercado': '30-50%',
                    'adopcion_tecnologia': '70-85%',
                    'inversion_media': 'USD 10,000-50,000'
                },
                'tecnologia': {
                    'uptime_estandar': '99.5-99.9%',
                    'response_time': '< 200ms',
                    'escalabilidad': 'Soporte 100k+ usuarios',
                    'seguridad': 'SOC 2 Type II'
                }
            }
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error definiendo benchmarks: {str(e)}")
            return {}
    
    async def _identificar_riesgos(self, producto: str, pais: str, restricciones: List[str] = None) -> List[Dict[str, Any]]:
        """Identificar riesgos del proyecto"""
        try:
            riesgos = [
                {
                    'riesgo': 'Cambios regulatorios',
                    'probabilidad': 'Media',
                    'impacto': 'Alto',
                    'mitigacion': 'Monitoreo constante de regulaciones',
                    'responsable': 'Legal'
                },
                {
                    'riesgo': 'Retrasos en desarrollo',
                    'probabilidad': 'Alta',
                    'impacto': 'Medio',
                    'mitigacion': 'Metodología ágil con sprints cortos',
                    'responsable': 'Tecnología'
                },
                {
                    'riesgo': 'Baja adopción del mercado',
                    'probabilidad': 'Media',
                    'impacto': 'Alto',
                    'mitigacion': 'Validación temprana con usuarios',
                    'responsable': 'Producto'
                },
                {
                    'riesgo': 'Problemas de escalabilidad',
                    'probabilidad': 'Baja',
                    'impacto': 'Alto',
                    'mitigacion': 'Arquitectura cloud-native',
                    'responsable': 'Tecnología'
                },
                {
                    'riesgo': 'Competencia agresiva',
                    'probabilidad': 'Alta',
                    'impacto': 'Medio',
                    'mitigacion': 'Diferenciación por servicio y soporte',
                    'responsable': 'Marketing'
                }
            ]
            
            # Agregar riesgos específicos por restricciones
            if restricciones:
                for restriccion in restricciones:
                    riesgos.append({
                        'riesgo': f'Restricción: {restriccion}',
                        'probabilidad': 'Alta',
                        'impacto': 'Medio',
                        'mitigacion': 'Plan de contingencia específico',
                        'responsable': 'Producto'
                    })
            
            return riesgos
            
        except Exception as e:
            logger.error(f"Error identificando riesgos: {str(e)}")
            return []
    
    async def _definir_recursos(self, producto: str, pais: str) -> Dict[str, Any]:
        """Definir recursos necesarios para el proyecto"""
        try:
            recursos = {
                'equipo': {
                    'producto': 2,
                    'tecnologia': 4,
                    'legal': 1,
                    'ventas': 3,
                    'marketing': 2,
                    'soporte': 2
                },
                'presupuesto_total': {
                    'desarrollo': 50000,
                    'marketing': 25000,
                    'legal': 15000,
                    'operaciones': 20000,
                    'contingencia': 10000
                },
                'herramientas': [
                    'Jira/Asana para gestión de proyecto',
                    'Figma para diseño',
                    'GitHub para desarrollo',
                    'Salesforce para CRM',
                    'HubSpot para marketing',
                    'Slack para comunicación'
                ],
                'infraestructura': [
                    'Servidores cloud (AWS/Azure)',
                    'CDN para distribución',
                    'Base de datos escalable',
                    'Sistema de monitoreo',
                    'Backup y disaster recovery'
                ]
            }
            
            return recursos
            
        except Exception as e:
            logger.error(f"Error definiendo recursos: {str(e)}")
            return {}
    
    async def _generar_timeline_detallado(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generar timeline detallado del proyecto"""
        try:
            fases = plan.get('fases', [])
            timeline = {
                'duracion_total': '6 meses',
                'fechas_clave': [],
                'milestones': [],
                'dependencias_criticas': []
            }
            
            fecha_inicio = datetime.now()
            
            for i, fase in enumerate(fases):
                duracion_semanas = fase.get('duracion_semanas', 4)
                fecha_fin = fecha_inicio + timedelta(weeks=duracion_semanas)
                
                milestone = {
                    'fase': fase['nombre'],
                    'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
                    'duracion': f'{duracion_semanas} semanas',
                    'objetivos': fase['objetivos'],
                    'entregables': fase['entregables']
                }
                
                timeline['milestones'].append(milestone)
                timeline['fechas_clave'].append({
                    'fecha': fecha_fin.strftime('%Y-%m-%d'),
                    'evento': f'Completar {fase["nombre"]}'
                })
                
                fecha_inicio = fecha_fin
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error generando timeline: {str(e)}")
            return {}
    
    async def _generar_checklist_lanzamiento(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar checklist de lanzamiento"""
        try:
            checklist = [
                {
                    'categoria': 'Producto',
                    'items': [
                        {'tarea': 'MVP completamente funcional', 'estado': 'Pendiente'},
                        {'tarea': 'Testing de calidad completado', 'estado': 'Pendiente'},
                        {'tarea': 'Documentación técnica lista', 'estado': 'Pendiente'},
                        {'tarea': 'Sistema de monitoreo activo', 'estado': 'Pendiente'}
                    ]
                },
                {
                    'categoria': 'Legal',
                    'items': [
                        {'tarea': 'Compliance regulatorio verificado', 'estado': 'Pendiente'},
                        {'tarea': 'Términos y condiciones actualizados', 'estado': 'Pendiente'},
                        {'tarea': 'Política de privacidad lista', 'estado': 'Pendiente'},
                        {'tarea': 'Certificaciones de seguridad', 'estado': 'Pendiente'}
                    ]
                },
                {
                    'categoria': 'Marketing',
                    'items': [
                        {'tarea': 'Campañas de lanzamiento preparadas', 'estado': 'Pendiente'},
                        {'tarea': 'Website actualizado', 'estado': 'Pendiente'},
                        {'tarea': 'Materiales de marketing listos', 'estado': 'Pendiente'},
                        {'tarea': 'Analytics configurado', 'estado': 'Pendiente'}
                    ]
                },
                {
                    'categoria': 'Ventas',
                    'items': [
                        {'tarea': 'Equipo comercial entrenado', 'estado': 'Pendiente'},
                        {'tarea': 'CRM configurado', 'estado': 'Pendiente'},
                        {'tarea': 'Procesos de venta definidos', 'estado': 'Pendiente'},
                        {'tarea': 'Pricing finalizado', 'estado': 'Pendiente'}
                    ]
                },
                {
                    'categoria': 'Soporte',
                    'items': [
                        {'tarea': 'Equipo de soporte preparado', 'estado': 'Pendiente'},
                        {'tarea': 'Sistema de tickets configurado', 'estado': 'Pendiente'},
                        {'tarea': 'FAQ y documentación de usuario', 'estado': 'Pendiente'},
                        {'tarea': 'Procesos de escalación definidos', 'estado': 'Pendiente'}
                    ]
                }
            ]
            
            return checklist
            
        except Exception as e:
            logger.error(f"Error generando checklist: {str(e)}")
            return []
    
    def _identificar_tipo_producto(self, producto: str) -> str:
        """Identificar tipo de producto para aplicar template correcto"""
        producto_lower = producto.lower()
        
        if 'onboarding' in producto_lower:
            return 'onboarding'
        elif 'wallet' in producto_lower:
            return 'wallet'
        elif 'kyc' in producto_lower or 'verificacion' in producto_lower:
            return 'kyc'
        elif 'payment' in producto_lower or 'pago' in producto_lower:
            return 'payment'
        else:
            return 'onboarding'  # Default
    
    async def generar_resumen_plan(self, plan: Dict[str, Any]) -> str:
        """Generar resumen ejecutivo del plan"""
        try:
            producto = plan.get('producto', 'Producto')
            pais = plan.get('pais', 'País')
            fases = plan.get('fases', [])
            duracion_total = plan.get('timeline_detallado', {}).get('duracion_total', 'N/A')
            
            resumen = f"""
# Plan de Lanzamiento - {producto}

## 📍 Mercado Objetivo: {pais}
## ⏱️ Duración Total: {duracion_total}

## 📋 Fases del Proyecto
"""
            
            for fase in fases:
                resumen += f"""
### {fase['nombre']}
- **Duración**: {fase['duracion_semanas']} semanas
- **Objetivos**: {', '.join(fase['objetivos'][:2])}
- **Entregables**: {', '.join(fase['entregables'][:2])}
"""
            
            resumen += f"""
## 👥 Equipos Involucrados
- Producto: {len(plan.get('tareas_por_equipo', {}).get('Producto', []))} tareas
- Tecnología: {len(plan.get('tareas_por_equipo', {}).get('Tecnología', []))} tareas
- Legal: {len(plan.get('tareas_por_equipo', {}).get('Legal', []))} tareas
- Ventas: {len(plan.get('tareas_por_equipo', {}).get('Ventas', []))} tareas
- Marketing: {len(plan.get('tareas_por_equipo', {}).get('Marketing', []))} tareas

## 📊 Indicadores de Éxito
- MRR Objetivo: {plan.get('indicadores', {}).get('negocio', {}).get('mrr_objetivo', 'N/A')}
- Adopción Objetivo: {plan.get('indicadores', {}).get('mercado', {}).get('adopcion_objetivo', 'N/A')}
- Satisfacción Cliente: {plan.get('indicadores', {}).get('mercado', {}).get('satisfaccion_cliente', 'N/A')}

## ⚠️ Riesgos Principales
"""
            
            riesgos = plan.get('riesgos', [])
            for riesgo in riesgos[:3]:
                resumen += f"- {riesgo.get('riesgo', 'Riesgo')} (Prob: {riesgo.get('probabilidad', 'N/A')}, Impacto: {riesgo.get('impacto', 'N/A')})\n"
            
            resumen += f"""
## 💰 Presupuesto Estimado
- Total: USD {sum(plan.get('recursos', {}).get('presupuesto_total', {}).values()):,}
- Desarrollo: USD {plan.get('recursos', {}).get('presupuesto_total', {}).get('desarrollo', 0):,}
- Marketing: USD {plan.get('recursos', {}).get('presupuesto_total', {}).get('marketing', 0):,}

## ✅ Próximos Pasos
1. Revisar y aprobar plan
2. Asignar recursos y equipo
3. Iniciar fase de investigación
4. Establecer reuniones de seguimiento semanales
"""
            
            return resumen
            
        except Exception as e:
            logger.error(f"Error generando resumen del plan: {str(e)}")
            return "Error generando resumen del plan"

# Función de utilidad
def get_planner_producto() -> PlannerProducto:
    """Obtener instancia del planner de producto"""
    return PlannerProducto() 