import sys
import clr

assembly_path = r"C:\Program Files\Microsoft.NET\ADOMD.NET\160\Microsoft.AnalysisServices.AdomdClient.dll"
clr.AddReference(assembly_path)
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

conn_str = "Data Source=localhost:60886"
query = """
EVALUATE
FILTER(
    SUMMARIZE(
        'dCentro Resultado',
        'dCentro Resultado'[CENCUS],
        'dCentro Resultado'[DESCRCENCUS]
    ),
    CONTAINSSTRING(UPPER('dCentro Resultado'[DESCRCENCUS]), "LOGISTICA")
)
"""

try:
    conn = AdomdConnection(conn_str)
    conn.Open()
    cmd = AdomdCommand(query, conn)
    reader = cmd.ExecuteReader()
    while reader.Read():
        print(f"{reader.GetValue(0)} - {reader.GetValue(1)}")
    conn.Close()
except Exception as e:
    print(f"Error: {e}")
