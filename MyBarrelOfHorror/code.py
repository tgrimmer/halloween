import time
import board
import asyncio
import array
from digitalio import DigitalInOut, Direction
import random
import pwmio
from adafruit_motor import servo

######################################################################
#
# This code belongs to the project "My cute barrel of horror"
#
######################################################################


# Constants
GlobalAnimationWakeUpLength = 3
GlobalAnimationLength = 5
GlobalAnimationTimeout = 5
GlobalIdleSmokeAnimationLength = 3;
GlobalIdleSmokeAnimationTimeOut = 60;
GlobalIdleWarningAnimationTimeOut = 30;

# Motion Sensor
motionSensor = DigitalInOut(board.GP2)
motionSensor.direction = Direction.INPUT

# Sound Pins
soundPin01 = DigitalInOut(board.GP7)
soundPin02 = DigitalInOut(board.GP8)
soundPin03 = DigitalInOut(board.GP9)
soundPin04 = DigitalInOut(board.GP10)
soundPin05 = DigitalInOut(board.GP11)
soundPin01.direction = soundPin02.direction = soundPin03.direction = soundPin04.direction = soundPin05.direction = Direction.OUTPUT
soundPin01.value = soundPin02.value = soundPin03.value = soundPin04.value = soundPin05.value = 1
idleSoundPins = [soundPin01, soundPin02]
animationSoundPins = [soundPin03, soundPin04, soundPin05]

# LED Strip
ledStripe = DigitalInOut(board.GP14)
ledStripe.direction = Direction.OUTPUT
ledStripe.value = 0

# Pneumatic Valve
pneumaticValve = DigitalInOut(board.GP20);
pneumaticValve.direction = Direction.OUTPUT
pneumaticValve.value = 0

# Smoke Machine Pin
smokeMachine = DigitalInOut(board.GP21);
smokeMachine.direction = Direction.OUTPUT
smokeMachine.value = 0

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
        
        
async def playFlickerAnimation(animationTime):
    print("warmUpFlickerAnimation")
    startTime = time.time()
    while (time.time() - startTime) < animationTime:
        ledStripe.value = 1
        await asyncio.sleep(0.04)
        ledStripe.value = 0
        await asyncio.sleep(0.02)


async def playWakeUpSound():
    print("playWakeUpSound")
    soundPin01.value = 0
    await asyncio.sleep(0.1)
    soundPin01.value = 1


async def playAnimationSound():
    print("playAnimationSound")
    soundIndex = random.randrange(0, len(animationSoundPins))
    print(("playAnimationSound index => {}").format(soundIndex))
    animationSoundPins[soundIndex].value = 0
    await asyncio.sleep(0.1)
    animationSoundPins[soundIndex].value = 1
    
    
async def enableSmoke(length):
    print("enableSmoke")
    smokeMachine.value = 1
    await asyncio.sleep(length)
    smokeMachine.value = 0


async def playSound(soundPins):
    print("playSound")
    soundIndex = random.randrange(0, len(soundPins))
    print(("playSound index => {}").format(soundIndex))
    soundPins[soundIndex].value = 0
    await asyncio.sleep(0.1)
    soundPins[soundIndex].value = 1
    
async def playWarnAnimation(repeatCount):
    for i in range(0,repeatCount):
        pneumaticValve.value = 1
        await asyncio.sleep(0.2)
        pneumaticValve.value = 0
        await asyncio.sleep(0.2)
        
    
async def main():
    lastAnimationTime = lastIdleSmokeAnimationTime = lastIdleFlickerAnimationTime = lastIdleSoundAnimationTime = lastIdleWarningAnimationTime = time.time()
    
    idleFlickerAnimationLength = random.randrange(1,5)
    idleFlickerAnimationTimeOut = random.randrange(1,15)

    # this counter is added a bit more variance to main animation, so we do not play the full animation every time
    animationDeferrer = random.randrange(0,5)
    currentAninationDeferCounter = 0;
    
    while True:
        
        pir_value = motionSensor.value
        if pir_value and ((time.time() - lastAnimationTime) > GlobalAnimationTimeout):
            print("motion dected so action!!!")
            
            # first warmup and warn the victim
            taskWakeUpFlickerAnimation = asyncio.create_task(playFlickerAnimation(2))
            taskPlayWakeUpSound = asyncio.create_task(playWakeUpSound())            
            await asyncio.gather(taskWakeUpFlickerAnimation, taskPlayWakeUpSound)
            
            # now check defer counter if we should play full animation
            if currentAninationDeferCounter == 0: #>= animationDeferrer:
                print ("Let's get ready to rumble...")
                
                # some warm-up
                await playWarnAnimation(3)
                
                # now here comes the agressive part...muhahahaha
                await asyncio.sleep(10)
                
                # go up
                print("go up")
                taskFlickerActionAnimation = asyncio.create_task(playFlickerAnimation(GlobalAnimationLength))
                taskPlayAnimationSound = asyncio.create_task(playSound(animationSoundPins))
                taskSmoke = asyncio.create_task(enableSmoke(2))
                pneumaticValve.value = 1;
                
                await asyncio.gather(taskFlickerActionAnimation, taskPlayAnimationSound, taskSmoke)
                
                # stay up
                print("stay up")
                ledStripe.value = 1
                await asyncio.sleep(3)
                
                # go down again
                print("go down")
                pneumaticValve.value = 0;
                ledStripe.value = 0
                
                # we are done...so take breath
                await asyncio.sleep(GlobalAnimationTimeout)
                animationDeferrer = random.randrange(0,5)                
                lastAnimationTime = lastIdleSmokeAnimationTime = lastIdleFlickerAnimationTime = lastIdleSoundAnimationTime = lastIdleWarningAnimationTime = time.time()
            else:
                print("nice try...better luck next time...");
                currentAninationDeferCounter+=1;
        
        # we are waiting for the next victim, so play idle animation
        else:
            idleAnimations = []
            if (time.time() - lastIdleFlickerAnimationTime) > idleFlickerAnimationTimeOut:
                print("idle flicker animation begin")
                taskFlickerIdle = asyncio.create_task(flickerIdle(idleFlickerAnimationLength))
                idleAnimations.append(taskFlickerIdle)
                idleFlickerAnimationLength = random.randrange(1,5)
                idleFlickerAnimationTimeOut = random.randrange(5,15)
                lastIdleFlickerAnimationTime = time.time()
                ledStripe.value = 0
                print("idle flicker animation end")
            
            if (time.time() - lastIdleSmokeAnimationTime) > GlobalIdleSmokeAnimationTimeOut:
                print("idle smoke animation begin")
                taskSmokeIdle = asyncio.create_task(enableSmoke(GlobalIdleSmokeAnimationLength))
                idleAnimations.append(taskSmokeIdle)
                lastIdleSmokeAnimationTime = time.time()
                print("idle smoke animation end")
                
            if (time.time() - lastIdleWarningAnimationTime) > GlobalIdleWarningAnimationTimeOut:
                print("idle warning animation begin")
                taskWarningIdle = asyncio.create_task(playWarnAnimation(5))
                taskAnimationSoundIdle = asyncio.create_task(playSound(idleSoundPins))
                idleAnimations.append(taskWarningIdle)
                idleAnimations.append(taskAnimationSoundIdle)
                lastIdleWarningAnimationTime = time.time()
                print("idle warning animation end")

            if len(idleAnimations) > 0:
                await asyncio.gather(*idleAnimations)

asyncio.run(main())













