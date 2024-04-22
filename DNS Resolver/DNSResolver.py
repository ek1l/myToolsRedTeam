import sys
import socket
import requests
import argparse
import os
import threading
from queue import Queue, Empty
from colorama import Fore, Style, init
import signal
from tqdm import tqdm
import time   

init(autoreset=True)


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


clear_terminal()

ascii_art = """
$$$$$$$$\\ $$\\   $$\\   $$\\   $$\\
$$  _____|$$ | $$  |$$$$ |  $$ |
$$ |      $$ |$$  / \\_$$ |  $$ |
$$$$$\\    $$$$$  /    $$ |  $$ |
$$  __|   $$  $$<     $$ |  $$ |
$$ |      $$ |\\$$\\    $$ |  $$ |
$$$$$$$$\\ $$ | \\$$\\ $$$$$$\\ $$$$$$$$\\
\\________|\\__|  \\__|\\______|\\________|



$$$$$$$$\\  $$$$$$\\   $$$$$$\\  $$\\       $$$$$$\\
\\__$$  __|$$  __$$\\ $$  __$$\\ $$ |     $$  __$$\\
   $$ |   $$ /  $$ |$$ /  $$ |$$ |     $$ /  \\__|
   $$ |   $$ |  $$ |$$ |  $$ |$$ |     \\$$$$$$\\
   $$ |   $$ |  $$ |$$ |  $$ |$$ |      \\____$$\\
   $$ |   $$ |  $$ |$$ |  $$ |$$ |     $$\\   $$ |
   $$ |    $$$$$$  | $$$$$$  |$$$$$$$$\\ \\$$$$$$  |
   \\__|    \\______/  \\______/ \\________| \\______/
"""

print(ascii_art + "®")


parser = argparse.ArgumentParser(
    description='Testar subdomínios com HTTP e HTTPS', add_help=False
)
parser.add_argument('domain', type=str, help='O domínio a ser testado')
parser.add_argument('wordlist', type=str, help='Caminho para a wordlist de subdomínios (arquivo local ou URL)')
parser.add_argument('threads', type=int, help='Número de threads a serem usadas')

if len(sys.argv) < 4:
    print(f"{Fore.RED}Faltam argumentos.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Siga os argumentos necessários: domain, wordlist, threads{Style.RESET_ALL}")
    sys.exit(1)

args = parser.parse_args()

domain = args.domain
wordlist_source = args.wordlist
num_threads = args.threads


try:
    if wordlist_source.startswith('http://') or wordlist_source.startswith('https://'):
        response = requests.get(wordlist_source)
        response.raise_for_status()
        lista_prefixos = response.text.split('\n')
    else:
        with open(wordlist_source, 'r') as file:
            lista_prefixos = file.readlines()
except Exception as e:
    print(f"{Fore.RED}Erro ao carregar a wordlist: {e}{Style.RESET_ALL}")
    sys.exit(1)

lista_prefixos = [x.strip() for x in lista_prefixos if x.strip()]

subdomain_queue = Queue()

continue_execution = True

progress_bar = tqdm(total=len(lista_prefixos), desc="Progresso", unit="subdomínio")


def resolve_subdomain():
    while continue_execution:
        try:
            prefix = subdomain_queue.get(timeout=1)
        except Empty:
            break

        sub = f"{prefix}.{domain}"
        try:
        
            ip = socket.gethostbyname(sub)

        
            sistemas = []
            for protocol in ['http', 'https']:
                url = f"{protocol}://{sub}"
                try:
                    r = requests.get(url, timeout=3)
                    if r.status_code in {200, 301, 302, 303, 201, 202, 203}:
                        sistemas.append(url)
                except requests.exceptions.RequestException:
                    pass

           
            info_ip = requests.get(f"https://rdap.db.ripe.net/ip/{ip}")
            bloco_ip = info_ip.json().get('handle', 'Desconhecido')

            sistema_str = ", ".join(sistemas) if sistemas else "Nenhum sistema acessível"

            print(
                f"{Fore.CYAN}Sub Domínio: {sub} -> {Fore.GREEN}IP: {ip} -> {Fore.YELLOW}Bloco IP: {bloco_ip}, {Fore.BLUE}Sistema(s): {sistema_str}{Style.RESET_ALL}"
            )
        except socket.gaierror:
            pass 
        except Exception as e:
            print(f"{Fore.RED}Erro ao testar subdomínio {sub}: {e}{Style.RESET_ALL}")

        subdomain_queue.task_done()
        progress_bar.update(1)

      
        time.sleep(0.5) 


for prefix in lista_prefixos:
    subdomain_queue.put(prefix)

threads = []


for _ in range(num_threads):
    thread = threading.Thread(target=resolve_subdomain)
    thread.daemon = True
    thread.start()
    threads.append(thread)


def signal_handler(signal, frame):
    global continue_execution
    continue_execution = False
    print(f"{Fore.RED}Interrupção detectada, parando a execução...{Style.RESET_ALL}")

signal.signal(signal.SIGINT, signal_handler)


subdomain_queue.join()

progress_bar.close()


for thread in threads:
    thread.join()
