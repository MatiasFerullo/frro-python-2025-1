# Cartera de Acciones con PyRofex

## Descripción
El proyecto consiste en el desarrollo de una aplicación web que permite a los usuarios gestionar y realizar un seguimiento personalizado de su portafolio de inversiones en acciones.  
La plataforma ofrece la funcionalidad de registrar y almacenar la composición del portafolio dentro de la sesión del usuario, permitiendo el acceso posterior a dicha información en cualquier momento.

## Objetivo
El sistema proporciona un resumen detallado del rendimiento de las inversiones, tanto a nivel general (portafolio completo) como individual (por acción específica), facilitando así el análisis y la toma de decisiones informadas.  
A través de una interfaz intuitiva, el usuario puede visualizar la evolución de su portafolio, identificar tendencias y evaluar el comportamiento de sus activos a lo largo del tiempo.

Esta solución está orientada a inversionistas individuales que deseen centralizar el seguimiento de sus activos de forma práctica, segura y accesible.

## Diagrama Entidad Relación
<img width="741" height="486" alt="CarteraFuturos" src="https://github.com/user-attachments/assets/ceb63486-2111-4bab-8298-f90bcf3d0eb4" />

## Sistema de Alertas Personalizadas
El usuario cuenta con un sistema de alertas configurables por:
- Precio mínimo/máximo de una acción. 
- Cambios súbitos en el valor total del portafolio.  

## Requerimientos Funcionales

### 1. Gestión de Usuario

#### 1.1 Registro de Usuario  
- El sistema debe permitir que un usuario se registre con una cuenta mediante correo electrónico y contraseña.  
- El registro debe incluir una validación de correo electrónico para confirmar la cuenta.

#### 1.2 Inicio de Sesión  
- El usuario debe poder iniciar sesión con su correo electrónico y contraseña.  
- El sistema debe ofrecer una opción para recuperar la contraseña en caso de olvido.

#### 1.3 Cierre de Sesión  
- El sistema debe permitir al usuario cerrar sesión de forma segura.

#### 1.4 Gestión de Sesiones  
- El sistema debe mantener la sesión activa durante un período configurable, sin necesidad de reingresar las credenciales.

### 2. Gestión de Portafolio de Inversiones

#### 2.1 Creación de Portafolio  
- El usuario debe poder crear un portafolio personalizado para gestionar sus inversiones.

#### 2.2 Adición de Acciones  
El usuario debe poder agregar acciones a su portafolio, incluyendo:  
- Nombre de la acción (ticker).  
- Cantidad de acciones adquiridas.  
- Fecha de adquisición.

#### 2.3 Visualización del Portafolio  
El usuario debe poder visualizar un resumen detallado del portafolio, incluyendo:  
- Total invertido.  
- Valor actual del portafolio.  
- Rentabilidad total (porcentaje de ganancia o pérdida).  
- Rentabilidad por acción (para cada activo individual).

#### 2.4 Edición de Acciones  
- El usuario debe poder editar la cantidad de acciones, el precio de compra o eliminar acciones del portafolio.

### 3. Alertas Personalizadas

#### 3.1 Alertas por Precio Mínimo/Máximo  
- El usuario debe poder establecer alertas para notificar cuando el precio de una acción alcance un valor mínimo o máximo definido.

#### 3.2 Alertas por Cambios Súbitos  
- El sistema debe permitir configurar alertas para notificar cambios importantes en el valor total del portafolio, basados en un umbral de variación predefinido.

#### 3.3 Notificaciones de Alertas  
- Las alertas deben enviarse al correo electrónico del usuario y/o mostrarse dentro de la interfaz de usuario como notificaciones en tiempo real.

## Stack Tecnológico

### Base de Datos  
Se usará MySQL debido a su simplicidad y rendimiento aceptable.

### Framework  
Se usará Flask, considerado un microframework que brinda las funcionalidades necesarias para el proyecto.

### API  
Se utilizará PyRofex, la API encargada de alimentar la base de datos.
