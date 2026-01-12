# 🚀 AIVideogen: AVGL Cheat Sheet (v3.0)

Este es su "acordeón" de programación para dirigir videos. AVGL es un lenguaje de marcado basado en **etiquetas estructuradas**.

## 1. El Contenedor Maestro: `<scene>`
Identifica cada bloque de contenido. El `title` genera los capítulos de YouTube.
```xml
<scene title="Título de la Escena">
   ...Contenido de la escena...
</scene>
```

## 2. Disparadores Visuales: `<asset />`
Cambia la imagen/video en cualquier punto. Los efectos son independientes y se mezclan.
- `type`: Nombre del archivo.
- `zoom`: "inicio:fin" (ej: `1.0:1.3`).
- `move`: "TIPO:inicio:fin" (ej: `HOR:0:100`).
- `overlay`: Capa visual (ej: `dust`, `glitch`, `grain`).

```xml
<asset type="imagen.png" zoom="1.0:1.2" move="HOR:0:100" overlay="dust" />
```

## 3. Comandos de Audio Dinámico
- `<sfx type="clic" volume="0.5" />`: Efecto instantáneo.
- `<ambient state="start" type="forest" />`: Inicia loop de ambiente.
- `<ambient state="stop" />`: Detiene el ambiente.
- `<music state="change" type="epic" />`: Cambia el tema de fondo.

## 4. Control de Narrativa
- `<pause duration="1.5" />`: Silencio dramático de X segundos.

---

## 🎬 Ejemplo de "Programación Visual"
```xml
<scene title="La Revelación">
  <asset type="scientist.png" zoom="1.1:1.3" />
  Él lo sabía... <pause duration="0.8" />
  <sfx type="glitch" />
  <asset type="formula.png" zoom="1.0:1.5" overlay="glitch" />
  La fecha es inevitable.
</scene>
```

> [!TIP]
> **Regla de Persistencia**: Un `<asset />` se queda en pantalla hasta que otro lo sustituya, permitiéndole cambiar de imagen incluso en medio de una frase.
