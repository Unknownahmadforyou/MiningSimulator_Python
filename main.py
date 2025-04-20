import hashlib
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import datetime
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import uuid

# Constants
MAX_NONCE = 100000000000
REWARD_POINTS_PER_REFERRAL = 100
REFERRAL_BONUS_PERCENTAGE = 0.1  # 10% bonus from referrals

class UserProfile:
    def __init__(self):
        self.username = "Miner"
        self.email = ""
        self.wallet_address = ""
        self.mining_preference = "cpu"
        self.notifications_enabled = True
        self.referral_code = str(uuid.uuid4())[:8]
        self.referral_points = 0
        self.total_referrals = 0
        self.referral_history = []
        self.theme = "light"  # Default theme

    def to_json(self):
        return {
            "username": self.username,
            "email": self.email,
            "wallet_address": self.wallet_address,
            "mining_preference": self.mining_preference,
            "notifications_enabled": self.notifications_enabled,
            "referral_code": self.referral_code,
            "referral_points": self.referral_points,
            "total_referrals": self.total_referrals,
            "referral_history": self.referral_history,
            "theme": self.theme
        }

    def from_json(self, data):
        self.username = data.get("username", "Miner")
        self.email = data.get("email", "")
        self.wallet_address = data.get("wallet_address", "")
        self.mining_preference = data.get("mining_preference", "cpu")
        self.notifications_enabled = data.get("notifications_enabled", True)
        self.referral_code = data.get("referral_code", str(uuid.uuid4())[:8])
        self.referral_points = data.get("referral_points", 0)
        self.total_referrals = data.get("total_referrals", 0)
        self.referral_history = data.get("referral_history", [])
        self.theme = data.get("theme", "light")

