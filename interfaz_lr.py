#!/usr/bin/env python3
"""
Interfaz de Usuario para el Analizador LR Completo
Proporciona una interfaz fácil de usar para ejecutar el flujo completo
"""

import asyncio
import json
import os
from typing import List, Dict, Any
from datetime import datetime

from analizador_lr_completo import AnalizadorLRCompleto

class InterfazLR:
    """
    Interfaz de usuario para el Analizador LR Completo
    """
    
    def __init__(self):
        """Inicializar interfaz"""
        self.analizador = AnalizadorLRCompleto()
        self.proveedores_predefinidos = [
            "Sumsub", "Jumio", "Onfido", "Veriff", "IDnow", 
            "Acuant", "Mitek", "iProov", "B2Broker", "Wallester"
        ]
    
    def mostrar_menu_principal(self):
        """Mostrar menú principal"""
        print("\n" + "="*60)
        print("🤖 ANALIZADOR LR COMPLETO - INTERFAZ DE USUARIO")
        print("="*60)
        print("1. Ejecutar flujo LR completo")
        print("2. Consulta interactiva")
        print("3. Ver proveedores disponibles")
        print("4. Configurar proveedores personalizados")
        print("5. Ver resultados guardados")
        print("6. Salir")
        print("="*60)
    
    def obtener_proveedores(self) -> List[str]:
        """Obtener lista de proveedores a analizar"""
        print("\n📋 PROVEEDORES DISPONIBLES:")
        for i, proveedor in enumerate(self.proveedores_predefinidos, 1):
            print(f"{i}. {proveedor}")
        
        print("\nOpciones:")
        print("a) Usar todos los proveedores predefinidos")
        print("b) Seleccionar proveedores específicos")
        print("c) Ingresar proveedores personalizados")
        
        opcion = input("\nSelecciona una opción (a/b/c): ").lower().strip()
        
        if opcion == 'a':
            return self.proveedores_predefinidos
        elif opcion == 'b':
            return self._seleccionar_proveedores()
        elif opcion == 'c':
            return self._ingresar_proveedores_personalizados()
        else:
            print("Opción inválida, usando proveedores predefinidos")
            return self.proveedores_predefinidos
    
    def _seleccionar_proveedores(self) -> List[str]:
        """Seleccionar proveedores específicos"""
        print("\nSelecciona los números de los proveedores (separados por comas):")
        seleccion = input("Ejemplo: 1,3,5,7: ").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in seleccion.split(',')]
            proveedores = [self.proveedores_predefinidos[i] for i in indices if 0 <= i < len(self.proveedores_predefinidos)]
            return proveedores
        except (ValueError, IndexError):
            print("Selección inválida, usando todos los proveedores")
            return self.proveedores_predefinidos
    
    def _ingresar_proveedores_personalizados(self) -> List[str]:
        """Ingresar proveedores personalizados"""
        print("\nIngresa los nombres de los proveedores (separados por comas):")
        proveedores_input = input("Ejemplo: Sumsub,Jumio,Onfido: ").strip()
        
        if proveedores_input:
            return [p.strip() for p in proveedores_input.split(',') if p.strip()]
        else:
            print("No se ingresaron proveedores, usando predefinidos")
            return self.proveedores_predefinidos
    
    async def ejecutar_flujo_completo(self):
        """Ejecutar el flujo LR completo"""
        print("\n🚀 INICIANDO FLUJO LR COMPLETO")
        print("="*50)
        
        # Obtener proveedores
        proveedores = self.obtener_proveedores()
        
        if not proveedores:
            print("❌ No se seleccionaron proveedores")
            return
        
        print(f"\n📊 Analizando {len(proveedores)} proveedores:")
        for i, proveedor in enumerate(proveedores, 1):
            print(f"  {i}. {proveedor}")
        
        # Confirmar ejecución
        confirmar = input("\n¿Continuar con el análisis? (s/n): ").lower().strip()
        if confirmar != 's':
            print("❌ Análisis cancelado")
            return
        
        try:
            print("\n⏳ Ejecutando flujo LR completo...")
            print("Esto puede tomar varios minutos...")
            
            # Ejecutar flujo
            resultados = await self.analizador.ejecutar_flujo_completo(proveedores)
            
            # Guardar resultados
            filename = self.analizador.guardar_resultados(resultados)
            
            # Mostrar resumen
            if filename:
                self._mostrar_resumen(resultados, filename)
            else:
                print("❌ Error guardando resultados")
            
        except Exception as e:
            print(f"❌ Error ejecutando flujo: {str(e)}")
    
    def _mostrar_resumen(self, resultados: Dict[str, Any], filename: str):
        """Mostrar resumen de resultados"""
        print("\n" + "="*50)
        print("📊 RESUMEN DE RESULTADOS")
        print("="*50)
        
        print(f"✅ Proveedores analizados: {resultados['proveedores_analizados']}")
        print(f"✅ Etapas completadas: {len(resultados['etapas'])}")
        print(f"❌ Errores: {len(resultados['errores'])}")
        print(f"💾 Resultados guardados en: {filename}")
        
        # Mostrar estadísticas por etapa
        if 'etapas' in resultados:
            print("\n📈 ESTADÍSTICAS POR ETAPA:")
            for etapa, datos in resultados['etapas'].items():
                if 'estadisticas' in datos:
                    stats = datos['estadisticas']
                    print(f"  {etapa.upper()}:")
                    for key, value in stats.items():
                        print(f"    {key}: {value}")
        
        # Mostrar errores si los hay
        if resultados['errores']:
            print("\n⚠️  ERRORES ENCONTRADOS:")
            for error in resultados['errores']:
                print(f"  - {error}")
    
    async def consulta_interactiva(self):
        """Realizar consulta interactiva"""
        print("\n💬 CONSULTA INTERACTIVA")
        print("="*30)
        
        print("Ejemplos de consultas:")
        print("- ¿Cuáles son los mejores proveedores de KYC en México?")
        print("- Compara los precios de Sumsub y Jumio")
        print("- ¿Qué tendencias observas en el mercado LATAM?")
        print("- Recomienda proveedores para Argentina")
        
        while True:
            pregunta = input("\nIngresa tu pregunta (o 'salir' para volver): ").strip()
            
            if pregunta.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not pregunta:
                print("❌ Por favor ingresa una pregunta")
                continue
            
            try:
                print("\n🤔 Procesando consulta...")
                respuesta = await self.analizador.consulta_interactiva(pregunta)
                
                print("\n💡 RESPUESTA:")
                print("-" * 30)
                print(respuesta)
                print("-" * 30)
                
            except Exception as e:
                print(f"❌ Error procesando consulta: {str(e)}")
    
    def ver_proveedores_disponibles(self):
        """Mostrar proveedores disponibles"""
        print("\n📋 PROVEEDORES DISPONIBLES")
        print("="*30)
        
        for i, proveedor in enumerate(self.proveedores_predefinidos, 1):
            print(f"{i:2d}. {proveedor}")
        
        print(f"\nTotal: {len(self.proveedores_predefinidos)} proveedores")
    
    def configurar_proveedores_personalizados(self):
        """Configurar proveedores personalizados"""
        print("\n⚙️  CONFIGURAR PROVEEDORES PERSONALIZADOS")
        print("="*40)
        
        print("Proveedores actuales:")
        for i, proveedor in enumerate(self.proveedores_predefinidos, 1):
            print(f"{i}. {proveedor}")
        
        print("\nIngresa nuevos proveedores (separados por comas):")
        nuevos = input("Deja vacío para mantener los actuales: ").strip()
        
        if nuevos:
            self.proveedores_predefinidos = [p.strip() for p in nuevos.split(',') if p.strip()]
            print(f"✅ Proveedores actualizados: {len(self.proveedores_predefinidos)} proveedores")
        else:
            print("ℹ️  Manteniendo proveedores actuales")
    
    def ver_resultados_guardados(self):
        """Ver archivos de resultados guardados"""
        print("\n📁 RESULTADOS GUARDADOS")
        print("="*30)
        
        archivos = [f for f in os.listdir('.') if f.startswith('resultados_lr_') and f.endswith('.json')]
        
        if not archivos:
            print("❌ No se encontraron archivos de resultados")
            return
        
        archivos.sort(reverse=True)  # Más recientes primero
        
        for i, archivo in enumerate(archivos, 1):
            # Obtener información del archivo
            stat = os.stat(archivo)
            fecha = datetime.fromtimestamp(stat.st_mtime)
            tamaño = stat.st_size / 1024  # KB
            
            print(f"{i}. {archivo}")
            print(f"   📅 {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   📊 {tamaño:.1f} KB")
        
        # Opción para ver contenido
        try:
            seleccion = input("\nSelecciona un archivo para ver su contenido (número) o Enter para volver: ").strip()
            if seleccion and seleccion.isdigit():
                indice = int(seleccion) - 1
                if 0 <= indice < len(archivos):
                    self._mostrar_contenido_archivo(archivos[indice])
        except (ValueError, IndexError):
            print("❌ Selección inválida")
    
    def _mostrar_contenido_archivo(self, archivo: str):
        """Mostrar contenido de un archivo de resultados"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            print(f"\n📄 CONTENIDO DE {archivo}")
            print("="*50)
            
            # Mostrar información básica
            print(f"📅 Timestamp: {datos.get('timestamp', 'N/A')}")
            print(f"📊 Proveedores analizados: {datos.get('proveedores_analizados', 0)}")
            print(f"✅ Etapas completadas: {len(datos.get('etapas', {}))}")
            print(f"❌ Errores: {len(datos.get('errores', []))}")
            
            # Mostrar estadísticas finales
            if 'estadisticas' in datos:
                print(f"\n📈 ESTADÍSTICAS FINALES:")
                for key, value in datos['estadisticas'].items():
                    print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"❌ Error leyendo archivo: {str(e)}")
    
    async def ejecutar(self):
        """Ejecutar la interfaz principal"""
        print("🤖 Bienvenido al Analizador LR Completo")
        print("Este sistema implementa el flujo completo: Scraping → Procesamiento → Embeddings → Almacenamiento → Consulta")
        
        while True:
            try:
                self.mostrar_menu_principal()
                opcion = input("\nSelecciona una opción (1-6): ").strip()
                
                if opcion == '1':
                    await self.ejecutar_flujo_completo()
                elif opcion == '2':
                    await self.consulta_interactiva()
                elif opcion == '3':
                    self.ver_proveedores_disponibles()
                elif opcion == '4':
                    self.configurar_proveedores_personalizados()
                elif opcion == '5':
                    self.ver_resultados_guardados()
                elif opcion == '6':
                    print("\n👋 ¡Gracias por usar el Analizador LR Completo!")
                    break
                else:
                    print("❌ Opción inválida, intenta de nuevo")
                
                input("\nPresiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {str(e)}")
                input("Presiona Enter para continuar...")

# Función principal
async def main():
    """Función principal"""
    interfaz = InterfazLR()
    await interfaz.ejecutar()

if __name__ == "__main__":
    asyncio.run(main()) 