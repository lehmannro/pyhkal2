@echo off
if "%1" == "" goto install
if "%1" == "clean" goto clean
if "%1" == "run" goto run
goto end
:clean
echo removing files..
rmdir /S /Q var
rmdir /S /Q build
rmdir /S /Q dist
del /Q pip-log.txt MANIFEST twistd.pid
goto end
:install
echo installing PyHKAL..
python -mvirtualenv --distribute --no-site-packages "var"
echo [build] > var\pydistutils.cfg && echo compiler = mingw32 >> var\pydistutils.cfg
var\Scripts\python setup.py --quiet install
:run
echo Running PyHKAL..
var\Scripts\python var\Scripts\twistd.py -n pyhkal config.yaml
:end
