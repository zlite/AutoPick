import cv2
import numpy
import math
import sys
class Line:
    '''A class for line'''
    def __init__(self,x0,y0,k):
        self.x0 = x0
        self.y0 = y0
        self.k  = k
    def getY(self,x):
        if (self.k == float("inf") or self.k == float("-inf")):
            self.y = float("inf")
            print ("y is inf!!")
        else:
            self.y = 1.0*self.k*(x-self.x0)+self.y0
        return self.y
    def getX(self,y):
        if(self.k == 0):
            self.x = float("inf")
            print ("x is inf!")
        else:
            self.x = (y-self.y0)*1.0/self.k+self.x0
        return self.x
    def update(self,x,y,k):
        self.x0 = x
        self.y0 = y
        self.k  = k
class FindObject:
    'A class to find object with opencv2. require: cv2 numpy'
    def __init__(self,img,debugFlag=False):
        self.img     = img
        self.hsvmask = None
        self.binary  = None
        self.debugFlag = debugFlag
        self.imgSize = img.shape
        print ("A FindObject Class is created!")
    def updateImg(self,img):
        '''update img
            input:img
            return: img
        '''
        if img is None :
            print("img is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit()
        self.img = img
        return self.img
    def hsvFilter(self,lower_color=(0,0,0),upper_color=(255,255,255)):
        ''' convert to HSV color space and threshold
            input: lower_color=(0,0,0),upper_color=(255,255,255)
            return: img
        '''
        self.hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(self.hsv, lower_color, upper_color)
        self.hsvmask = cv2.bitwise_and(self.img, self.img, mask=self.mask)

        if self.debugFlag is True :
            cv2.imshow('hsvFilter',self.hsvmask)
        return self.hsvmask
    def converToBinary(self,thresholdValue=0):
        ''' convert to binary 
            input: thresholdValue=0
            return: img
            attention: hsvFileter need run firstly
        '''
        if self.hsvmask is None:
            print("hsvmask is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit()
        else:
            self.gray = cv2.cvtColor(self.hsvmask,cv2.COLOR_BGR2GRAY)
            self.retval,self.binary = cv2.threshold(self.gray, thresholdValue, 255, cv2.THRESH_BINARY)
            if self.debugFlag is True :
                cv2.imshow('converToBinary',self.binary)
            return self.binary
    def erode(self,shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None):
        ''' Erodes an image by using a specific structuring element.
            input : shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None
            return: img
            attention: converToBinary need run before this
        '''
        if binaryImg is None:
            binaryImg = self.binary
        if binaryImg is None:
            print("binary is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit() 
        else:
            kernel = cv2.getStructuringElement(shape,ksize)
            self.erodeImg = cv2.erode(binaryImg,kernel)  
            if self.debugFlag is True :
                cv2.imshow('erode',self.erodeImg)
            return self.erodeImg               
    def dilate(self,shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None):
        ''' Dilates an image by using a specific structuring element.
            input : shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None
            return: img
            attention: converToBinary need run before this
        '''
        if binaryImg is None:
            binaryImg = self.binary
        if binaryImg is None:
            print("binary is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit() 
        else:
            kernel = cv2.getStructuringElement(shape,ksize)
            self.dilateImg = cv2.dilate(binaryImg,kernel)  
            if self.debugFlag is True :
                cv2.imshow('dilate',self.dilateImg)
            return self.dilateImg
    def getCenter(self):
        pass

class FindBall(FindObject):
    def __init__(self, img, debugFlag=False):
        FindObject.__init__(self, img, debugFlag=False)
        self.PickPosition = 0
        self.Height       = 0
    '''find  ball '''
    def getCenter(self,binaryImg=None,contoursRange=(60,1000),dilateFlag=True, ksize=(3,3)):
        '''Get the center the of the ball
        input : binaryImg,contoursRange=(200,1000)
        return: coutours,img
        '''
        self.CenterP=[]
        if binaryImg is None :
            binaryImg = self.binary
        if binaryImg is None :
            print("binary is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit()
        else:  
            if dilateFlag is True :
                tempImg = binaryImg
                binaryImg=self.dilate(ksize=ksize,binaryImg=tempImg)
            self.contourImg,self.contours,hierarchy = cv2.findContours(binaryImg,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            i = 0
            count = len(self.contours)
            while (i<count):
                if self.contours[i].shape[0] < contoursRange[0] or self.contours[i].shape[0] > contoursRange[1]:
                    del self.contours[i]
                    count = count - 1
                    i = i - 1
                i = i + 1
            i = 0
            count = len(self.contours)
            while (i < count ):
                x, y, w, h = cv2.boundingRect(self.contours[i])
                if w > h:
                    k=w/h
                else:
                    k=h/w
                if k > 3:
                    #delete narrow contours
                    del self.contours[i]
                    count = count - 1
                    continue
                else:
                    area = math.fabs(cv2.contourArea(self.contours[i]))
                    if area >0:
                        if (w*h/area) > 3:
                            #delete tilt and narrow contours 
                            del self.contours[i]
                            count = count - 1
                            i = i - 1
                    i = i + 1

            if len(self.contours) >=1 :
                i=0 
                count = len(self.contours)
                _white =  (255, 255, 255)
                while(i<count):
                    x, y, w, h = cv2.boundingRect(self.contours[i])
                    lx = x + w/2
                    ly = y + h/2
                    
                    self.CenterP.append([lx,ly])
                    i=i+1
                self.CenterP = numpy.asarray(self.CenterP)
                idex = numpy.lexsort([self.CenterP[:,1],self.CenterP[:,0]])
                self.CenterP = self.CenterP[idex,:]
                return  self.contours,self.CenterP
            else :
                self.CenterP = numpy.asarray(self.CenterP)
                return self.contours,self.CenterP

    def draw(self,calFlag = False):
        _white =  (255, 255, 255)
        self.drawImg = self.img.copy()
        if len(self.contours) > 0 and len(self.contours) == len(self.CenterP):
            #cv2.drawContours(self.drawImg,self.contours,-1,_white,5)
            i=0
            count = len(self.CenterP)
            while(i<count):
                cv2.circle(self.drawImg, (self.CenterP[i][0], self.CenterP[i][1]),4, _white, -1)
                area = math.fabs(cv2.contourArea(self.contours[i]))
                cv2.circle(self.drawImg, (self.CenterP[i][0], self.CenterP[i][1]), int(math.sqrt(area/math.pi)), _white, 0)
                i = i + 1
            if calFlag is True:
                 cv2.line(self.drawImg,(self.PickPosition,0),(self.PickPosition,self.imgSize[0]),(255,255,0),3)
                 cv2.line(self.drawImg,(0,self.Height),(self.imgSize[1],self.Height),(255,255,0),3)
            cv2.imshow("Redball",self.drawImg)
        else:
            if calFlag is True:
                 cv2.line(self.drawImg,(self.PickPosition,0),(self.PickPosition,self.imgSize[0]),(255,255,0),3)
                 cv2.line(self.drawImg,(0,self.Height),(self.imgSize[1],self.Height),(255,255,0),3)
            cv2.imshow("Redball",self.drawImg)
    def calculate(self,PickPosition,Height):
        self.PickPosition = PickPosition
        self.Height       = Height
        if self.PickPosition < 0 or self.PickPosition > self.imgSize[1]:
            self.PickPosition = int(self.imgSize[0]/10)
        if self.Height < 0 or self.Height > self.imgSize[0]:
            self.Height = int(self.imgSize[0]/2.0)
        if len(self.contours) > 0 and len(self.contours) == len(self.CenterP):
            if len(self.CenterP) == 1:
                distance = self.CenterP[0][0] - self.PickPosition
                highFlag = None
                if self.Height > self.CenterP[0][1]:
                    highFlag = True
                else:
                    highFlag = False
                return int(distance),highFlag
            else:
                minID = 0
                minDistanceAbs = self.imgSize[0]
                for i in range(len(self.CenterP)):
                    distance = self.CenterP[i][0] - self.PickPosition
                    if abs(distance) < minDistanceAbs:
                        minDistanceAbs = abs(distance)
                        minID = i
                distance = self.CenterP[minID][0] - self.PickPosition
                highFlag = None
                if self.Height > self.CenterP[minID][1]:
                    highFlag = True
                else:
                    highFlag = False
                return int(distance),highFlag
        else:
            return None,None

    def BigOrSmall(self, PickPosition, BallSize):
        self.PickPosition = PickPosition
        self.BallSize     = BallSize
        if self.PickPosition < 0 or self.PickPosition > self.imgSize[1]:
            self.PickPosition = int(self.imgSize[0]/10)
        if len(self.contours) > 0 and len(self.contours) == len(self.CenterP):
            if len(self.CenterP) == 1:
                distance = self.CenterP[0][0] - self.PickPosition
                bigFlag  = None
                if self.BallSize < self.contours[0].shape[0]:
                    bigFlag = True
                else:
                    bigFlag = False
                return int(distance),bigFlag
            else:
                minID = 0
                minDistanceAbs = self.imgSize[0]
                for i in range(len(self.CenterP)):
                    distance = self.CenterP[i][0] - self.PickPosition
                    if abs(distance) < minDistanceAbs:
                        minDistanceAbs = abs(distance)
                        minID = i
                distance = self.CenterP[minID][0] - self.PickPosition
                bigFlag = None
                if self.BallSize < self.contours[minID].shape[0]:
                    bigFlag = True
                else:
                    bigFlag = False
                return int(distance),bigFlag
        else:
            return None,None
class FindTrack(FindObject):
    def __init__(self,img,debugFlag=False):
        self.img     = img
        self.hsvmask = None
        self.binary  = None
        self.blurtImg= None
        self.edges   = None
        self.debugFlag = debugFlag
        self.prospect = None
        self.target   = None
        self.imgSize = img.shape
        self.Middle = Line(self.imgSize[1]/2,0,float("inf"))
        print ("A FindTrack Class is created!")
    def getCenter(self,blurSize=15,minVal=50,maxVal=150,\
        linePointCount=60,minLineLength=120,maxLineGap=10,\
        slopeThreshold=math.tan(math.pi/6),defaultPos=0):
        '''Get the middle line of the track
            input:
                blurSize=15,        #size for blur
                minVal=50,          #value for edges
                maxVal=150,         #value for edges
                linePointCount=60,  #value for HoughLinesP
                minLineLength=120,  #value for HoughLinesP
                maxLineGap=10,      #value for HoughLinesP
                slopeThreshold=math.tan(math.pi/6)        #the slope to del some lines
            output:
                Line::Middle         #euqation of the middle line   
        '''
        #Blur Canny HoughLines. To get lines in the picture.
        self.blurtImg = cv2.medianBlur(self.binary.copy(),15)
        self.edges = cv2.Canny(self.blurtImg.copy(),minVal,maxVal)
        self.lines = cv2.HoughLinesP(self.edges,1,numpy.pi/180,linePointCount,minLineLength,maxLineGap) 
        self.lineTemp = self.img.copy()
        if self.lines is not None:
            #separate left and right lines according to slope
            self.leftLines = []
            self.rightLines = []           
            for item in self.lines:
                x1 = item[0][0]
                y1 = item[0][1]
                x2 = item[0][2]
                y2 = item[0][3]
                if (0 == (x2-x1)):
                    if y2 > y1 :
                        k = float("inf")
                    else:
                        k = float("-inf")
                else :
                    k  = (y2 - y1)*1.0/(x2 - x1)
                if (k < 0.0 - slopeThreshold ):
                    self.leftLines.append(item[0])
                if (k > slopeThreshold ):
                    self.rightLines.append(item[0])
            #get middle line equation
            self.imgSize = self.lineTemp.shape           
            tempMiddleX =[0,0]
            tempMiddleY =[0,0]
            if len(self.leftLines)>0 and len(self.rightLines)>0:  
                count = min(len(self.rightLines),len(self.leftLines))
                i=0 
                sumRX=[0,0]
                sumLX=[0,0]
                #We use points from left line and rignt line to get the middle line point
                while(i < count ):
                    #kL left line slope;kR right line slope
                    if ((self.leftLines[i][2]-self.leftLines[i][0]) == 0):
                        kL = float("inf")
                    else:
                        kL =  (self.leftLines[i][3]-self.leftLines[i][1])*1.0/(self.leftLines[i][2]-self.leftLines[i][0])
                    if ((self.rightLines[i][2]-self.rightLines[i][0]) == 0):
                        kR = float("inf")
                    else:
                        kR =  (self.rightLines[i][3]-self.rightLines[i][1])*1.0/(self.rightLines[i][2]-self.rightLines[i][0])                  
                    #LineL LineR,The equation of left line and right line
                    LineL = Line(self.leftLines[i][0],self.leftLines[i][1],kL)
                    LineR = Line(self.rightLines[i][0],self.rightLines[i][1],kR) 
                    sumLX[0] = sumLX[0] + LineL.getX(self.imgSize[0]*1.0/2)
                    sumLX[1] = sumLX[1] + LineL.getX(self.imgSize[0]*1.0*2/3)
                    sumRX[0] = sumRX[0] + LineR.getX(self.imgSize[0]*1.0/2)
                    sumRX[1] = sumRX[1] + LineR.getX(self.imgSize[0]*1.0*2/3)
                    i = i + 1
                tempMiddleY[0] = self.imgSize[0]*1.0/2
                tempMiddleY[1] = self.imgSize[0]*1.0*2/3
                tempMiddleX[0] = (sumLX[0]*1.0/count+sumRX[0]*1.0/count)/2.0
                tempMiddleX[1] = (sumLX[1]*1.0/count+sumRX[1]*1.0/count)/2.0
                
                if tempMiddleX[1] == tempMiddleX[0] :
                    tempMiddleK = float("inf")
                else :
                    tempMiddleK = (tempMiddleY[1]-tempMiddleY[0])*1.0 /(tempMiddleX[1]-tempMiddleX[0])
                #middle line equation
                self.Middle.update(tempMiddleX[0],tempMiddleY[0],tempMiddleK)
            else:
                # if we can not get two side lines ,middle line is set to defaultPos
                self.Middle.update(defaultPos, 0, float("inf"))
        else:
            # if there are no lines,middle line is set to defaultPos
            self.leftLines = None
            self.rightLines= None
            self.Middle.update(defaultPos, 0, float("inf"))
        if self.debugFlag is True:
            cv2.imshow("canny",self.edges)   
            if self.leftLines is not None :
                for item in self.leftLines:
                    cv2.line(self.lineTemp,(item[0],item[1]),(item[2],item[3]  ),(255,0,0),3)
            if self.rightLines is not None :
                for item in self.rightLines:
                    cv2.line(self.lineTemp,(item[0],item[1]),(item[2],item[3]  ),(0,0,255),3)       
            cv2.line(self.lineTemp,(self.imgSize[1]/2,0),(self.imgSize[1]/2,self.imgSize[0]),(255,255,0),3)
            cv2.line(self.lineTemp,(0,int(self.imgSize[0]*1.0/2)),(self.imgSize[1],int(self.imgSize[0]*1.0/2)),(255,255,0),1)
            cv2.line(self.lineTemp,(0,int(self.imgSize[0]*1.0*2/3)),(self.imgSize[1],int(self.imgSize[0]*1.0*2/3)),(255,255,0),1)
            cv2.line(self.lineTemp,\
            (int(self.Middle.getX(0)),0),\
            (int(self.Middle.getX(self.imgSize[0])),self.imgSize[0]),\
            (0,255,255),3)
            cv2.imshow("Lines after slope choose",self.lineTemp)
            return self.Middle
        else:
            return self.Middle
    def draw(self,DeltaFlag=False):
        if self.leftLines is not None :
            for item in self.leftLines:
                cv2.line(self.lineTemp,(item[0],item[1]),(item[2],item[3]  ),(255,0,0),3)
        if self.rightLines is not None :
            for item in self.rightLines:
                cv2.line(self.lineTemp,(item[0],item[1]),(item[2],item[3]  ),(0,0,255),3)       
        cv2.line(self.lineTemp,(self.imgSize[1]/2,0),(self.imgSize[1]/2,self.imgSize[0]),(255,255,0),3)
        cv2.line(self.lineTemp,(0,int(self.imgSize[0]*1.0/2)),(self.imgSize[1],int(self.imgSize[0]*1.0/2)),(255,255,0),1)
        cv2.line(self.lineTemp,(0,int(self.imgSize[0]*1.0*2/3)),(self.imgSize[1],int(self.imgSize[0]*1.0*2/3)),(255,255,0),1)
        cv2.line(self.lineTemp,\
        (int(self.Middle.getX(0)),0),\
        (int(self.Middle.getX(self.imgSize[0])),self.imgSize[0]),\
        (0,255,255),3)
        if DeltaFlag is True:
            print "DeltaFlag is true"
            cv2.line(self.lineTemp,\
                     (self.target, 0),\
                     (self.target, self.imgSize[0]),\
                     (0, 255, 255), 3)
        cv2.imshow("FindTrack",self.lineTemp)
    def getDelta(self,default=True,prospect=0,target=0):
        if default is True:
            self.prospect = int(self.imgSize[0]*2.0/3)
            self.target   = int(self.imgSize[1]/2.0)
        else:
            self.prospect = int(prospect)
            self.target   = int(target)
        return int(self.target-self.Middle.getX(self.prospect))

class BallShow:
    def __init__(self,ball):
        self.key = ord('q')
        self.ball = ball
    def updateBall(self,ball):
        self.ball = ball
    def switchWindow(self,key):
        if key < 256 and key >= 0:
            if  chr(key) in "qwer":
                self.key = key
    def showImg(self):
        if   self.key == ord('q'):
            cv2.imshow("process",self.ball.hsvmask)
        elif self.key == ord('w'):
            cv2.imshow("process",self.ball.binary)
        elif self.key == ord('e'):
            cv2.imshow("process",self.ball.dilateImg)
        elif self.key == ord('r'):
            cv2.imshow("process",self.ball.img)
        else:
            pass
class TrackShow:
    def __init__(self,track):
        self.key = ord('q')
        self.track = track
    def updateBall(self,ball):
        self.track = track
    def switchWindow(self,key):
        if key < 256 and key >= 0:
            if  chr(key) in "qwer":
                self.key = key
    def showImg(self):
        if   self.key == ord('q'):
            cv2.imshow("process",self.track.hsvmask)
        elif self.key == ord('w'):
            cv2.imshow("process",self.track.binary)
        elif self.key == ord('e'):
            cv2.imshow("process",self.track.blurtImg)
        elif self.key == ord('r'):
            cv2.imshow("process",self.track.edges)
        else:
            pass    
