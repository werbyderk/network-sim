import docker
import os
import time

WAN_NAME = "net_sim_wan"
# GATEWAY_LAN_IP = "192.168.1.2"

docker_client = docker.from_env()

class Host:
    next_device_id = 1
    hosts = []
    def __init__(self, name, py_script_path, py_deps_path, ports, start_cmd):
        self.container = None
        self.connected = False
        try:
            self.name = name
            self.py_script_path = py_script_path
            self.py_deps_path = py_deps_path
            self.ports = ports
            self.start_cmd = start_cmd
            self.id = 'h' + str(Host.next_device_id)
            Host.next_device_id += 1
            # docker run -d --name <name> -p <ports>python:3.10-alpine
            # docker cp python_script.py <name>:/python_script.py
            # docker cp requirements.txt <name>:/requirements.txt
            # docker exec <name> python3 -m pip install -r requirements.txt
            # docker exec <name> python3 python_script.py
            print(f"Starting {self.name}...")
            self.container = docker_client.containers.run(
                'python:3.10-alpine',
                name=name,
                ports={str(port): str(port) for port in ports},
                detach=True,
                cap_add=['NET_ADMIN', 'SYS_ADMIN'],
                privileged=True,
                command=['tail', '-f', '/dev/null'] 
            )

            # Wait for container to be running
            start_time = time.time()
            timeout = 5
            while True:
                self.container.reload()
                if self.container.status == 'running':
                    break
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Container {name} failed to start within {timeout} seconds")
                time.sleep(0.1)

            print(f"Container {name} is running, copying files...")
            
            # Verify container is still running before copying files
            self.container.reload()
            if self.container.status != 'running':
                raise RuntimeError(f"Container {name} is not running after startup")


            script_name = py_script_path.split('/')[-1]
            with open(py_script_path, 'r') as f:
                script_content = f.read().replace('"', '\\"')
            result = self.container.exec_run(['sh', '-c', f'echo "{script_content}" > {script_name}'], workdir='/home')
            if result.exit_code != 0:
                raise RuntimeError(f"Failed to copy script file: {result.output.decode()}")

            with open(py_deps_path, 'r') as f:
                deps_content = f.read().replace('"', '\\"')
            result = self.container.exec_run(['sh', '-c', f'echo "{deps_content}" > requirements.txt'], workdir='/home')
            if result.exit_code != 0:
                raise RuntimeError(f"Failed to copy requirements file: {result.output.decode()}")

            print(f"Installing dependencies for {name}...")
            result = self.container.exec_run(['python3', '-m', 'pip', 'install', '-r', 'requirements.txt'], workdir='/home')
            if result.exit_code != 0:
                raise RuntimeError(f"Failed to install dependencies: {result.output.decode()}")

            # print(f"Starting script for {name}...")
            result = self.container.exec_run(start_cmd.split(' '), workdir='/home', detach=True)
            # if result.exit_code != 0:
            #     raise RuntimeError(f"Failed to start script: {result.output}")
            Host.hosts.append(self)
        except Exception as e:
            print(f"Error creating host {self.name}: {e}")
            self.remove()
            raise e

    def remove(self):
        if self.container is not None:
            self.container.kill()
            self.container.remove()
        Host.hosts.remove(self)



