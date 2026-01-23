# Laboratório Vagrant para Red Hat Enterprise Linux RHCSA 10 (Exame EX200) usando Rocky 9.6

Este repositório contém um ambiente automatizado para estudos do exame RHCSA 10, utilizando o Rocky Linux 9.6 como base.

## 🚀 Como usar este laboratório

1.  **Pré-requisitos:**
    *   [Instalar o VirtualBox](https://www.virtualbox.org)
    *   [Instalar o Vagrant](https://developer.hashicorp.com)

2.  **Preparação do Ambiente:**
    Abra uma janela do terminal PowerShell e execute:
    ```powershell
    mkdir ~/vagrant
    cd ~/vagrant
    ```

3.  **Configuração dos Arquivos:**
    *   Baixe o arquivo `.zip` deste repositório e coloque-o no diretório `~/vagrant`.
    *   Extraia o conteúdo, recorte e cole-o diretamente na pasta `~/vagrant`.
    *   **Limpeza:** Exclua o arquivo `.zip` e a pasta vazia que restou da extração.

4.  **Subindo as Máquinas:**
    Execute o comando abaixo para construir as VMs automaticamente com base no `Vagrantfile`:
    ```bash
    vagrant up
    ```
    *O script configurará 3 VMs: **ansible**, **node1** e **node2**.*

5.  **Acesso às Máquinas:**
    Em três terminais separados, execute os comandos para acessar cada box via SSH:
    ```bash
    vagrant ssh ansible
    ```
    ```bash
    vagrant ssh node1
    ```
    ```bash
    vagrant ssh node2
    ```
    *A partir do acesso, você pode praticar configurações em `/etc/ssh/sshd_config`, alterar senhas de root e outras tarefas do exame.*

    ## 🌐 Acesso Remoto via Web (ttyd)

Para acessar o terminal das suas VMs via navegador na porta **7681**, adicione este script de provisionamento ao seu `Vagrantfile` ou execute-o dentro das máquinas:

### Instalação e Liberação de Porta
Este comando instala o repositório EPEL, o pacote `ttyd` e configura o Firewall do Rocky 9:

```bash
# Instalar dependências e ttyd
cd c:/RHCSA_lab
vagrant ssh anssible
sudo dnf install -y epel-release
sudo dnf install -y ttyd

# Abrir a porta 7681 no FirewallD
sudo firewall-cmd --permanent --add-port=7681/tcp
sudo firewall-cmd --reload

# Iniciar o ttyd (exemplo de execução em background na porta 7681)
# Substitua 'bash' pelo shell desejado
ttyd -p 7681 bash &
### 🐍 Dependências de Python (Ambiente de Automação)

Como este laboratório foca em **Ansible** para o exame RHCSA 10, os seguintes pacotes Python são instalados automaticamente ou necessários para o funcionamento dos nós:

*   **Python 3.9+**: Versão padrão do Rocky 9 (utilizada para rodar o core do Ansible).
*   **python3-pip**: Gerenciador de pacotes para extensões adicionais.
*   **python3-libxml2 / python3-libxslt**: Dependências comuns para manipulação de arquivos XML/HTML em automações.
*   **Selinux Python Bindings**: Necessário para que o Ansible gerencie permissões de SELinux nas VMs.

#### Script de instalação rápida das dependências (Provisionamento):
Caso queira garantir que todas as dependências de Python estejam presentes para o Ansible, utilize este comando:

```bash
# Instalando dependências de Python no nó Ansible e nos Nodes
sudo dnf install -y python3 python3-pip python3-devel

# Dependência específica para o Ansible gerenciar o SELinux (Essencial para o exame)
sudo dnf install -y python3-policycoreutils


## 🛠️ Comandos de Gerenciamento

| Ação | Comando |
| :--- | :--- |
| **entra no diretorio**  | `cd c:/RHCSA_lab` |
| **roda python** | `python app.py` |
| **Parar** todas as VMs | `vagrant halt` |
| **Reiniciar** todas as VMs | `vagrant reload` |
| **Excluir (Destruir)** todas as VMs | `vagrant destroy` |

---

## 📝 Minha Lista de Tarefas (To-do List)

- [ ] **Compatibilidade Linux:** Atualmente testado apenas no Windows 11. Em breve, versão para distribuições Linux usando o provedor `libvirt`.
- [ ] **Interface Gráfica (GUI):** Investigar provisionamento para habilitar GNOME:
  ```ruby
  config.vm.provision "shell", inline: <<-SHELL
    sudo yum -y groupinstall @"GNOME Desktop"
    sudo systemctl set-default graphical.target
    sudo systemctl isolate graphical.target
  SHELL
