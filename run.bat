@echo off
echo.
python grade.py jff/%1.jff jff/%1.json jff/%1.in
python format_for_canvas.py --comments jff