class Block:
    def __init__(self, block_number, transactions, previous_hash, difficulty):
        self.block_number = block_number
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hash = None
    
    def to_json(self):
        return {
            "block_number": self.block_number,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = []
        # Genesis block
        genesis_block = Block(0, "Genesis Block", "0"*64, 1)
        genesis_block.hash = self.calculate_hash(genesis_block, 0)
        genesis_block.nonce = 0
        self.chain.append(genesis_block)
        
    def calculate_hash(self, block, nonce):
        text = (str(block.block_number) + 
                block.transactions + 
                block.previous_hash + 
                str(nonce) + 
                block.timestamp)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    def add_block(self, transactions, difficulty):
        block_number = len(self.chain)
        previous_hash = self.chain[-1].hash
        new_block = Block(block_number, transactions, previous_hash, difficulty)
        return new_block
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # Check hash validity
            if current.hash != self.calculate_hash(current, current.nonce):
                return False
                
            # Check link to previous block
            if current.previous_hash != previous.hash:
                return False
        
        return True
    
    def to_json(self):
        return [block.to_json() for block in self.chain]

class MiningSimulator:
    def __init__(self, root):
        self.root = root
        root.title("Bitcoin Mining Simulator")
        root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize blockchain and user profile
        self.blockchain = Blockchain()
        self.user_profile = UserProfile()
        self.load_profile()
        
        # Mining variables
        self.mining_thread = None
        self.is_mining = False
        self.mining_speed = 0
        self.start_time = 0
        self.hash_count = 0
        self.found_blocks = 0
        self.difficulty = 4
        self.available_balance = 0.0
        
        # Create GUI frames
        self.create_header_frame()
        self.create_blockchain_frame()
        self.create_mining_frame()
        self.create_transaction_frame()
        self.create_monitoring_frame()
        self.create_profile_frame()
        self.create_referral_frame()
        
        # Initialize plots
        self.initialize_plots()
        
        # Update stats periodically
        self.update_stats()
        
        # Apply theme
        self.apply_theme()
    
    def create_header_frame(self):
        header_frame = tk.Frame(self.root, bg=self.get_theme_color("header_bg"), height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme toggle
        self.theme_switch = ttk.Checkbutton(
            header_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            style="Switch.TCheckbutton"
        )
        self.theme_switch.pack(side=tk.RIGHT, padx=10)
        
        title_label = tk.Label(
            header_frame, 
            text="Bitcoin Mining Simulator", 
            font=("Arial", 20, "bold"),
            fg=self.get_theme_color("text"),
            bg=self.get_theme_color("header_bg")
        )
        title_label.pack(pady=10)
    
    def create_blockchain_frame(self):
        blockchain_frame = tk.LabelFrame(
            self.root, 
            text="Blockchain Explorer", 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        blockchain_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.blockchain_text = scrolledtext.ScrolledText(
            blockchain_frame, 
            height=10, 
            font=("Courier", 10),
            bg="#f8f8f8"
        )
        self.blockchain_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Update blockchain display
        self.update_blockchain_display()
    
    def create_mining_frame(self):
        mining_frame = tk.LabelFrame(
            self.root, 
            text="Mining Control", 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        mining_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Difficulty slider
        difficulty_frame = tk.Frame(mining_frame, bg="#f0f0f0")
        difficulty_frame.pack(fill=tk.X, padx=10, pady=5)
        
        difficulty_label = tk.Label(
            difficulty_frame, 
            text="Mining Difficulty: ",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        difficulty_label.pack(side=tk.LEFT)
        
        self.difficulty_slider = ttk.Scale(
            difficulty_frame,
            from_=1,
            to=6,
            orient=tk.HORIZONTAL,
            length=300,
            command=self.update_difficulty_label
        )
        self.difficulty_slider.set(self.difficulty)
        self.difficulty_slider.pack(side=tk.LEFT, padx=5)
        
        self.difficulty_value_label = tk.Label(
            difficulty_frame, 
            text=f"{self.difficulty}",
            font=("Arial", 10),
            bg="#f0f0f0",
            width=5
        )
        self.difficulty_value_label.pack(side=tk.LEFT)
        
        # Mining status and controls
        controls_frame = tk.Frame(mining_frame, bg="#f0f0f0")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            controls_frame, 
            text="Status: Idle",
            font=("Arial", 10),
            bg="#f0f0f0",
            width=20,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.hashrate_label = tk.Label(
            controls_frame, 
            text="Hashrate: 0 H/s",
            font=("Arial", 10),
            bg="#f0f0f0",
            width=20,
            anchor=tk.W
        )
        self.hashrate_label.pack(side=tk.LEFT, padx=5)
        
        self.balance_label = tk.Label(
            controls_frame, 
            text=f"Balance: {self.available_balance:.8f} BTC",
            font=("Arial", 10),
            bg="#f0f0f0",
            width=25,
            anchor=tk.W
        )
        self.balance_label.pack(side=tk.LEFT, padx=5)
        
        # Mining buttons
        button_frame = tk.Frame(mining_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mine_button = tk.Button(
            button_frame, 
            text="Start Mining",
            command=self.toggle_mining,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            relief=tk.RAISED,
            bd=3
        )
        self.mine_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        clear_button = tk.Button(
            button_frame, 
            text="Reset Blockchain",
            command=self.reset_blockchain,
            bg="#F95959",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            relief=tk.RAISED,
            bd=3
        )
        clear_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_transaction_frame(self):
        transaction_frame = tk.LabelFrame(
            self.root, 
            text="Create Transaction", 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        transaction_frame.pack(fill=tk.X, padx=10, pady=5)
        
        entry_frame = tk.Frame(transaction_frame, bg="#f0f0f0")
        entry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            entry_frame, 
            text="Sender:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.sender_entry = tk.Entry(
            entry_frame,
            font=("Arial", 10),
            width=30
        )
        self.sender_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.sender_entry.insert(0, "Alice")
        
        tk.Label(
            entry_frame, 
            text="Recipient:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.recipient_entry = tk.Entry(
            entry_frame,
            font=("Arial", 10),
            width=30
        )
        self.recipient_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.recipient_entry.insert(0, "Bob")
        
        tk.Label(
            entry_frame, 
            text="Amount:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.amount_entry = tk.Entry(
            entry_frame,
            font=("Arial", 10),
            width=10
        )
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.amount_entry.insert(0, "10")
        
        add_button = tk.Button(
            entry_frame, 
            text="Add Transaction",
            command=self.add_transaction,
            bg="#3D87BF",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            relief=tk.RAISED,
            bd=3
        )
        add_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.transaction_text = scrolledtext.ScrolledText(
            transaction_frame, 
            height=3, 
            font=("Courier", 10),
            bg="#f8f8f8"
        )
        self.transaction_text.pack(fill=tk.X, padx=10, pady=5)
        self.transaction_text.insert(tk.END, "Enter transaction details above")
    
    def create_monitoring_frame(self):
        monitoring_frame = tk.LabelFrame(
            self.root, 
            text="Mining Performance", 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        monitoring_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 3), dpi=100)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=monitoring_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def create_profile_frame(self):
        profile_frame = tk.LabelFrame(
            self.root, 
            text="Profile Settings", 
            font=("Arial", 12, "bold"),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        )
        profile_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Profile form
        form_frame = tk.Frame(profile_frame, bg=self.get_theme_color("bg"))
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Username
        tk.Label(
            form_frame, 
            text="Username:",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.username_entry = tk.Entry(form_frame, font=("Arial", 10))
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.username_entry.insert(0, self.user_profile.username)
        
        # Email
        tk.Label(
            form_frame, 
            text="Email:",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.email_entry = tk.Entry(form_frame, font=("Arial", 10))
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        self.email_entry.insert(0, self.user_profile.email)
        
        # Wallet Address
        tk.Label(
            form_frame, 
            text="Wallet Address:",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.wallet_entry = tk.Entry(form_frame, font=("Arial", 10))
        self.wallet_entry.grid(row=2, column=1, padx=5, pady=5)
        self.wallet_entry.insert(0, self.user_profile.wallet_address)
        
        # Mining Preference
        tk.Label(
            form_frame, 
            text="Mining Preference:",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.mining_pref_var = tk.StringVar(value=self.user_profile.mining_preference)
        mining_pref_menu = ttk.Combobox(
            form_frame,
            textvariable=self.mining_pref_var,
            values=["cpu", "gpu", "both"],
            state="readonly"
        )
        mining_pref_menu.grid(row=3, column=1, padx=5, pady=5)
        
        # Notifications
        self.notifications_var = tk.BooleanVar(value=self.user_profile.notifications_enabled)
        ttk.Checkbutton(
            form_frame,
            text="Enable Notifications",
            variable=self.notifications_var
        ).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # Save button
        ttk.Button(
            form_frame,
            text="Save Profile",
            command=self.save_profile
        ).grid(row=5, column=0, columnspan=2, pady=10)

    def create_referral_frame(self):
        referral_frame = tk.LabelFrame(
            self.root, 
            text="Refer & Earn", 
            font=("Arial", 12, "bold"),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        )
        referral_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Referral code
        code_frame = tk.Frame(referral_frame, bg=self.get_theme_color("bg"))
        code_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            code_frame, 
            text="Your Referral Code:",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).pack(side=tk.LEFT, padx=5)
        
        self.referral_code_label = tk.Label(
            code_frame,
            text=self.user_profile.referral_code,
            font=("Arial", 10, "bold"),
            bg=self.get_theme_color("bg"),
            fg="#f7931a"
        )
        self.referral_code_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            code_frame,
            text="Copy",
            command=self.copy_referral_code
        ).pack(side=tk.LEFT, padx=5)
        
        # Referral stats
        stats_frame = tk.Frame(referral_frame, bg=self.get_theme_color("bg"))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            stats_frame, 
            text=f"Total Referrals: {self.user_profile.total_referrals}",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            stats_frame, 
            text=f"Reward Points: {self.user_profile.referral_points}",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).pack(side=tk.LEFT, padx=5)
        
        # Referral history
        history_frame = tk.Frame(referral_frame, bg=self.get_theme_color("bg"))
        history_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            history_frame, 
            text="Recent Referrals:",
            font=("Arial", 10),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        ).pack(anchor=tk.W, padx=5)
        
        self.referral_history_text = scrolledtext.ScrolledText(
            history_frame,
            height=5,
            font=("Courier", 9),
            bg=self.get_theme_color("bg"),
            fg=self.get_theme_color("text")
        )
        self.referral_history_text.pack(fill=tk.X, padx=5, pady=5)
        self.update_referral_history()
    
    def initialize_plots(self):
        # Clear figure
        self.fig.clear()
        
        # Create hashrate chart
        self.hashrate_ax = self.fig.add_subplot(121)
        self.hashrate_ax.set_title('Mining Hashrate')
        self.hashrate_ax.set_xlabel('Time')
        self.hashrate_ax.set_ylabel('Hashes/sec')
        self.hashrate_plot, = self.hashrate_ax.plot([], [], 'b-')
        self.hashrate_data_x = []
        self.hashrate_data_y = []
        
        # Create block time chart
        self.block_ax = self.fig.add_subplot(122)
        self.block_ax.set_title('Block Mining Time')
        self.block_ax.set_xlabel('Block Number')
        self.block_ax.set_ylabel('Time (seconds)')
        self.block_plot, = self.block_ax.plot([], [], 'r-')
        self.block_data_x = []
        self.block_data_y = []
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_difficulty_label(self, value):
        self.difficulty = int(float(value))
        self.difficulty_value_label.config(text=f"{self.difficulty}")
    
    def toggle_mining(self):
        if self.is_mining:
            self.stop_mining()
        else:
            self.start_mining()
    
    def start_mining(self):
        if not self.is_mining:
            self.is_mining = True
            self.mine_button.config(text="Stop Mining", bg="#F95959")
            self.status_label.config(text="Status: Mining...")
            
            # Get transaction data
            transactions = self.transaction_text.get("1.0", tk.END).strip()
            if transactions == "Enter transaction details above" or transactions == "":
                transactions = f"Miner->Reward->6.25 BTC\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.transaction_text.delete("1.0", tk.END)
                self.transaction_text.insert(tk.END, transactions)
            
            # Start mining thread
            self.mining_thread = threading.Thread(target=self.mine_block, args=(transactions,))
            self.mining_thread.daemon = True
            self.mining_thread.start()
    
    def stop_mining(self):
        if self.is_mining:
            self.is_mining = False
            self.mine_button.config(text="Start Mining", bg="#4CAF50")
            self.status_label.config(text="Status: Stopped")
    
    def mine_block(self, transactions):
        new_block = self.blockchain.add_block(transactions, self.difficulty)
        prefix_str = '0' * self.difficulty
        
        self.start_time = time.time()
        self.hash_count = 0
        block_start_time = time.time()
        
        for nonce in range(MAX_NONCE):
            if not self.is_mining:
                return
            
            # Calculate hash
            hash_result = self.blockchain.calculate_hash(new_block, nonce)
            self.hash_count += 1
            
            # Update UI every 10000 hashes
            if self.hash_count % 10000 == 0:
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.mining_speed = self.hash_count / elapsed
                    # Update on main thread
                    self.root.after(0, self.update_mining_stats)
            
            # Check if hash matches difficulty
            if hash_result.startswith(prefix_str):
                # Block found
                new_block.nonce = nonce
                new_block.hash = hash_result
                self.blockchain.chain.append(new_block)
                
                # Calculate mining time
                mining_time = time.time() - block_start_time
                
                # Add mining reward
                self.found_blocks += 1
                self.available_balance += 6.25  # BTC reward
                
                # Update block time chart
                self.block_data_x.append(new_block.block_number)
                self.block_data_y.append(mining_time)
                
                # Update UI on main thread
                self.root.after(0, self.update_ui_after_block_found, mining_time, hash_result)
                return
    
    def update_ui_after_block_found(self, mining_time, hash_result):
        # Update blockchain display
        self.update_blockchain_display()
        
        # Update stats
        self.balance_label.config(text=f"Balance: {self.available_balance:.8f} BTC")
        
        # Show success message
        messagebox.showinfo(
            "Block Mined!", 
            f"Successfully mined block!\nNonce: {self.blockchain.get_latest_block().nonce}\n"
            f"Hash: {hash_result[:20]}...\nTime: {mining_time:.2f} seconds"
        )
        
        # Reset mining status
        self.stop_mining()
        
        # Clear transaction text
        self.transaction_text.delete("1.0", tk.END)
        self.transaction_text.insert(tk.END, "Enter transaction details above")
    
    def reset_blockchain(self):
        if messagebox.askyesno("Reset Blockchain", "Are you sure you want to reset the blockchain?"):
            self.stop_mining()
            self.blockchain = Blockchain()
            self.update_blockchain_display()
            self.found_blocks = 0
            self.available_balance = 0.0
            self.balance_label.config(text=f"Balance: {self.available_balance:.8f} BTC")
            
            # Reset charts
            self.hashrate_data_x = []
            self.hashrate_data_y = []
            self.block_data_x = []
            self.block_data_y = []
            self.update_charts()
    
    def add_transaction(self):
        sender = self.sender_entry.get()
        recipient = self.recipient_entry.get()
        amount = self.amount_entry.get()
        
        if not sender or not recipient or not amount:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            amount_float = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return
        
        transaction_text = f"{sender}->{recipient}->{amount}\n"
        self.transaction_text.delete("1.0", tk.END)
        self.transaction_text.insert(tk.END, transaction_text)
        
        messagebox.showinfo("Success", "Transaction added to pending block")
    
    def update_blockchain_display(self):
        self.blockchain_text.delete("1.0", tk.END)
        for block in self.blockchain.chain:
            self.blockchain_text.insert(tk.END, f"Block #{block.block_number}\n")
            self.blockchain_text.insert(tk.END, f"Timestamp: {block.timestamp}\n")
            self.blockchain_text.insert(tk.END, f"Transactions: {block.transactions}\n")
            self.blockchain_text.insert(tk.END, f"Previous Hash: {block.previous_hash[:15]}...\n")
            self.blockchain_text.insert(tk.END, f"Hash: {block.hash[:15]}...\n")
            self.blockchain_text.insert(tk.END, f"Nonce: {block.nonce}\n")
            self.blockchain_text.insert(tk.END, f"Difficulty: {block.difficulty}\n")
            self.blockchain_text.insert(tk.END, "-" * 50 + "\n")
        
        # Highlight text
        self.blockchain_text.tag_add("header", "1.0", "1.end")
        self.blockchain_text.tag_config("header", foreground="blue", font=("Courier", 10, "bold"))
    
    def update_mining_stats(self):
        self.hashrate_label.config(text=f"Hashrate: {self.mining_speed:.2f} H/s")
        
        # Update hashrate chart
        current_time = time.time() - self.start_time
        self.hashrate_data_x.append(current_time)
        self.hashrate_data_y.append(self.mining_speed)
        
        # Keep only last 50 data points
        if len(self.hashrate_data_x) > 50:
            self.hashrate_data_x = self.hashrate_data_x[-50:]
            self.hashrate_data_y = self.hashrate_data_y[-50:]
        
        self.update_charts()
    
    def update_charts(self):
        # Update hashrate chart
        if self.hashrate_data_x:
            self.hashrate_plot.set_data(self.hashrate_data_x, self.hashrate_data_y)
            self.hashrate_ax.relim()
            self.hashrate_ax.autoscale_view()
        
        # Update block time chart
        if self.block_data_x:
            self.block_plot.set_data(self.block_data_x, self.block_data_y)
            self.block_ax.relim()
            self.block_ax.autoscale_view()
        
        self.canvas.draw()
    
    def update_stats(self):
        # Update UI elements if mining is active
        if self.is_mining:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                self.mining_speed = self.hash_count / elapsed
                self.hashrate_label.config(text=f"Hashrate: {self.mining_speed:.2f} H/s")
        
        # Schedule the next update
        self.root.after(1000, self.update_stats)
    
    def save_blockchain(self, filename="blockchain.json"):
        with open(filename, "w") as f:
            json.dump(self.blockchain.to_json(), f, indent=4)
        messagebox.showinfo("Success", f"Blockchain saved to {filename}")
    
    def load_blockchain(self, filename="blockchain.json"):
        try:
            with open(filename, "r") as f:
                blockchain_data = json.load(f)
            
            # Create new blockchain
            self.blockchain = Blockchain()
            self.blockchain.chain = []
            
            # Add blocks from file
            for block_data in blockchain_data:
                block = Block(
                    block_data["block_number"],
                    block_data["transactions"],
                    block_data["previous_hash"],
                    block_data["difficulty"]
                )
                block.hash = block_data["hash"]
                block.nonce = block_data["nonce"]
                block.timestamp = block_data["timestamp"]
                self.blockchain.chain.append(block)
            
            self.update_blockchain_display()
            messagebox.showinfo("Success", f"Blockchain loaded from {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load blockchain: {str(e)}")

    def toggle_theme(self):
        self.user_profile.theme = "dark" if self.user_profile.theme == "light" else "light"
        self.apply_theme()
        self.save_profile()

    def apply_theme(self):
        theme_colors = {
            "light": {
                "bg": "#f0f0f0",
                "text": "#333333",
                "header_bg": "#1E3D59",
                "card_bg": "#ffffff",
                "input_bg": "#ffffff"
            },
            "dark": {
                "bg": "#1a1a1a",
                "text": "#ffffff",
                "header_bg": "#0d1a26",
                "card_bg": "#2d2d2d",
                "input_bg": "#333333"
            }
        }
        
        colors = theme_colors[self.user_profile.theme]
        self.root.configure(bg=colors["bg"])
        
        # Update all widgets with new colors
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                widget.configure(bg=colors["bg"], fg=colors["text"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=colors["bg"], fg=colors["text"])
                    elif isinstance(child, tk.Entry):
                        child.configure(bg=colors["input_bg"], fg=colors["text"])
                    elif isinstance(child, scrolledtext.ScrolledText):
                        child.configure(bg=colors["bg"], fg=colors["text"])

    def get_theme_color(self, color_type):
        theme_colors = {
            "light": {
                "bg": "#f0f0f0",
                "text": "#333333",
                "header_bg": "#1E3D59",
                "card_bg": "#ffffff",
                "input_bg": "#ffffff"
            },
            "dark": {
                "bg": "#1a1a1a",
                "text": "#ffffff",
                "header_bg": "#0d1a26",
                "card_bg": "#2d2d2d",
                "input_bg": "#333333"
            }
        }
        return theme_colors[self.user_profile.theme][color_type]

    def save_profile(self):
        self.user_profile.username = self.username_entry.get()
        self.user_profile.email = self.email_entry.get()
        self.user_profile.wallet_address = self.wallet_entry.get()
        self.user_profile.mining_preference = self.mining_pref_var.get()
        self.user_profile.notifications_enabled = self.notifications_var.get()
        
        try:
            with open("profile.json", "w") as f:
                json.dump(self.user_profile.to_json(), f)
            messagebox.showinfo("Success", "Profile saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")

    def load_profile(self):
        try:
            with open("profile.json", "r") as f:
                data = json.load(f)
                self.user_profile.from_json(data)
        except FileNotFoundError:
            # Use default profile if file doesn't exist
            pass

    def copy_referral_code(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.user_profile.referral_code)
        messagebox.showinfo("Success", "Referral code copied to clipboard!")

    def update_referral_history(self):
        self.referral_history_text.delete(1.0, tk.END)
        for referral in self.user_profile.referral_history[-5:]:  # Show last 5 referrals
            self.referral_history_text.insert(tk.END, f"{referral['date']}: {referral['code']} - {referral['points']} points\n")

    def add_referral(self, code):
        if code == self.user_profile.referral_code:
            messagebox.showerror("Error", "Cannot use your own referral code!")
            return False
        
        # Add referral points
        self.user_profile.referral_points += REWARD_POINTS_PER_REFERRAL
        self.user_profile.total_referrals += 1
        
        # Add to history
        self.user_profile.referral_history.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "code": code,
            "points": REWARD_POINTS_PER_REFERRAL
        })
        
        # Update UI
        self.update_referral_history()
        self.save_profile()
        
        messagebox.showinfo("Success", f"Referral added! You earned {REWARD_POINTS_PER_REFERRAL} points!")
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = MiningSimulator(root)
    root.mainloop()
