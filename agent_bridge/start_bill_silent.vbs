Set WshShell = CreateObject("WScript.Shell")
' Ejecuta el script de Python de forma totalmente invisible (0)
WshShell.Run "pythonw.exe c:\Users\hp\aivideogen\agent_bridge\bill_receiver.py", 0
Set WshShell = Nothing
