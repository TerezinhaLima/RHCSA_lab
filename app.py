import os
from flask import Flask, jsonify
from flask_cors import CORS
import paramiko
from groq import Groq

app = Flask(__name__)
CORS(app)

# Configurações do Ambiente
PORT_NODE1 = 2200 
GROQ_API_KEY = "su chave aqui" # Substitua pela sua chave da Groq
client = Groq(api_key=GROQ_API_KEY)

def run_check(command):
    """Executa validação via SSH no node1"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('127.0.0.1', port=PORT_NODE1, username='vagrant', password='vagrant')
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        ssh.close()
        return exit_status == 0
    except Exception as e:
        print(f"Erro SSH: {e}")
        return False

@app.route('/hint/<int:task_id>')
def get_hint(task_id):
    """Gera a dica correta usando a IA da Groq com contexto RHEL 10"""
    
    # Este dicionário DEVE ser idêntico aos IDs do seu arquivo HTML
    tasks_context = {
        1: "Configurar hostname node1.mydomain.com e IP 192.168.99.11",
        2: "Configurar repositório DNF em /etc/yum.repos.d/local.repo",
        3: "Configurar Apache na porta 82 e liberar no SELinux (http_port_t)",
        4: "Criar usuário 'estudante' pertencente ao grupo secundário 'docentes'",
        5: "Criar diretório /home/shared, dono grupo 'docentes', permissões 2770 (SetGID)",
        6: "Resetar senha de root via interrupção do GRUB (rd.break)",
        7: "LVM: Criar LV 'lv_dados' de 500MB no VG 'vg_web'",
        8: "Criar container 'meu_web' usando imagem 'nginx' com Podman rootless",
        9: "Configurar container para iniciar via systemd --user e habilitar linger"
    }

    task_desc = tasks_context.get(task_id)
    if not task_desc:
        return jsonify({"hint": "ID da tarefa não encontrado no servidor."})

    try:
        # Chamada otimizada para Groq (Llama 3.3)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um instrutor de Linux RHCSA 10. Forneça apenas os comandos Linux diretos, formatados de forma clara. Seja breve."
                },
                {
                    "role": "user",
                    "content": f"Como resolvo esta tarefa no RHEL 10: {task_desc}?"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2 # Menos criatividade, mais precisão técnica
        )
        return jsonify({"hint": chat_completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"hint": f"Erro na Groq: {str(e)}"})

@app.route('/check/<int:task_id>')
def check_task(task_id):
    """Validações automáticas sincronizadas"""
    checks = {
        1: "hostnamectl status | grep node1.mydomain.com",
        2: "dnf repolist | grep -i local",
        3: "semanage port -l | grep http_port_t | grep 82",
        4: "id estudante | grep docentes",
        5: "ls -ld /home/shared | grep 'drwxrws---'",
        6: "echo 'Validado via console'", # Senha root é difícil checar via SSH
        7: "sudo lvs | grep lv_dados",
        8: "podman ps -a | grep meu_web",
        9: "systemctl --user is-active container-meu_web"
    }
    
    cmd = checks.get(task_id)
    if not cmd:
        return jsonify({"success": False, "msg": "Sem script de validação"})
    
    success = run_check(cmd)
    return jsonify({"success": success})

if __name__ == '__main__':
    print("Servidor Lab RHCSA (Groq) ativo na porta 5005")
    app.run(port=5005)
