# Start / Installation (Windows PowerShell)

Kurze Schritte, um das Projekt lokal zu starten (Windows PowerShell):

1) Virtuelle Umgebung erstellen und aktivieren

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
```

2) Abhängigkeiten installieren

```powershell
py -m pip install -r requirements.txt
```

Hinweis: `requirements.txt` enthält die benötigten Pakete für das gesamte Repo. Falls du nur `Projekt` separat nutzen willst, gibt es auch `Projekt/requirements.txt`.

3) Spiel starten

- Root `game.py` ausführen:

```powershell
py game.py
```

- Oder die Hauptdatei in `Projekt` ausführen:

```powershell
py Projekt\main.py
```

Alternative ohne virtuelle Umgebung (global installieren):

```powershell
py -m pip install --user -r requirements.txt
```

Wenn du Probleme mit `pygame`-Installation hast, poste die Fehlermeldung und ich helfe weiter.

## Pygame-Extensions und 3D-Unterstützung

Wenn du zusätzliche Pygame-Extensions (z.B. Menüs, GUI) oder 3D-Funktionalität brauchst, hier sind empfohlene Pakete und Installationsbefehle.

- Gängige Erweiterungen (Menüs, GUI):

```powershell
py -m pip install pygame-menu pygame_gui
```

- 3D / OpenGL mit `PyOpenGL` (verwende `PyOpenGL-accelerate` optional für Performance):

```powershell
py -m pip install PyOpenGL PyOpenGL-accelerate
```

- Alternative/modernere OpenGL-API: `moderngl` (nützlich für moderne OpenGL-Workflows):

```powershell
py -m pip install moderngl
```

- Alles in einem (falls du alle empfohlenen Erweiterungen installierst):

```powershell
py -m pip install -r requirements.txt pygame-menu pygame_gui PyOpenGL-accelerate moderngl
```

Wichtige Hinweise (Windows):
- Für einige Pakete (oder beim Bauen von Wheels) brauchst du die "Visual C++ Build Tools". Installiere sie falls Fehler wie "Microsoft Visual C++ 14.0 is required" auftreten.
- Wenn `PyOpenGL-accelerate` beim Kompilieren Probleme macht, kannst du zunächst nur `PyOpenGL` installieren; `PyOpenGL-accelerate` ist optional, aber beschleunigt manche OpenGL-Operationen.

Teste, ob eine OpenGL-Kontext-Erstellung funktioniert, indem du das Spiel startest (`py Projekt\main.py`) — wenn das Fenster und die Grafik-Initialisierung funktioniert, ist OpenGL einsatzbereit.

Wenn du möchtest, kann ich eine kleine Testdatei hinzufügen, die ein leeres OpenGL-Fenster mit `pygame` + `PyOpenGL` öffnet, um die Installation zu verifizieren.

## Empfohlener Ein-Kommando-Start (sicher)

Ich habe ein PowerShell-Startskript `run_game.ps1` im Projektroot hinzugefügt, das folgendes sicherstellt:
- Legt bei Bedarf `.venv` an und aktiviert sie
- Installiert `requirements.txt` (mit Fallback zu `pygame-ce`, falls ein Source-Build fehlschlägt)
- Startet automatisch `game.py` oder `Projekt\main.py` (auto-detektiert)

Beispiel (aus Projekt-Root in PowerShell):

```powershell
.\run_game.ps1         # auto-detect und starten
.\run_game.ps1 -Entry Projekt\main.py
```

Das Skript ist nützlich, wenn du eine wiederholbare, sichere Startprozedur willst.

## Neuerungen: Kampf, Spawns, Knockback, Tests

- **Angriffssteuerung:** Leertaste (`SPACE`) löst jetzt eine Nahkampfattacke aus.
- **Gegner-Spawning:** `SpawnManager` spawnt mehrere Gegner um den Spieler; Gegner haben `Health` und `Movement` (für Knockback).
- **Knockback:** Treffer können jetzt Knockback anwenden, sofern die Attack-Komponente `knockback` gesetzt hat.
- **Tests:** Es gibt neue Unit-Tests unter `tests/test_combat.py`. Führe sie mit:

```powershell
py -m pip install -r requirements.txt
py -m pip install pytest
py -m pytest tests/test_combat.py
```

