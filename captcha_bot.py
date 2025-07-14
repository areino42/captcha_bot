# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 17:06:57 2025

@author: andres
"""

#############################################
# Python 3.12.7 | packaged by Anaconda, Inc. |
##############################################

from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib.request
import time
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from bs4 import BeautifulSoup





ACCESS_KEY = 'XXXXXXXXXXXXXXXXX'
SECRET_KEY = 'XXXXXXXXXXXXXXXXX'



def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("CARGA EXITOSA")
        return True
    except FileNotFoundError:
        print("ARCHIVO NO ENCONTRADO")
        return False
    except NoCredentialsError:
        print("CREDENCIALES INCORRECTAS")
        return False



transcribe = boto3.client('transcribe',
                          aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY,
                          region_name = "us-east-1")




driver = webdriver.Firefox()
driver.get('https://www.google.com/recaptcha/api2/demo')
time.sleep(3) 
print('CAPTCHA')



driver.switch_to.frame(driver.find_element(By.XPATH,"//iframe[@title='reCAPTCHA']"))

driver.find_element(By.XPATH,"//div[@class='recaptcha-checkbox-border']").click()  
time.sleep(3)


# Regresamos al contenido anterior
#********************************#
driver.switch_to.default_content() 
#********************************#

driver.switch_to.frame(driver.find_element(By.XPATH,"//iframe[@title='El reCAPTCHA caduca dentro de dos minutos']"))


driver.find_element(By.XPATH,"//button[@id='recaptcha-audio-button']").click()  
time.sleep(16)


src = driver.find_element(By.ID,"audio-source").get_attribute("src")
urllib.request.urlretrieve(src, r"C:/Users/XXXXX/XXXXXX/captcha_audio.mp3")
print("ARCHIVO AUDIO DESCARGADO")


uploaded = upload_to_aws("C:/Users/XXXXXX/XXXXXX/captcha_audio.mp3",
                "bucket_name",
                "XXXXXX/XXXXXXX/captcha_audio.mp3")


time.sleep(3)
transcribe.start_transcription_job(
    TranscriptionJobName = "captcha_job",
    Media = {'MediaFileUri': "s3://bucket_name/XXXXXX/XXXXXX/captcha_audio.mp3"},
    MediaFormat = 'mp3',
    LanguageCode = 'es-ES')


# Tiempo promedio de transcripcion de AWS Transcribe
#********************************#
time.sleep(60)
#********************************#
print("TERMINA TRANSCRIPCION")


result_c = transcribe.get_transcription_job(TranscriptionJobName="captcha_job")
data_c = pd.read_json(result_c['TranscriptionJob']['Transcript']['TranscriptFileUri'])

transcripts_row = data_c.loc['transcripts', 'results']
if isinstance(transcripts_row, list) and len(transcripts_row) > 0:
    transcripts_dict = transcripts_row[0] 
texto_captcha = transcripts_dict['transcript']
print(texto_captcha)


time.sleep(2)
transcribe.delete_transcription_job(TranscriptionJobName="captcha_job")

time.sleep(2)
entrada_capt = driver.find_element(By.ID,'audio-response')
entrada_capt.click()

time.sleep(2)        
entrada_capt.send_keys(str(texto_captcha))

time.sleep(2) 
driver.find_element(By.ID,'recaptcha-verify-button').click()


time.sleep(2)
# Regresamos al contenido anterior
#********************************#
driver.switch_to.default_content() 
#********************************#
print('PASA CHAPTCHA')




driver.find_element(By.XPATH,"//input[@id='recaptcha-demo-submit']").click() 
print('OK')    


time.sleep(2)
# Pasamos al contenido HTML
#********************************#
html = driver.page_source
soup = BeautifulSoup(html,"html.parser")
print(soup.text)
#********************************#







































