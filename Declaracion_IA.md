# Declaración sobre el uso de inteligencia artificial generativa

Sí utilicé inteligencia artificial generativa en esta prueba. Usé Claude como asistente durante todo el desarrollo y Github Copilot propio de Visual Code para completaciones redundantes. A continuación describo en qué partes la usé, con qué propósito y qué hice yo.

## En qué partes usé IA

**Análisis y planeación**
- Le pedí a la IA que me ayudara a analizar el enunciado, identificar aspectos que se me escaparan del análisis inicial. Tener en cuenta que los archivos .csv nunca fueron entregados por seguridad de la información.

**Backend (Python)**
- El código de lectura de archivos (`read_csv.py`), el motor de reglas (`conciliator.py`) y las 30 pruebas automáticas fueron generados con IA a partir de los supuestos que definí.
- El archivo de `causas.py` fue un archivo que generé con IA a partir del readme inicial de los supuestos creados para que quedara con mejor manejo que etiqueta de error iba a salir en cada caso y aquí podría consultar si su origen era de calculo, formato o de regla contable

**Frontend (Angular)**
- La IA generó el código de los componentes según los parámetros de las causas que le dicté, el servicio que consume la API, los modelos y los estilos fueron pasados por mí de cada componente de bancolombia que me gustara, para que lo realizara similar.


**Documentación**
- La usé para organizar y redactar el README a partir de mis supuestos y de los resultados obtenidos y el código dentro del Visual Studo Code y para dar forma a esta declaración.
- La estructura de la presentación partió de una propuesta de la IA.

## Lo que hice yo

- **Revisar los archivos de prueba.** Realicé una revisión previa en excel para definir las reglas básicas y tener un resultado manual antes de realizar la programación para comparar al final de las pruebas, comprendí los archivos de prueba e identifiqué los casos que traían: duplicados, campos vacíos, facturas sin contabilizar, estados pendientes, diferencias de cálculo y registros contables en cero.

- **Definí los supuestos de negocio.** Decidí cómo tratar los estados pendientes, los registros en cero, los duplicados y los cambios de periodo, y qué tarifas se consideran válidas. La IA me ayudó a organizarlos y redactarlos de una manera más organizada en el Readme pero las decisiones y supuestos fueron tomadas por mí.
- **Revisé y cuestioné los resultados.** Por ejemplo, la propuesta inicial trataba los registros contables sin factura como una simple advertencia. Consideré que la conciliación debía hacerse en ambas direcciones y lo cambié a inconsistencia. También noté que las facturas duplicadas mostraban causas distintas, lo analicé y organicé para que el detalle indicara en qué otra fila aparece el duplicado.
- **Integré y ejecuté la solución en mi equipo.** Configuré el entorno, organicé el repositorio, corrí las pruebas, verifiqué los resultados en pantalla con los archivos de prueba y comprobé que coincidieran con lo esperado.
- **Revisé el código para entenderlo.** Puedo explicar el funcionamiento de cada regla, el flujo entre Angular y Python y las decisiones técnicas tomadas.
- **Contenido de la presentación.** El contenido, las imágenes y la organizacion fueron realizadas por mi persona, la IA solo realizó la estructura inicial del titulo de cada diapositiva.