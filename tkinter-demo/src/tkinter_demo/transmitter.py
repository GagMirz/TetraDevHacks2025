import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
from constants import BAUDRATE, START_TRANSMIT, START_BYTE, END_BYTE, END_TRANSMIT
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def refresh_ports(event=None):
    current_selection = port_var.get()
    ports = list_serial_ports()
    port_combo['values'] = ports
    if current_selection in ports:
        port_combo.set(current_selection)
    elif ports:
        port_combo.current(0)
    else:
        port_combo.set('')

def send_text_thread():
    port = port_var.get()
    if not port:
        status_var.set("Please select a serial port.")
        return

    entered_text = text_box.get("1.0", tk.END).strip()
    if not entered_text:
        status_var.set("The text box is empty.")
        return

    status_var.set("Loading...")
    try:
        with serial.Serial(port, BAUDRATE, timeout=1) as ser:
            text_frame = START_TRANSMIT + bytes([len(entered_text)]) + START_BYTE + entered_text.encode('UTF-8') + END_BYTE + END_TRANSMIT

            ser.write(text_frame)
            ser.flush()
        status_var.set(f"Sent to ESP32 on {port}")
    except serial.SerialException as e:
        status_var.set(f"Error: {e}")

def confirm_text():
    threading.Thread(target=send_text_thread, daemon=True).start()

app = tk.Tk()
app.title("Send Text to ESP32")
app.geometry("500x350")
app.resizable(False, False)

tk.Label(app, text="Select Serial Port and Send Text:").pack(pady=(10, 5))

port_var = tk.StringVar()
port_combo = ttk.Combobox(app, textvariable=port_var, state="readonly", width=30)
port_combo.pack(pady=(5))
port_combo.bind("<Button-1>", refresh_ports)

tk.Label(app, text="Text to send:").pack()

text_box = tk.Text(app, height=12, width=60, wrap=tk.WORD, padx=10, pady=10)
text_box.pack(pady=5, padx=20, fill='x')

text_box.insert(tk.END, "This will be sent to the ESP32 over serial.")

mini_frame = tk.Frame(app)
mini_frame.pack(fill='x', pady=(0, 10), padx=20)

status_var = tk.StringVar()
status_label = tk.Label(mini_frame, textvariable=status_var, anchor='w')
status_label.pack(side='left', fill='x', expand=True)

confirm_button = tk.Button(mini_frame, text="Send to ESP32", command=confirm_text)
confirm_button.pack(side='right')

refresh_ports()
app.mainloop()

if __name__ == '__main__':
    ...
