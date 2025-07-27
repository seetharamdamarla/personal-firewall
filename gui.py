import tkinter as tk

class FirewallGUI:
    def __init__(self, root, packet_queue):
        self.root = root
        self.queue = packet_queue
        self.packet_count = 0

        self.root.title("Python Firewall Monitor")
        self.root.geometry("350x220")
        self.root.resizable(False, False)

        self.status_label = tk.Label(root, text="Status: Starting...", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.packet_label = tk.Label(root, text="Packets Processed: 0", font=("Arial", 12))
        self.packet_label.pack(pady=5)

        self.action_label = tk.Label(root, text="Last Action: -", font=("Arial", 12))
        self.action_label.pack(pady=5)

        self.src_label = tk.Label(root, text="Source IP: -", font=("Arial", 12))
        self.src_label.pack(pady=5)

        self.proto_label = tk.Label(root, text="Protocol: -", font=("Arial", 12))
        self.proto_label.pack(pady=5)

        self.update_gui()

    def update_gui(self):
        while not self.queue.empty():
            data = self.queue.get()
            self.packet_count += 1

            self.status_label.config(text="Status: Running")
            self.packet_label.config(text=f"Packets Processed: {self.packet_count}")
            self.action_label.config(text=f"Last Action: {data['action']}")
            self.src_label.config(text=f"Source IP: {data['src_ip']}")
            self.proto_label.config(text=f"Protocol: {data['protocol']}")

        self.root.after(500, self.update_gui)

def start_gui(packet_queue):
    root = tk.Tk()
    app = FirewallGUI(root, packet_queue)
    root.mainloop()
