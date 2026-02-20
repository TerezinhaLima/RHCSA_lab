import os
from flask import Flask, jsonify
from flask_cors import CORS
import paramiko
from groq import Groq
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurações do Ambiente
PORT_NODE1 = 2200
PORT_NODE2 = 2201
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')  # Pegue do .env
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def run_check(command, node=1):
    """Executa validação via SSH no node especificado"""
    try:
        port = PORT_NODE1 if node == 1 else PORT_NODE2
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('127.0.0.1', port=port, username='vagrant', password='vagrant')
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        ssh.close()
        return exit_status == 0
    except Exception as e:
        print(f"Erro SSH no node{node}: {e}")
        return False

@app.route('/hint/<int:task_id>')
def get_hint(task_id):
    """Gera a dica usando IA da Groq"""
    
    tasks_context = {
        # NODE 1 - Questões 1-13
        1: "Configurar rede e hostname: IP 10.129.203.120/24, Gateway 10.129.203.112, DNS 10.129.203.112, hostname node1.lab.example.com",
        2: "Configurar repositórios DNF em /etc/yum.repos.d/exam.repo com baseurl file:///mnt/BaseOS e file:///mnt/AppStream",
        3: "Corrigir SELinux: Apache na porta 82 com conteúdo em /var/www/html acessível via http://10.129.203.120:82",
        4: "Criar grupo sysmgrs, usuários john, emma (membros) e michael (sem shell) com senha compedel@314",
        5: "Configurar autofs para montar /rhome/remoteuser18 de serverb.lab.example.com:/rhome/remoteuser18",
        6: "Criar cron job para usuário john executar /bin/echo 'hello world' diariamente às 12:30",
        7: "Configurar cliente NTP para usar classroom.example.com como servidor",
        8: "Encontrar e copiar todos os arquivos de emma para /root/find.user",
        9: "Encontrar todas as ocorrências de 'ich' em /usr/share/dict/words e salvar em /root/lines",
        10: "Criar usuário alex com UID 2345 e senha Compedel@124",
        11: "Criar backup de /usr/local como /root/backup.tar.gz usando gzip",
        12: "Configurar umask para usuário john: arquivos com 444, diretórios com 555",
        13: "Criar script, serviço e timer systemd para capturar lista de arquivos em /tmp a cada minuto",
        
        # NODE 2 - Questões 14-20
        14: "Resetar senha root para compedel@777 via modo rescue",
        15: "Configurar repositórios no node2: file:///mnt/BaseOS e file:///mnt/AppStream",
        16: "Criar partição swap de 756MiB em /dev/sdb e ativar na inicialização",
        17: "Redimensionar volume lógico VO para 230MiB no VG VG",
        18: "Configurar Flatpak para usuário student com repositório flatdb e instalar codium",
        19: "Criar LV 'qa' de 60 extensões (16MiB cada) no VG qagroup em /dev/sdc, formatar ext4 e montar em /mnt/qa",
        20: "Configurar perfil tuned recomendado para o sistema"
    }

    task_desc = tasks_context.get(task_id)
    if not task_desc:
        return jsonify({"hint": "ID da tarefa não encontrado no servidor."})

    if not client:
        return jsonify({"hint": "Dica rápida: " + get_fallback_hint(task_id)})

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um instrutor de Linux RHCSA. Forneça apenas os comandos Linux diretos e objetivos para resolver a tarefa. Inclua explicações breves quando necessário."
                },
                {
                    "role": "user",
                    "content": f"Como resolvo esta tarefa no RHEL 9/Rocky Linux: {task_desc}?"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        return jsonify({"hint": chat_completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"hint": f"Erro na API: {str(e)}. Dica offline: {get_fallback_hint(task_id)}"})

def get_fallback_hint(task_id):
    """Dicas offline caso a API falhe"""
    hints = {
        1: "Use 'nmtui' ou edite /etc/sysconfig/network-scripts/ifcfg-* e /etc/hostname",
        2: "Crie /etc/yum.repos.d/exam.repo com [BaseOS] e [AppStream] apontando para file:///mnt/",
        3: "Instale httpd, configure Listen 82 no httpd.conf, ajuste SELinux: semanage port -a -t http_port_t -p tcp 82",
        4: "groupadd sysmgrs; useradd -G sysmgrs john; useradd -G sysmgrs emma; useradd -s /sbin/nologin michael; passwd para todos",
        5: "yum install autofs; edite /etc/auto.master e /etc/auto.misc; systemctl enable --now autofs",
        6: "crontab -e -u john; adicione '30 12 * * * /bin/echo \"hello world\"'",
        7: "yum install chrony; edite /etc/chrony.conf; systemctl restart chronyd",
        8: "find / -user emma -exec cp -rpvf {} /root/find.user/ \\;",
        9: "grep 'ich' /usr/share/dict/words > /root/lines",
        10: "useradd -u 2345 alex; passwd alex",
        11: "tar --gzip -cvf /root/backup.tar.gz /usr/local",
        12: "su john; umask 277; touch test; mkdir testdir",
        13: "Crie script em /usr/local/bin/log_capture; crie serviço e timer no systemd",
        14: "No boot, edite GRUB: adicione 'rd.break' ou 'rw init=/bin/bash'",
        15: "Mesmo comando da questão 2, mas no node2",
        16: "fdisk /dev/sdb; partição +756M tipo swap; mkswap; /etc/fstab",
        17: "lvresize -L 230M /dev/VG/VO -r",
        18: "su student; flatpak remote-add --user flatdb https://flathub.org/repo/flathub.flatpakrepo",
        19: "fdisk /dev/sdc; pvcreate; vgcreate -s 16M qagroup; lvcreate -l 60 -n qa; mkfs.ext4; montar",
        20: "yum install tuned; tuned-adm recommend; tuned-adm profile [perfil_recomendado]"
    }
    return hints.get(task_id, "Consulte a documentação do RHCSA")

@app.route('/check/<int:task_id>')
def check_task(task_id):
    """Validações automáticas"""
    
    # Validações para Node1 (questões 1-13)
    checks_node1 = {
        1: "hostnamectl status | grep node1.lab.example.com && ip a show | grep 10.129.203.120/24",
        2: "test -f /etc/yum.repos.d/exam.repo && grep -E 'baseurl.*file:///mnt/(BaseOS|AppStream)' /etc/yum.repos.d/exam.repo",
        3: "semanage port -l | grep http_port_t | grep 82 && curl -s http://10.129.203.120:82 | grep -q html",
        4: "id john | grep sysmgrs && id emma | grep sysmgrs && cat /etc/passwd | grep michael | grep nologin",
        5: "systemctl is-active autofs && mount | grep /rhome/remoteuser18",
        6: "crontab -l -u john | grep '30 12.*hello world'",
        7: "chronyc sources | grep -E '\\*|\\+'",
        8: "test -d /root/find.user && find /root/find.user -type f | wc -l",
        9: "test -f /root/lines && grep -q ich /root/lines",
        10: "id alex | grep 'uid=2345'",
        11: "test -f /root/backup.tar.gz && file /root/backup.tar.gz | grep gzip",
        12: "su - john -c 'touch testfile && mkdir testdir && ls -ld testfile testdir' | grep -E 'r--r--r--|r-xr-xr-x'",
        13: "systemctl is-active log_capture.timer && test -f /root/log_output/system_logs.trc"
    }
    
    # Validações para Node2 (questões 14-20)
    checks_node2 = {
        14: "echo 'Validação manual - senha root alterada?'",
        15: "ssh -p 2201 vagrant@127.0.0.1 'test -f /etc/yum.repos.d/exam.repo'",
        16: "ssh -p 2201 vagrant@127.0.0.1 'swapon --show | grep /dev/sdb'",
        17: "ssh -p 2201 vagrant@127.0.0.1 'lvs | grep VO | awk \"{print \\$4}\" | grep -E \"217-243\"'",
        18: "ssh -p 2201 vagrant@127.0.0.1 'su - student -c \"flatpak list | grep codium\"'",
        19: "ssh -p 2201 vagrant@127.0.0.1 'mount | grep /mnt/qa && lvs | grep qa'",
        20: "ssh -p 2201 vagrant@127.0.0.1 'tuned-adm active | grep -v off'"
    }
    
    if task_id <= 13:
        cmd = checks_node1.get(task_id)
        node = 1
    else:
        cmd = checks_node2.get(task_id)
        node = 2
    
    if not cmd:
        return jsonify({"success": False, "msg": "Sem script de validação"})
    
    success = run_check(cmd, node)
    return jsonify({"success": success})

@app.route('/')
def index():
    return jsonify({"status": "RHCSA Lab Server Running", "nodes": ["node1:2200", "node2:2201"]})

if __name__ == '__main__':
    print("="*50)
    print("Servidor Lab RHCSA V10")
    print("Questões: Node1 (1-13) | Node2 (14-20)")
    print("Porta: 5005")
    print("="*50)
    app.run(port=5005, debug=True)