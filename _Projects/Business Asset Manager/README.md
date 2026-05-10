# 🗂️ Asset Manager

> Automatically sort your files into organized folders — by file type, instantly.

---

## 📌 What It Does

**Asset Manager** is a lightweight Python script that scans a folder and automatically sorts every file into a named subfolder based on its extension.

No more messy Downloads folders. Run the script once — everything is in its place.

---

## 📂 Sorting Logic

| File Type | Extension | Sorted Into |
|-----------|-----------|-------------|
| Text Files | `.txt` | `Text/` |
| Word Documents | `.docx` | `Doc/` |
| Images | `.png` | `Img/` |
| Videos | `.mp4` | `Ved/` |

Folders are created automatically if they don't already exist.

---

## ✨ Features

- 📁 **Auto Folder Creation** — Subfolders are created on the fly, no manual setup needed
- 🔀 **Smart Sorting** — Moves files based on their extension
- ⚡ **Zero Dependencies** — Uses only Python's built-in `os` and `shutil` libraries
- 🔒 **Safe Moves** — Uses `shutil.move()` so files are relocated, not duplicated

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/asset-manager.git
cd asset-manager
```

### 2. Set Your Target Folder

Open `asset_manager.py` and update the `path` variable to point to your folder:

```python
path = "C:/Users/YourName/Downloads/your-folder"
```

### 3. Run the Script

```bash
python asset_manager.py
```

That's it. Check your folder — everything is sorted.

---

## 🧰 Requirements

- Python 3.9+
- No external libraries needed

---

## ⚠️ Limitations

- Currently supports `.txt`, `.docx`, `.png`, and `.mp4` only
- Files with unrecognized extensions are left in place
- Does not handle subfolders inside the target directory

---

## 🔮 Planned Improvements

- [ ] Support for more file types (`.pdf`, `.jpg`, `.mp3`, `.xlsx`, etc.)
- [ ] Command-line argument for dynamic folder path
- [ ] Undo/restore functionality
- [ ] GUI or Streamlit interface

---

## 🙋 About

Built by a self-taught developer as part of an AI & Python automation learning roadmap.

---

## 📄 License

MIT License — free to use, modify, and distribute.
