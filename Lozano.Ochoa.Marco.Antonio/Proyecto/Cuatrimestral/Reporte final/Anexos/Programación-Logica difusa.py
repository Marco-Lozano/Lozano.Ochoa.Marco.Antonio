import numpy as np          			         #Libreria para utilizar funciones matematicas
import skfuzzy as fuzz    				 #Libreria para el control difuso
import time                				 #Libreria para controlar el reloj del procesador
import RPi.GPIO as GPIO    		 		 #Libreria para utilizar los pines gpio
import serial               		 		 #Libreria para utilizar puerto serial

frdm = serial.Serial('/dev/ttyACM0', baudrate=57600, timeout=1.0)   #Configuracion del puerto serial en variable frdm

GPIO.setwarnings(False)                                  #Desactivacion de las alertas
GPIO.setmode(GPIO.BCM)		
GPIO.setup(12, GPIO.OUT)				 #Se asignan la funcion de los pines como salida
pwm1 = GPIO.PWM(12, 100)                                 #De tipo pwm
GPIO.setup(13, GPIO.OUT)                                                                  
pwm2 = GPIO.PWM(13, 100)
GPIO.setup(16, GPIO.OUT)
pwm3 = GPIO.PWM(16, 100)

while True:

    vals = [0]*3                                               #Vector para guardar datos del serial
    for i in range(3):                                         #Inicio del ciclo for
        vals[0] = frdm.readline()                              #Lectura del primer potenciometro
        vals[1] = frdm.readline()                              #Lectura del segundo potenciometro
        vpot1 = vals[0]                                	  #El vector se guarda en otra variable
        vpot2 = vals[1]
    spot1 = float(vpot)                                    #El dato se convierte a flotante
    spot2 = float(vldr)
    pot1 = spot1*0.98                                       #Se multiplica para no desbordar el valor desfuzzificado
    pot2 = spot2*0.98
    
    time.sleep(0.05)  					#Retraso de 50 ms
    pot1_x = np.arange(0, 5.05, 0.1)                    		#Se crea vector para especificar el rango en x
    pot2_x = np.arange(0, 5.05, 0.1)
    intensidad_led_x = np.arange(0, 5.05, 0.1)
    
    voltaje_pot1_lo     = fuzz.trimf(pot1_x, [0,0,2.5])              #Se fuzzifican las variables de entrada y salida
    voltaje_pot1_md     = fuzz.trimf(pot1_x, [0,2.5,5])
    voltaje_pot1_hi     = fuzz.trimf(pot1_x, [2.5,5,5])
    voltaje_pot2_lo   = fuzz.trimf(pot2_x, [0,0,2.5])
    voltaje_pot2_md   = fuzz.trimf(pot2_x, [0,2.5,5])
    voltaje_pot2_hi   = fuzz.trimf(pot2_x, [2.5,5,5])
    intensidad_led_lo  = fuzz.trimf(intensidad_led_x,[0,0,2.5])
    intensidad_led_md  = fuzz.trimf(intensidad_led_x,[0,2.5,5])
    intensidad_led_hi  = fuzz.trimf(intensidad_led_x,[2.5,5,5])
    
    voltaje_pot1_nivel_lo = fuzz.interp_membership(pot1_x,voltaje_pot1_lo, pot1)     	 #Se hace la lectura en las funciones
    voltaje_pot1_nivel_md = fuzz.interp_membership(pot1_x,voltaje_pot1_md, pot1)      	 #de pertenencia
    voltaje_pot1_nivel_hi = fuzz.interp_membership(pot1_x,voltaje_pot1_hi, pot1)
    voltaje_pot2_nivel_lo = fuzz.interp_membership(pot2_x,voltaje_pot2_lo, pot2)
    voltaje_pot2_nivel_md = fuzz.interp_membership(pot2_x,voltaje_pot2_md, pot2)
    voltaje_pot2_nivel_hi = fuzz.interp_membership(pot2_x,voltaje_pot2_hi, pot2)

    active_rule1 = np.fmin(voltaje_pot_nivel_lo,voltaje_foto_nivel_lo)           	#Se crean las reglas de comportamiento
    control_activation_1 = np.fmin(active_rule1,intensidad_led_lo)  		#Funcion de numpy para obtener el valor minimo
    
    active_rule2 = np.fmin(voltaje_pot_nivel_lo,voltaje_foto_nivel_md)
    control_activation_2 = np.fmin(active_rule2,intensidad_led_lo)
    
    active_rule3 = np.fmin(voltaje_pot_nivel_lo,voltaje_foto_nivel_hi)
    control_activation_3 = np.fmin(active_rule3,intensidad_led_md)
    
    active_rule4 = np.fmin(voltaje_pot_nivel_md,voltaje_foto_nivel_lo)
    control_activation_4 = np.fmin(active_rule4,intensidad_led_lo)

    active_rule5 = np.fmin(voltaje_pot_nivel_md,voltaje_foto_nivel_md)
    control_activation_5 = np.fmin(active_rule5,intensidad_led_md)
    
    active_rule6 = np.fmin(voltaje_pot_nivel_md,voltaje_foto_nivel_hi)
    control_activation_6 = np.fmin(active_rule6,intensidad_led_hi)
    
    active_rule7 = np.fmin(voltaje_pot_nivel_hi,voltaje_foto_nivel_lo)
    control_activation_7 = np.fmin(active_rule7,intensidad_led_md)
    
    active_rule8 = np.fmin(voltaje_pot_nivel_hi,voltaje_foto_nivel_md)
    control_activation_8 = np.fmin(active_rule8,intensidad_led_hi)
    
    active_rule9 = np.fmin(voltaje_pot_nivel_hi,voltaje_foto_nivel_hi)
    control_activation_9 = np.fmin(active_rule9,intensidad_led_hi)

    c1 = np.fmax(control_activation_1, control_activation_2)        #Funcion de numpy para obtener el valor maximo
    c2 = np.fmax(control_activation_3, control_activation_4)
    c3 = np.fmax(control_activation_5, control_activation_6)
    c4 = np.fmax(control_activation_7, control_activation_8)
    c5 = control_activation_9
    c6 = np.fmax(c2, c3)
    c7 = np.fmax(c3, c4)
    c8 = np.fmax(c4, c5)
    c9 = np.fmax(c5, c6)
    aggregated = np.fmax(c1,c9)

    control_value = fuzz.defuzz(intensidad_led_x,aggregated,'centroid')     #Funcion de scikit para obtener el centroide
    c = control_value-1
    a=c*30                                                                  #Multiplicacion para mandar al pwm
    b=abs(a)								    #Se obtiene el valor absoluto para evitar errores
    if b>0 and b<30:                                        #Si el valor desfuzzificado esta dentro del primer tercio
        pwm1.start(b)                                       #se activa el led verde
        pwm2.start(0)
        pwm3.start(0)
    if b>30 and b<60:                                       #Si esta dentro del segundo se activa el led amarillo
        pwm2.start(b)
        pwm1.start(0)
        pwm3.start(0)
    if b>60 and b<100:                                      #Y dentro del tercero se activa el led rojo
        pwm3.start(b)
        pwm1.start(0)
        pwm2.start(0)
    
    print 'Valor PWM LED: ',b                               #Se imprime el valor del pwm
