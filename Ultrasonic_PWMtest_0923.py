import RPi.GPIO as gpio
import time
import math

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)

LeftGoPin = 7
LeftBackPin = 11
RightGoPin = 13
RightBackPin = 15
MoterPin = 12
TriggerPin = 16
EchoPin = 18
DelayTime = 250

gpio.setup(LeftGoPin, gpio.OUT)     # left go
gpio.setup(LeftBackPin, gpio.OUT)   # left back
gpio.setup(RightGoPin, gpio.OUT)    # right go
gpio.setup(RightBackPin, gpio.OUT)  # right back
gpio.setup(MoterPin, gpio.OUT)
gpio.setup(TriggerPin, gpio.OUT)
gpio.setup(EchoPin, gpio.IN)

# Initialize PWM for output pins
pwm_moter = gpio.PWM(MoterPin, 50)    # Initialize PWM on pwmPin 50Hz frequency(for ultrasound)  1/50 =  0.02 = 20 ms
LeftGo_pwm = gpio.PWM(LeftGoPin, 100)
LeftBack_pwm = gpio.PWM(LeftBackPin, 100)
RightGo_pwm = gpio.PWM(RightGoPin, 100)
RightBack_pwm = gpio.PWM(RightBackPin, 100)

pwm_moter.start(7.5)                # start the PWM on 7.5% duty cycle (duty cycle value can be 0.0 to 100.0%, floats are OK)
LeftGo_pwm.start(0)
LeftBack_pwm.start(0)
RightGo_pwm.start(0)
RightBack_pwm.start(0)

def nonstop_go( delay ) :
    LeftGo_pwm.ChangeDutyCycle(80)
    LeftBack_pwm.ChangeDutyCycle( 0 )
    RightGo_pwm.ChangeDutyCycle(80)
    RightBack_pwm.ChangeDutyCycle( 0 )
    time.sleep( delay )
    print("nonstop" , delay)
    

def go( delay ) :
    #print ("delay" ,delay)
    start = time.time()
    LeftGo_pwm.ChangeDutyCycle(80)
    LeftBack_pwm.ChangeDutyCycle( 0 )
    RightGo_pwm.ChangeDutyCycle(80)
    RightBack_pwm.ChangeDutyCycle( 0 )
    end = time.time()
    carStop = False
    while end-start < delay and carStop == False :
        distance = GetDistance()  # get front distance
        print ("GOfront distance" ,distance)
        if distance < 18 :
            stop(10)
            carStop = True
        end = time.time()
    return end -start    
    #time.sleep(delay)

def stop( delay ) :
    LeftGo_pwm.ChangeDutyCycle( 0 )
    LeftBack_pwm.ChangeDutyCycle( 0 )
    RightGo_pwm.ChangeDutyCycle( 0 )
    RightBack_pwm.ChangeDutyCycle( 0 )
    time.sleep( float(delay/1000) )
    print( "stop" )

def back( delay ) :
    LeftGo_pwm.ChangeDutyCycle( 0 )
    LeftBack_pwm.ChangeDutyCycle(50)
    RightGo_pwm.ChangeDutyCycle( 0 )
    RightBack_pwm.ChangeDutyCycle(50)
    time.sleep( delay )
    print("back")

def right( delay ) : 
    LeftGo_pwm.ChangeDutyCycle(100)
    LeftBack_pwm.ChangeDutyCycle( 0 )
    RightGo_pwm.ChangeDutyCycle( 0 )
    RightBack_pwm.ChangeDutyCycle(50)
    print("right")
    time.sleep( delay )

def left( delay ) :
    LeftGo_pwm.ChangeDutyCycle( 0 )
    LeftBack_pwm.ChangeDutyCycle(50)
    RightGo_pwm.ChangeDutyCycle(100)
    RightBack_pwm.ChangeDutyCycle( 0 )
    print( "left" )
    time.sleep( delay )

def MoterTurn( value ) :

    a = value                            # duty cycle
    if a >= 2.5 and a <= 12 :
        pwm_moter.ChangeDutyCycle( a )    # change the duty cycle to a% 
        time.sleep(0.01)
    else :
        print ("error" , a)

def SendTrigger() :
    gpio.output(TriggerPin, True)
    time.sleep(0.01)
    gpio.output(TriggerPin, False)

def WaitEcho(value, timeout) :
    count = timeout
    while gpio.input(EchoPin) != value and count > 0 :
        count = count - 1

def GetDistance() :
    SendTrigger()
    WaitEcho(True, 5000)
    start = time.time()
    WaitEcho(False, 5000)
    finish = time.time()
    PulseLen = finish - start
    distance = PulseLen * 340 * 100 / 2
    return (distance)
    
    
