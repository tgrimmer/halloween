import time
import board
import asyncio
from digitalio import DigitalInOut, Direction
import random
import pwmio
from adafruit_motor import servo

######################################################################
# This is the first project I am using CircuitPython. If you find
# something incorrect in the code, please contact me and let me 
# know, what can be done better :-)
######################################################################


# Constants
GlobalAnimationStartLength = 3
GlobalAnimationTime = 5
GlobalAnimationTimeOut = 5
GlobalAnimationHeadStartAngle = 50
GlobalAnimationHeadEndAngle = 0
GlobalAnimationTailIdleAngle = 30
GlobalAnimationTailMinAngle = 60
GlobalAnimationTailMaxAngle = 1

# Motion Sensor
motionSensor = DigitalInOut(board.GP2)
motionSensor.direction = Direction.INPUT

# Sound Pins
soundPin01 = DigitalInOut(board.GP18)
soundPin02 = DigitalInOut(board.GP19)
soundPin03 = DigitalInOut(board.GP20)
soundPin04 = DigitalInOut(board.GP21)
soundPin01.direction = soundPin02.direction = soundPin03.direction = soundPin04.direction = Direction.OUTPUT
soundPin01.value = soundPin02.value = soundPin03.value = soundPin04.value = 1
animationSoundPins = [soundPin02, soundPin03, soundPin04]

# LED Strip
ledStripe = DigitalInOut(board.GP14)
ledStripe.direction = Direction.OUTPUT
ledStripe.value = 0
 
# Motor Head
motorPinHead = pwmio.PWMOut(board.GP6, duty_cycle=2 ** 15, frequency=50)
motorHead = servo.Servo(motorPinHead)
motorHead.angle = GlobalAnimationHeadStartAngle

# Motor Tail
motorPinTail = pwmio.PWMOut(board.GP7, duty_cycle=2 ** 15, frequency=50)
motorTail = servo.Servo(motorPinTail)
motorTail.angle = GlobalAnimationTailIdleAngle



async def flickerIdle(animationTime):
    print("flickerIdle")
    startTime = time.time()
    pause = 0
    while (time.time() - startTime) < animationTime:
        ledStripe.value = 1
        pause = random.randrange(50, 250) / 1000
        await asyncio.sleep(pause)
        ledStripe.value = 0
        pause = random.randrange(5, 75) / 1000
        await asyncio.sleep(pause)
        
        

async def warmUpFlickerAnimation():
    print("warmUpFlickerAnimation")
    startTime = time.time()
    while (time.time() - startTime) < GlobalAnimationStartLength:
        ledStripe.value = 1
        await asyncio.sleep(0.04)
        ledStripe.value = 0
        await asyncio.sleep(0.02)
    ledStripe.value = 1
    
async def flickerAnimation():
    print("flickerActionAnimation")
    startTime = time.time()
    pause = 0
    while (time.time() - startTime) < GlobalAnimationTime:
        ledStripe.value = 1
        pause = random.randrange(10, 250) / 1000
        await asyncio.sleep(pause)
        ledStripe.value = 0
        pause = random.randrange(25, 100) / 1000
        await asyncio.sleep(pause)
        
async def warmUpPlaySound():
    print("warmUpPlaySound")
    soundPin01.value = 0
    await asyncio.sleep(0.1)
    soundPin01.value = 1
    
async def playAnimationStartHead():
    print("playAnimationStartHead")
    startTime = time.time()
    pause = GlobalAnimationStartLength / (GlobalAnimationHeadStartAngle - GlobalAnimationHeadEndAngle)
    #print (("pause => {}").format(pause))
    for angle in range(GlobalAnimationHeadStartAngle, GlobalAnimationHeadEndAngle, -2):
        motorHead.angle = angle
        await asyncio.sleep(pause)
    
    
async def playAnimationSound():
    print("playAnimationSound")
    soundIndex = random.randrange(0, len(animationSoundPins))
    print(("playAnimationSound index => {}").format(soundIndex))
    soundToPlay =  animationSoundPins[soundIndex]
    soundToPlay.value = 0
    await asyncio.sleep(0.1)
    soundToPlay.value = 1

async def playAnimationHead(motorPin, startAngle, endAngle, degrees):
    startTime = time.time()
    forwardDegrees = degrees * (-1)
    while (time.time() - startTime) < GlobalAnimationTime:
        for angle in range(startAngle, endAngle, forwardDegrees):  
            motorPin.angle = angle
            await asyncio.sleep(0.02)
        for angle in range(endAngle, startAngle, degrees):
            motorPin.angle = angle
            await asyncio.sleep(0.02)


async def main():
    lastIdleAnimationTime = time.time()
    ledStripe.value = 1
    
    
    idleAnimationTime = random.randrange(1,5)
    IdleAnimationTimeOut = random.randrange(1,15)
    while True:
        
        pir_value = motionSensor.value
        if pir_value:
            print("motion dected so action!!!")
            # first warmup
            taskWarmUpFlickerAnimation = asyncio.create_task(warmUpFlickerAnimation())
            taskWarmUpPlaySound = asyncio.create_task(warmUpPlaySound())
            taskPlayAnimationStartHead = asyncio.create_task(playAnimationStartHead())
            
            await asyncio.gather(taskWarmUpFlickerAnimation, taskWarmUpPlaySound, taskPlayAnimationStartHead)
            
            # now here comes the agressive part...muhahahaha
            await asyncio.sleep(1)
            
            taskFlickerActionAnimation = asyncio.create_task(flickerAnimation())
            taskPlayAnimationSound = asyncio.create_task(playAnimationSound())
            taskPlayAnimationHead = asyncio.create_task(playAnimationHead(motorHead, GlobalAnimationHeadStartAngle, GlobalAnimationHeadEndAngle, 2))
            taskPlayAnimationTail = asyncio.create_task(playAnimationHead(motorTail, GlobalAnimationTailMinAngle, GlobalAnimationTailMaxAngle, 5))
            
            await asyncio.gather(taskFlickerActionAnimation, taskPlayAnimationSound, taskPlayAnimationHead, taskPlayAnimationTail)
            
            # we are done...so take breath
            ledStripe.value = 0
            motorTail.angle = GlobalAnimationTailIdleAngle
            motorHead.angle = GlobalAnimationHeadStartAngle
            await asyncio.sleep(GlobalAnimationTimeOut)
            ledStripe.value = 1
            lastIdleAnimationTime = time.time()
            
        else:
            if (time.time() - lastIdleAnimationTime) > IdleAnimationTimeOut:
                print("do idle animation")
                taskFlickerIdle = asyncio.create_task(flickerIdle())
                
                await asyncio.gather(taskFlickerIdle)
                idleAnimationTime = random.randrange(1,5)
                IdleAnimationTimeOut = random.randrange(1,15)
                lastIdleAnimationTime = time.time()
                ledStripe.value = 1
                print(("new idleAnimationTime => {}").format(idleAnimationTime))
                print("done")

asyncio.run(main())