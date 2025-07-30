import tkinter as tk
from queue import Queue

class FirewallGUI:
    def __init__(self, root, packet_queue):
        self.root = root
        self.queue = packet_queue
        self.packet_count = 0
        self.monitoring = False  

        self.root.title("Personal Firewall Monitor")
        self.root.geometry("700x450")
        self.root.configure(bg="#0d0d0d")
        self.root.resizable(False, False)

        self.heading = tk.Label(root, text="Real-Time Packet Monitor",
                                font=("Consolas", 20, "bold"), fg="#00ff00", bg="#0d0d0d")
        self.heading.pack(pady=15)
        self.info_frame = tk.Frame(root, bg="#1a1a1a", bd=2, relief="groove")
        self.info_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.status_label = self.create_label("Status: Not Monitoring")
        self.packet_label = self.create_label("Packets Processed: 0")
        self.action_label = self.create_label("Last Action: -")
        self.src_label = self.create_label("Source IP: -")
        self.proto_label = self.create_label("Protocol: -")

        self.button_frame = tk.Frame(root, bg="#0d0d0d")
        self.button_frame.pack(pady=10)

        self.start_button = self.create_button("Start Monitoring", self.start_monitoring)
        self.pause_button = self.create_button("Pause Monitoring", self.pause_monitoring)
        self.stop_button = self.create_button("Stop Firewall", self.stop_firewall)

        self.update_gui()

    def create_label(self, text):
        label = tk.Label(self.info_frame, text=text, font=("Consolas", 14),
                         fg="#33ff33", bg="#1a1a1a", anchor="w")
        label.pack(fill="x", padx=20, pady=6)
        return label

    def create_button(self, text, command):
        btn = tk.Button(self.button_frame, text=text, font=("Consolas", 12, "bold"),
                        fg="#00ff00", bg="#262626", activebackground="#009900",
                        activeforeground="white", command=command, width=18, bd=0)
        btn.pack(side="left", padx=15)
        return btn

    def start_monitoring(self):
        self.monitoring = True
        self.status_label.config(text="Status: Running")

    def pause_monitoring(self):
        self.monitoring = False
        self.status_label.config(text="Status: Paused")

    def stop_firewall(self):
        self.root.destroy()

    def update_gui(self):
        if self.monitoring:
            while not self.queue.empty():
                data = self.queue.get()
                self.packet_count += 1

                self.packet_label.config(text=f"Packets Processed: {self.packet_count}")
                self.action_label.config(text=f"Last Action: {data['action']}")
                self.src_label.config(text=f"Source IP: {data['src_ip']}")
                self.proto_label.config(text=f"Protocol: {data['protocol']}")

        self.root.after(500, self.update_gui)

def start_gui(packet_queue):
    root = tk.Tk()
    FirewallGUI(root, packet_queue)
    root.mainloop()

if __name__ == "__main__":
    from threading import Thread
    import time

    def simulate_packets(q):
        dummy_data = [
            {"action": "Allowed", "src_ip": "192.168.1.5", "protocol": "TCP"},
            {"action": "Blocked", "src_ip": "10.0.0.8", "protocol": "UDP"},
            {"action": "Allowed", "src_ip": "172.16.0.3", "protocol": "ICMP"},
        ]
        while True:
            for pkt in dummy_data:
                q.put(pkt)
                time.sleep(1)

    q = Queue()
    t = Thread(target=simulate_packets, args=(q,), daemon=True)
    t.start()

    start_gui(q)
