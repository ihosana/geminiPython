import vosk
import pyaudio
import json
import os
import speech_recognition as sr
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
import io
import sys
import random
import threading
from gtts import gTTS
import google.generativeai as genai
import RPi.GPIO as GPIO
import time


#-----------CONFIGURAÇÃO DOS PINOS-----------
#Led_vermelho=17
#Led_azul=27
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(Led_vermelho, GPIO.OUT)
#GPIO.setup(Led_azul, GPIO.OUT)

#GPIO.output(Led_vermelho, GPIO.LOW)
#GPIO.output(Led_azul, GPIO.LOW)

# --- CONFIGURAÇÃO ---
# * Verifique se esta é a pasta onde você descompactou o modelo *
# Exemplo: 'vosk-model-small-pt-0.3'
#-----------CONFIGURAÇÃO DO MODELO VOSK-------
MODEL_PATH = "/home/ihosa/Downloads/test_vosk/model"
SAMPLE_RATE = 44100
CHUNK_SIZE = 4000

#-----------CONFIGURAÇÃO DO MODELO GEMINI-----
genai.configure(api_key="AIzaSyAxFqenTpi06cVst5ttHjkGYxflr-IQhcw")
model = genai.GenerativeModel("gemini-2.5-flash")

# Palavras chaves
palavra_chave_robo="robô"
palavra_chave_historia="história"

# Lista de Elogios e Palavras Irrelevantes
elogios=["UAU!!","Que Legal!!","Nossa!Que demais!!", "Que incrível!!", "Parece legal!","Voçês estão demais hoje!!", "Voçês são muito inteligentes!","Continuem assim","Boa!!","Voçês estão mandando bem!!", "Muito Bemm!!", "Isso é muito divertido!!"]
palavras_excluidas=[
    "de", "a", "o", "e", "que", "em", "um", "uma", "os", "as", "do", "da","como"
    "no", "na", "nos", "nas", "se", "por", "para", "pra", "pro",
    "com", "ao", "aos", "à", "às", "mais", "já", "me", "te", "lhe","também",
    "eu", "tu", "ele", "ela", "nós", "vós", "eles", "elas", "você", "vocês", "gosto",
    "amo", "sou", "apaixonada", "eu", "queria", "ir", "gostamos", "gosta", "doi",
    "teria", "alguma", "história", "não","sim", "tem", "algum", "pronto","adoro","merda"
]

def palavras_relevantes(texto):
    palavras = texto.lower().split()  # divide em lista
    filtradas = [p for p in palavras if p not in palavras_excluidas] # remove irrelevantes
    return filtradas

def falar(resposta):
  # GPIO.output(Led_azul, GPIO.LOW)
   #GPIO.output(Led_vermelho, GPIO.HIGH)
   time.sleep(1)
   tts=gTTS(text=resposta, lang="pt-br")
   tts.save("resposta3.mp3")
   os.system("mpg123 -q resposta3.mp3")
   #GPIO.output(Led_vermelho, GPIO.LOW)

# --- FUNÇÃO DE RECONHECIMENTO CONTÍNUO ---
def ouvir_e_imprimir_continuo():
    flag=False
    lista_gostos=[]
    # Verifica se o caminho do modelo existe
    if not os.path.isdir(MODEL_PATH):
        print(f"ERRO: Modelo Vosk não encontrado em: {MODEL_PATH}")
        print("Baixe o modelo e ajuste a variável MODEL_PATH.")
        return

    # 1. Carrega o modelo Vosk
    model = vosk.Model(MODEL_PATH)
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    # 2. Configura o PyAudio para capturar o microfone
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    print("--- PRONTO: Fale algo. O texto aparecerá em tempo real. (Ctrl+C para parar) ---")

   #GPIO.output(Led_azul, GPIO.HIGH)
   #GPIO.output(Led_vermelho, GPIO.LOW)
    try:
     
        while True:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
           
            if len(data) == 0:
                break

            # 4. Processa o áudio e verifica se há um resultado
            if rec.AcceptWaveform(data):
                # Resultado final da frase (após uma pausa)
                result = json.loads(rec.Result())
                if result.get("text"):
                    lista_gostos.extend({result['text']})
                    print(f"\n[FINAL]: {result['text']}")
                    falar(random.choice(elogios))
            else:
                # 5. Imprime o resultado parcial em tempo real
                partial = json.loads(rec.PartialResult()).get("partial", "")
                # O '\r' (carriage return) permite reescrever a linha
                print(partial, end='\r', flush=True)
                if palavra_chave_historia in partial.lower() and flag == False:
                    flag=True
                    return lista_gostos
                    print("opaaa")
                    break
                else:
                    if palavra_chave_robo in partial.lower():
                        break
    except KeyboardInterrupt:
        print("\nReconhecimento de fala interrompido pelo usuário.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
    finally:
        # 6. Limpa e fecha os recursos
        stream.stop_stream()
        stream.close()
        p.terminate()

        final_result = json.loads(rec.FinalResult())
        if final_result.get("text"):
            return lista_gostos
             #print(f"[FIM DO ÁUDIO]: {final_result['text']}")
           
   #GPIO.output(Led_azul, GPIO.HIGH)


def main():
    # Apresentação do Robô
    introducao="Olá, eu sou O Barsa Bot, Gosto de fazer perguntas e de interagir escutando vocês. E o que vocês mais gostam de fazer?"
    falar(introducao)
    lista_gostos=ouvir_e_imprimir_continuo()
    print(lista_gostos)
 
    #Gerar história
    falar("Isso que voçês contaram foi muito interessante, baseado nisso, vou contar uma história")
    pergunta="Faça 1 historia de 6 linhas para crianças de 4 anos de idade, com as seguintes caracteristicas:".join(lista_gostos)
    response = model.generate_content(pergunta)
    resposta_texto = response.text
    historia=resposta_texto;
    print(f"Resposta do Gemini: {resposta_texto}")
    falar(resposta_texto)
   
   
    #Palavra chave + MORAL da historia    
    captar = ouvir_e_imprimir_continuo()
    response = model.generate_content("Qual a moral da historia:"+historia)
    resposta_texto = response.text
    print(f"Resposta do Gemini: {resposta_texto}")
    falar(resposta_texto)
   
    #Palavra chave + DESPEDIDA
    despedida="Foi muitooo divertido interagir com voçês. Até mais, BEIJOS "
    falar(despedida);
   
   
       
if __name__ == "__main__":
    main()
