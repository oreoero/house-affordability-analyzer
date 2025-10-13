# 🏠 Home Affordability Calculator

An interactive web application for calculating home affordability with comprehensive mortgage analysis, payment breakdowns, and scenario comparisons.

## ✨ Features

- **Real-time Calculations**: Instant updates as you adjust parameters
- **Payment Breakdown**: Visual pie chart showing monthly payment components
- **Scenario Analysis**: Compare different home prices, interest rates, and down payments
- **Affordability Metrics**: Front-end and back-end debt-to-income ratios
- **Interactive Charts**: Plotly-powered visualizations for detailed analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/home-affordability-calculator.git
   cd home-affordability-calculator
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

### Running the Application

Start the Streamlit application:

```bash
uv run streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`

## 🔧 Usage

1. **Adjust Parameters**: Use the sidebar to input your financial information:
   - Home price
   - Down payment percentage
   - Interest rate
   - Loan term
   - Monthly income and debts
   - Property tax and insurance

2. **View Results**: The main dashboard shows:
   - Loan details and monthly costs
   - Affordability ratios with color-coded indicators
   - Payment breakdown chart
   - Comparison scenarios

3. **Analyze Scenarios**: Interactive charts help you understand how different variables affect affordability

## 📊 Affordability Guidelines

- **Front-End Ratio**: ≤28% (housing costs only)
- **Back-End Ratio**: ≤36% (total debt payments)

## 🛠 Development

### Project Structure

```
home-affordability-calculator/
├── main.py                   # Main Streamlit application
├── pyproject.toml            # Project dependencies
├── uv.lock                   # Dependency lock file
└── README.md                 # This file
```

### Adding Dependencies

```bash
uv add package-name
```

### Updating Dependencies

```bash
uv sync --upgrade
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.