class Gateway:
    next_device_id = 1
    gateways = []
    wan = None

    def config_zebra(self):
        zebra_conf = f"""frr version 8.4_git
frr defaults traditional
!
hostname {self.name}
!
interface eth1
 ip address {self.lan_ip}/{24}
exit
!
interface eth2
 ip address {self.wan_ip}/{24}
exit
!
no ipv6 forwarding
!
"""
        return zebra_conf
    

    def config_staticd(self):
        staticd_conf = f"""
frr version 8.4_git
frr defaults traditional
!
hostname {self.name}
!
!
!
ip route {self.lan_ip}/{24} {self.wan_ip}
!
!
"""
        return staticd_conf
    @staticmethod
    def get_next_wan_ip() -> str:
        return f"10.0.0.{Gateway.next_device_id + 1}"
    
    def __init__(self, name):
        self.name = name
        self.lan = None
        self.container = None
        self.hosts = []
        try: 
            if not Gateway.wan:
                Gateway.wan = docker_client.networks.create(
                    name=WAN_NAME,
                    driver='bridge',
                    ipam={'driver': 'default', 'config': [{'subnet': '10.0.0.0/24'}]}
                )
            Gateway.gateways.append(self)
            self.wan_ip = Gateway.get_next_wan_ip()
            raw_id = Gateway.next_device_id
            self.id = 'g' + str(raw_id)
            Gateway.next_device_id += 1
            self.lan_ip = f"192.168.{raw_id}.2"
            print(f"Creating LAN network {self.name}")
            self.lan = docker_client.networks.create(
                name=self.name,
                driver='bridge',
                ipam={
                    'driver': 'default',
                    'config': [{
                        'subnet': f'192.168.{raw_id}.0/24'
                    }]
                }
            )
            
            print(f"Creating Gateway {self.name}")
            self.container = docker_client.containers.run(
                'frrouting/frr:latest',
                name=name,
                hostname=name,
                cap_add=['NET_ADMIN', 'SYS_ADMIN'],
                privileged=True,
                sysctls={'net.ipv4.ip_forward': 1},
                detach=True
            )


            # Connect to networks with specific IPs
            print(f"Connecting to network {self.name} with IP {self.lan_ip}")
            docker_client.networks.get(self.name).connect(self.container, ipv4_address=self.lan_ip)
            print(f"Connecting to network {WAN_NAME} with IP {self.wan_ip}")
            docker_client.networks.get(WAN_NAME).connect(self.container, ipv4_address=self.wan_ip)

            # Copy config files
            self.write_file_to_container(self.container, '/etc/frr/zebra.conf', self.config_zebra())
            self.write_file_to_container(self.container, '/etc/frr/staticd.conf', self.config_staticd())

            print(f"Wrote config files. Restarting {self.name}.")
            self.container.restart()
            start_time = time.time()
            timeout = 5 
            while True:
                self.container.reload() 
                if self.container.status == 'running':
                    break
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Container {name} failed to start within {timeout} seconds")
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error creating gateway {self.name}: {e}")
            self.remove()
            raise e

    def write_file_to_container(self, container, path, content):
        # Create the directory if it doesn't exist
        container.exec_run(f'mkdir -p {os.path.dirname(path)}')
        # Write the content to the file
        container.exec_run(f'echo "{content}" > {path}')

    def add_host(self, host, ip):
        host.ip = ip
        
        # Connect host to network with specific IP
        docker_client.networks.get(self.name).connect(
            docker_client.containers.get(host.name),
            ipv4_address=ip
        )
        # 32 bit mask to treat all other ips as remote (route through gateway)
        docker_client.containers.get(host.name).exec_run([
            'ip', 'route', 'add', self.lan_ip, 'dev', 'eth1'
        ])
        docker_client.containers.get(host.name).exec_run([
            'ip', 'addr', 'add', f'{ip}/{32}', 'dev', 'eth1'
        ])
        docker_client.containers.get(host.name).exec_run([
            'ip', 'addr', 'del', f'{ip}/{24}', 'dev', 'eth1'
        ])

        # Add default route
        docker_client.containers.get(host.name).exec_run(
            ['ip', 'route', 'del', 'default']
        )
        docker_client.containers.get(host.name).exec_run(
            ['ip', 'route', 'add', 'default', 'via', self.lan_ip]
        )
        
        host.connected = True
        self.hosts.append(host)

    def remove(self):
        while self.hosts:
            host = self.hosts.pop()
            print(f"Removing host {host.name}")
            host.remove()
        if self.container is not None:
            self.container.kill()
            self.container.remove()
        if self.lan is not None:
            self.lan.remove()
        Gateway.gateways.remove(self)
        print(f"Removed gateway {self.name}")


if __name__ == "__main__":
    # List all networks
    for network in docker_client.networks.list():
        print(f"Network: {network.name}, Subnet: {network.attrs['IPAM']['Config']}")
    try:
        gateway = Gateway("gateway1")
        host1 = Host("host1", "client/client.py", "client/requirements.txt", None, "python3 client.py")
        host2 = Host("host2", "server/server.py", "server/requirements.txt", {"8081": "8081"}, "python3 server.py")
        gateway.add_host(host1, "192.168.1.100")
        gateway.add_host(host2, "192.168.1.101")
        print("Done. Press Enter to exit.")
        input()
        gateway.container.kill()
        gateway.container.remove()
        host1.container.kill()
        host1.container.remove()
        host2.container.kill()
        host2.container.remove()
        Gateway.wan.remove()
        gateway.lan.remove()
    except Exception as e:
        print(f"Error: {e}")
        if gateway is not None:
            gateway.container.kill()
            gateway.container.remove()
        # if host1 is not None:
        #     host1.container.kill()
        #     host1.container.remove()
        # if host2 is not None:
        #     host2.container.kill()
        #     host2.container.remove()
        # if Gateway.wan is not None:
        #     Gateway.wan.remove()