def have_front_space(listDist, start, end) :
    while start < end :
        if (start % 4 == 1) or (start % 4 == 2):
            if listDist[start] < 60 :
                return False
        start = start + 1
    
    return True

def Find_listDist_min(start, end):
    i = start
    j = start + 1
    min = i
    
    while j < end :
        if listDist[j] < listDist[i] :
            i = j
            min = i
        j = j + 1
    
    return min

def find_goalX(start):
    # x1: right, x2: left
    if listDist[start+1] <= 40:     # right deg(30) has obstacle
        x1 = listX[start+1]
    elif listDist[start+1] > 40:    # right deg(30) has no obstacle
        if listDist[start] <= 40:   # right deg(60) has obstacle
            x1 = listX[start]
        else:                       # right deg(60) has no obstacle
            x1 = listX[start+1]
            
    if listDist[start+2] <= 40:     # left deg(30) has obstacle
        x2 = listX[start+2]    
    elif listDist[start+2] > 40:    # left deg(30) has no obstacle
        if listDist[start+3] <= 40: # left deg(60) has obstacle
            x2 = listX[start+3]
        else:                       # left deg(60) has no obstacle
            x2 = listX[start+2]
    return(x1 + x2)/2


def GetCheckTurn(goalX, degree):
    if goalX > 0:
        right(1/90*degree)
        Turn = (1/90*degree)
    elif goalX<0:
        left(1/90*degree)
        Turn = -(1/90*degree)
    return Turn


def Back_to_original_direct():
    motor_right = 0.05*50+0.19*50*(70)/180
    right_front = GetDistance()
    motor_left = 0.05*50+0.19*50*(110)/180
    left_front = GetDistance()
    if right_front <= 20 and left_front <= 20 :
        back(0.001)
        if CheckTurn > 0:
            left(CheckTurn)
        else:
            right(CheckTurn)
    else:
        
        if CheckTurn > 0:
            left(CheckTurn)
        else:
            right(CheckTurn)
        
    
        
ShortestAngleLeft = 0
ShortestAngleRight = 0
ShortestDistLeft = 0
ShortestDistRight = 0
distance = 0
Dist = 0
CannotRight = False
CannotLeft = False
     
distance = 0
CheckBack = False
CannotGo = False
CheckTurn = 0  # + right - left
RightDirect = False

total_turn = 0
SPEED = 19.75
DEGREE = 120
GOAL = 60
side_dist = 0
carX = 0
carY = 0
listX = []
listY = []
listDist = []
listDegree = []
listAll = -1
listNow = 0
MaplistX = []
MaplistY = []

