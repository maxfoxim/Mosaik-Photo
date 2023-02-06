#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
!!! WICHTIG !!!
Das Hauptbild muss sRGB formatiert sein, nicht CMYK. Ansonsten wird die Helligkeit nicht korrekt berechnet.

Erstellt aus einem grossen Bild ein Mosaik aus vielen kleinen Werten
11.4.20 besserer Zufallsalgortihmus
"""

import os
from PIL import Image,ImageStat
import random
from PIL.ExifTags import TAGS

def sortSecond(val): 
    return val[0]  

def brightness( bild ):
   stat = ImageStat.Stat(bild)
   return stat.mean[0]

def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    keys = list(info.keys())
    keys = [k for k in keys if k in TAGS]
    for tag, value in info.items():
        #print (info.items())
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
        #print ("tag",tag,"value",value,"decoded",decoded)
    return ret

def zufalls_bild(zufallsarray,orignal_array):
    if len(zufallsarray)<2:
        random.shuffle(orignal_array)
        zufallsarray=orignal_array
        #print ("NEU SORTIERT---------------------",zufallsarray,len(zufallsarray))
    
    auswahl=zufallsarray[0]
    del zufallsarray[0]
    #print ("Auswahl",auswahl,array)
    return auswahl,zufallsarray
    
        
    

#Welcher Ordner mit Mosaikbildern eingelesen soll, danach nur JPEG Dateien einlesen die kein "klein" im Namen haben
Ordner="mosaik_pictures_private"
JPG_Dateien_Roh=os.listdir(Ordner)
JPG_Dateien=[i for i in JPG_Dateien_Roh if i.find("JPEG")>=0 or i.find("JPG")>=0 or i.find("jpeg")>=0 or i.find("jpg")>=0] #ds_store Datei rauslöschen
print("Nur JPEGs",len(JPG_Dateien),JPG_Dateien)
JPG_Dateien=[i for i in JPG_Dateien if i.find("weiss")<0] # weißes Bild extra behandeln und rausnehmen

JPG_Dateien_gross=[i for i in JPG_Dateien if i.find("klein")<0] # nur geschnittene reinnehmen
JPG_Dateien_gross.sort()
print("Dateien_gross(ohne _klein):",len(JPG_Dateien_gross),JPG_Dateien_gross)

# Hauptbild das aus Mosaiken bestehen soll
Datei="Emilia.jpg"
Neu_Konvertieren=True # Mosaikbilder verkleinern
bilder_anzahl=70 # Anzahl Bilder in x UND y Richtung, also insgesamt bilder_anzahl**2
Background_Color=(255, 255, 255)

Image_Einfuegen = Image.open(Datei)
#Pixelwerte automatisch bestimmen
try:
    exif_daten=get_exif(Datei)
    pixel_x=exif_daten["ExifImageWidth"]
    pixel_y=exif_daten["ExifImageHeight"]
except:
    pixel_x=3508 
    pixel_y=2481
print("Pixel Ursprungsbild",pixel_x,pixel_y)
#Groesse des eingelesen Bildes
#pixel_x=6000
#pixel_y=4077

x_anzahl_bilder=bilder_anzahl 
y_anzahl_bilder=bilder_anzahl
verkleinerung  =bilder_anzahl #Wie stark ein Originalbild zum Mosaikbild verkleinert wird
breite_ausschnitt=int(pixel_x/x_anzahl_bilder) # Wie groß ein Mosaikbild ist
hoehe_ausschnitt =int(pixel_y/y_anzahl_bilder)
gesamt_anzahl_bilder=x_anzahl_bilder*y_anzahl_bilder 

# Variabeln
x_einfuegen=0
y_einfuegen=0
index_x=0
index_y=0

helligkeiten=[]

#Berechne die Helligkeiten der einzelnen Bereiche des Hauptbildes
bild=0
for i in range(gesamt_anzahl_bilder):
    # Ausschnitt definiern 
    teilausschnitt = Image_Einfuegen.crop((x_einfuegen, y_einfuegen, x_einfuegen+breite_ausschnitt, y_einfuegen+hoehe_ausschnitt)) 
    #Helligkeit bestimmen
    helligkeit_ausschnitt=brightness(teilausschnitt)
    if helligkeit_ausschnitt>0:
        print(bild,"Ausschnitthelligkeit",round(helligkeit_ausschnitt,2))
        print("Index x y",index_x,index_y)
    #print("Koordinaten",x_einfuegen, y_einfuegen, x_einfuegen+breite_ausschnitt, y_einfuegen+hoehe_ausschnitt)
    # Platzierung hochiteriern 
    x_einfuegen=int(breite_ausschnitt*index_x) # fuer x Achse
    y_einfuegen=int( hoehe_ausschnitt*index_y) # fuer y Achse
    helligkeiten.append(helligkeit_ausschnitt)
    if index_x==(x_anzahl_bilder-1): # wenn x an Grenze, gehe eine Zeile tiefer
        index_y=index_y+1
    index_x=(index_x+1)%x_anzahl_bilder # Modulo x Grenze
    bild=bild+1
    
    #print ("------------------------------------------")


#erstelle "weiße" Leinwand für neues Bild
image_Org = Image.new('RGB', (pixel_x, pixel_y))
anzahl_bilder=len(JPG_Dateien)

# Mosaikbilder verkleinern
i=0
if Neu_Konvertieren:
    for Datei in JPG_Dateien_gross:    
        print(i,"Datei verkleinern", Datei)
        Datei=Ordner+"/"+Datei    
        Image_klein = Image.open(Datei)
        Image_klein = Image_klein.resize((int(pixel_x/verkleinerung), int(pixel_y/verkleinerung))) 
        Endungsindex=Datei.find(".")
        Image_klein.save(Datei[:Endungsindex]+"_klein.JPEG") 
        i=i+1


#JPG_Dateien=os.listdir(Ordner)
#JPG_Dateien=[i for i in JPG_Dateien if i.find("JPEG")>=0 or i.find("JPG")>=0 or i.find("jpeg")>=0] #ds_store Datei rauslöschen
JPG_Dateien_klein=[i for i in JPG_Dateien if i.find("klein")>0] # nur geschnittene reinnehmen

print("kleine Dateien",JPG_Dateien_klein)

#Berechne die durchschnittliche Helligkeit jedes einzelns Mosaikbildes
helligkeiten_bilder_einzel=[]
for Datei in JPG_Dateien_klein[:]:
    Datei=Ordner+"/"+Datei
    Endungsindex=Datei.find(".")
    Image_Einfuegen=Image.open(Datei[:Endungsindex]+".jpeg")
    helligkeiten_bilder_einzel.append([brightness(Image_Einfuegen),Datei])

#Sortiere die Bilder nach ihrer Helligkeit
helligkeiten_bilder_einzel.sort(key = sortSecond, reverse = False)

JPG_Dateien=[]
index_x=0
index_y=0
ZufallsMosaik=True
anzahl_mosaik_bilder=len(helligkeiten_bilder_einzel)
print("Helligkeiten der Bilder",helligkeiten_bilder_einzel)
for i in range(gesamt_anzahl_bilder):
    #Datei=random.choice(JPG_Dateien_klein) # fur zufällige Auswahl
    
    # wähle ein passendes Mosaikbild aus: hier geht es nach der Reihenfolge
    # wie hell(dunkel) ein Bild ist. Bsp: Hellstes Bild hat Index 0, dunkelstes Bild
    # Index(len(JPG_Dateien_klein)). 
    # Geteilt durch 255 um auf 255 zu normieren. 
    index_bild=int(helligkeiten[i]*(len(helligkeiten_bilder_einzel)-1)/255)     
    
    #passende Datei auswählen
    if ZufallsMosaik:
        if index_bild==anzahl_mosaik_bilder-1: ##weißes Bild
            Datei=helligkeiten_bilder_einzel[index_bild][1]
        else:
            #Datei=random.choice(JPG_Dateien_klein[:-1])  ## zufälliges Bild
            Datei,JPG_Dateien=zufalls_bild(JPG_Dateien,JPG_Dateien_klein[:-1])
            Datei=Ordner+"/"+Datei    
    else:
        Datei=helligkeiten_bilder_einzel[index_bild][1]
    
    #Hintergrund der rein weiß ist, auch mit weiß überlagern
    if helligkeiten[i]>254:
        #Image_Einfuegen = Image.open(Ordner+"/"+"weiss_klein.JPEG") #spezielles Hintergrundbild
        Image_Einfuegen = Image.new("RGB", (800, 1280), Background_Color)
    else:
        #Image_Einfuegen = Image.open(Datei)
        Image_Einfuegen=Image.open(Datei[:-5]+".JPEG")

    #print("Datei",Datei,"IndexBild",index_bild)
    #print("Helligkeiten",round(helligkeiten[i],2))

    # Geschnittenes Bild laden    
    #Image_Einfuegen=Image.open(Datei[:-5]+".jpeg")
    Helligkeit=brightness(Image_Einfuegen)
    #print("Helligkeit_Eingefügtes_Bild",round(Helligkeit,2))
    #Geschnittenes Bild einfügen
    image_Org.paste(Image_Einfuegen, (int(x_einfuegen), int(y_einfuegen))) 
    
    #print(index_x,"x_achse",x_einfuegen)
    #print(index_y,"y_achse",y_einfuegen)

    # Platzierung hochiteriern, siehe auch weiter oben
    x_einfuegen=breite_ausschnitt*index_x
    y_einfuegen=hoehe_ausschnitt*index_y
    if index_x==(x_anzahl_bilder-1):
        index_y=index_y+1
    index_x=(index_x+1)%x_anzahl_bilder
    
    
    #print("---------------------------------------------------------------")

#image_Org.show()
#Finales Bild speichern
#image_Org.save("Final_"+str(bilder_anzahl)+".jpg",dpi=(300, 300)) 
image_Org.save("Private.jpg",dpi=(300, 300)) 

