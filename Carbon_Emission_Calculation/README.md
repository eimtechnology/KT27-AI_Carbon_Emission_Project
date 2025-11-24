# Image Normalization Tool

A simple yet powerful GUI application for image normalization using PyTorch and traditional Computer Vision techniques. This tool allows you to experiment with different normalization methods, visualize the results, and save the processed images.

## Features

- **PyTorch Normalization**: Apply mean and standard deviation normalization (e.g., for ImageNet).
- **Color Normalization**:
  - Histogram Equalization
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - White Balance
  - Mean-Std Normalization
- **Image Adjustments**: Fine-tune target brightness and contrast.
- **Side-by-Side Comparison**: View Original, PyTorch Normalized, and Color Normalized images simultaneously.
- **Detailed Statistics**: View channel-wise statistics (Mean, Std) for all processing stages.
- **Download/Save**: Save processed images in high resolution with automatic timestamping.

## Requirements

- Python 3.8 or higher
- Dependencies (installed automatically via run scripts):
  - torch
  - torchvision
  - Pillow
  - matplotlib
  - numpy
  - opencv-python

## How to Run

### Windows
Double-click `run_app.bat` or run in terminal:
```bash
run_app.bat
```

### Mac / Linux
Run the shell script in terminal:
```bash
chmod +x run_app.sh
./run_app.sh
```

## Usage

1. Click **"Browse"** to select an image file.
2. Adjust **PyTorch Parameters** (Mean/Std) or **Color Parameters** as needed.
3. Click the **Process** buttons to apply changes.
4. Use the **Download** section to save your results.

## License

MIT License
