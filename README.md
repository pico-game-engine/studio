# Pico Game Engine Studio
A simple python game engine studio for creating 3D sprites for the Pico Game Engine. 

## Features
- Code editor for creating sprites and editing and viewing generated sprite code.
- 3D viewer to visualize sprites.
- Creator tab with a palette of objects to create sprites with, and a list of created sprites to edit or delete.
- Sprite presets created from previous Pico Game Engine games.
- Export sprite code to be used in the Pico Game Engine (C++ header).

## Installation
1. Clone the repository:
```bash
git clone https://github.com/pico-game-engine/studio.git
```
2. Navigate to the project directory:
```bash
cd studio
```
3. Create a virtual environment and activate it:

Windows:
```bash
python -m venv venv
./venv/Scripts/activate
```
macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
4. Install the required dependencies:
```bash
pip install -r requirements.txt
```
5. Run the application:
```bash
python studio.py
```

Or optionally compile it as an app using PyInstaller:
```bash
pyinstaller PicoGameEngineStudio.spec
```

Then run the executable from the `dist` folder.
