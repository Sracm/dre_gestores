import os
import re

base_dir = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS"

new_configs = {
    "ORACLE_USER": "POWERBI",
    "ORACLE_PASSWORD": "@Yzmpq100#",
    "ORACLE_DSN": "192.168.1.55/ORCL"
}

updated_files = []

for root, dirs, files in os.walk(base_dir):
    # Ignorar pastas de ambiente virtual, git, node_modules etc
    if any(ignore in root for ignore in ['.git', 'venv', 'env', 'node_modules', '__pycache__', '.gemini']):
        continue
        
    if '.env' in files:
        env_path = os.path.join(root, '.env')
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            changed = False
            
            for key, val in new_configs.items():
                if f"{key}=" in new_content:
                    # Substituir o valor existente
                    new_content = re.sub(rf"^{key}=.*", f"{key}={val}", new_content, flags=re.MULTILINE)
                    changed = True
                else:
                    # Adicionar no final se a chave nao existir
                    if not new_content.endswith('\n'):
                        new_content += '\n'
                    new_content += f"{key}={val}\n"
                    changed = True
                    
            if changed and new_content != content:
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_files.append(env_path)
                
        except Exception as e:
            print(f"Erro ao processar {env_path}: {e}")

if updated_files:
    print(f"Atualizados {len(updated_files)} arquivos .env:")
    for f in updated_files:
        print(f"- {f}")
else:
    print("Nenhum arquivo .env precisou de atualização (já estavam com essas credenciais).")
