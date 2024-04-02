REM bpython set_output.py DA1=-6.2

REM python set_output.py --com 14 DA4=0.333 DA5=0.533 DA10=9.976

:loop

python ../set_output.py DA1=-5.0 DA2=-5.0 DA3=-5.0 DA4=-5.0 DA5=-5.0 DA6=-5.0 DA7=-5.0 DA8=-5.0 DA9=-5.0 DA10=-5.0

timeout /t 3
goto loop
 
 
pause