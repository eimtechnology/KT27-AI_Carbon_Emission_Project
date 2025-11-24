import torch
import torchvision.transforms as transforms
from PIL import Image, ImageTk, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import cv2
import os
from datetime import datetime

def normalize_image(image_path, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    """
    Normalize image using PyTorch
    
    Args:
        image_path: Image file path
        mean: Normalization mean values (ImageNet standard)
        std: Normalization standard deviation values (ImageNet standard)
    
    Returns:
        normalized_tensor: Normalized tensor
        original_tensor: Original image tensor
    """
    # Load image
    image = Image.open(image_path).convert('RGB')
    
    # Convert to tensor
    to_tensor = transforms.ToTensor()
    original_tensor = to_tensor(image)
    
    # Normalize
    normalize = transforms.Normalize(mean=mean, std=std)
    normalized_tensor = normalize(original_tensor)
    
    return normalized_tensor, original_tensor, image

def denormalize_tensor(normalized_tensor, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    """
    Convert normalized tensor back to visualizable image
    """
    # Copy tensor to avoid modifying original data
    denorm = normalized_tensor.clone()
    
    # Denormalize
    for t, m, s in zip(denorm, mean, std):
        t.mul_(s).add_(m)
    
    # Clamp pixel values to [0,1] range
    denorm = torch.clamp(denorm, 0, 1)
    
    return denorm

def color_normalize_image(image, method='histogram_equalization'):
    """
    Apply different color normalization methods
    
    Args:
        image: PIL Image
        method: Normalization method ('histogram_equalization', 'clahe', 'white_balance', 'mean_std')
    
    Returns:
        normalized_image: PIL Image
    """
    # Convert PIL to numpy array
    img_array = np.array(image)
    
    if method == 'histogram_equalization':
        # Convert to YUV and apply histogram equalization to Y channel
        img_yuv = cv2.cvtColor(img_array, cv2.COLOR_RGB2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        normalized_array = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
        
    elif method == 'clahe':
        # Contrast Limited Adaptive Histogram Equalization
        img_yuv = cv2.cvtColor(img_array, cv2.COLOR_RGB2YUV)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])
        normalized_array = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
        
    elif method == 'white_balance':
        # Simple white balance using gray world assumption
        img_float = img_array.astype(np.float32)
        mean_rgb = np.mean(img_float, axis=(0,1))
        gray_value = np.mean(mean_rgb)
        normalized_array = (img_float * gray_value / mean_rgb).astype(np.uint8)
        normalized_array = np.clip(normalized_array, 0, 255)
        
    elif method == 'mean_std':
        # Normalize to zero mean and unit variance
        img_float = img_array.astype(np.float32)
        mean = np.mean(img_float, axis=(0,1))
        std = np.std(img_float, axis=(0,1))
        normalized_array = (img_float - mean) / (std + 1e-8)
        # Scale back to [0, 255] range
        normalized_array = (normalized_array - normalized_array.min()) / (normalized_array.max() - normalized_array.min())
        normalized_array = (normalized_array * 255).astype(np.uint8)
        
    else:
        normalized_array = img_array
    
    return Image.fromarray(normalized_array)

def brightness_normalize(image, target_brightness=128):
    """
    Normalize image brightness to target value
    """
    img_array = np.array(image)
    current_brightness = np.mean(img_array)
    factor = target_brightness / current_brightness
    normalized_array = np.clip(img_array * factor, 0, 255).astype(np.uint8)
    return Image.fromarray(normalized_array)

def contrast_normalize(image, target_contrast=64):
    """
    Normalize image contrast
    """
    enhancer = ImageEnhance.Contrast(image)
    # Calculate contrast factor based on current contrast
    img_array = np.array(image)
    current_contrast = np.std(img_array)
    factor = target_contrast / current_contrast
    return enhancer.enhance(factor)

class ImageNormalizationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyTorch Image & Color Normalization Demo")
        self.root.geometry("1400x900")
        
        # Variables
        self.image_path = tk.StringVar()
        self.mean_values = [tk.StringVar(value="0.485"), tk.StringVar(value="0.456"), tk.StringVar(value="0.406")]
        self.std_values = [tk.StringVar(value="0.229"), tk.StringVar(value="0.224"), tk.StringVar(value="0.225")]
        self.color_method = tk.StringVar(value="histogram_equalization")
        self.brightness_target = tk.StringVar(value="128")
        self.contrast_target = tk.StringVar(value="64")
        
        # Store processed images for download
        self.current_original = None
        self.current_pytorch = None
        self.current_color = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Label(main_frame, text="Image File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.image_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # PyTorch Normalization parameters
        pytorch_frame = ttk.LabelFrame(main_frame, text="PyTorch Normalization Parameters", padding="10")
        pytorch_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Mean values
        ttk.Label(pytorch_frame, text="Mean (R, G, B):").grid(row=0, column=0, sticky=tk.W)
        for i, var in enumerate(self.mean_values):
            ttk.Entry(pytorch_frame, textvariable=var, width=10).grid(row=0, column=i+1, padx=2)
        
        # Std values
        ttk.Label(pytorch_frame, text="Std (R, G, B):").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        for i, var in enumerate(self.std_values):
            ttk.Entry(pytorch_frame, textvariable=var, width=10).grid(row=1, column=i+1, padx=2, pady=(10,0))
        
        # Color Normalization parameters
        color_frame = ttk.LabelFrame(main_frame, text="Color Normalization Parameters", padding="10")
        color_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Color method selection
        ttk.Label(color_frame, text="Color Method:").grid(row=0, column=0, sticky=tk.W)
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_method, width=20, state="readonly")
        color_combo['values'] = ('histogram_equalization', 'clahe', 'white_balance', 'mean_std')
        color_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Brightness and contrast controls
        ttk.Label(color_frame, text="Target Brightness:").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        ttk.Entry(color_frame, textvariable=self.brightness_target, width=10).grid(row=1, column=1, padx=5, pady=(10,0), sticky=tk.W)
        
        ttk.Label(color_frame, text="Target Contrast:").grid(row=1, column=2, sticky=tk.W, padx=(20,0), pady=(10,0))
        ttk.Entry(color_frame, textvariable=self.contrast_target, width=10).grid(row=1, column=3, padx=5, pady=(10,0), sticky=tk.W)
        
        # Process buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Process PyTorch Normalization", command=self.process_pytorch).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Process Color Normalization", command=self.process_color).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Process Both", command=self.process_both).grid(row=0, column=2, padx=5)
        
        # Download buttons frame
        download_frame = ttk.LabelFrame(main_frame, text="Download Images", padding="10")
        download_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(download_frame, text="Download Original", command=self.download_original).grid(row=0, column=0, padx=5)
        ttk.Button(download_frame, text="Download PyTorch Normalized", command=self.download_pytorch).grid(row=0, column=1, padx=5)
        ttk.Button(download_frame, text="Download Color Normalized", command=self.download_color).grid(row=0, column=2, padx=5)
        ttk.Button(download_frame, text="Download All Images", command=self.download_all).grid(row=0, column=3, padx=5)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(5, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.columnconfigure(1, weight=1)
        self.results_frame.columnconfigure(2, weight=1)
        
        # Image display labels
        self.original_label = ttk.Label(self.results_frame, text="Original Image", anchor=tk.CENTER)
        self.original_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.pytorch_label = ttk.Label(self.results_frame, text="PyTorch Normalized", anchor=tk.CENTER)
        self.pytorch_label.grid(row=0, column=1, padx=5, pady=5)
        
        self.color_label = ttk.Label(self.results_frame, text="Color Normalized", anchor=tk.CENTER)
        self.color_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Statistics frame
        self.stats_text = tk.Text(self.results_frame, height=15, width=60)
        self.stats_text.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Scrollbar for stats
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=scrollbar.set)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif")]
        )
        if file_path:
            self.image_path.set(file_path)
    
    def process_pytorch(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file first!")
            return
        
        try:
            # Get normalization parameters
            mean = [float(var.get()) for var in self.mean_values]
            std = [float(var.get()) for var in self.std_values]
            
            # Process image in a separate thread to avoid GUI freezing
            thread = threading.Thread(target=self._process_pytorch_thread, args=(mean, std))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for mean and std!")
    
    def process_color(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file first!")
            return
        
        try:
            # Get color normalization parameters
            brightness = float(self.brightness_target.get())
            contrast = float(self.contrast_target.get())
            method = self.color_method.get()
            
            # Process image in a separate thread to avoid GUI freezing
            thread = threading.Thread(target=self._process_color_thread, args=(method, brightness, contrast))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for brightness and contrast!")
    
    def process_both(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file first!")
            return
        
        try:
            # Get all parameters
            mean = [float(var.get()) for var in self.mean_values]
            std = [float(var.get()) for var in self.std_values]
            brightness = float(self.brightness_target.get())
            contrast = float(self.contrast_target.get())
            method = self.color_method.get()
            
            # Process image in a separate thread to avoid GUI freezing
            thread = threading.Thread(target=self._process_both_thread, args=(mean, std, method, brightness, contrast))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values!")
    
    def download_original(self):
        """Download the original image"""
        if self.current_original is None:
            messagebox.showerror("Error", "No original image available for download!")
            return
        self._save_image(self.current_original, "original")
    
    def download_pytorch(self):
        """Download the PyTorch normalized image"""
        if self.current_pytorch is None:
            messagebox.showerror("Error", "No PyTorch normalized image available for download!")
            return
        self._save_image(self.current_pytorch, "pytorch_normalized")
    
    def download_color(self):
        """Download the color normalized image"""
        if self.current_color is None:
            messagebox.showerror("Error", "No color normalized image available for download!")
            return
        self._save_image(self.current_color, "color_normalized")
    
    def download_all(self):
        """Download all available images"""
        if self.current_original is None:
            messagebox.showerror("Error", "No images available for download!")
            return
        
        # Ask for directory to save all images
        directory = filedialog.askdirectory(title="Select Directory to Save All Images")
        if not directory:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Save original
            original_path = os.path.join(directory, f"original_{timestamp}.png")
            self.current_original.save(original_path)
            
            # Save PyTorch normalized if available
            if self.current_pytorch is not None:
                pytorch_path = os.path.join(directory, f"pytorch_normalized_{timestamp}.png")
                self.current_pytorch.save(pytorch_path)
            
            # Save color normalized if available
            if self.current_color is not None:
                color_path = os.path.join(directory, f"color_normalized_{timestamp}.png")
                self.current_color.save(color_path)
            
            messagebox.showinfo("Success", f"All images saved to:\n{directory}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save images: {str(e)}")
    
    def _save_image(self, image, image_type):
        """Save a single image with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get the original filename for reference
        original_filename = os.path.basename(self.image_path.get()) if self.image_path.get() else "image"
        original_name = os.path.splitext(original_filename)[0]
        
        # Suggest filename
        suggested_filename = f"{original_name}_{image_type}_{timestamp}.png"
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            title=f"Save {image_type.replace('_', ' ').title()} Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            initialvalue=suggested_filename
        )
        
        if file_path:
            try:
                image.save(file_path)
                messagebox.showinfo("Success", f"Image saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def _process_pytorch_thread(self, mean, std):
        try:
            # Load and process image
            image_path = self.image_path.get()
            normalized_tensor, original_tensor, original_image = normalize_image(image_path, mean, std)
            denormalized_tensor = denormalize_tensor(normalized_tensor, mean, std)
            
            # Update GUI in main thread
            self.root.after(0, self._update_pytorch_gui, original_image, denormalized_tensor, normalized_tensor, original_tensor)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process image: {str(e)}"))
    
    def _process_color_thread(self, method, brightness, contrast):
        try:
            # Load and process image
            image_path = self.image_path.get()
            original_image = Image.open(image_path).convert('RGB')
            
            # Apply color normalization
            color_normalized = color_normalize_image(original_image, method)
            
            # Apply brightness and contrast normalization
            brightness_normalized = brightness_normalize(color_normalized, brightness)
            final_normalized = contrast_normalize(brightness_normalized, contrast)
            
            # Update GUI in main thread
            self.root.after(0, self._update_color_gui, original_image, final_normalized, method, brightness, contrast)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process color normalization: {str(e)}"))
    
    def _process_both_thread(self, mean, std, method, brightness, contrast):
        try:
            # Load and process image
            image_path = self.image_path.get()
            original_image = Image.open(image_path).convert('RGB')
            
            # Apply PyTorch normalization
            normalized_tensor, original_tensor, _ = normalize_image(image_path, mean, std)
            denormalized_tensor = denormalize_tensor(normalized_tensor, mean, std)
            
            # Apply color normalization
            color_normalized = color_normalize_image(original_image, method)
            brightness_normalized = brightness_normalize(color_normalized, brightness)
            final_color_normalized = contrast_normalize(brightness_normalized, contrast)
            
            # Update GUI in main thread
            self.root.after(0, self._update_both_gui, original_image, denormalized_tensor, final_color_normalized, 
                          normalized_tensor, original_tensor, method, brightness, contrast)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process both normalizations: {str(e)}"))
    
    def _update_pytorch_gui(self, original_image, denormalized_tensor, normalized_tensor, original_tensor):
        # Store images for download (full resolution)
        self.current_original = original_image
        denorm_np = denormalized_tensor.permute(1, 2, 0).numpy()
        denorm_np = (denorm_np * 255).astype(np.uint8)
        self.current_pytorch = Image.fromarray(denorm_np)
        self.current_color = None  # Clear color normalized image
        
        # Resize images for display
        display_size = (250, 250)
        original_display = original_image.resize(display_size, Image.Resampling.LANCZOS)
        denormalized_display = self.current_pytorch.resize(display_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        original_photo = ImageTk.PhotoImage(original_display)
        denormalized_photo = ImageTk.PhotoImage(denormalized_display)
        
        # Update labels
        self.original_label.configure(image=original_photo, text="")
        self.original_label.image = original_photo
        
        self.pytorch_label.configure(image=denormalized_photo, text="")
        self.pytorch_label.image = denormalized_photo
        
        # Update statistics
        self.stats_text.delete(1.0, tk.END)
        stats = f"""PyTorch Normalization Results:
{'='*60}

Original Image:
- Shape: {original_tensor.shape}
- Range: [{original_tensor.min().item():.4f}, {original_tensor.max().item():.4f}]
- Mean: {original_tensor.mean().item():.4f}
- Std: {original_tensor.std().item():.4f}

Normalized Tensor:
- Shape: {normalized_tensor.shape}
- Range: [{normalized_tensor.min().item():.4f}, {normalized_tensor.max().item():.4f}]
- Mean: {normalized_tensor.mean().item():.4f}
- Std: {normalized_tensor.std().item():.4f}
- Data Type: {normalized_tensor.dtype}

Normalization Parameters Used:
- Mean: {[float(var.get()) for var in self.mean_values]}
- Std: {[float(var.get()) for var in self.std_values]}

Channel-wise Statistics (Normalized):
- Red Channel: Mean={normalized_tensor[0].mean().item():.4f}, Std={normalized_tensor[0].std().item():.4f}
- Green Channel: Mean={normalized_tensor[1].mean().item():.4f}, Std={normalized_tensor[1].std().item():.4f}
- Blue Channel: Mean={normalized_tensor[2].mean().item():.4f}, Std={normalized_tensor[2].std().item():.4f}
"""
        self.stats_text.insert(1.0, stats)
    
    def _update_color_gui(self, original_image, color_normalized, method, brightness, contrast):
        # Store images for download (full resolution)
        self.current_original = original_image
        self.current_color = color_normalized
        self.current_pytorch = None  # Clear PyTorch normalized image
        
        # Resize images for display
        display_size = (250, 250)
        original_display = original_image.resize(display_size, Image.Resampling.LANCZOS)
        color_display = color_normalized.resize(display_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        original_photo = ImageTk.PhotoImage(original_display)
        color_photo = ImageTk.PhotoImage(color_display)
        
        # Update labels
        self.original_label.configure(image=original_photo, text="")
        self.original_label.image = original_photo
        
        self.color_label.configure(image=color_photo, text="")
        self.color_label.image = color_photo
        
        # Update statistics
        self.stats_text.delete(1.0, tk.END)
        stats = f"""Color Normalization Results:
{'='*60}

Color Normalization Method: {method}

Original Image Statistics:
- Size: {original_image.size}
- Mode: {original_image.mode}
- Current Brightness: {np.mean(np.array(original_image)):.2f}
- Current Contrast (Std): {np.std(np.array(original_image)):.2f}

Color Normalized Image Statistics:
- Size: {color_normalized.size}
- Mode: {color_normalized.mode}
- Final Brightness: {np.mean(np.array(color_normalized)):.2f}
- Final Contrast (Std): {np.std(np.array(color_normalized)):.2f}

Parameters Used:
- Method: {method}
- Target Brightness: {brightness}
- Target Contrast: {contrast}

RGB Channel Statistics (Normalized):
- Red Channel: Mean={np.mean(np.array(color_normalized)[:,:,0]):.2f}, Std={np.std(np.array(color_normalized)[:,:,0]):.2f}
- Green Channel: Mean={np.mean(np.array(color_normalized)[:,:,1]):.2f}, Std={np.std(np.array(color_normalized)[:,:,1]):.2f}
- Blue Channel: Mean={np.mean(np.array(color_normalized)[:,:,2]):.2f}, Std={np.std(np.array(color_normalized)[:,:,2]):.2f}
"""
        self.stats_text.insert(1.0, stats)
    
    def _update_both_gui(self, original_image, denormalized_tensor, color_normalized, normalized_tensor, original_tensor, method, brightness, contrast):
        # Store images for download (full resolution)
        self.current_original = original_image
        denorm_np = denormalized_tensor.permute(1, 2, 0).numpy()
        denorm_np = (denorm_np * 255).astype(np.uint8)
        self.current_pytorch = Image.fromarray(denorm_np)
        self.current_color = color_normalized
        
        # Resize images for display
        display_size = (250, 250)
        original_display = original_image.resize(display_size, Image.Resampling.LANCZOS)
        denormalized_display = self.current_pytorch.resize(display_size, Image.Resampling.LANCZOS)
        color_display = color_normalized.resize(display_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        original_photo = ImageTk.PhotoImage(original_display)
        pytorch_photo = ImageTk.PhotoImage(denormalized_display)
        color_photo = ImageTk.PhotoImage(color_display)
        
        # Update labels
        self.original_label.configure(image=original_photo, text="")
        self.original_label.image = original_photo
        
        self.pytorch_label.configure(image=pytorch_photo, text="")
        self.pytorch_label.image = pytorch_photo
        
        self.color_label.configure(image=color_photo, text="")
        self.color_label.image = color_photo
        
        # Update statistics
        self.stats_text.delete(1.0, tk.END)
        stats = f"""Combined Normalization Results:
{'='*60}

PyTorch Normalization:
- Shape: {normalized_tensor.shape}
- Range: [{normalized_tensor.min().item():.4f}, {normalized_tensor.max().item():.4f}]
- Mean: {normalized_tensor.mean().item():.4f}
- Std: {normalized_tensor.std().item():.4f}

Color Normalization:
- Method: {method}
- Target Brightness: {brightness}
- Target Contrast: {contrast}
- Final Brightness: {np.mean(np.array(color_normalized)):.2f}
- Final Contrast: {np.std(np.array(color_normalized)):.2f}

Parameters Used:
- PyTorch Mean: {[float(var.get()) for var in self.mean_values]}
- PyTorch Std: {[float(var.get()) for var in self.std_values]}
- Color Method: {method}

Comparison:
- Original Image Brightness: {np.mean(np.array(original_image)):.2f}
- PyTorch Normalized Mean: {normalized_tensor.mean().item():.4f}
- Color Normalized Brightness: {np.mean(np.array(color_normalized)):.2f}
"""
        self.stats_text.insert(1.0, stats)

def main():
    root = tk.Tk()
    app = ImageNormalizationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
