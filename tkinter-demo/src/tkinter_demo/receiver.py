import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading
import time
from constants import BAUDRATE, START_TRANSMIT, END_TRANSMIT

root = tk.Tk()
root.title("Arduino Serial Reader")

serial_port = {'conn': None}
running = {'status': False}
serial_thread = {'thread': None}

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def toggle_connection():
    if running['status']:
        running['status'] = False
        connect_btn.config(text="Connect")
    else:
        port = port_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a serial port.")
            return
        try:
            serial_port['conn'] = serial.Serial(port, BAUDRATE, timeout=1)
            time.sleep(2)
            running['status'] = True
            connect_btn.config(text="Disconnect")
            serial_thread['thread'] = threading.Thread(target=read_serial, daemon=True)
            serial_thread['thread'].start()
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", str(e))

def disconnect_on_port_change():
    if running['status']:
        messagebox.showinfo("Disconnected", "Port changed. Disconnecting current connection.")
        running['status'] = False
        connect_btn.config(text="Connect")
        if serial_port['conn'] and serial_port['conn'].is_open:
            serial_port['conn'].close()

def read_serial():
    buffer = []
    is_open = False

    with open("arduino_log.txt", "a") as file:
        while running['status'] and serial_port['conn'].is_open:
            try:
                if serial_port['conn'].in_waiting:
                    lineAsByte = serial_port['conn'].readline()
                    if lineAsByte != b' \r\n':
                      lineAsByte = lineAsByte.strip()
                    else:
                      lineAsByte = bytes([0x20])
                    print(lineAsByte)
                    if lineAsByte:
                      if lineAsByte == START_TRANSMIT:
                        buffer.append(lineAsByte)
                        is_open = True
                      elif lineAsByte == END_TRANSMIT and len(buffer) > 4:
                        if is_open:
                            buffer.append(lineAsByte)
                            is_open = False
                            gathered_data_size = buffer[1][0]
                            print(is_open)
                            print(buffer)
                            if gathered_data_size == len(buffer) - 5:

                              payload = [i.decode('utf-8') for i  in buffer[3:-2]]
                              print(payload)
                              print(payload)
                              timestamped = f"[{time.strftime('%H:%M:%S')}] {''.join(payload)}"
                              text_area.configure(state='normal')
                              text_area.insert(tk.END, timestamped + '\n')
                              text_area.see(tk.END)
                              text_area.configure(state='disabled')

                              buffer = []
                              is_open = False
                            else:
                              print("Data size mismatch:", gathered_data_size, len(buffer))

                              buffer = []
                              is_open = False
                        else :
                            print("Received END_TRANSMIT without START_TRANSMIT")

                            buffer = []
                            is_open = False

                      elif is_open:
                        buffer.append(lineAsByte)
                      else:
                        print("Received data outside of START_TRANSMIT/END_TRANSMIT block:", text_area)

            except Exception as e:
                print("Read error:", e)
                break
    if serial_port['conn'] and serial_port['conn'].is_open:
        serial_port['conn'].close()

top_frame = ttk.Frame(root, padding=10)
top_frame.pack(fill='x')

ttk.Label(top_frame, text="Serial Port:").pack(side='left')
port_var = tk.StringVar()
port_var = tk.StringVar()
port_var.trace_add("write", lambda *args: disconnect_on_port_change())
port_combo = ttk.Combobox(top_frame, textvariable=port_var, width=30)
port_combo['values'] = list_serial_ports()
port_combo.pack(side='left', padx=5)

connect_btn = ttk.Button(top_frame, text="Connect", command=toggle_connection)
connect_btn.pack(side='left', padx=10)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_area.configure(state='disabled')
text_area.pack(padx=10, pady=10, fill='both', expand=True)

root.mainloop()

if __name__ == '__main__':
  ...
