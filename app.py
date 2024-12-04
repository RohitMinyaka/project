import tkinter as tk
import customtkinter
import psutil
import socket
import winreg
import serial.tools.list_ports
import platform
from datetime import datetime

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class SystemInfoApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("System Information")
        self.geometry("1200x700")
        self.resizable(True, True)

        self.data_cache = {}

        # Set the window icon
        self.iconbitmap("w.ico")  # Replace with the actual path to your .ico file


        # Create tabview for dashboard with tabs on top
        self.tabview = customtkinter.CTkTabview(self, corner_radius=10)
        self.tabview.pack(expand=True, fill="both")

        # Create tabs without font argument here
        self.create_tabs()

        # Footer section
        self.footer_frame = customtkinter.CTkFrame(self)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Theme selection dropdown in footer
        self.theme_var = tk.StringVar(value="System")
        self.theme_dropdown = customtkinter.CTkOptionMenu(
            master=self.footer_frame,
            variable=self.theme_var,
            values=["System", "Dark", "Light"],
            command=self.change_theme,
            font=("Arial", 18)
        )
        self.theme_dropdown.pack(side=tk.LEFT, padx=10, pady=10)

        # Refresh button in footer
        self.refresh_button = customtkinter.CTkButton(self.footer_frame, text="Refresh", command=self.refresh_info, font=("Arial", 18))
        self.refresh_button.pack(side=tk.LEFT, padx=10, pady=10)

    def create_tabs(self):

        self.info_tab = self.tabview.add("Detailed Info")
        self.create_info_buttons()


        self.dashboard_tab = self.tabview.add("Dashboard")
        self.create_dashboard_content()

        
        self.info_text_box = customtkinter.CTkTextbox(self.info_tab, height=20, font=("Arial", 24))
        self.info_text_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.info_tab.columnconfigure(0, weight=1)
        self.info_tab.rowconfigure(1, weight=1)

    def create_dashboard_content(self):
        self.dashboard_frame = customtkinter.CTkFrame(self.dashboard_tab, corner_radius=15, fg_color="#2d2d2d")
        self.dashboard_frame.pack(padx=20, pady=20, fill="both", expand=True)

        info = [
            ("System Summary", self.get_system_info_summary()),
            ("Memory Usage", self.get_memory_info()),
            ("CPU Usage", self.get_cpu_info())
        ]
        for title, content in info:
            card = self.create_info_card(title, content)
            card.pack(padx=20, pady=10, fill="both", expand=True)

    def create_info_card(self, title, content):
        card_frame = customtkinter.CTkFrame(self.dashboard_frame, corner_radius=10, fg_color="#1c1c1c")
        card_label = customtkinter.CTkLabel(card_frame, text=title, font=("Arial", 18, "bold"), text_color="white")
        card_label.pack(padx=10, pady=10)
        card_content = customtkinter.CTkLabel(card_frame, text=content, font=("Arial", 18), text_color="white")
        card_content.pack(padx=10, pady=10)
        return card_frame

    def get_system_info(self):
        if "system_info" not in self.data_cache:
            self.data_cache["system_info"] = {
                "Platform": platform.system(),
                "Release": platform.release(),
                "Version": platform.version(),
                "Machine": platform.machine(),
                "Processor": platform.processor(),
                "Device Name": socket.gethostname()
            }
        return self.data_cache["system_info"]

    def get_system_info_summary(self):
        info = self.get_system_info()
        return "\n".join([f"{key}: {value}" for key, value in info.items()])

    def get_memory_info(self):
        if "memory_info" not in self.data_cache:
            memory = psutil.virtual_memory()
            self.data_cache["memory_info"] = f"Total: {memory.total / (1024.0 ** 3):.2f} GB\n" \
                                             f"Available: {memory.available / (1024.0 ** 3):.2f} GB\n" \
                                             f"Used: {memory.used / (1024.0 ** 3):.2f} GB\n" \
                                             f"Memory Usage: {memory.percent}%"
        return self.data_cache["memory_info"]

    def get_cpu_info(self):
        if "cpu_info" not in self.data_cache:
            cpu_usage = psutil.cpu_percent(interval=1)
            num_logical = psutil.cpu_count(logical=True)
            num_physical = psutil.cpu_count(logical=False)
            self.data_cache["cpu_info"] = f"CPU Usage: {cpu_usage}%\n" \
                                          f"Logical Cores: {num_logical}\n" \
                                          f"Physical Cores: {num_physical}"
        return self.data_cache["cpu_info"]

    def get_disk_info(self):
        if "disk_info" not in self.data_cache:
            disk_info = []
            for partition in psutil.disk_partitions():
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(f"=== {partition.device} ===")
                disk_info.append(f"Total: {usage.total / (1024.0 ** 3):.2f} GB")
                disk_info.append(f"Used: {usage.used / (1024.0 ** 3):.2f} GB")
                disk_info.append(f"Free: {usage.free / (1024.0 ** 3):.2f} GB")
                disk_info.append(f"Percentage: {usage.percent}%\n")
            self.data_cache["disk_info"] = "\n".join(disk_info)
        return self.data_cache["disk_info"]

    def create_info_buttons(self):
        button_frame = customtkinter.CTkFrame(self.info_tab)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        commands = [
            ("Memory Info", self.display_memory_info),
            ("CPU Info", self.display_cpu_info),
            ("Disk Info", self.display_disk_info),
            ("Network Info", self.display_network_info),
            ("Installed Software", self.display_installed_software),
            ("Connected Devices", self.display_device_info),
        ]

        for idx, (text, command) in enumerate(commands):
            row = idx // 6
            col = idx % 6
            button = customtkinter.CTkButton(button_frame, text=text, command=command, width=150, font=("Arial", 18))
            button.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")

        for col in range(6):
            button_frame.grid_columnconfigure(col, weight=1)
        button_frame.grid_rowconfigure(len(commands) // 6, weight=1)

    def refresh_info(self):
        self.data_cache.clear()
        self.update_dashboard()

    def change_theme(self, theme):
        customtkinter.set_appearance_mode(theme.lower())

    def update_dashboard(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        self.create_dashboard_content()

    def display_memory_info(self):
        self.update_info_text_box("Memory Information", self.get_memory_info())

    def display_cpu_info(self):
        self.update_info_text_box("CPU Information", self.get_cpu_info())

    def display_disk_info(self):
        self.update_info_text_box("Disk Information", self.get_disk_info())

    def display_network_info(self):
        self.update_info_text_box("Network Information", self.get_network_info())

    def get_network_info(self):
        if "network_info" not in self.data_cache:
            network_info = []
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            network_info.append(f"Hostname: {hostname}")
            network_info.append(f"Primary IP Address: {ip_address}\n")

            interfaces = psutil.net_if_addrs()
            for interface, addrs in interfaces.items():
                network_info.append(f"Interface: {interface}")
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        network_info.append(f"  IPv4: {addr.address} (Subnet: {addr.netmask})")
                    elif addr.family == socket.AF_INET6:
                        network_info.append(f"  IPv6: {addr.address} (Subnet: {addr.netmask})")
                network_info.append("")

            net_stats = psutil.net_io_counters()
            network_info.append(f"Total Bytes Sent: {net_stats.bytes_sent / (1024 ** 2):.2f} MB")
            network_info.append(f"Total Bytes Received: {net_stats.bytes_recv / (1024 ** 2):.2f} MB")

            self.data_cache["network_info"] = "\n".join(network_info)
        return self.data_cache["network_info"]

    def display_installed_software(self):
        self.update_info_text_box("Installed Software", self.get_installed_software())

    def get_installed_software(self):
        if "installed_software" not in self.data_cache:
            software_info = []
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                    sub_key = winreg.EnumKey(reg_key, i)
                    sub_key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{sub_key}"
                    try:
                        reg_sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key_path)
                        display_name, _ = winreg.QueryValueEx(reg_sub_key, "DisplayName")
                        install_date, _ = winreg.QueryValueEx(reg_sub_key, "InstallDate")
                        install_date = datetime.strptime(str(install_date), "%Y%m%d").date()
                        software_info.append(f"{display_name} - Installed on: {install_date}")
                    except:
                        continue
            except Exception as e:
                software_info.append(f"Error retrieving software: {e}")
            self.data_cache["installed_software"] = "\n".join(software_info)
        return self.data_cache["installed_software"]

    def display_device_info(self):
        self.update_info_text_box("Connected Devices", self.get_connected_devices())

    def get_connected_devices(self):
        if "connected_devices" not in self.data_cache:
            devices = []
            for port in serial.tools.list_ports.comports():
                devices.append(f"Device: {port.device} - {port.description}")
            self.data_cache["connected_devices"] = "\n".join(devices)
        return self.data_cache["connected_devices"]

    def update_info_text_box(self, title, content):
        self.info_text_box.delete(1.0, tk.END)
        self.info_text_box.insert(tk.END, f"{title}\n\n{content}")


if __name__ == "__main__":
    app = SystemInfoApp()
    app.mainloop()
