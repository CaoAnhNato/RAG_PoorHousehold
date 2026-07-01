import os
import sys
import subprocess
import time

print("Terminating existing streamlit processes...")
subprocess.run('wmic process where "commandline like \'%streamlit%\'" call terminate', shell=True)
time.sleep(2)

print("Starting new streamlit process...")
python_exe = os.path.join("venv", "Scripts", "python.exe")
streamlit_script = os.path.join("app", "streamlit_chatbot.py")

subprocess.Popen(
    [python_exe, "-m", "streamlit", "run", streamlit_script],
    creationflags=subprocess.CREATE_NO_WINDOW
)
print("Restart initiated successfully.")
