# SSH Manager App

Interfaz gráfica de [sshmanager](https://github.com/superc839e/sshmanager): servidores SSH guardados, dos paneles (tu PC y el servidor) con **arrastrar y soltar**, fila de transferencias y consola. Funciona en Windows y Linux.

*Graphical interface for [sshmanager](https://github.com/superc839e/sshmanager): saved SSH servers, two panels (your PC and the server) with **drag and drop**, a transfer queue and a console. Works on Windows and Linux.*

## Instalar / Install

**Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/superc839e/sshmanagerapp/main/instalar_linux.sh | bash
```
**Windows** (CMD o PowerShell)
```bat
curl.exe -L -o instalar_windows.bat https://raw.githubusercontent.com/superc839e/sshmanagerapp/main/instalar_windows.bat
.\instalar_windows.bat
```
Las dependencias (PySide6, paramiko) se descargan solas y los errores comunes de descarga se corrigen automáticamente. En Linux avisa si falta alguna librería del sistema y te da el comando exacto.

## Uso / Usage

| Comando | Qué hace |
|---|---|
| `sshmanagerapp` | Abre la app |
| `sshmanagerapp --connect NOMBRE` | Abre y conecta a un servidor guardado |
| `sshmanagerapp --tui [NOMBRE]` | Abre sshmanager (terminal) |
| `sshmanagerapp -u` | Actualiza desde GitHub |
| `sshmanagerapp -d` | Desinstala (no toca tus servidores) |
| `sshmanagerapp -l es\|en` | Cambia el idioma |
| `sshmanagerapp --doctor` / `--repair` | Diagnostica / repara problemas comunes |
| `sshmanagerapp -h [es\|en]` | Manual |

## Conexión con sshmanager / Link with sshmanager

La app y la terminal comparten **servidores, fila de transferencias e idioma**. Si ambas están abiertas se avisan al instante de los cambios; desde la terminal pulsa `g` para abrir la app, y desde la app usa **Terminal** para abrir sshmanager.

*Both apps share **servers, transfer queue and language**. When both are open they notify each other instantly; press `g` in the terminal to open the app, and use **Terminal** in the app to open sshmanager.*

## Archivos / Files

`sshmanagerapp.py` (la app), `instalar_linux.sh`, `instalar_windows.bat`. El núcleo (`sshmanager_core.py`) viene de [sshmanager](https://github.com/superc839e/sshmanager).
