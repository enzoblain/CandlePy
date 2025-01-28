
# 🌟 CandlePy

**CandlePy** is a Python-based interactive tool for rendering beautiful candlestick charts. It uses the **SDL2** graphics library to visualize market data in real-time, offering an easy-to-understand way of exploring price movements with candlestick patterns.

## Features
- 📊 **Real-Time Candlestick Chart**: Visualize live market data with real-time updates.
- 🎨 **Customizable Themes**: Change colors for bullish, bearish candles, and the background.
- 🖼️ **Screenshot Functionality**: Capture your candlestick chart with the press of a button.
- ⏸️ **Pause the Chart**: Control chart updates with a simple pause/play toggle.

## Getting Started

### Prerequisites
Before running **CandlePy**, make sure you have Python 3.x installed along with the following dependencies:
- `PySDL2`
- `pandas`
- `numpy`

You can install them using pip:
```bash
pip install PySDL2 pandas numpy
```

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/enzoblain/CandlePy.git
   ```
2. Navigate into the project folder:
   ```bash
   cd CandlePy
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
To run the **CandlePy** window and see the candlestick chart in action, execute the following command:
```bash
python main.py
```

### Key Controls
- ⏸️ **Spacebar**: Pause or resume the chart updates.
- 📸 **Enter**: Take a screenshot of the current chart.
- ❌ **Esc**: Close the window.

### Adding Candles
You can add new candles to the chart programmatically using the `addCandle()` function. A new candle is represented as a dictionary with the following fields:
- `datetime`: The timestamp of the candle (e.g., UNIX timestamp).
- `open`: The opening price of the candle.
- `close`: The closing price of the candle.
- `high`: The highest price during the candle's time period.
- `low`: The lowest price during the candle's time period.

Example:
```python
candle = {
    "datetime": 1617554000,  # Example UNIX timestamp
    "open": 132.5,
    "close": 135.0,
    "high": 136.0,
    "low": 131.0
}

window.addCandle(candle)
```

### Customizing the Theme
You can customize the look and feel of your chart by adjusting the theme settings in [themes file](`themes.json`) such as this.
```python
theme = {
    "Background": (255, 255, 255),  # White background
    "Candle": {
        "Bullish": (0, 255, 0),  # Green for bullish candles
        "Bearish": (255, 0, 0)   # Red for bearish candles
    }
}

window = SDL2Window(theme=theme)
```

## Contributing
We welcome contributions! Feel free to fork the repository and create pull requests. If you have ideas for new features or improvements, please open an issue or contribute directly.

## License
Distributed under the MIT License. See `LICENSE` for more information.

---

🚀 **CandlePy** is continuously being improved! Stay tuned for more exciting features and updates! 🌟
