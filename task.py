#Módulos a utilizar
import numpy as np
import pandas as pd


#print stars 
def stars(number):
	for i in range(number):
		print("*", end = "")
	print("")

#Mensajes de error para la Actividad-PREDECESORES-DIAS(Di,j)
def errorCodeMsg():
	print("Error en el archivo de entrada : ACTIVIDAD ")
	quit()
	
def errorPredMsg():
	print("Error en el archivo de entrada : PREDECESORES ")
	quit()


def errorDaysMsg():
	print("Error en el archivo de entrada : Di,j ")
	quit()

# Analiza si el código en predecesores y sucesores está 
# en la lista de códigos de tarea:
def getTaskCode(mydata, code):
	x = 0
	flag = 0
	for i in mydata['ACTIVIDAD']:
		if(i == code):
			flag = 1
			break
		
		x+=1
		
	if(flag == 1):
		return x
	else:
		errorCodeMsg()
		
		

# Método de la ruta crítica, función hacia adelante:
# ES -> Inicio Tempreno
# EF -> Fin Temprano


def forwardPass(mydata):
	ntask = mydata.shape[0]
	ES = np.zeros(ntask, dtype = np.int8)
	EF = np.zeros(ntask, dtype = np.int8)
	temp = [] #Mantener la lista temporal
	
	
	for i in range(ntask):
		if(mydata['PREDECESORES'][i] == None):
			ES[i] = 0
			try:
				EF[i] = ES[i] + mydata['Di,j'][i]
			except:
				errorDaysMsg()
				
		else:
			for j in mydata['PREDECESORES'][i]:
				index = getTaskCode(mydata,j)
				if(index == i):
					errorPredMsg()
				else:
					temp.append(EF[index])
				
			ES[i] = max(temp)
			try:
				EF[i] = ES[i] + mydata['Di,j'][i]
			except:
				errorDaysMsg()
			
		#Reestablecer lista temporal
		temp = []
		
	
	#Actualizar tabla(dataFrame):
	mydata['ES'] = ES
	mydata['EF'] = EF
	
	return mydata
	
	
# Método de la ruta crítica, función hacia atrás:
# LS -> Inicio Tardío
# LF -> Fin Tardío

def backwardPass(mydata):
	ntask = mydata.shape[0]
	temp = []
	LS = np.zeros(ntask, dtype = np.int8)
	LF = np.zeros(ntask, dtype = np.int8)
	SUCCESSORS = np.empty(ntask, dtype = object)
	
	#Creación de la columna Sucesores:
	
	for i in range(ntask-1, -1,-1):
		if(mydata['PREDECESORES'][i] != None):
			for j in mydata['PREDECESORES'][i]:
				index = getTaskCode(mydata,j)
				if(SUCCESSORS[index] != None):
					SUCCESSORS[index] += mydata['ACTIVIDAD'][i]
				else:
					SUCCESSORS[index] = mydata['ACTIVIDAD'][i]
				
	#Incorporacion de la columna en la data frame(tabla):
				
	mydata["SUCESORES"] = SUCCESSORS
	
	#Calcular LF -> Fin Tardío y LS -> Inicio Tardío:
	
	for i in range(ntask-1, -1, -1):
		if(mydata['SUCESORES'][i] == None):
			LF[i] = np.max(mydata['EF'])
			LS[i] = LF[i] - mydata['Di,j'][i]
		else:
			for j in mydata['SUCESORES'][i]:
				index = getTaskCode(mydata,j)
				temp.append(LS[index])
			
			LF[i] = min(temp)
			LS[i] = LF[i] - mydata['Di,j'][i]
			
			#Reestablecer la lista temporal:
			temp = [] 
			
	
	#Incorporación del LF y LS en la data frame(tabla):
	
	mydata['LS'] = LS
	mydata['LF'] = LF
	
	return mydata
	
#Calcular para MTi,j(SLACK) y el estado Crítico (CRITICAL):	
def slack(mydata):
	ntask = mydata.shape[0]
	
	SLACK = np.zeros(shape = ntask, dtype = np.int8)
	CRITICAL = np.empty(shape = ntask,dtype = object)
	
	for i in range(ntask):
		SLACK[i] = mydata['LS'][i] - mydata['ES'][i]
		if(SLACK[i] == 0):
			CRITICAL[i] = "SI"
		else:
			CRITICAL[i] = "NO"
			
	#Incorporación del MTi,j y el estado Crítico a la data frame(tabla):
	
	mydata['MTi,j'] = SLACK
	mydata['RUTA CRÍTICA'] = CRITICAL
	
	
	#Reorganizar las columnas en la tabla(dataFrame):
	mydata = mydata.reindex(columns = ['DESCR', 'ACTIVIDAD','PREDECESORES','SUCESORES','Di,j','ES','LS','EF','LF','MTi,j','RUTA CRÍTICA'])
	
	return mydata
	
#Función wrapper:
	
def computeCPM(mydata):
	mydata = forwardPass(mydata)
	mydata = backwardPass(mydata)
	mydata = slack(mydata)
	return mydata

#Imprimir presentación
			
def printTask(mydata):
	print("PROGRAMA DEL MÉTODO PERT-CPM-RUTA_CRÍTICA:: ROSA MERA BURGOS")
	print("")
	stars(90)
	print("ES = Inicio Temprano; EF = Fin Temprano; LS = Inicio Tardío, LF = Fin Tardío")
	stars(90)
	print(mydata)
	stars(90)
	