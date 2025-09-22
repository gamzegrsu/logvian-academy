import docker
import os
import time

# --- Docker Client TCP üzerinden ---
docker_client = None
try:
    # Docker Desktop TCP ayarını açtıysan:
    # Settings → General → "Expose daemon on tcp://localhost:2375 without TLS"
    docker_client = docker.DockerClient(base_url="tcp://localhost:2375")
    docker_client.ping()
    print("✅ Docker istemcisi başarıyla bağlandı (TCP üzerinden)")
except Exception as e:
    print(f"⚠️ Docker bağlantısı atlanıyor: {e}")
    docker_client = None
    print("💡 Docker Lab’ları çalıştırmak için Docker Desktop’ta TCP’yi açın")

def start_lab_container(task_id: str, user_id: str):
    if docker_client is None:
        raise RuntimeError("Docker client bağlı değil. Lab çalıştırılamıyor.")

    container_name = f"lab_{task_id}_{user_id}"
    image_name = f"lab_{task_id}:latest"

    # Lab container’ı çalıştır
    container = docker_client.containers.run(
        image_name,
        name=container_name,
        detach=True,
        ports={"5000/tcp": None},  # random port
    )

    # Port mapping hazır olana kadar bekle
    time.sleep(2)
    container.reload()
    host_port = container.attrs["NetworkSettings"]["Ports"]["5000/tcp"][0]["HostPort"]

    host = os.getenv("LAB_HOST", "localhost")
    url = f"http://{host}:{host_port}"

    return {
        "container_name": container_name,
        "lab_url": url,
        "task_id": task_id
    }

def stop_lab_container(container_name: str):
    if docker_client is None:
        raise RuntimeError("Docker client bağlı değil. Lab durdurulamıyor.")

    container = docker_client.containers.get(container_name)
    container.stop()
    container.remove()
    return True

def list_running_labs():
    if docker_client is None:
        return {}

    labs = {}
    for c in docker_client.containers.list():
        if c.name.startswith("lab_"):
            ports = c.attrs["NetworkSettings"]["Ports"]
            host_port = ports["5000/tcp"][0]["HostPort"]
            labs[c.name] = {
                "status": c.status,
                "url": f"http://{os.getenv('LAB_HOST', 'localhost')}:{host_port}"
            }
    return labs

