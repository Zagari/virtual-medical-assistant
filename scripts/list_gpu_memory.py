import subprocess

def list_gpu_processes():

      result = subprocess.run(
          ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
           "--format=csv,noheader,nounits"],
          capture_output=True, text=True
      )

      if result.returncode != 0:
          print("Erro ao executar nvidia-smi:", result.stderr.strip())
          return

      lines = result.stdout.strip().split("\n")
      if not lines or lines == [""]:
          print("Nenhum processo usando a GPU.")
          return

      print(f"{'PID':<10} {'Processo':<40} {'Memória (MiB)':<15}")
      print("-" * 65)
      for line in lines:
          pid, name, mem = [x.strip() for x in line.split(",")]
          print(f"{pid:<10} {name:<40} {mem:<15}")

if __name__ == "__main__":
      list_gpu_processes()
