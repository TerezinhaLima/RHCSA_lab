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

## 🛠️ Comandos de Gerenciamento

| Ação | Comando |
| :--- | :--- |
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
