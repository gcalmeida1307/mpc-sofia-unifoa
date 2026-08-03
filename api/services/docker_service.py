import subprocess


class DockerService:
    def list_containers(self):
        try:
            result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, check=True)
            return result.stdout.strip().splitlines()
        except Exception as exc:
            return {"error": str(exc)}

    def restart_container(self, name: str):
        try:
            subprocess.run(["docker", "restart", name], capture_output=True, text=True, check=True)
            return {"status": "ok", "container": name}
        except Exception as exc:
            return {"error": str(exc)}
