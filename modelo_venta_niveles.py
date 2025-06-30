"""
Modelo de venta por niveles basado en datos de Supabase.
Genera propuestas de precios y configuraciones para diferentes niveles de servicio.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import SupabaseManager

class ModeloVentaNiveles:
    """Generador de modelos de venta por niveles."""
    
    def __init__(self):
        """Inicializar el modelo con conexión a Supabase."""
        self.supabase_manager = SupabaseManager()
        
        # Definir niveles de servicio
        self.niveles = {
            1: {
                "nombre": "Wallet Base",
                "descripcion": "Funcionalidad básica de wallet con soporte multi-moneda",
                "modulos_incluidos": ["Wallet Base"],
                "caracteristicas": [
                    "Wallet básico multi-moneda",
                    "Transferencias P2P",
                    "Historial de transacciones",
                    "API básica de integración",
                    "Soporte técnico por email"
                ]
            },
            2: {
                "nombre": "Wallet + Criptoactivos",
                "descripcion": "Wallet avanzado con soporte completo para criptomonedas",
                "modulos_incluidos": ["Wallet Base", "Wallet Avanzado"],
                "caracteristicas": [
                    "Todo del nivel 1",
                    "Soporte para 50+ criptomonedas",
                    "Cold storage integration",
                    "Staking y yield farming",
                    "Análisis de mercado básico",
                    "Soporte técnico prioritario"
                ]
            },
            3: {
                "nombre": "Wallet + Cripto + Tarjeta",
                "descripcion": "Solución completa con tarjetas de débito/crédito",
                "modulos_incluidos": ["Wallet Base", "Wallet Avanzado", "Tarjeta"],
                "caracteristicas": [
                    "Todo del nivel 2",
                    "Tarjetas de débito virtuales",
                    "Tarjetas físicas personalizadas",
                    "Cashback y recompensas",
                    "Integración con Apple Pay/Google Pay",
                    "Soporte 24/7"
                ]
            },
            4: {
                "nombre": "Wallet + Cripto + Tarjeta + KYC/KYB",
                "descripcion": "Solución completa con verificación de identidad",
                "modulos_incluidos": ["Wallet Base", "Wallet Avanzado", "Tarjeta", "KYC/KYB"],
                "caracteristicas": [
                    "Todo del nivel 3",
                    "Verificación de identidad automatizada",
                    "Cumplimiento regulatorio completo",
                    "Reportes de compliance",
                    "Integración con autoridades",
                    "Gestor de cuenta dedicado"
                ]
            },
            5: {
                "nombre": "Full Stack Enterprise",
                "descripcion": "Solución completa enterprise con todos los módulos",
                "modulos_incluidos": ["Wallet Base", "Wallet Avanzado", "Tarjeta", "KYC/KYB", "Trading Platform", "Payment Gateway", "Compliance"],
                "caracteristicas": [
                    "Todo del nivel 4",
                    "Plataforma de trading completa",
                    "Pasarela de pagos multi-método",
                    "Liquidez institucional",
                    "API enterprise completa",
                    "SLA garantizado",
                    "Equipo de implementación dedicado"
                ]
            }
        }
    
    def obtener_precios_mercado(self) -> Dict[str, List[float]]:
        """
        Obtener precios del mercado desde Supabase.
        
        Returns:
            Diccionario con precios por clasificación
        """
        try:
            # Obtener datos analizados por GPT
            response = self.supabase_manager.client.table('precios_modulos').select('*').eq('analizado_gpt', True).execute()
            
            precios_por_clasificacion = {}
            
            for record in response.data:
                clasificacion = record.get('clasificacion_gpt', 'No clasificado')
                precio_gpt = record.get('precio_gpt', 'No especificado')
                
                # Extraer valor numérico del precio
                if precio_gpt and precio_gpt != 'No especificado':
                    try:
                        # Limpiar precio y convertir a número
                        precio_limpio = precio_gpt.replace('$', '').replace(',', '').replace('USD', '').strip()
                        if precio_limpio and precio_limpio != 'No especificado':
                            precio_num = float(precio_limpio)
                            
                            if clasificacion not in precios_por_clasificacion:
                                precios_por_clasificacion[clasificacion] = []
                            
                            precios_por_clasificacion[clasificacion].append(precio_num)
                    except ValueError:
                        continue
            
            return precios_por_clasificacion
            
        except Exception as e:
            print(f"❌ Error obteniendo precios del mercado: {str(e)}")
            return {}
    
    def calcular_precio_nivel(self, nivel: int, precios_mercado: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Calcular precio sugerido para un nivel específico.
        
        Args:
            nivel: Número del nivel
            precios_mercado: Precios del mercado por clasificación
            
        Returns:
            Diccionario con información del nivel y precios
        """
        if nivel not in self.niveles:
            return {}
        
        nivel_info = self.niveles[nivel]
        modulos = nivel_info['modulos_incluidos']
        
        # Calcular costo base sumando precios de módulos
        costos_modulos = []
        for modulo in modulos:
            if modulo in precios_mercado and precios_mercado[modulo]:
                # Usar el precio promedio del módulo
                precio_promedio = sum(precios_mercado[modulo]) / len(precios_mercado[modulo])
                costos_modulos.append(precio_promedio)
            else:
                # Precio estimado si no hay datos del mercado
                precios_estimados = {
                    "Wallet Base": 2000,
                    "Wallet Avanzado": 3500,
                    "Tarjeta": 2500,
                    "KYC/KYB": 3000,
                    "Trading Platform": 8000,
                    "Payment Gateway": 4000,
                    "Compliance": 5000
                }
                costos_modulos.append(precios_estimados.get(modulo, 2000))
        
        costo_base = sum(costos_modulos)
        
        # Aplicar márgenes según el nivel
        margenes = {
            1: 1.5,  # 50% de margen
            2: 1.6,  # 60% de margen
            3: 1.7,  # 70% de margen
            4: 1.8,  # 80% de margen
            5: 2.0   # 100% de margen
        }
        
        precio_sugerido = costo_base * margenes.get(nivel, 1.5)
        
        # Descuentos por volumen
        descuentos = {
            1: 0,    # Sin descuento
            2: 0.05, # 5% descuento
            3: 0.10, # 10% descuento
            4: 0.15, # 15% descuento
            5: 0.20  # 20% descuento
        }
        
        descuento = descuentos.get(nivel, 0)
        precio_final = precio_sugerido * (1 - descuento)
        
        return {
            "nivel": nivel,
            "nombre": nivel_info['nombre'],
            "descripcion": nivel_info['descripcion'],
            "modulos_incluidos": modulos,
            "caracteristicas": nivel_info['caracteristicas'],
            "costo_base": round(costo_base, 2),
            "precio_sugerido": round(precio_sugerido, 2),
            "descuento": f"{descuento * 100}%",
            "precio_final": round(precio_final, 2),
            "margen_estimado": round(((precio_final - costo_base) / precio_final) * 100, 1)
        }
    
    def generar_modelo_completo(self) -> Dict[str, Any]:
        """
        Generar modelo completo de venta por niveles.
        
        Returns:
            Diccionario con el modelo completo
        """
        print("📊 Generando modelo de venta por niveles...")
        
        precios_mercado = self.obtener_precios_mercado()
        
        modelo = {
            "fecha_generacion": datetime.now().isoformat(),
            "resumen_mercado": {
                "total_proveedores": len(set([r.get('fuente') for r in self.supabase_manager.client.table('precios_modulos').select('fuente').execute().data])),
                "total_modulos_analizados": len([r for r in self.supabase_manager.client.table('precios_modulos').select('*').eq('analizado_gpt', True).execute().data]),
                "clasificaciones_disponibles": list(precios_mercado.keys())
            },
            "niveles": {}
        }
        
        for nivel in self.niveles.keys():
            nivel_info = self.calcular_precio_nivel(nivel, precios_mercado)
            if nivel_info:
                modelo["niveles"][nivel] = nivel_info
        
        return modelo
    
    def exportar_modelo(self, formato: str = 'json') -> str:
        """
        Exportar modelo en diferentes formatos.
        
        Args:
            formato: 'json', 'csv', o 'html'
            
        Returns:
            Contenido del archivo exportado
        """
        modelo = self.generar_modelo_completo()
        
        if formato == 'json':
            return json.dumps(modelo, indent=2, ensure_ascii=False)
        
        elif formato == 'csv':
            csv_content = "Nivel,Nombre,Descripción,Costo Base,Precio Sugerido,Descuento,Precio Final,Margen Estimado\n"
            
            for nivel_info in modelo['niveles'].values():
                csv_content += f"{nivel_info['nivel']},\"{nivel_info['nombre']}\",\"{nivel_info['descripcion']}\","
                csv_content += f"{nivel_info['costo_base']},{nivel_info['precio_sugerido']},{nivel_info['descuento']},"
                csv_content += f"{nivel_info['precio_final']},{nivel_info['margen_estimado']}%\n"
            
            return csv_content
        
        elif formato == 'html':
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Modelo de Venta por Niveles</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .nivel { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                    .nivel h3 { color: #333; margin-top: 0; }
                    .precio { font-size: 1.2em; font-weight: bold; color: #2c5aa0; }
                    .caracteristicas { margin-top: 10px; }
                    .caracteristicas ul { margin: 5px 0; }
                </style>
            </head>
            <body>
                <h1>Modelo de Venta por Niveles</h1>
                <p>Generado el: {fecha}</p>
            """.format(fecha=modelo['fecha_generacion'])
            
            for nivel_info in modelo['niveles'].values():
                html_content += f"""
                <div class="nivel">
                    <h3>Nivel {nivel_info['nivel']}: {nivel_info['nombre']}</h3>
                    <p><strong>Descripción:</strong> {nivel_info['descripcion']}</p>
                    <p class="precio">
                        Costo Base: ${nivel_info['costo_base']:,} | 
                        Precio Sugerido: ${nivel_info['precio_sugerido']:,} | 
                        Descuento: {nivel_info['descuento']} | 
                        <span style="color: #28a745;">Precio Final: ${nivel_info['precio_final']:,}</span>
                    </p>
                    <p><strong>Margen Estimado:</strong> {nivel_info['margen_estimado']}%</p>
                    <div class="caracteristicas">
                        <strong>Características:</strong>
                        <ul>
                """
                
                for caracteristica in nivel_info['caracteristicas']:
                    html_content += f"<li>{caracteristica}</li>"
                
                html_content += """
                        </ul>
                    </div>
                </div>
                """
            
            html_content += """
            </body>
            </html>
            """
            
            return html_content
        
        return "Formato no soportado"

def main():
    """Función principal del generador de modelos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generador de modelo de venta por niveles')
    parser.add_argument('--formato', choices=['json', 'csv', 'html'], default='json',
                       help='Formato de exportación')
    parser.add_argument('--output', help='Archivo de salida')
    
    args = parser.parse_args()
    
    print("💰 Generador de Modelo de Venta por Niveles")
    print("=" * 50)
    
    try:
        generador = ModeloVentaNiveles()
        contenido = generador.exportar_modelo(args.formato)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"✅ Modelo exportado a: {args.output}")
        else:
            print(contenido)
            
    except Exception as e:
        print(f"❌ Error generando modelo: {str(e)}")

if __name__ == "__main__":
    main() 