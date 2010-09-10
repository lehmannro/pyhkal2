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
REM Redistribute .py files
rmdir /S /Q var\Lib\site-packages\pyhkal-0.0.0-py2.6.egg\pyhkal
xcopy pyhkal var\Lib\site-packages\pyhkal-0.0.0-py2.6.egg\pyhkal /Q /Y /I
xcopy contrib var\Lib\site-packages\pyhkal-0.0.0-py2.6.egg\pyhkal\contrib /Q /Y /I
xcopy test var\Lib\site-packages\pyhkal-0.0.0-py2.6.egg\pyhkal\test /Q /Y /I
python -mcompileall -q var\Lib\site-packages\pyhkal-0.0.0-py2.6.egg\pyhkal
var\Scripts\python var\Scripts\twistd.py -n pyhkal config.yaml
:end