'''
if 0 <= DEGREE and DEGREE <= 90:
    right(1/90*DEGREE)
    #print("lala")
else:
    left(1/90*(DEGREE-90) )
'''
while True :                  # 39.5/2    19.75 cm/sec
    stop(50 )
          
    ShortestDist = 0
    CannotRight = False
    CannotLeft = False 
    PreviousDist = distance
      
    #time.sleep(1)
    MoterTurn(2.5)
    time.sleep(1)
    RightDistance = GetDistance() # get right distance
    print ("Right distance" ,RightDistance)
    
    Angle = 30 #  shortest angle
    
    while Angle < 90 :
        MoterTurnAngle = 0.05*50+0.19*50*(Angle)/180   
        #edge = 10/math.sin(math.pi/(180/Angle))
        MoterTurn(MoterTurnAngle)
        time.sleep(1)
        Dist = GetDistance()
        
        listX.append( Dist*math.sin(math.pi/(180/Angle)) )
        listY.append( Dist*math.cos(math.pi/(180/Angle)) )
        MaplistX.append( Dist*math.sin(math.pi/(180/Angle)) + CarX )
        MaplistY.append( Dist*math.cos(math.pi/(180/Angle)) + CarY )

        listDist.append ( Dist )
        listDegree.append ( Angle ) 
        listNow = listNow + 1
        print("Right", Angle, ": ", Dist)
        Angle = Angle + 30  
            
        if ShortestDist == 0 or ShortestDist > Dist:
            ShortestDist = Dist
        
        #print("RightShortestDistLeft" ,Dist )
        #print("RightEdge", edge)
        #print("RightMoterTurnAngle" , Angle)
        '''
        if( Dist < 15) :
            CannotRight = True
            ShortestAngleRight = Angle
            ShortestDistRight = Dist
        Angle = Angle + 30
        '''
    
    MoterTurn(7.25)             # moter turn to middle
    time.sleep(1)
    distance = GetDistance()  # get front distance
    print ("front distance" ,distance)
    
   
    Angle = 120  #  angle   150 120 

    while Angle < 180 and CannotLeft == False:
        MoterTurnAngle = 0.05*50+0.19*50*(Angle)/180   
        #edge = 10/math.sin(math.pi/(180/Angle))
        MoterTurn(MoterTurnAngle)
        time.sleep(1)
        Dist = GetDistance()
        
        listX.append ( Dist*math.sin(math.pi/(180/Angle)) )
        listY.append ( Dist*math.cos(math.pi/(180/Angle)) )
        MaplistX.append( Dist*math.sin(math.pi/(180/Angle)) + CarX )
        MaplistY.append( Dist*math.cos(math.pi/(180/Angle)) + CarY )

        listDist.append ( Dist )
        listDegree.append( Angle ) 
        listNow = listNow + 1
        print("Left", Angle, ": ", Dist)
        Angle = Angle + 30
        
        if ShortestDist == 0 or ShortestDist > Dist:
            ShortestDist = Dist
        #print("LeftShortestDistLeft" ,Dist )
        #print("LeftEdge", edge)
        #print("LeftMoterTurnAngle" , Angle)
        '''
        if( Dist < 15 ) :
            CannotLeft = True
            ShortestAngleLeft = Angle
            ShortestDistLeft = Dist
        else :
            Angle = Angle + 30 
        '''
    
    MoterTurn(12)
    time.sleep(1)
    LeftDistance = GetDistance() # get left distance
    print ("Left distance" ,LeftDistance)
    
    MoterTurn(7.25)             # moter turn to middle
    time.sleep(1)
    
    Direct = True
    
    
    
    '''
    if (CheckTurn > 0 and RightDirect == True and side_dist < 0 ) or (CheckTurn < 0 and RightDirect == True and side_dist > 0 ):
        CheckTurn = 0
        RightDirect = False
    '''
    '''
    if CheckTurn > 0 and RightDirect == True : #and side_dist > 0:
        if LeftDistance > 10 or ShortestDistLeft > 10 :
            RightDirect = False
            
            if side_dist > 0:
                left(0.8+CheckTurn)
                print( "CheckTurn " , CheckTurn)
                stop(100)
                Dist = GetDistance()
                time.sleep(1) 
                if Dist < abs(side_dist) :
                    go_time = go(Dist)
                else :
                    go_time = go(abs(side_dist))
                side_dist = side_dist - (go_time*SPEED)
            
                right(0.9)
            else :
                left(CheckTurn)
            CheckTurn = 0
            Direct = False
            
    elif CheckTurn < 0 and RightDirect == True :#and side_dist < 0:
        if RightDistance > 10 and ShortestDistRight > 10 :
            if side_dist < 0:
                right(0.8+(CheckTurn*-1))
                stop(100)
                Dist = GetDistance()
                time.sleep(1)
                if Dist < abs(side_dist) :
                    go_time = go(Dist)
                else :
                    go_time = go(abs(side_dist))
                print( "side_dist " , side_dist )
                side_dist = side_dist + (go_time*SPEED)
                left(0.9)
            else:
                right(CheckTurn*-1)
            CheckTurn = 0
            RightDirect = False
            Direct = False
    '''
    '''
    if (distance < 15 or CheckBack == True )  and Direct == True:
        stop(0.1)
        CannotGo = True
        if LeftDistance <= 10 and RightDistance <= 10 :  # cannot back fist
            CheckBack= True
            back(0.000000001)   # front distance*1/4  PreviousDist/SPEED/16
            
        else :
            if CheckBack == False :   # last step is not back
                back(0.000000001)  #PreviousDist/SPEED/25
                
            CheckBack = False
       
        
        time.sleep(1)
    '''   
    listcur = listNow - 4         
    if distance < 15:
        if LeftDistance <= 10 and RightDistance <= 10 :  # cannot back fist
            #CheckBack= True
            back(0.000000001)   # front distance*1/4  PreviousDist/SPEED/16   
        else :
            back(0.000000001)  #PreviousDist/SPEED/25    
    
    if ( distance > 60 ) and (have_front_space(listDist, listcur, listNow) == True) :
        go_time = go(distance /SPEED/2)
        carY = carY + go_time*SPEED
        print("(", carX, ",", carY, ")")    
            
    elif distance <= 60 or (have_front_space(listDist, listcur, listNow) == False) :       
        min = Find_listDist_min(listcur, listNow) # min = the position of minimun dist
        goalY =  listDist[min]*math.cos(math.pi/(180/listDegree[min])) 
        goalX = find_goalX(listcur)
        absX = abs( goalX)
        absY = abs( goalY)
        degree = math.degrees(math.atan(absX/absY))
        hypotenuse = math.pow((math.pow(absX, 2) + math.pow(absY, 2)), 0.5)
            
        CheckTurn = GetCheckTurn(goalX, degree)
        go_time = go(hypotenuse/SPEED)
        carY = carY + (SPEED*go_time) * math.cos(math.pi*degree/180)
        if goalX < carX :
            carX = carX - (SPEED*go_time) * math.sin(math.pi*degree/180)
        else :
            carX = carX + (SPEED*go_time) * math.sin(math.pi*degree/180)
        #Back_to_original_direct() 
        
        
    elif LeftDistance >= RightDistance :
        left(1)
        CheckTurn = CheckTurn-1
        
    else :
        right(1)
        CheckTurn = CheckTurn+1
        
    '''                
    if CheckBack == False and Direct == True:   
        if CannotGo == False :#and distance >= 40 or (distance >= LeftDistance and distance >= RightDistance )) :

    
            print("Find")
            if CannotRight == True :
                print("main right nonono")
            if CannotLeft == True  :
                print("main left nonono")
                
            if CannotRight == False and CannotLeft == False :
                print("!!!!!!!!!CheckTurn", CheckTurn )
                if CheckTurn == 0 :
                    if ShortestDist < 70 :
                        go_time = go(ShortestDist*2 /SPEED/3)
                        GOAL = GOAL - go_time*SPEED
                        print ("goShortest" , ShortestDist )
                    else :
                        go_time = go(distance*3/SPEED/4)
                        GOAL = GOAL - go_time*SPEED
                        print ("go" , distance)
                elif CheckTurn > 0 :
                    theta = (90)*CheckTurn
                    go_time = go(ShortestDistLeft/SPEED)
                    GOAL = GOAL - (go_time*SPEED*math.cos(math.pi*(theta/180)))
                    side_dist = side_dist + (go_time*SPEED*math.sin(math.pi*(theta/180)))
                    print ("goDistLeft" ,ShortestDistLeft)
                    RightDirect = True
                else :
                    theta = (90)*(-CheckTurn)
                    go_time = go(ShortestDistRight/SPEED)
                    GOAL = GOAL - (go_time*SPEED*math.cos(math.pi*(theta/180)))
                    side_dist = side_dist - (go_time*SPEED*math.sin(math.pi*(theta/180)))
                    print ("goDistRight" , ShortestDistRight)
                
                    RightDirect = True
                
            elif CannotRight == True and CannotLeft == True :
                if LeftDistance >= RightDistance :
                    left(0.6)
                    CheckTurn = CheckTurn-0.6
                else :
                    right(0.6)
                    CheckTurn = CheckTurn+0.6
                CannotLeft = False
                CannotRight = False
                    
            elif CannotRight == True :
                if ShortestAngleRight == 40 :
                    left(0.15)    #0.35 is about degree 30
                    CheckTurn = CheckTurn-0.15
                elif ShortestAngleRight == 70 :
                    left(0.25)
                    CheckTurn = CheckTurn-0.25
        
                CannotRight = False
            else :
                if ShortestAngleLeft == 110 :
                    right(0.25)
                    CheckTurn = CheckTurn+0.25
                elif ShortestAngleLeft == 140 :
                    right(0.15)
                    CheckTurn = CheckTurn+0.15
                CannotLeft = False
                
              
        elif LeftDistance >= RightDistance :
            left(1)
            CheckTurn = CheckTurn-1
            if CannotGo == True :
                CannotGo = False
        else :
            right(1)
            CheckTurn = CheckTurn+1
            if CannotGo == True :
                CannotGo = False
    '''            
    
    
    
    
    
    
    
 #   if distance > 30 :
   #     go(distance/19.75/2)
   #     print ("go")
        
   # if distance <= 10 :       # front distance <= 10cm turn back
    #    stop(0.1)
   #     back(0.2)
   # if distance <= 30 :        # front distance < 25cm get left and right distan$
  #      stop(100)
  #      MoterTurn(11)
   #     RightDistance = GetDistance() # get right distance
  #      time.sleep(1)
  #      MoterTurn(4)
  #      LeftDistance = GetDistance() # get left distance
  #      time.sleep(1)
  #      if LeftDistance < 10 and RightDistance < 10 :
  #          back(0.5)
  #      elif LeftDistance > RightDistance :
  #          left(0.5)
  #      else :
  #          right(0.5)
 #       stop(0.1)





