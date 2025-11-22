# Poppler Setup for Windows

Poppler is required for the `pdf2image` library to convert PDF files to images. Here's how to install it on Windows:

## Step 1: Download Poppler

1. Go to the [Poppler Windows releases page](https://github.com/oschwartz10612/poppler-windows/releases)
2. Download the **latest release** (currently `Release 25.11.0-0`)
3. Look for the file named `Release-25.11.0-0.zip` (or similar) in the Assets section
4. Download the ZIP file

## Step 2: Extract Poppler

1. Extract the ZIP file to a location on your computer
   - Recommended location: `C:\poppler` or `C:\Program Files\poppler`
   - You can also extract it to your project folder if you prefer

2. After extraction, you should have a folder structure like:
   ```
   poppler-25.11.0-0/
     ├── bin/
     ├── include/
     ├── lib/
     └── share/
   ```

## Step 3: Add Poppler to System PATH

You need to add Poppler's `bin` folder to your Windows PATH so Python can find it.

### Option A: Using System Environment Variables (Recommended)

1. Press `Win + R`, type `sysdm.cpl`, and press Enter
2. Go to the **Advanced** tab
3. Click **Environment Variables**
4. Under **System variables**, find and select **Path**, then click **Edit**
5. Click **New** and add the path to Poppler's `bin` folder:
   - Example: `C:\poppler\Library\bin` or `C:\poppler\bin` (depending on where you extracted it)
6. Click **OK** on all dialogs
7. **Restart your terminal/PowerShell** for changes to take effect

### Option B: Using PowerShell (Temporary - Only for Current Session)

If you don't want to modify system PATH permanently, you can add it temporarily:

```powershell
$env:Path += ";C:\poppler\Library\bin"
```

Replace `C:\poppler\Library\bin` with your actual Poppler bin path.

## Step 4: Verify Installation

Open a **new** PowerShell/Command Prompt window and run:

```powershell
pdftoppm -h
```

If you see help text, Poppler is installed correctly! If you get an error, check that:
- The PATH was added correctly
- You restarted your terminal
- The path to the `bin` folder is correct

## Alternative: Use poppler_path in Code

If you prefer not to modify PATH, you can specify the Poppler path directly in the code. However, this requires modifying the `pdf_processor.py` file to use the `poppler_path` parameter in `convert_from_path()`.

## Troubleshooting

- **"pdftoppm not found"**: Make sure you added the `bin` folder (not the root folder) to PATH
- **Still not working**: Try restarting your computer after adding to PATH
- **Wrong path**: Check the exact location of the `bin` folder in your extracted Poppler directory

## Quick Test

After setup, test if it works by running your backend:

```bash
cd backend
python main.py
```

If you see the server start without errors, Poppler is working correctly!

