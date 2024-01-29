REM bpython set_output.py DA1=-6.2

REM python set_output.py --com 14 DA4=0.333 DA5=0.533 DA10=9.976

:loop

python ../set_output.py DA1=-1.0 DA2=-2.0 DA3=-3.0 DA4=-4.0 DA5=-5.0 DA6=-6.0 DA7=-7.0 DA8=-8.0 DA9=-9.0 DA10=-10.0

timeout /t 3

python ../set_output.py DA1=1.0 DA2=2.0 DA3=3.0 DA4=4.0 DA5=5.0 DA6=6.0 DA7=7.0 DA8=8.0 DA9=9.0 DA10=10.0

timeout /t 3

goto loop
 
 
pause