import pandas as pd 
import matplotlib.pyplot as plt
import datetime
from datetime import datetime


PATH = "data/battery/"


def battery_data_reader(node_id):
    columns = ["datetime", "voltage_drop", "f1_", "battery_percentage", "conf_id", "installation_ref", "node_id"]

    if node_id == 1: 
        df_ = pd.read_parquet(f"{PATH}battery_node1.parquet", engine = "pyarrow")
    elif node_id == 2: 
        df_ = pd.read_parquet(f"{PATH}battery_node2.parquet", engine = "pyarrow")
    else: 
        raise ValueError("Node ID must be 1 or 2")
    df_.columns = columns
    return df_
    
def main(): 

    n1 = battery_data_reader(1)
    n2 = battery_data_reader(2)

    print("Plotting battery data for node 1")
    plt.figure(figsize=(16,4))
    plt.plot(n1.datetime, n1.voltage_drop, marker = "o", linestyle = "None", color = "blue", label = "Node 1")
    plt.plot(n2.datetime, n2.voltage_drop, marker = "o", linestyle = "None", color = "red", label = "Node 2")
    plt.title("Voltage drop over time")
    plt.xlabel("Time")
    plt.ylabel("Voltage drop")
    plt.ylim([3.8,4.4])
    plt.show()




if __name__ == "__main__": 
    main()

    
    