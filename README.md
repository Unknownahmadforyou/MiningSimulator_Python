# Bitcoin Mining Simulator

A Python-based Bitcoin mining simulator that provides a realistic experience of cryptocurrency mining with a user-friendly graphical interface.

![Bitcoin Mining Simulator](screenshot.png)

## Features

### Core Mining Features
- Real-time mining simulation with adjustable difficulty
- Blockchain visualization and management
- Transaction creation and management
- Mining performance monitoring with charts
- Real-time hashrate and balance tracking
- Block time analysis

### User Features
- Dark/Light mode support
- Profile management
- Referral system with rewards
- Mining preference settings (CPU/GPU/Both)
- Notification system
- Wallet integration

### Technical Features
- SHA-256 hashing algorithm implementation
- Real-time performance monitoring
- Data persistence (blockchain and profile)
- Export/Import blockchain functionality
- Responsive GUI with Tkinter
- Matplotlib integration for charts

## Requirements

- Python 3.7+
- Required Python packages:
  ```
  tkinter
  matplotlib
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bitcoin-mining-simulator.git
   cd bitcoin-mining-simulator
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the simulator:
   ```bash
   python main.py
   ```

## Usage

### Starting Mining
1. Adjust the mining difficulty using the slider
2. Click "Start Mining" to begin
3. Monitor your hashrate and balance in real-time

### Creating Transactions
1. Enter sender and recipient details
2. Specify the amount
3. Click "Add Transaction" to add to the pending pool

### Profile Management
1. Access profile settings from the main interface
2. Update your information:
   - Username
   - Email
   - Wallet Address
   - Mining Preferences
   - Notification Settings

### Referral System
1. Share your unique referral code
2. Earn 100 points for each successful referral
3. Get 10% bonus from referral mining rewards
4. Track your referral history and points

### Theme Switching
- Toggle between light and dark mode using the switch in the header
- Theme preference is saved automatically

## Project Structure

```
bitcoin-mining-simulator/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── profile.json        # User profile data
└── blockchain.json     # Blockchain data
```

## Technical Details

### Mining Algorithm
- Uses SHA-256 hashing
- Adjustable difficulty levels
- Real-time hashrate calculation
- Block reward system

### Blockchain Implementation
- Genesis block creation
- Block validation
- Transaction management
- Chain integrity verification

### Data Persistence
- JSON-based storage
- Automatic saving of blockchain and profile data
- Import/Export functionality

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Bitcoin Core for inspiration
- Python community for excellent libraries
- Cryptocurrency community for educational resources

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Roadmap

- [ ] Multi-user support
- [ ] Network simulation
- [ ] Advanced mining algorithms
- [ ] Mobile app version
- [ ] Web interface
- [ ] API integration

## Disclaimer

This is a simulation for educational purposes only. It does not involve real cryptocurrency mining or transactions. 