# assemble_single_file.py
import os

with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

with open("app.js", "r", encoding="utf-8") as f:
    js_content = f.read()

# Replace <script src="app.js"></script> with inline script
inline_script = f"<script>\n{js_content}\n</script>"
final_single_file = html_content.replace('<script src="app.js"></script>', inline_script)

if os.path.exists("ic_vault_minimal.png"):
    import base64
    with open("ic_vault_minimal.png", "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
    final_single_file = final_single_file.replace('src="ic_vault_minimal.png"', f'src="data:image/png;base64,{img_b64}"')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_single_file)

os.makedirs("app/src/main/assets", exist_ok=True)
with open("app/src/main/assets/index.html", "w", encoding="utf-8") as f:
    f.write(final_single_file)

print(f"Successfully generated single-file index.html ({len(final_single_file)} bytes) in root and in app/src/main/assets/")
