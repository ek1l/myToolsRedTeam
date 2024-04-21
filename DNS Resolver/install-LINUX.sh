#!/bin/bash

 
if ! command -v python3 &>/dev/null; then
  echo "Python 3 não está instalado. Por favor, instale Python 3 para continuar."
  exit 1
fi


if ! command -v pip3 &>/dev/null; then
  echo "pip não está instalado. Por favor, instale pip para continuar."
  exit 1
fi

pip3 install -r requirements.txt

echo "Instalação concluída!"
